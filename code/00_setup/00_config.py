# 00_config.py -- baseline project configuration
from __future__ import annotations
import os
from pathlib import Path


def _find_project_root(start: Path = Path.cwd(), max_up: int = 10) -> Path:
    cur = start.resolve()
    for _ in range(max_up + 1):
        if (cur / "code" / "run_all.py").exists() or \
           (cur / "code" / "run_all.R").exists() or \
           (cur / "code" / "run_all.do").exists():
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    raise RuntimeError(
        "Could not locate project root. "
        "Set EIG_PROJECT_ROOT or run from the repo root."
    )


# Project root: env var takes priority, then walk upward from this file
_env_root = os.environ.get("EIG_PROJECT_ROOT", "")
PATH_PROJECT = Path(_env_root).resolve() if _env_root else _find_project_root(
    Path(__file__).resolve().parent
)

# Paths
PATH_CODE                = PATH_PROJECT / "code"
PATH_DATA                = PATH_PROJECT / "data"
PATH_DATA_RAW            = PATH_DATA / "raw"
PATH_DATA_PROCESSED      = PATH_DATA / "processed"
PATH_OUTPUT              = PATH_PROJECT / "output"
PATH_OUTPUT_FIG_MAIN     = PATH_OUTPUT / "figures" / "main"
PATH_OUTPUT_FIG_APPENDIX = PATH_OUTPUT / "figures" / "appendix"
PATH_OUTPUT_TBL_MAIN     = PATH_OUTPUT / "tables" / "main"
PATH_OUTPUT_TBL_APPENDIX = PATH_OUTPUT / "tables" / "appendix"
PATH_OUTPUT_INTERMEDIATE = PATH_OUTPUT / "data" / "intermediate_results"

# Project settings
cfg = {
    "project_name":       "eig-wagesubsidy-policy-sim",
    "audience":           "Public — interactive web simulation + blog post",
    "project_scope_tier": 1,   # 1=Descriptive/Blog  2=Analytical Brief  3=Full Research Paper
    "currency_base_year": 2025,
    "fig_width":          6.5,
    "fig_height":         3.5,
    "fig_dpi":            300,
    "seed":               1234,
    # Wage subsidy policy parameters (EIG 80-80 Rule)
    "ws_median_hourly_wage":  21.00,  # median hourly wage among hourly workers (excludes salaried)
    "ws_target_pct":          0.80,   # target wage = 80% of median
    "ws_subsidy_pct":         0.80,   # subsidy covers 80% of gap
    "ws_base_wage":           7.25,   # federal minimum wage — NOT state minimums (base wage floor)
    "ws_simulation_year":     2026,   # PolicyEngine simulation year
    # Derived (convenience)
    "ws_target_wage":         16.80,  # 0.80 * 21.00
    "ws_max_subsidy":          7.64,  # 0.80 * (16.80 - 7.25)
    "ws_hours_per_year":      2000,   # 40 hrs/wk * 50 wks
    "ws_subsidy_hours_cap":     40,   # subsidy eligibility capped at 40 hrs/wk per job
}

