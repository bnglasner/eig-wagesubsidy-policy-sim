# ORG Validation Framework

## Purpose
This framework validates the CPS ORG-based wage-subsidy pipeline using a method that is consistent with the data-generating process.

It explicitly avoids treating ORG-vs-ASEC record-level or level-by-level equality as a hard requirement, because ORG and ASEC measure different concepts:
- ORG: point-in-time wage rates and current-work status.
- ASEC: prior-year annual income totals and annualized household structure.

## Core Principle
Use ORG to identify worker eligibility and wage rates. Use PE schedules to estimate household-level fiscal interactions. Use ASEC only as a macro calibration anchor for moments (composition and scale), not person-level linkage.

## Validation Modules

### 1) Internal Coherence (ORG-only)
Checks:
- Federal floor correctly applied (`$7.25` minimum before eligibility test).
- Weight denominator uses unique `(year, month)` groups present in pooled ORG.
- Weighted mean annual hours are in a plausible range.
- State ranking pattern remains economically plausible (e.g., CA below TX/FL under current target).

Why this matters:
- Confirms that the ORG eligibility construction itself is internally consistent before any external comparison.

### 2) Moment Calibration (ORG to ASEC moments)
Construct ASEC proxy moments:
- Eligible worker total.
- Eligible state shares.
- Eligible family-type shares.

Calibrate ORG eligible weights with capped factors:
- State factors and family factors.
- Final scaling to ASEC total.

Outputs:
- Fit before and after calibration:
  - total gap (%)
  - state share MAE (pp)
  - family share MAE (pp)
- Calibrated policy estimates (gross/net) alongside central ORG estimates.

Why this matters:
- Anchors ORG outputs to annual household-distribution moments without forcing invalid record matching.

### 3) Uncertainty Bounds
Run assumption variants and report ranges:
- `hours +/- 10%`
- target wage at `75%`, `80%`, `85%` of median
- drop rows with missing raw annual-hours signal (counterfactual sensitivity)

Report:
- central gross/net
- min/max gross/net across variants
- range as % of central estimate

Why this matters:
- Converts assumption uncertainty into transparent policy ranges.

### 4) Stability Tests
Re-estimate under alternate sampling windows:
- all pooled months
- each available year separately
- leave-one-month-out over observed `(year, month)` groups

Report:
- worker and cost variation across windows
- leave-one-month-out gross-cost coefficient of variation

Why this matters:
- Verifies that results are not driven by a single month or narrow subsample.

## Grading Scheme (Framework-Specific)
The framework grades diagnostics most relevant to ORG use:
- calibration total gap after weighting
- calibration state-share MAE after weighting
- calibration family-share MAE after weighting
- annual-hours plausibility band
- uncertainty range width
- leave-one-month-out stability

Overall grade:
- `Green`: no failures and at most one caution.
- `Yellow`: limited failures (<=2) with usable central estimate + caveats.
- `Red`: broad instability or poor calibration fit requiring further specification work.

## Script and Artifacts
Runner:
- `WORKSPACE/code/04_robustness_heterogeneity/04b_org_validation_framework.py`

Primary output folder:
- `WORKSPACE/output/validation/org_framework_20260308/`

Key artifacts:
- `framework_manifest.json`
- `org_framework_validation_report.md`
- `calibration_fit.csv`
- `calibration_factors.csv`
- `uncertainty_bounds.csv`
- `stability_checks.csv`
- `framework_grades.csv`

## Interpretation Guidance
- Central ORG estimate is the primary policy estimate.
- Calibrated estimate is a sensitivity anchor to ASEC moments.
- Report central + calibrated + uncertainty range together.
- Do not interpret ORG-vs-ASEC residual differences as model failure by default; interpret them as concept and frame differences unless internal coherence or stability fails.
