# ORG Validation Framework Report

## Executive Summary
- Overall framework grade: **Yellow**
- Central ORG estimate: 23.65M workers, $100.89B gross, $66.78B net.
- Target wage: $16.80/hr.
- This report validates ORG as the worker-eligibility backbone and treats ASEC as a moment-calibration reference, not a record-level benchmark.

## 1. Internal Coherence
- Federal floor correctly applied: True
- Weighted mean annual hours: 1611.5
- CA rank by eligible workers: 3

## 2. Moment Calibration to ASEC
- ASEC proxy eligible workers: 34.95M
- Fit improvement (total gap): 32.34% -> 0.00%
- Fit improvement (state share MAE): 0.53pp -> 0.10pp
- Fit improvement (family share MAE): 4.94pp -> 1.60pp
- Calibrated policy estimate: $148.45B gross, $95.35B net

## 3. Uncertainty Bounds
- Central gross: $100.89B
- Gross range across variants: $71.77B to $132.90B
- Net range across variants: $48.79B to $82.22B

## 4. Stability Checks
- Year/month sample count tested: 15
- Leave-one-month-out gross cost CV: 0.53%
- Year windows observed: year_2025, year_2026

## 5. Grading Table
- calibration_total_gap_pct_after: 0.0000 -> Acceptable
- calibration_state_share_mae_pp_after: 0.1005 -> Acceptable
- calibration_family_share_mae_pp_after: 1.6047 -> Caution
- hours_mean_in_expected_band: 1611.4714 -> Acceptable
- uncertainty_gross_range_pct: 60.5844 -> Failure
- leave_one_month_out_gross_cv_pct: 0.5332 -> Acceptable

## 6. Interpretation
- ORG is validated for eligibility identification and wage-rate targeting.
- ASEC is best used as a macro calibration anchor (population composition moments).
- Policy results should be reported as a central estimate plus uncertainty bounds, not as a single deterministic number.

## 7. Artifacts
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/framework_manifest.json`
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/central_summary.json`
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/calibration_fit.csv`
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/calibration_factors.csv`
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/uncertainty_bounds.csv`
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/stability_checks.csv`
- `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_framework_20260308/framework_grades.csv`

## Caveats
- ASEC moments are built from locally cached `enhanced_cps_2024.h5` materialized arrays and proxy family-unit logic.
- Calibration factors are capped to avoid overfitting to noisy cells.
- This framework does not imply ORG and ASEC should match at record level.
