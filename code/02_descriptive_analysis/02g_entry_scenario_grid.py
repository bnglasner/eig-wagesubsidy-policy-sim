"""
02g_entry_scenario_grid.py — Joint scenario grid + full decomposition for induced entry.

Holistic-evaluation follow-up (2026-07-09, user sign-off). The 0.83M headline was a THREE-WAY
conservative floor (non-employment penalty 0, offer-dispersion λ 0.75, accepted-wage σ) presented
as a neutral central; and the 02f uncertainty band varied ONE axis at a time, hiding the joint
envelope (interacting levers compound super-additively through reachability and the per-cell
λ-bisection). This stage resolves both:

  1. **Headline scenarios** (`entry_headline_scenarios.parquet`) — three internally-consistent,
     jointly-specified bundles:
       - Conservative floor : penalty 0, λ 0.75, eps central   (the current 0.83M, now LABELED)
       - Evidence-central   : status-differentiated penalty (mean ≈10%), λ 0.75, eps central
       - High               : penalty 20%, λ 1.00, eps upper   (a joint corner)
  2. **Full decomposition** (`entry_scenario_grid.parquet`) — the 27-cell cartesian product
     penalty {0,10,20%} × λ {0.5,0.75,1.0} × eps {lower,central,upper}. Because each pool carries
     required_net_gain_{lower,central,upper}, the 3 eps edges are read off each pool for free, so
     the 27 cells come from only 9 pool builds.

Mechanism: rebuild 01h with the selector env vars 02f already defines (EIG_MPL_PENALTY,
EIG_MPL_LAMBDA, EIG_MPL_STATUS_PENALTY), read each suffixed pool, and run 02d's
_entrants_from_pool on it. The canonical nonemployed_pool.parquet is never touched; suffixed pools
are cleaned up at the end (mirrors 02f). Deterministic.

Output: output/data/intermediate_results/population/{entry_scenario_grid,entry_headline_scenarios}.parquet
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
cfg = _cfg.cfg
PATH_DATA_PROCESSED = _cfg.PATH_DATA_PROCESSED
POP = _cfg.PATH_OUTPUT_INTERMEDIATE / "population"

_d_spec = importlib.util.spec_from_file_location(
    "mod_02d", _CODE / "02_descriptive_analysis" / "02d_matching_simulation.py")
_d = importlib.util.module_from_spec(_d_spec); sys.modules["mod_02d"] = _d; _d_spec.loader.exec_module(_d)

_LAMBDA_CENTRAL = float(cfg["matching"].get("offer_dispersion", {}).get("lambda_central", 0.75))


def _pool_name(penalty: float, lam: float, status_penalty: str = "", tag: str = "") -> str:
    """Reproduce 01h's _POOL_SUFFIX for the (penalty, λ, status-penalty) selectors."""
    suffix = ""
    if penalty > 0:
        suffix += f"__pen{int(round(penalty * 100))}"
    if status_penalty:
        suffix += "__skewstat" + tag
    if abs(lam - _LAMBDA_CENTRAL) > 1e-9:
        suffix += f"__lam{int(round(lam * 100))}"
    return f"nonemployed_pool{suffix}.parquet"


def _build_pool(penalty: float, lam: float, status_penalty: str = "", tag: str = "") -> Path:
    """Build (if absent) the 01h pool for these selectors; return its path. The canonical
    pool (penalty 0, λ central, no status penalty) is assumed already on disk."""
    path = PATH_DATA_PROCESSED / _pool_name(penalty, lam, status_penalty, tag)
    if path.exists():
        return path
    env = dict(os.environ)
    if penalty > 0:
        env["EIG_MPL_PENALTY"] = str(penalty)
    if abs(lam - _LAMBDA_CENTRAL) > 1e-9:
        env["EIG_MPL_LAMBDA"] = str(lam)
    if status_penalty:
        env["EIG_MPL_STATUS_PENALTY"] = status_penalty
        if tag:
            env["EIG_POOL_TAG"] = tag
    subprocess.run([sys.executable, str(_CODE / "01_data_preparation" / "01h_nonemployed_pool.py")],
                   cwd=str(_ROOT), env=env, check=True)
    return path


