"""
01i_household_links.py — Real within-household links from the raw CPS ORG rosters.

Replaces the withdrawn plan to statistically match the non-employed pool to ASEC earner
households (rev1 W4): that match was blocked (ASEC microdata absent from this checkout) and,
as specified, econometrically vacuous as an exclusion restriction (matched spouse income is a
function of the same covariates already in the selection equation — see
Infrastructure/explorations/2026-07-08_entry-remodel-methodology-stress-test.md, ST-5/ST-6).
The raw ORG partitions are full rectangular household extracts (all persons, RELATE roster),
so real spouse links are buildable directly:

  - Spouse identification: RELATE head (101) <-> spouse-of-head (202/203) pairing within
    (YEAR, MONTH, SERIAL). No SPLOC in the current extract, so married persons in complex
    households where neither partner is head (~3.4% of married-spouse-present adults; ~5.1%
    within the non-employed pool) are flagged unlinkable rather than guessed. A queued SPLOC
    re-pull closes this gap later (rev2 Decision 6).
  - spouse_is_employed: spouse EMPSTAT in {10,12}. EMPSTAT is populated for all persons 15+
    in every rotation, so this covers the full pool, not just ORG months.
  - spouse_earnweek: spouse EARNWEEK2 with the *2-era sentinel stripped — observed only in
    the spouse's own ORG rotation (MISH 4/8), kept for sensitivity use, NOT the primary shifter.
  - own_child_under5: for heads/spouses, any own child (RELATE 301) with AGE < 5 in the
    household — essentially exact for that group (0.11% inconsistency vs NCHILD). For
    non-head/spouse persons, own-child attribution is ambiguous without MOMLOC/POPLOC; the
    household-level flag below is the disclosed fallback (a queued NCHLT5 re-pull replaces both).
  - hh_child_under5: any household member with AGE < 5 (childcare-NEED proxy; over-attributes
    own-child status by ~1.3pp for heads/spouses, mostly co-resident grandchildren).
  - hh_other_nonemployed_adult: another non-employed 16-64 adult in the household (crude
    informal-childcare / shared-fixed-cost shifter; disclosed as weak).

Output: data/processed/household_links.parquet — one row per person 16-64 in the raw
partitions, keyed by (YEAR, MONTH, SERIAL, PERNUM). 01h merges this onto its estimation
sample and non-employed pool.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
PATH_PROJECT = _cfg_mod.PATH_PROJECT
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED

_EMPLOYED_EMPSTAT = {10, 12}
_HEAD, _SPOUSE_CODES = 101, {201, 202, 203}
_HH_KEY = ["YEAR", "MONTH", "SERIAL"]


def _find_raw_org_dir() -> Path | None:
    import os
    env = os.environ.get("EIG_ORG_RAW_DIR", "")
    cands = ([Path(env)] if env else []) + [
        PATH_PROJECT / "data" / "raw" / "cps_org",
        PATH_PROJECT.parent / "EIG-Wage-Figure-Explain-Everything" / "data" / "raw" / "cps_org"]
    for c in cands:
        if c.is_dir() and list(c.glob("year=*/part-0.parquet")):
            return c
    return None


def _strip_earnweek_sentinel(ew: np.ndarray, yr: np.ndarray, mo: np.ndarray) -> np.ndarray:
    """EARNWEEK sentinel, era-specific (mirrors 01h): legacy 9999.99 through 2023m3;
    *2-era magic 999999.99 after."""
    star2 = (yr > 2023) | ((yr == 2023) & (mo >= 4))
    return np.where(ew >= np.where(star2, 999999.99, 9999.99), np.nan, ew)


def build_links(org: pd.DataFrame) -> pd.DataFrame:
    """Person-level link table for all persons 16-64 in `org` (full rosters required)."""
    cols = ["YEAR", "MONTH", "SERIAL", "PERNUM", "RELATE", "AGE", "MARST", "EMPSTAT", "MISH"]
    ew_col = "EARNWEEK2" if "EARNWEEK2" in org.columns else None
    roster = org[cols + ([ew_col] if ew_col else [])].copy()
    for c in ("YEAR", "MONTH", "SERIAL", "PERNUM", "RELATE", "AGE", "MARST", "EMPSTAT", "MISH"):
        roster[c] = roster[c].astype(float)

    # Household-level aggregates over the FULL roster (all ages).
    hh = roster.groupby(_HH_KEY, sort=False)
    hh_any_under5 = hh["AGE"].agg(lambda a: bool((a < 5).any()))
    hh_own_child_under5 = roster[roster["RELATE"] == 301].groupby(_HH_KEY)["AGE"].agg(
        lambda a: bool((a < 5).any()))
    n_nonemp_adult = roster[(roster["AGE"].between(16, 64)) &
                            (~roster["EMPSTAT"].isin(list(_EMPLOYED_EMPSTAT)))].groupby(_HH_KEY).size()

    # Spouse pairing: exactly the head (101) and the spouse-of-head (201/202/203) per household.
    heads = roster[roster["RELATE"] == _HEAD].set_index(_HH_KEY)
    spouses = roster[roster["RELATE"].isin(list(_SPOUSE_CODES))].set_index(_HH_KEY)
    # No household carries >1 spouse record in this extract (verified 2026-07-08); guard anyway.
    spouses = spouses[~spouses.index.duplicated(keep="first")]
    heads = heads[~heads.index.duplicated(keep="first")]

    def _partner_frame(members: pd.DataFrame, partners: pd.DataFrame) -> pd.DataFrame:
        """For each member row (indexed by hh), pull the partner's PERNUM/EMPSTAT/EARNWEEK/MISH."""
        j = members.join(partners[["PERNUM", "EMPSTAT", "MISH"] + ([ew_col] if ew_col else [])],
                         rsuffix="_sp", how="left")
        return j

    heads_j = _partner_frame(heads, spouses)
    spouses_j = _partner_frame(spouses, heads)
    linked = pd.concat([heads_j, spouses_j]).reset_index()

    out = roster[roster["AGE"].between(16, 64)][_HH_KEY + ["PERNUM", "RELATE", "MARST", "EMPSTAT"]].copy()
    link_cols = _HH_KEY + ["PERNUM", "PERNUM_sp", "EMPSTAT_sp", "MISH_sp"] + \
        ([f"{ew_col}_sp"] if ew_col else [])
    out = out.merge(linked[link_cols], on=_HH_KEY + ["PERNUM"], how="left")

    married = out["MARST"].isin([1.0, 2.0])
    has_partner = out["PERNUM_sp"].notna()
    out["spouse_linkable"] = (married & has_partner)
    out["spouse_is_employed"] = np.where(
        out["spouse_linkable"], out["EMPSTAT_sp"].isin(list(_EMPLOYED_EMPSTAT)), False)
    # Spouse weekly earnings: only meaningful in the spouse's ORG rotation (MISH 4/8).
    if ew_col:
        ew = out[f"{ew_col}_sp"].to_numpy(float)
        yr = out["YEAR"].to_numpy(float)
        mo = out["MONTH"].to_numpy(float)
        ew = _strip_earnweek_sentinel(ew, yr, mo)
        in_org = out["MISH_sp"].isin([4.0, 8.0]).to_numpy()
        out["spouse_earnweek"] = np.where(out["spouse_linkable"] & in_org, ew, np.nan)
    else:
        out["spouse_earnweek"] = np.nan

    # Child flags. Own-child version is head/spouse-accurate only; others get the HH fallback.
    idx = out.set_index(_HH_KEY).index
    out["hh_child_under5"] = hh_any_under5.reindex(idx).astype("boolean").fillna(False).to_numpy(bool)
    own_u5 = hh_own_child_under5.reindex(idx).astype("boolean").fillna(False).to_numpy(bool)
    is_head_or_spouse = out["RELATE"].isin([float(_HEAD)] + [float(c) for c in _SPOUSE_CODES])
    out["own_child_under5"] = np.where(is_head_or_spouse, own_u5, out["hh_child_under5"])
    out["child_under5_source"] = np.where(is_head_or_spouse, "own_roster", "hh_fallback")
    # "Another non-employed 16-64 adult in the household": subtract self only when self is
    # non-employed (CE-004 — a flat -1 undercounted for employed persons).
    self_nonemp = (~out["EMPSTAT"].isin(list(_EMPLOYED_EMPSTAT))).to_numpy().astype(float)
    out["hh_other_nonemployed_adult"] = (
        n_nonemp_adult.reindex(idx).fillna(0).to_numpy(float) - self_nonemp) > 0

    keep = _HH_KEY + ["PERNUM", "spouse_linkable", "spouse_is_employed", "spouse_earnweek",
                      "own_child_under5", "hh_child_under5", "child_under5_source",
                      "hh_other_nonemployed_adult"]
    for k in ("YEAR", "MONTH", "SERIAL", "PERNUM"):
        out[k] = out[k].astype(np.int64)
    return out[keep]


def main() -> None:
    raw_dir = _find_raw_org_dir()
    if raw_dir is None:
        print("01i | Raw ORG partitions not found — cannot build household links.")
        return
    parts = sorted(raw_dir.glob("year=*/part-0.parquet"))[-2:]
    org = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    print(f"01i | Read {len(org):,} raw ORG rows ({[p.parent.name for p in parts]})")
    links = build_links(org)
    out_path = PATH_DATA_PROCESSED / "household_links.parquet"
    links.to_parquet(out_path, index=False)
    n_married_linkable = links["spouse_linkable"].sum()
    print(f"01i | Wrote {out_path} | {len(links):,} persons 16-64 | "
          f"spouse-linkable: {n_married_linkable:,} "
          f"| spouse employed among linkable: {links.loc[links['spouse_linkable'], 'spouse_is_employed'].mean():.1%} "
          f"| spouse earnings observed: {links['spouse_earnweek'].notna().sum():,} "
          f"| own_child_under5: {links['own_child_under5'].mean():.1%} "
          f"(hh fallback share: {(links['child_under5_source'] == 'hh_fallback').mean():.1%})")


if __name__ == "__main__":
    main()