# ── Dynamic (behavioral) cost modeling ──────────────────────────────────────
# Labor-supply responses to the 80-80 subsidy, reported as a SENSITIVITY BAND
# across the contested elasticity literature — never a single point estimate.
# Consumed by code/02_descriptive_analysis/02b_behavioral_scenarios.py.
# Spec: Infrastructure/specs/2026-06-25_dynamic-cost-modeling.md
#
# IMPORTANT — these are TRANSPORTED, ex-ante assumptions. No elasticity has been
# estimated for a per-hour wage-FILL design; all values are imported from EITC /
# CTC / NIT / in-work-credit evidence and applied to a different budget-set
# geometry. The extensive margin is disputed at its foundation:
#   Kleven 2024 (~0, fragile)  vs  Chetty 2012 (~0.25)  vs  Keane 2011 (higher);
#   the 2021 CTC debate used eps_ext as high as 0.75 (Corinth et al. w29366).
# The 80-80 also delivers a very LARGE proportional wage gain at the bottom
# (g can exceed 1.0 near the minimum wage), well outside the marginal variation
# these elasticities were estimated on, so the linear eps*g approximation likely
# OVERSTATES responses — especially the extensive margin. Read the band, not a point.
#
# CELL-SPECIFIC extensive margin. The extensive (participation) elasticity is NOT
# constant across the eligible population — it is large for single mothers and near
# zero for prime-age men (CBO review, McClelland & Mok 2012: ~0-0.1 for men/single
# women vs 0.3-1.2 for EITC-eligible low-income single mothers; the gap is the whole
# point). The 80-80 base is ~41% men, ~48% other women, ~11% single mothers, so a
# single blended elasticity would mis-weight the response. eps_ext is therefore keyed
# by demographic cell (assigned in 02b from sex_label + family_type_key):
#   single_mothers : Female & single-with-children   (strongest extensive evidence)
#   other_women    : Female, not a single mother      (married women responsive; CBO)
#   men            : Male                              (prime-age men ~0-0.15; EITC does not transfer)
#
# Per scenario:
#   eps_ext     dict {cell: extensive elasticity}     -> induced entrants
#   eps_int     intensive-margin (hours) elasticity (scalar; small per consensus)
#   eta_income  income-effect parameter (>=0) reducing hours. Default 0.
#   passthrough first-order share (phi) of the per-hour subsidy captured by employers.
#               0 = full worker capture. Superseded by the incidence module (02c) once
#               a labor-demand elasticity is sourced; kept here as a fallback knob.
cfg["behavioral"] = {
    "enabled": True,
    "stimulus": "proportional_wage_gain",   # g_i = subsidy_hr_i / employer_wage_i
    # Schedule income grid max (output/.../individual_schedules); used to flag extrapolation.
    "schedule_income_max": 65000.0,
    "cells": ["single_mothers", "other_women", "men"],
    # Bounded response function. The behavioral response is NOT linear in the wage gain g:
    # a constant elasticity applied linearly (1 + eps*g) over-extrapolates because the 80-80
    # delivers very large g (50-100%+) far outside the marginal variation the elasticities were
    # estimated on. We use a saturating Michaelis-Menten form with local slope eps at g->0 (so it
    # is calibrated to the literature elasticity at the margin) and a ceiling M as g grows:
    #   m(g) = 1 + (M-1) * (eps*g) / ((M-1) + eps*g)     for eps*g > 0
    #   m(g) = 1 + eps*g                                  for eps*g <= 0 (wage below outside option -> exit)
    # ceiling_ext: a band's employment can at most rise to M_ext x baseline (participation is
    # bounded — a low-wage demographic cannot more than ~half-again its employment). ceiling_int:
    # hours can at most rise to M_int x (part-time -> full-time and a bit). Both are disclosed
    # judgment bounds; sensitivity is via these values.
    "saturation": {"ceiling_ext": 1.50, "ceiling_int": 1.40},
    # Incidence / wage pass-through (02c). The employer wage adjusts so a single national
    # low-wage labor market clears: induced labor supply moves down a constant-elasticity
    # demand curve, the employer wage falls, the per-job subsidy s(w_emp) rises, iterate to
    # a fixed point. eta_d is the own-wage labor-demand elasticity for a US low-skill pool.
    # Sourced (catalog): Hamermesh 1993 (~-0.3 consensus); Lichter-Peichl-Siegloch 2015
    # (bias-corrected ~-0.3, more elastic for low-skill); Popp 2023 (~-0.43). Busso-Gregory-
    # Kline 2013 (Empowerment Zones): pass-through is SLACK-DEPENDENT — workers keep more when
    # the market is slack (elastic demand, |eta_d| large -> small wage drop), employers capture
    # more when tight (inelastic demand, |eta_d| small -> large wage drop / Rothstein channel).
    "incidence": {
        "enabled": True,
        "eta_d": {"central": -0.30, "slack": -0.50, "tight": -0.15},
        # SEGMENTED competitive markets: each $1 employer-wage band clears on its OWN realized
        # (cell-specific) supply shift, so the wage falls only where labor supply actually
        # expands — a band of mostly prime-age men (eps_ext ~0) sees ~no decline. This encodes
        # the competitive discipline: an employer cannot unilaterally cut pay without losing
        # workers to in-band competitors; only a genuine supply increase moves the market wage.
        "segment_width": 1.0,        # employer-wage band width ($/hr)
        # Induced entrants are low-productivity and enter at the BOTTOM of the wage ladder, not
        # cloned into every band. They are distributed across bands at or below entry_ceiling
        # (proportional to incumbent density), so the supply shock — and any wage decline — is
        # localized where new workers actually land. Middle/upper bands get no entrants, so with
        # a near-zero hours response their wages (and subsidies) are essentially unchanged.
        "entry_ceiling": 11.0,       # entrants land only in bands with employer wage <= $11/hr
        # Outside-option floor: total compensation (wage + subsidy) cannot be bid below the
        # worker's pre-policy wage (floor_frac=1.0). Universal subsidy raises every employer's
        # offer, so competitors poach anyone pushed below their outside option. Set <1 to allow
        # some incumbent wage loss (Rothstein-style incidence on inframarginal workers).
        "comp_floor_frac": 1.00,
        "theta_hard_floor": 0.30,    # numerical backstop on the per-band wage multiplier
        "tol": 1e-4, "max_iter": 80,
    },
    "scenarios": {
        "static": {
            "eps_ext": {"single_mothers": 0.00, "other_women": 0.00, "men": 0.00},
            "eps_int": 0.00, "eta_income": 0.00, "passthrough": 0.00,
            "source": "Reference: no behavioral response (reproduces 02a static cost)."},
        "lower": {
            "eps_ext": {"single_mothers": 0.25, "other_women": 0.10, "men": 0.00},
            "eps_int": 0.00, "eta_income": 0.00, "passthrough": 0.00,
            "source": "Kleven-haircut low end: men ~0; single mothers at CBO EITC floor (0.3 minus haircut)."},
        "central": {
            "eps_ext": {"single_mothers": 0.50, "other_women": 0.20, "men": 0.05},
            "eps_int": 0.05, "eta_income": 0.00, "passthrough": 0.00,
            "source": "CBO central: men 0-0.1 -> 0.05; single mothers mid EITC range 0.5; intensive ~near-zero (EITC: large entry, negligible hours)."},
        "upper": {
            "eps_ext": {"single_mothers": 0.80, "other_women": 0.40, "men": 0.15},
            "eps_int": 0.15, "eta_income": 0.00, "passthrough": 0.00,
            "source": "CBO upper: men 0.15; single mothers near top of 0.3-1.2 EITC range (0.8); intensive 0.15."},
    },
}

