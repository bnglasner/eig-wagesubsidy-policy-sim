"""
02c_incidence.py — Wage incidence with entrants entering at the BOTTOM of the distribution.

Rebuilt after recognizing the prior version's flaw: it cloned extensive-margin entrants into
every wage band, manufacturing supply shifts (and wage declines, and subsidy backfill) in the
middle and upper bands where new low-skill workers would never actually land. The corrected
theory: induced entrants are low-productivity and enter at the bottom of the wage ladder, so the
supply shock — and any wage decline — localizes there (where the minimum wage then converts it
into rationing/queuing rather than a wage cut). Middle/upper bands receive no entrants, so with a
near-zero hours response their wages, and their subsidies, are essentially unchanged.

Mechanism, market by market (competitive incidence; labor demand fixed; eta_d is an own-group
elasticity applied within a band):
  - Incumbents stay in their band; their only supply change is the (near-zero) HOURS margin.
  - Induced entrants are sized from the cell-specific extensive response and POOLED, then placed
    across bands at/below entry_ceiling (proportional to incumbent density) — low entry wages.
  - Each band clears its own supply shift against demand at the realized (floor-truncated) wage;
    where the floor binds (bottom), excess supply is rationed (queuing, not jobs).

Params: cfg["behavioral"]["incidence"] (eta_d, entry_ceiling, comp_floor_frac, ...) and the
scenario eps_int (intensive, near-zero central). Spec: Amendment 1, A1.2d.

Output: incidence_decomposition.parquet (waterfall) + incidence_by_segment.parquet (per band).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_APP = _HERE.parents[2] / "app"
for _p in [str(_CODE / "00_setup"), str(_APP)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg = _cfg_mod.cfg
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED
PATH_OUTPUT_INTERMEDIATE = _cfg_mod.PATH_OUTPUT_INTERMEDIATE

_b_spec = importlib.util.spec_from_file_location(
    "mod_02b", _CODE / "02_descriptive_analysis" / "02b_behavioral_scenarios.py"
)
_b = importlib.util.module_from_spec(_b_spec)
_b_spec.loader.exec_module(_b)

_OUT_DIR = PATH_OUTPUT_INTERMEDIATE / "population"
_INPUT_PATH = PATH_DATA_PROCESSED / "hourly_workers.parquet"
FED_MIN = float(cfg.get("ws_base_wage", 7.25))
SUBSIDY_PCT = float(cfg.get("ws_subsidy_pct", 0.80))
_SAT = cfg.get("behavioral", {}).get("saturation", {"ceiling_ext": 1.5, "ceiling_int": 1.4})


def _recover_target(w: pd.DataFrame) -> float:
    ew = w["employer_wage"].to_numpy(float)
    shr = w["subsidy_hr"].to_numpy(float)
    return float(np.median(ew + shr / SUBSIDY_PCT))


def entrant_placement(w: pd.DataFrame, scn: dict, entry_ceiling: float) -> np.ndarray:
    """Total induced entrants (sized from the cell-specific extensive response at baseline
    wages) distributed across bands at/below entry_ceiling, proportional to incumbent weight.
    Entrants are low-skill and enter low; they are NOT cloned into middle/upper bands."""
    w0 = w["employer_wage"].to_numpy(float)
    shr = w["subsidy_hr"].to_numpy(float)
    weight = w["weight"].to_numpy(float)
    g_base = np.divide(shr, w0, out=np.zeros_like(shr), where=w0 > 0)
    cells = _b.assign_cell(w)
    eps_ext = np.array([float(scn["eps_ext"][c]) for c in cells], dtype=float)
    m_ext = _b.response_multiplier(eps_ext, g_base, _SAT["ceiling_ext"])
    e_want = float((weight * (m_ext - 1.0)).sum())          # total people pulled into work
    bottom = w0 <= entry_ceiling
    placed = np.zeros(len(w), float)
    denom = float(weight[bottom].sum())
    if denom > 0:
        placed[bottom] = weight[bottom] / denom * e_want      # land at the bottom of the ladder
    return placed


def _behavioral(w: pd.DataFrame, scn: dict, theta_vec: np.ndarray, target: float,
                floor_frac: float, w_entrant_placed: np.ndarray,
                absorption: np.ndarray | None = None) -> dict:
    """Per-worker quantities. Incumbents adjust only HOURS (intensive); entrants are the
    pre-placed bottom pool. `absorption` rations the induced hours AND the entrants where the
    wage floor binds. The outside-option floor keeps comp >= floor_frac*w0."""
    w0 = w["employer_wage"].to_numpy(float)
    annual_hours = w["annual_hours"].to_numpy(float)
    baseline_income = w["baseline_income"].to_numpy(float)
    subsidy_hr0 = w["subsidy_hr"].to_numpy(float)
    subsidy_annual0 = w["subsidy_annual"].to_numpy(float)
    weight = w["weight"].to_numpy(float)

    subsidy_hours0 = np.divide(subsidy_annual0, subsidy_hr0,
                               out=np.zeros_like(subsidy_annual0), where=subsidy_hr0 > 0)
    is_capped = subsidy_hours0 < annual_hours - 1e-6
    eps_int = float(scn["eps_int"])

    floor_wage = np.maximum(FED_MIN, 5.0 * floor_frac * w0 - 4.0 * target)
    w_emp = np.maximum(theta_vec * w0, floor_wage)
    s_hr = SUBSIDY_PCT * np.maximum(0.0, target - w_emp)
    comp = w_emp + s_hr
    g = np.divide(comp - w0, w0, out=np.zeros_like(comp), where=w0 > 0)

    hours_mult = _b.response_multiplier(eps_int, g, _SAT["ceiling_int"])
    w_entrant = np.asarray(w_entrant_placed, dtype=float).copy()
    if absorption is not None:
        hours_mult = 1.0 + absorption * (hours_mult - 1.0)
        w_entrant = absorption * w_entrant

    annual_hours_b = annual_hours * hours_mult
    subsidy_hours_b = np.where(is_capped, np.minimum(annual_hours_b, subsidy_hours0), annual_hours_b)
    subsidy_annual_b = s_hr * subsidy_hours_b
    employer_earned_b = w_emp * annual_hours_b

    return {
        "weight": weight, "w_entrant": w_entrant,
        "annual_hours_b": annual_hours_b, "subsidy_annual_b": subsidy_annual_b,
        "employer_earned_b": employer_earned_b, "baseline_income": baseline_income,
        "w0": w0, "w_emp": w_emp,
        "L_s": (weight + w_entrant) * annual_hours_b,
    }


def _cost(w: pd.DataFrame, arr: dict) -> tuple:
    employer_earned_b = arr["employer_earned_b"]; subsidy_annual_b = arr["subsidy_annual_b"]
    baseline_income = arr["baseline_income"]; weight, we = arr["weight"], arr["w_entrant"]
    i_policy = employer_earned_b + subsidy_annual_b
    net_cont = np.zeros(len(w), float); net_ent = np.zeros(len(w), float)
    key = pd.DataFrame({"f": w["family_type_key"].to_numpy(), "s": w["state_code"].to_numpy()}, index=w.index)
    for (fkey, state), idx in key.groupby(["f", "s"]).groups.items():
        sched = _b._resolve_schedule(fkey, state)
        pos = key.index.get_indexer(idx)
        if sched is None:
            continue
        ni_p = _b._ni_adjusted(sched, i_policy[pos])
        ni_cf = _b._ni_adjusted(sched, baseline_income[pos])
        ni_0 = _b._ni_adjusted(sched, np.zeros_like(i_policy[pos]))
        eb = employer_earned_b[pos]
        net_cont[pos] = (ni_p - ni_cf) - (eb - baseline_income[pos])
        net_ent[pos] = (ni_p - ni_0) - eb
    gross = float((subsidy_annual_b * (weight + we)).sum() / 1e9)
    net = float((net_cont * weight + net_ent * we).sum() / 1e9)
    savings = float(((arr["w0"] - arr["w_emp"]) * arr["annual_hours_b"] * (weight + we)).sum() / 1e9)
    return gross, net, savings


def _solve_segmented(w, scn, eta_d, target, icfg, placed):
    floor_frac = float(icfg["comp_floor_frac"]); hard_floor = float(icfg["theta_hard_floor"])
    tol, max_iter = float(icfg["tol"]), int(icfg["max_iter"]); width = float(icfg["segment_width"])
    seg = np.floor(w["employer_wage"].to_numpy(float) / width).astype(int)
    theta_vec = np.ones(len(w), float); absorption_vec = np.ones(len(w), float)
    annual_hours = w["annual_hours"].to_numpy(float); weight = w["weight"].to_numpy(float)
    for s in np.unique(seg):
        m = seg == s
        L0 = float((weight[m] * annual_hours[m]).sum())
        if L0 <= 0:
            continue
        hrs0 = weight[m] * annual_hours[m]; w_sub = w.loc[m]; placed_sub = placed[m]

        def metrics(theta):
            a = _behavioral(w_sub, scn, np.full(m.sum(), theta), target, floor_frac, placed_sub)
            theta_real = float((a["w_emp"] * hrs0).sum() / (a["w0"] * hrs0).sum())
            return a["L_s"].sum(), L0 * theta_real ** eta_d

        def excess(theta):
            ls, ld = metrics(theta); return (ls - ld) / L0

        if excess(1.0) <= tol:
            theta_s = 1.0
        elif excess(hard_floor) > 0:
            theta_s = hard_floor
        else:
            lo, hi = hard_floor, 1.0; theta_s = 0.5 * (lo + hi)
            for _ in range(max_iter):
                mid = 0.5 * (lo + hi); e = excess(mid); theta_s = mid
                if abs(e) < tol:
                    break
                hi, lo = (mid, lo) if e > 0 else (hi, mid)
        ls, ld = metrics(theta_s); induced = ls - L0
        rho = 1.0 if induced <= 1e-9 else min(1.0, max(0.0, (ld - L0) / induced))
        theta_vec[m] = theta_s; absorption_vec[m] = rho
    return theta_vec, absorption_vec


def _wage_change_pct(arr):
    hrs = arr["annual_hours_b"] * (arr["weight"] + arr["w_entrant"])
    return float(((arr["w_emp"] / arr["w0"] - 1.0) * hrs).sum() / hrs.sum() * 100) if hrs.sum() else 0.0


def main() -> None:
    bcfg = cfg.get("behavioral", {}); icfg = bcfg.get("incidence", {})
    if not bcfg.get("enabled") or not icfg.get("enabled"):
        print("02c | incidence modeling disabled — skipping."); return
    if not _INPUT_PATH.exists():
        raise FileNotFoundError(f"{_INPUT_PATH} not found. Run 01a first.")

    print("02c | Loading hourly_workers.parquet …")
    w = pd.read_parquet(_INPUT_PATH)
    target = _recover_target(w); floor = float(icfg["comp_floor_frac"])
    central = bcfg["scenarios"]["central"]
    placed = entrant_placement(w, central, float(icfg["entry_ceiling"]))
    ones = np.ones(len(w)); zero = np.zeros(len(w))
    print(f"  Target ${target:.2f}/hr | entrants enter <= ${icfg['entry_ceiling']:.0f}/hr "
          f"(pool {placed.sum()/1e6:.2f}M, central) | intensive eps_int={central['eps_int']}")

    static = {**central, "eps_ext": {k: 0.0 for k in central["eps_ext"]}, "eps_int": 0.0}
    entry = {**central, "eps_int": 0.0}
    rows = []
    for label, sc, pl in [("static", static, zero), ("+entry", entry, placed),
                          ("+entry+hours (no incidence)", central, placed)]:
        g, n, _ = _cost(w, _behavioral(w, sc, ones, target, floor, pl))
        rows.append({"step": label, "eta_d": None, "wage_change_pct": 0.0,
                     "gross_cost_bn": round(g, 2), "net_cost_bn": round(n, 2), "worker_capture_pct": 100.0})

    for tag, eta_d in icfg["eta_d"].items():
        th, ab = _solve_segmented(w, central, eta_d, target, icfg, placed)
        arr = _behavioral(w, central, th, target, floor, placed, absorption=ab)
        g, n, sav = _cost(w, arr)
        rows.append({"step": f"+incidence ({tag})", "eta_d": eta_d,
                     "wage_change_pct": round(_wage_change_pct(arr), 1),
                     "gross_cost_bn": round(g, 2), "net_cost_bn": round(n, 2),
                     "worker_capture_pct": round((1 - sav / g) * 100, 1) if g else None})

    pd.DataFrame(rows).to_parquet(_OUT_DIR / "incidence_decomposition.parquet", index=False)
    print(f"  {'step':<30} | {'eta_d':>6} | {'wage Δ':>7} | {'gross':>7} | {'net':>7} | {'wkr cap':>7}")
    for r in rows:
        ed = f"{r['eta_d']:6.2f}" if r["eta_d"] is not None else "   n/a"
        print(f"  {r['step']:<30} | {ed} | {r['wage_change_pct']:6.1f}% | "
              f"{r['gross_cost_bn']:6.2f} | {r['net_cost_bn']:6.2f} | {r['worker_capture_pct']:6.1f}%")

    # Per-band diagnostics at central eta_d.
    th, ab = _solve_segmented(w, central, icfg["eta_d"]["central"], target, icfg, placed)
    arr = _behavioral(w, central, th, target, floor, placed, absorption=ab)
    seg = np.floor(w["employer_wage"].to_numpy(float) / float(icfg["segment_width"])).astype(int)
    w0 = w["employer_wage"].to_numpy(float)
    seg_rows = []
    for s in np.unique(seg):
        m = seg == s
        L0 = float((w.loc[m, "weight"] * w.loc[m, "annual_hours"]).sum())
        if L0 <= 0:
            continue
        hrs = arr["annual_hours_b"][m] * (arr["weight"][m] + arr["w_entrant"][m])
        wage_chg = float(((arr["w_emp"][m] / w0[m] - 1.0) * hrs).sum() / hrs.sum()) if hrs.sum() else 0.0
        seg_rows.append({
            "wage_band": f"${s:.0f}-{s+1:.0f}",
            "incumbents_k": round(float(w.loc[m, "weight"].sum()) / 1e3, 1),
            "entrants_realized_k": round(float(arr["w_entrant"][m].sum()) / 1e3, 1),
            "wage_change_pct": round(wage_chg * 100, 1),
            "absorption": round(float(np.unique(ab[m])[0]), 2),
        })
    pd.DataFrame(seg_rows).to_parquet(_OUT_DIR / "incidence_by_segment.parquet", index=False)
    print(f"\n  Per-band (central): incumbents | realized entrants | wage change | absorption")
    for r in seg_rows:
        print(f"    {r['wage_band']:>8} | {r['incumbents_k']:8.1f}k | ent {r['entrants_realized_k']:7.1f}k "
              f"| wage {r['wage_change_pct']:6.1f}% | absorb {r['absorption']:.2f}")
    print(f"\n02c | Complete. Wrote incidence_decomposition.parquet + incidence_by_segment.parquet")


if __name__ == "__main__":
    main()
