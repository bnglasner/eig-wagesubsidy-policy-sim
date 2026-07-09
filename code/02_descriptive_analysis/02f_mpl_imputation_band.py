"""
02f_mpl_imputation_band.py — MPL-imputation sensitivity band (methodology review MR-001).

The non-employed pool's potential wage (MPL) is imputed by a Heckman two-step whose selection
correction has no bulletproof exclusion restriction, so it is identified off the inverse-Mills
functional form. The headline pipeline uses the conditional (D=0 selection-consistent)
prediction. This script bounds that fragility: it rebuilds the pool under all three imputations
the two-step produces — conditional, Mills=0 (unconditional), and plain OLS (no IMR) — and
reports induced entry and entrant fiscal cost (central band edge, beta=central, rigid) under
each. The spread is the MPL-imputation uncertainty the draft discloses alongside the
elasticity band.

Mechanism: re-run 01h with EIG_MPL_IMPUTATION set (writes suffixed pool files; the canonical
nonemployed_pool.parquet — the conditional variant — is NOT touched), then run 02d's
_entrants_from_pool on each pool.

Output: output/data/intermediate_results/population/mpl_imputation_band.parquet
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_ROOT = _HERE.parents[2]
_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg = importlib.util.module_from_spec(_cfg_spec); _cfg_spec.loader.exec_module(_cfg)
PATH_DATA_PROCESSED = _cfg.PATH_DATA_PROCESSED
POP = _cfg.PATH_OUTPUT_INTERMEDIATE / "population"

# Import 02d for the entrant calculation and target recovery.
_d_spec = importlib.util.spec_from_file_location(
    "mod_02d", _CODE / "02_descriptive_analysis" / "02d_matching_simulation.py")
_d = importlib.util.module_from_spec(_d_spec); sys.modules["mod_02d"] = _d; _d_spec.loader.exec_module(_d)

# Two disclosed uncertainty axes over the pool's imputed potential wage (MPL):
#   axis "imputation" — the three Heckman prediction variants (MR-001). On the paid-hourly
#     frame (E2, 2026-07-09) these nearly converge, showing the earlier 7x entry spread was
#     substantially salaried-frame contamination.
#   axis "penalty" — an explicit non-employment wage-offer penalty {0, 10%, 20%} anchored to
#     Schmieder-von Wachter-Bender (2016, ~0.8%/month offer decay) and Krueger-Mueller (2016,
#     accepted wages ~0.90x prior): the unobserved-penalty evidence the weakly-identified
#     selection correction cannot detect. This is now the DOMINANT MPL uncertainty.
_VARIANTS = {
    "conditional": ("nonemployed_pool.parquet", "imputation",
                    "conditional Mills (D=0) — headline", {}),
    "mills0": ("nonemployed_pool__mills0.parquet", "imputation",
               "Mills=0 (unconditional)", {"EIG_MPL_IMPUTATION": "mills0"}),
    "plain": ("nonemployed_pool__plain.parquet", "imputation",
              "plain OLS (no IMR)", {"EIG_MPL_IMPUTATION": "plain"}),
    "pen10": ("nonemployed_pool__pen10.parquet", "penalty",
              "10% non-employment wage penalty (Schmieder/KM-anchored)", {"EIG_MPL_PENALTY": "0.10"}),
    "pen20": ("nonemployed_pool__pen20.parquet", "penalty",
              "20% non-employment wage penalty (long-spell bound)", {"EIG_MPL_PENALTY": "0.20"}),
    # Offer-dispersion band (2026-07-09): lambda scales the group residual SD used for the
    # mean-preserving offer spread (headline lambda = 0.75, nets out CPS measurement error).
    "lam050": ("nonemployed_pool__lam50.parquet", "dispersion",
               "offer dispersion lambda=0.50 (conservative)", {"EIG_MPL_LAMBDA": "0.50"}),
    "lam100": ("nonemployed_pool__lam100.parquet", "dispersion",
               "offer dispersion lambda=1.00 (full residual)", {"EIG_MPL_LAMBDA": "1.00"}),
    # Left-skew hypothesis (2026-07-09): duration-heterogeneous penalties by prior status
    # (unemployed small per KM accepted-wage evidence; long-detached groups large per
    # compounded Schmieder decay) — a mixture that left-skews the aggregate offer
    # distribution instead of shifting it uniformly.
    "skewstat": ("nonemployed_pool__skewstat.parquet", "skew",
                 "status-mixture penalty (U 5% / NILF 15% / dis+ret 20%) — left-skewed offers",
                 {"EIG_MPL_STATUS_PENALTY": "unemployed:0.05,nilf_other:0.15,disabled:0.20,retired:0.20"}),
    "skewstat_hi": ("nonemployed_pool__skewstat_hi.parquet", "skew",
                    "heavier mixture (U 10% / NILF 25% / dis+ret 30%) — strong left skew",
                    {"EIG_MPL_STATUS_PENALTY": "unemployed:0.10,nilf_other:0.25,disabled:0.30,retired:0.30",
                     "EIG_POOL_TAG": "_hi"}),
}
TARGET = float(_cfg.cfg.get("ws_target_wage", 16.80))


def _build_variant_pool(env_over: dict) -> None:
    """Re-run 01h with selector env vars to produce the suffixed pool."""
    env = dict(os.environ, **env_over)
    subprocess.run([sys.executable, str(_CODE / "01_data_preparation" / "01h_nonemployed_pool.py")],
                   cwd=str(_ROOT), env=env, check=True)


def main() -> None:
    mcfg = _cfg.cfg.get("matching", {})
    beta_c = float(mcfg["beta"]["central"])
    # Recover the target the incumbent side uses (keeps entrants on the same target as 02d).
    w = pd.read_parquet(PATH_DATA_PROCESSED / "hourly_workers.parquet")
    target = _d._recover_target(w)

    rows = []
    for variant, (fname, axis, label, env_over) in _VARIANTS.items():
        path = PATH_DATA_PROCESSED / fname
        if variant != "conditional":
            _build_variant_pool(env_over)         # conditional pool already on disk (canonical)
        if not path.exists():
            print(f"02f | [warn] {fname} missing — skipping {variant}."); continue
        pool = pd.read_parquet(path)
        mp = pool["mpl"].to_numpy(float); wt = pool["weight"].to_numpy(float)
        med = float(np.asarray(mp)[np.argsort(mp)][np.searchsorted(
            np.cumsum(wt[np.argsort(mp)]), wt.sum() * 0.5)])
        pct_below = 100 * wt[mp < TARGET].sum() / wt.sum()
        ge, ne, fce, induced_M, by_cell, det = _d._entrants_from_pool(pool, beta_c, target, edge="central")
        rows.append({
            "variant": variant, "axis": axis, "label": label,
            "pool_median_mpl": round(med, 2), "pct_mpl_below_target": round(pct_below, 1),
            "induced_M": induced_M,
            **{f"induced_{c}_M": v for c, v in by_cell.items()},
            "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1),
        })
    band = pd.DataFrame(rows)
    POP.mkdir(parents=True, exist_ok=True)
    out = POP / "mpl_imputation_band.parquet"
    band.to_parquet(out, index=False)
    print(f"\n02f | Wrote {out}")
    print(band.to_string(index=False))
    # Clean up the non-canonical suffixed pools so they do not pollute the manifest/consumers.
    for variant, (fname, _, _, _) in _VARIANTS.items():
        if variant == "conditional":
            continue
        for p in (PATH_DATA_PROCESSED / fname,
                  PATH_DATA_PROCESSED / fname.replace("nonemployed_pool", "nonemployed_pool_diagnostics").replace(".parquet", ".json")):
            if p.exists():
                p.unlink()


if __name__ == "__main__":
    main()