# ── Structural search-and-matching simulation (02d) ─────────────────────────
# Resolves A1.3: employment by match VIABILITY (surplus y - r >= 0), wages by Nash bargaining
# (w = r + beta*(y - r)), the 80-80 subsidy as added match surplus split beta/(1-beta) between
# worker and firm. Incidence = (1 - beta) — a bounded, micro-founded bargaining share — NOT an
# aggregate labor-demand elasticity (which produced the spurious band-wage collapses). Wages are
# bounded in [r, y], so they cannot collapse to the floor.
# Foundations (catalog): Mortensen-Pissarides 1994 (viability/job creation); Diamond 1982 /
# Pissarides 2000 (Nash split); Hungerbuhler-Lehmann 2006 (subsidy split beta/(1-beta));
# Hosios 1990 (beta=0.5 efficient); Shimer 2005 (beta~0.7); Rothstein 2010 (~70% worker capture
# => beta~0.7); Hall-Milgrom 2008 (wage rigidity => firms capture more, beta_eff low);
# Krueger-Mueller 2016 (reservation ~ prior wage); Flinn 2006 (min-wage truncation).
# TRANSPORTED: no beta/reservation estimate exists for an 80-80-style wage fill; values imported.
cfg["matching"] = {
    "enabled": True,
    # Worker bargaining power beta (share of match surplus, incl. the subsidy, kept by the worker).
    "beta": {"central": 0.50, "measured": 0.70, "rigid": 0.30},
    # Reservation wage as a share of the worker's current (prior) wage — Krueger-Mueller anchor.
    "reservation_ratio": 0.80,
    # Induced entrants enter at a low marginal product: this percentile of the eligible wage dist.
    "entry_wage_percentile": 15,
    # Incumbent wage rigidity (Hall-Milgrom 2008; new-hire vs incumbent wage-flexibility evidence):
    # existing matches' wages are sticky and do NOT renegotiate down when the subsidy appears, so
    # bargaining incidence (firm capture) falls only on NEW matches (entrants). The fully-flexible
    # alternative (all wages renegotiate) is reported as the incidence UPPER bound.
    "incumbent_wage_rigid": True,
    # ── Extensive-margin band for the STRUCTURAL entry model (01h/02d) ──────────
    # Literature role: PRIOR/BAND, not a solved point target (spec
    # 2026-07-08_entry-from-nonemployment-remodel.md, M2; challenge report same date).
    # This namespace is deliberately SEPARATE from cfg["behavioral"]["scenarios"], which 02b
    # continues to consume as a labeled reduced-form "EITC/CBO benchmark" (a legitimate,
    # disclosed use of the literature as a literal target). 01h calibrates one reservation-wage
    # column per edge; 02d reports the band in entry_margin_band.parquet.
    # Calibration conventions (user sign-off 2026-07-08): NET stimulus basis, saturating
    # person-level response (same response_multiplier/ceiling_ext as 02b), net viability
    # criterion inside the lambda-bisection, any-employment margin for anchor conversions.
    # Band provenance per cell: docs/entry_from_nonemployment_methodology.md.
    # VALUES: W2c user sign-off 2026-07-08, from primary-verified anchors under the
    # any-employment / net-stimulus conventions:
    #   single_mothers upper 0.65 — SSP-anchored (implied eps≈0.49 from +10.4pp on 30.1% base
    #     over net stimulus ≈0.7; headroom for SSP's 30-hr full-time conditioning). Central 0.50
    #     EITC/CBO mid; lower 0.25 Kleven-haircut floor.
    #   other_women 0.05/0.20/0.40 — two-channel provenance (household-phase-out negatives
    #     excluded as inapplicable; coordination channel bounds lower near zero; PPE-cohabiting
    #     and Paycheck Plus NYC women (+3.2pp*** pooled) anchor the upper).
    #   men 0.00/0.05/0.15 — central CBO mid retained; upper = Paycheck-Plus-NYC diluted
    #     (pooled +2.8 ns reading; subgroup ~30-40% of cell); lower = Atlanta precise null.
    "eps_ext_band": {
        "lower":   {"single_mothers": 0.25, "other_women": 0.05, "men": 0.00},
        "central": {"single_mothers": 0.50, "other_women": 0.20, "men": 0.05},
        "upper":   {"single_mothers": 0.65, "other_women": 0.40, "men": 0.15},
    },
    # ── Entry-propensity status weights (E1, reality assessment 2026-07-09) ────
    # Within each cell, the entry lottery is weighted by prior labor-force status so the
    # calibrated aggregate (unchanged by construction) lands on labor-market-proximate people
    # instead of hash-uniformly (which made 68% of entrants 16-24 NILF and only 9.4% unemployed).
    # DISCLOSED judgment weights, literature-informed:
    #   unemployed 5.0 — CPS monthly flows: U->E ~25-28% vs N->E ~4.5% (ratio ~5.5)
    #   nilf_other 1.0 — reference category (probit propensity handles age/education within it)
    #   disabled 0.15 / retired 0.15 — Maestas-Mullen-Strand 2013 (marginal SSDI work capacity
    #     ~23% x 28pp under full benefit denial); Krueger 2017 (retirements essentially permanent)
    # Combined with the selection-probit propensity Phi(Xg) and normalized to mean 1 within
    # (cell x reachable), so cell-level calibration targets are unaffected.
    "entry_status_weights": {"unemployed": 5.0, "nilf_other": 1.0,
                             "disabled": 0.15, "retired": 0.15},
    # ── Intensive-margin (hours) band for incumbents (E5, reality assessment) ──
    # eps_int = 0.05 is an EITC-design artifact (the credit's plateau/phase-out suppresses the
    # marginal-hour incentive the 80-80 deliberately preserves: a $10 worker's marginal hour to
    # 40/wk pays $15.44, +54%). Evidence for clean, no-phase-out wage variation:
    #   lower 0.05 — EITC-literature hours null (kept as the benchmark-continuity floor)
    #   central 0.20 — conservative side of Chetty (2012) Hicksian intensive consensus (0.33)
    #   upper 0.33 — Chetty (2012) consensus; Fehr-Goette (2007) Frisch ~1.1+ is the far bound
    # Applied in 02d to eligible incumbents below 40 hrs/wk (saturating form, ceiling_int,
    # gross-g stimulus per the 02b convention), reported as a separate sensitivity table —
    # the 02b benchmark scenario table keeps its own eps_int untouched.
    "eps_int_band": {"lower": 0.05, "central": 0.20, "upper": 0.33},
    # ── Offer dispersion for the imputed potential-wage distribution (2026-07-09) ──
    # Mean imputation makes reachability a deterministic cliff at each person's conditional
    # mean (a 40yo BA man: P(offer<target)=0; reality ~11%). Offers are drawn as mean-
    # preserving lognormal spread around the (Mills-corrected, smeared) conditional mean:
    #   w_i = E[w|X_i,D=0] * exp(lambda*sigma_g(i)*z_i - (lambda*sigma_g(i))^2/2)
    # sigma_g = wage-equation residual SD by education x age group (estimated in 01h; ranges
    # ~0.29 for older dropouts to ~0.50 for older BAs — dispersion rises with education/age,
    # per the wage-structure literature). z_i is a hash-quantile draw (salted independently
    # of the entry lottery; deterministic). lambda scales the SD because residual variance
    # bundles real heterogeneity + offer dispersion (Hall-Mueller 2016 within-person offered-
    # wage SD ~0.24) with CPS measurement error (~0.10-0.15 log pts, not real):
    #   central 0.75 (nets out approximate measurement error) | band {0.50, 1.00} via 02f.
    "offer_dispersion": {"lambda_central": 0.75, "band": [0.50, 1.00]},
    # ── Entry re-center + scenario grid (2026-07-09 holistic evaluation, user sign-off) ──
    # Q1 decision (Option A): the 0.83M headline was a THREE-WAY conservative floor (penalty 0,
    # λ 0.75, accepted-wage σ) presented as a neutral central. The evidence-central corrects the
    # one non-neutral choice — a zero non-employment wage penalty — with a STATUS-DIFFERENTIATED
    # penalty (short-spell unemployed light per Krueger-Mueller ~0.90×; long-detached groups
    # heavier per compounded Schmieder-vWB 0.8%/mo), weighted mean ≈10%. λ stays 0.75 (avoids
    # compounding two upward corrections). 0.83M (penalty 0) is retained as the labeled
    # conservative FLOOR. Consumed by 02g_entry_scenario_grid.py.
    "entry_recenter": {
        # status-differentiated penalty for the evidence-central bundle (mean ≈10-11% on the pool)
        "evidence_central_status_penalty": {
            "unemployed": 0.05, "nilf_other": 0.10, "disabled": 0.15, "retired": 0.15},
        "evidence_central_lambda": 0.75,
        "conservative_floor_lambda": 0.75,   # penalty 0, current headline path
        "high_penalty": 0.20, "high_lambda": 1.00, "high_eps_edge": "upper",
    },
    # Full joint decomposition (Q2 decision: grid + full decomposition). 02g runs the cartesian
    # product; eps edges are read from each pool's pre-computed required_net_gain_{edge} columns,
    # so 3 penalty × 3 λ = 9 pool builds yield all 27 cells (no extra rebuild per eps edge).
    "entry_scenario_grid": {
        "penalty": [0.0, 0.10, 0.20],
        "lambda": [0.50, 0.75, 1.00],
        "eps_edge": ["lower", "central", "upper"],
    },
    # Entrant-hours mapping modes for the PI-3 sensitivity (02d). "rank" is the headline
    # (MPL-percentile → incumbent-hours-percentile, corr ≈ +0.9 so entrants get the fewest hours);
    # "independent" draws hours from the cell distribution uncoupled from MPL; "median" assigns the
    # cell-median. The rank↔independent gap bounds how much the low marginal cost per entrant and
    # the entry-FTE figure depend on the untested rank-rank coupling.
    "entry_hours_modes": ["rank", "independent", "median"],
}

# Directory creation — base dirs (all tiers)
for _d in [PATH_DATA_RAW, PATH_DATA_PROCESSED, PATH_OUTPUT_FIG_MAIN, PATH_OUTPUT_TBL_MAIN]:
    _d.mkdir(parents=True, exist_ok=True)

# Tier 2+: intermediate results
if cfg["project_scope_tier"] >= 2:
    PATH_OUTPUT_INTERMEDIATE.mkdir(parents=True, exist_ok=True)

# Tier 3: appendix directories
if cfg["project_scope_tier"] >= 3:
    PATH_OUTPUT_FIG_APPENDIX.mkdir(parents=True, exist_ok=True)
    PATH_OUTPUT_TBL_APPENDIX.mkdir(parents=True, exist_ok=True)

print(f"Loaded config. Project root: {PATH_PROJECT}")