def _entry_row(pool: pd.DataFrame, beta: float, target: float, edge: str) -> dict:
    ge, ne, fce, ind, by_cell, det = _d._entrants_from_pool(pool, beta, target, edge=edge)
    return {"induced_M": ind,
            **{f"induced_{c}_M": v for c, v in by_cell.items()},
            "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1)}


def main() -> None:
    mcfg = cfg.get("matching", {})
    beta_c = float(mcfg["beta"]["central"])
    grid = mcfg.get("entry_scenario_grid", {})
    rec = mcfg.get("entry_recenter", {})
    pens = grid.get("penalty", [0.0, 0.10, 0.20])
    lams = grid.get("lambda", [0.50, 0.75, 1.00])
    edges = grid.get("eps_edge", ["lower", "central", "upper"])

    w = pd.read_parquet(PATH_DATA_PROCESSED / "hourly_workers.parquet")
    target = _d._recover_target(w)

    built: list[Path] = []   # non-canonical pools to clean up

    def _get_pool(penalty, lam, status_penalty="", tag=""):
        canonical = (penalty == 0 and abs(lam - _LAMBDA_CENTRAL) < 1e-9 and not status_penalty)
        p = _build_pool(penalty, lam, status_penalty, tag)
        if not canonical and p not in built:
            built.append(p)
        return pd.read_parquet(p)

    # ---- Full 27-cell decomposition (penalty × λ × eps). 9 pool builds; 3 eps edges free each. --
    grid_rows = []
    for penalty in pens:
        for lam in lams:
            pool = _get_pool(penalty, lam)
            mp = pool["mpl"].to_numpy(float); wt = pool["weight"].to_numpy(float)
            pct_below = 100 * wt[mp < target].sum() / wt.sum()
            for edge in edges:
                r = _entry_row(pool, beta_c, target, edge)
                grid_rows.append({"penalty": penalty, "lambda": lam, "eps_edge": edge,
                                  "pct_mpl_below_target": round(pct_below, 1), **r})
    grid_df = pd.DataFrame(grid_rows)
    POP.mkdir(parents=True, exist_ok=True)
    grid_df.to_parquet(POP / "entry_scenario_grid.parquet", index=False)

    # ---- Three headline joint bundles. -----------------------------------------------------------
    sp = rec.get("evidence_central_status_penalty",
                 {"unemployed": 0.05, "nilf_other": 0.10, "disabled": 0.15, "retired": 0.15})
    sp_str = ",".join(f"{k}:{v}" for k, v in sp.items())
    evc_lam = float(rec.get("evidence_central_lambda", _LAMBDA_CENTRAL))
    hi_pen = float(rec.get("high_penalty", 0.20)); hi_lam = float(rec.get("high_lambda", 1.00))
    hi_edge = rec.get("high_eps_edge", "upper")

    head_rows = [
        {"scenario": "conservative_floor", "penalty": "0", "lambda": _LAMBDA_CENTRAL,
         "eps_edge": "central", "note": "current headline path, now labeled the floor",
         **_entry_row(_get_pool(0.0, _LAMBDA_CENTRAL), beta_c, target, "central")},
        {"scenario": "evidence_central",
         "penalty": f"status-diff ({sp_str})", "lambda": evc_lam, "eps_edge": "central",
         "note": "corrects penalty=0 with a status-differentiated ~10% penalty",
         **_entry_row(_get_pool(0.0, evc_lam, status_penalty=sp_str, tag="_evc"),
                      beta_c, target, "central")},
        {"scenario": "high", "penalty": str(hi_pen), "lambda": hi_lam, "eps_edge": hi_edge,
         "note": "joint upper corner (penalty × λ × eps)",
         **_entry_row(_get_pool(hi_pen, hi_lam), beta_c, target, hi_edge)},
    ]
    head_df = pd.DataFrame(head_rows)
    head_df.to_parquet(POP / "entry_headline_scenarios.parquet", index=False)

    print("\n02g | entry_headline_scenarios.parquet (three joint bundles):")
    print(head_df[["scenario", "penalty", "lambda", "eps_edge", "induced_M",
                   "induced_single_mothers_M", "induced_other_women_M", "induced_men_M",
                   "entrant_gross_bn", "entrant_net_bn"]].to_string(index=False))
    print(f"\n02g | entry_scenario_grid.parquet — {len(grid_df)} cells "
          f"(induced_M range {grid_df.induced_M.min():.2f}–{grid_df.induced_M.max():.2f})")

    # ---- Persist the evidence-central pool + composition for the headline figures. --------------
    # fig07b (entrants by prior status) and fig12 (median-g_net clawback) should reflect the
    # published headline, not the floor. Copy the evidence-central pool to a stable name and write
    # its entrant-by-status composition; both survive the suffixed-pool cleanup below.
    evc_pool = _get_pool(0.0, evc_lam, status_penalty=sp_str, tag="_evc")
    evc_pool.to_parquet(PATH_DATA_PROCESSED / "nonemployed_pool_evidence_central.parquet", index=False)
    _, _, _, _, _, det = _d._entrants_from_pool(evc_pool, beta_c, target, edge="central")
    comp = pd.DataFrame([{"prior_status": s, "entrants_M": det.get(f"entrants_{s}_M", 0.0)}
                         for s in ("unemployed", "nilf_other", "disabled", "retired")])
    comp.to_parquet(POP / "entry_central_composition.parquet", index=False)
    print("02g | evidence-central composition (M):",
          {r["prior_status"]: r["entrants_M"] for r in comp.to_dict("records")})

    # ---- PI-3 + coordination/take-up stress tests ON THE EVIDENCE-CENTRAL POOL. ------------------
    # MR-006/CC-003/AS-002 (full-review 2026-07-09): the published marginal-cost/FTE and the
    # spouse-coordination/take-up sensitivities must be computed on the 1.25M evidence-central pool,
    # not the 0.83M floor. Overwrite 02d's floor-pool entrant_hours_sensitivity and add an
    # evidence-central stress table so the drafts quote a single consistent base.
    ehs = _d.entrant_hours_sensitivity(evc_pool, beta_c, target)
    ehs.to_parquet(POP / "entrant_hours_sensitivity.parquet", index=False)
    ge0, ne0, _, ind0, _, _ = _d._entrants_from_pool(evc_pool, beta_c, target, edge="central")
    stress = [{"variant": "evidence-central", "induced_M": ind0,
               "entrant_gross_bn": round(ge0, 1), "entrant_net_bn": round(ne0, 1)}]
    wt_evc = evc_pool["weight"].to_numpy(float)
    sp_evc = (evc_pool["spouse_is_employed"].astype(bool).to_numpy()
              if "spouse_is_employed" in evc_pool.columns else np.zeros(len(evc_pool), bool))
    for tag, wov in (("spouse-employed zeroed", wt_evc * np.where(sp_evc, 0.0, 1.0)),
                     ("take-up 0.80", wt_evc * 0.80)):
        ge, ne, _, ind, _, _ = _d._entrants_from_pool(
            evc_pool, beta_c, target, edge="central", weight_override=wov)
        stress.append({"variant": tag, "induced_M": ind,
                       "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1)})
    pd.DataFrame(stress).to_parquet(POP / "entry_central_stress.parquet", index=False)
    print("02g | entry_central_stress.parquet (evidence-central base):",
          {r["variant"]: r["induced_M"] for r in stress})
    print("02g | entrant_hours_sensitivity.parquet recomputed on the evidence-central pool:")
    print(ehs.to_string(index=False))

    # ---- Cleanup non-canonical pools + their diagnostics (mirrors 02f). --------------------------
    for p in built:
        for q in (p, PATH_DATA_PROCESSED / p.name.replace(
                "nonemployed_pool", "nonemployed_pool_diagnostics").replace(".parquet", ".json")):
            if q.exists():
                q.unlink()
    canonical = PATH_DATA_PROCESSED / "nonemployed_pool.parquet"
    assert canonical.exists(), "02g must not remove the canonical pool"
    print(f"02g | cleaned {len(built)} suffixed pools; canonical pool preserved.")


if __name__ == "__main__":
    main()
