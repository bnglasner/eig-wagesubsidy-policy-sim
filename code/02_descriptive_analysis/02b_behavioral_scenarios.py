"""
02b_behavioral_scenarios.py — Dynamic (behavioral) cost of the 80-80 subsidy.

Extends the STATIC cost model (02a) with labor-supply responses, reported as a
SENSITIVITY BAND across the contested elasticity literature (static / lower /
central / upper). The static path in 01a and 02a is NEVER modified — this stage
reads the same hourly_workers.parquet and the same pre-computed PolicyEngine
schedules, and the `static` scenario here reproduces 02a's gross/net cost exactly
(verified by tests/test_behavioral_static_parity.py).

Spec:  Infrastructure/specs/2026-06-25_dynamic-cost-modeling.md
Params: cfg["behavioral"] in code/00_setup/00_config.py (transported, ex-ante).

Model (per worker i, per scenario)
-----------------------------------
Behavioral stimulus — proportional gross wage gain on subsidized hours:
    g_i = subsidy_hr_i / employer_wage_i
Intensive margin (continuing workers change hours):
    hours_mult_i = max(0, 1 + eps_int*g_i - eta_income*(subsidy_annual_i / baseline_income_i))
Extensive margin (induced entrants resembling the marginal worker; expected-value,
not simulated individuals):
    weight_mult_i = 1 + eps_ext*g_i           (>= 1)
    w_continuing_i = weight_i                  (original employed)
    w_entrant_i    = weight_i*(weight_mult_i - 1)
Wage pass-through (employer captures phi of the per-hour subsidy via wage depression;
first-order — the legislated subsidy_hr is held fixed to avoid a GE fixed point):
    employer_wage_eff_i = employer_wage_i - phi*subsidy_hr_i

Government net cost uses the unified identity (derivation in the spec); with
NI(.) the schedule's net household income at a given EARNED income and I_cf the
no-policy counterfactual earned income:
    net_cost_density_i = [NI(I_policy) - NI(I_cf)] - (employer_earned_b_i - I_cf)
    I_policy = employer_earned_b_i + subsidy_annual_b_i   (subsidy treated as income, as in 02a)
    I_cf = baseline_income_i (continuing)  or  0 (entrant: not working -> non-work transfers)
Gross cost density_i = subsidy_annual_b_i (paid on both continuing and entrant weights).

For the static scenario (all params 0): weight_mult=1, hours_mult=1, employer_wage_eff=
employer_wage, so net_cost_density reduces to NI(baseline+subsidy)-NI(baseline) — exactly
02a's net_income delta (with the same ACA/Medicaid add-back), and gross cost is unchanged.

Output (output/data/intermediate_results/population/)
------------------------------------------------------
  behavioral_scenarios.parquet   one row per scenario (band)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Path / config setup (mirrors 02a) ──────────────────────────────────────────
_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_APP = _HERE.parents[2] / "app"

for _p in [str(_CODE / "00_setup"), str(_APP)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg = _cfg_mod.cfg
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED
PATH_OUTPUT_INTERMEDIATE = _cfg_mod.PATH_OUTPUT_INTERMEDIATE

from utils.household_sim import _SCHEDULES_DIR  # noqa: E402

_OUT_DIR = PATH_OUTPUT_INTERMEDIATE / "population"
_OUT_DIR.mkdir(parents=True, exist_ok=True)
_INPUT_PATH = PATH_DATA_PROCESSED / "hourly_workers.parquet"

# Columns interpolated for the net-income identity. net_income plus the two
# in-kind health components 02a adds back (see 02a lines 169-175).
_NI_COLS = ["net_income", "aca_ptc", "medicaid_chip"]

# ── Schedule cache + fallback (mirrors 02a._load_schedule / _lookup_deltas) ─────
_schedule_cache: dict[tuple[str, str], pd.DataFrame | None] = {}


def _load_schedule(family_type_key: str, state_code: str) -> pd.DataFrame | None:
    cache_key = (family_type_key, state_code)
    if cache_key not in _schedule_cache:
        path = _SCHEDULES_DIR / f"{family_type_key}_{state_code}.parquet"
        _schedule_cache[cache_key] = pd.read_parquet(path) if path.exists() else None
    return _schedule_cache[cache_key]


def _resolve_schedule(fkey: str, state: str) -> pd.DataFrame | None:
    """Same fallback ladder as 02a: exact -> single_0c/state -> fkey/TX -> single_0c/TX."""
    for f, s in [(fkey, state), ("single_0c", state), (fkey, "TX"), ("single_0c", "TX")]:
        sched = _load_schedule(f, s)
        if sched is not None:
            return sched
    return None


def _ni_adjusted(schedule: pd.DataFrame, income: np.ndarray) -> np.ndarray:
    """Net household income at `income`, with ACA PTC and Medicaid/CHIP added back
    (mirrors 02a's net_income delta construction). np.interp clamps outside the grid."""
    axis = schedule.index.values.astype(float)
    ni = np.interp(income, axis, schedule["net_income"].values)
    for col in ("aca_ptc", "medicaid_chip"):
        if col in schedule.columns:
            ni = ni + np.interp(income, axis, schedule[col].values)
    return ni


# ── Bounded (saturating) response function ──────────────────────────────────────

def response_multiplier(eps, g, ceiling: float):
    """Behavioral multiplier with local slope `eps` at g->0 and asymptote `ceiling` (M).
    Michaelis-Menten for positive stimulus; linear (bounded at 0) when g<=0 (wage pushed
    below the outside option -> exit). `eps` may be scalar or array; `g` is an array.
        m(g) = 1 + (M-1) * eps*g / ((M-1) + eps*g),  eps*g > 0
             = 1 + eps*g (>=0),                       eps*g <= 0
    Calibrated to the literature elasticity at the margin but bounded for large g."""
    eps = np.asarray(eps, dtype=float)
    g = np.asarray(g, dtype=float)
    eg = eps * g
    M = float(ceiling)
    sat = 1.0 + (M - 1.0) * eg / ((M - 1.0) + eg)   # valid where eg > 0
    lin = np.maximum(0.0, 1.0 + eg)                  # negative-stimulus branch
    return np.where(eg > 0.0, sat, lin)


# ── Demographic cell assignment (for cell-specific extensive elasticities) ──────

def assign_cell(workers: pd.DataFrame) -> np.ndarray:
    """Map each worker to an extensive-margin cell from sex_label + family_type_key.
    single_mothers = Female & single-with-children; other_women = any other Female;
    men = Male. Unknown sex defaults to other_women (the intermediate elasticity)."""
    sex = workers["sex_label"].astype("string").to_numpy() if "sex_label" in workers else None
    fkey = workers["family_type_key"].astype("string").to_numpy()
    cells = np.full(len(workers), "other_women", dtype=object)
    if sex is None:
        return cells
    is_female = sex == "Female"
    is_male = sex == "Male"
    is_single_kids = fkey == "single_2c"
    cells[is_male] = "men"
    cells[is_female & is_single_kids] = "single_mothers"
    cells[is_female & ~is_single_kids] = "other_women"
    return cells


# ── Behavioral transform ────────────────────────────────────────────────────────

def apply_behavioral_response(workers: pd.DataFrame, scn: dict) -> pd.DataFrame:
    """Return per-worker behavioral quantities for one scenario. Pure function of
    `workers` columns and the scenario params; does not mutate `workers`.

    Uses only the columns present in hourly_workers.parquet (annual quantities).
    Subsidized hours are recovered as subsidy_annual / subsidy_hr and the 40 hr/wk
    cap is handled at the annual level: a worker is 'capped' when their subsidized
    hours are below their total annual hours (i.e. they work > 40 hr/wk and the
    overtime hours are unsubsidized). For capped workers the subsidy is frozen at
    the cap as hours rise (marginal hours unsubsidized); for uncapped workers the
    subsidy scales with hours (all hours subsidized). Both are exact at hours_mult=1.
    """
    w = workers
    employer_wage = w["employer_wage"].to_numpy(float)
    annual_hours = w["annual_hours"].to_numpy(float)
    baseline_income = w["baseline_income"].to_numpy(float)
    subsidy_hr = w["subsidy_hr"].to_numpy(float)
    subsidy_annual = w["subsidy_annual"].to_numpy(float)
    weight = w["weight"].to_numpy(float)

    # Cell-specific extensive elasticity: map each worker's cell -> its eps_ext.
    cells = assign_cell(w)
    eps_ext_by_cell = scn["eps_ext"]
    eps_ext = np.array([float(eps_ext_by_cell[c]) for c in cells], dtype=float)
    eps_int = float(scn["eps_int"])
    eta_income = float(scn["eta_income"])
    phi = float(scn["passthrough"])

    # Subsidized annual hours implied by the static subsidy (subsidy_hr > 0 for all eligible).
    subsidy_hours = np.divide(subsidy_annual, subsidy_hr,
                              out=np.zeros_like(subsidy_annual), where=subsidy_hr > 0)
    is_capped = subsidy_hours < annual_hours - 1e-6   # works > 40 hr/wk: overtime unsubsidized

    # Stimulus: proportional gross wage gain on subsidized hours (employer_wage > 0).
    g = np.divide(subsidy_hr, employer_wage,
                  out=np.zeros_like(subsidy_hr), where=employer_wage > 0)

    # Bounded (saturating) responses; local slope = elasticity, asymptote = ceiling.
    sat = cfg.get("behavioral", {}).get("saturation", {"ceiling_ext": 1.5, "ceiling_int": 1.4})
    # Intensive margin (substitution up via the bounded form, income effect down, linear); floored at 0.
    inc_share = np.divide(subsidy_annual, baseline_income,
                          out=np.zeros_like(baseline_income), where=baseline_income > 0)
    hours_mult = np.maximum(0.0, response_multiplier(eps_int, g, sat["ceiling_int"])
                            - eta_income * inc_share)

    # Extensive margin (induced entrants; bounded).
    weight_mult = response_multiplier(eps_ext, g, sat["ceiling_ext"])
    w_entrant = weight * (weight_mult - 1.0)

    # Pass-through: employer trims the cash wage by phi * subsidy_hr (subsidy_hr held fixed).
    employer_wage_eff = employer_wage - phi * subsidy_hr

    # Hours after response, and subsidy on those hours (annual cap rule above).
    annual_hours_b = annual_hours * hours_mult
    subsidy_hours_b = np.where(
        is_capped,
        np.minimum(annual_hours_b, subsidy_hours),  # frozen at cap as hours rise
        annual_hours_b,                              # all hours subsidized
    )
    subsidy_annual_b = subsidy_hr * subsidy_hours_b

    employer_earned_b = employer_wage_eff * annual_hours_b

    return pd.DataFrame({
        "family_type_key": w["family_type_key"].to_numpy(),
        "state_code": w["state_code"].to_numpy(),
        "cell": cells,
        "weight": weight,
        "w_entrant": w_entrant,
        "g": g,
        "baseline_income": baseline_income,      # no-policy counterfactual earned income
        "employer_earned_b": employer_earned_b,   # with-policy employer earnings
        "subsidy_annual_b": subsidy_annual_b,
    }, index=w.index)


def _scenario_costs(workers: pd.DataFrame, scn: dict, income_max: float) -> dict:
    """Aggregate gross/net cost and counts for one scenario."""
    b = apply_behavioral_response(workers, scn)

    i_policy = (b["employer_earned_b"] + b["subsidy_annual_b"]).to_numpy(float)
    i_cf_cont = b["baseline_income"].to_numpy(float)
    employer_earned_b = b["employer_earned_b"].to_numpy(float)

    net_density_cont = np.zeros(len(b), float)
    net_density_ent = np.zeros(len(b), float)

    n_above_grid = 0
    for (fkey, state), idx in b.groupby(["family_type_key", "state_code"]).groups.items():
        schedule = _resolve_schedule(fkey, state)
        pos = b.index.get_indexer(idx)
        if schedule is None:
            continue  # no schedule anywhere -> zero deltas (matches 02a)
        ip = i_policy[pos]
        ni_policy = _ni_adjusted(schedule, ip)
        ni_cf_cont = _ni_adjusted(schedule, i_cf_cont[pos])
        ni_zero = _ni_adjusted(schedule, np.zeros_like(ip))
        eb = employer_earned_b[pos]
        # Unified identity: net cost = [NI(policy) - NI(cf)] - induced employer earnings.
        net_density_cont[pos] = (ni_policy - ni_cf_cont) - (eb - i_cf_cont[pos])
        net_density_ent[pos] = (ni_policy - ni_zero) - eb
        n_above_grid += int(np.sum(ip > income_max))

    w = b["weight"].to_numpy(float)
    we = b["w_entrant"].to_numpy(float)
    subsidy_b = b["subsidy_annual_b"].to_numpy(float)

    gross_cost_bn = float((subsidy_b * (w + we)).sum() / 1e9)
    net_cost_bn = float((net_density_cont * w + net_density_ent * we).sum() / 1e9)
    n_workers_mn = float((w + we).sum() / 1e6)
    induced_mn = float(we.sum() / 1e6)
    avg_g = float((b["g"].to_numpy(float) * w).sum() / w.sum()) if w.sum() else 0.0

    # Induced entrants by demographic cell (the diagnostic for who drives entry).
    cell_arr = b["cell"].to_numpy()
    induced_by_cell = {
        c: round(float(we[cell_arr == c].sum() / 1e6), 2)
        for c in ("single_mothers", "other_women", "men")
    }

    return {
        "eps_ext_men": scn["eps_ext"]["men"],
        "eps_ext_single_mothers": scn["eps_ext"]["single_mothers"],
        "eps_ext_other_women": scn["eps_ext"]["other_women"],
        "eps_int": scn["eps_int"],
        "eta_income": scn["eta_income"], "passthrough": scn["passthrough"],
        "gross_cost_bn": round(gross_cost_bn, 2),
        "net_cost_bn": round(net_cost_bn, 2),
        "recapture_pct": round((1 - net_cost_bn / gross_cost_bn) * 100, 1) if gross_cost_bn else None,
        "n_workers_mn": round(n_workers_mn, 2),
        "induced_workers_mn": round(induced_mn, 2),
        "induced_single_mothers_mn": induced_by_cell["single_mothers"],
        "induced_other_women_mn": induced_by_cell["other_women"],
        "induced_men_mn": induced_by_cell["men"],
        "avg_pct_return_gain": round(avg_g * 100, 1),
        "pct_income_above_grid": round(n_above_grid / max(len(b), 1) * 100, 1),
        "source": scn["source"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    bcfg = cfg.get("behavioral", {})
    if not bcfg.get("enabled", False):
        print("02b | behavioral modeling disabled in config — skipping.")
        return
    if not _INPUT_PATH.exists():
        raise FileNotFoundError(
            f"hourly_workers.parquet not found at {_INPUT_PATH}\nRun 01a_data_ingest.py first."
        )

    print("02b | Loading hourly_workers.parquet …")
    workers = pd.read_parquet(_INPUT_PATH)
    print(f"  Records: {len(workers):,}")

    income_max = float(bcfg.get("schedule_income_max", 65000.0))
    scenarios = bcfg["scenarios"]

    rows = []
    print("02b | Computing behavioral cost band (transported ex-ante elasticities) …")
    for name, scn in scenarios.items():
        res = _scenario_costs(workers, scn, income_max)
        res = {"scenario": name, **res}
        rows.append(res)
        print(f"  {name:8s} | gross ${res['gross_cost_bn']:6.2f}B | net ${res['net_cost_bn']:6.2f}B "
              f"| recapture {res['recapture_pct']}% | workers {res['n_workers_mn']:.2f}M "
              f"(+{res['induced_workers_mn']:.2f}M induced) | avg wage gain {res['avg_pct_return_gain']}%")
        if res["induced_workers_mn"] > 0:
            print(f"           induced by cell: single mothers {res['induced_single_mothers_mn']}M | "
                  f"other women {res['induced_other_women_mn']}M | men {res['induced_men_mn']}M")
        if res["pct_income_above_grid"] > 0:
            print(f"           [warn] {res['pct_income_above_grid']}% of workers exceed the "
                  f"${income_max:,.0f} schedule grid (taxes/transfers clamped at the top — "
                  f"consider extending the grid in 01b).")

    band = pd.DataFrame(rows)
    out_path = _OUT_DIR / "behavioral_scenarios.parquet"
    band.to_parquet(out_path, index=False)
    print(f"\n02b | Complete. Wrote {out_path}")
    print("  NOTE: elasticities are TRANSPORTED ex-ante assumptions (no wage-fill estimate "
          "exists); the bottom-end proportional wage gain is large, so eps*g likely overstates "
          "responses. Report the band, not a single point. See the spec for disclosures.")


if __name__ == "__main__":
    main()
