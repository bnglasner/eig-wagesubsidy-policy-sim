# ORG vs ASEC Consistency Validation Plan and Pre-Draft Report

## Metadata
- Created: 2026-03-08
- Project: EIG Wage Subsidy Policy Simulation
- Scope: Pre-run plan, thresholds, and report scaffold for ORG vs ASEC/PE consistency testing
- Status: Draft (pre-run)

## 1. Execution Plan
1. Freeze inputs and reproducibility
2. Build harmonized comparison datasets
3. Run tests A-G in sequence
4. Score each metric with traffic-light thresholds
5. Produce consolidated report and release recommendation

## 2. Predefined Thresholds

### Test A: Population and Weights
- National worker count gap:
  - Acceptable: <=5%
  - Caution: >5% and <=10%
  - Failure: >10%
- State-level worker count gap (median across states):
  - Acceptable: <=8%
  - Caution: >8% and <=15%
  - Failure: >15%
- Any large-state gap (CA/TX/FL/NY):
  - Acceptable: <=12%
  - Caution: >12% and <=20%
  - Failure: >20%

### Test B: Wage Distribution
- Quantile gap at p10/p25/p50/p75/p90:
  - Acceptable: <=10%
  - Caution: >10% and <=20%
  - Failure: >20%
- KS statistic:
  - Acceptable: <=0.08
  - Caution: >0.08 and <=0.15
  - Failure: >0.15

### Test C: Annual Earnings Bridge
- Median baseline-income gap:
  - Acceptable: <=10%
  - Caution: >10% and <=20%
  - Failure: >20%
- Decomposition residual:
  - Acceptable: <=15%
  - Caution: >15% and <=30%
  - Failure: >30%

### Test D: Eligibility Consistency
- Eligible worker count gap:
  - Acceptable: <=10%
  - Caution: >10% and <=20%
  - Failure: >20%
- Eligible share gap:
  - Acceptable: <=2 pp
  - Caution: >2 and <=5 pp
  - Failure: >5 pp
- State rank correlation (Spearman):
  - Acceptable: >=0.90
  - Caution: >=0.75 and <0.90
  - Failure: <0.75

### Test E: Household Composition Coherence
- Family-type share gap per bucket:
  - Acceptable: <=3 pp
  - Caution: >3 and <=6 pp
  - Failure: >6 pp
- Total absolute deviation (4 buckets):
  - Acceptable: <=8 pp
  - Caution: >8 and <=15 pp
  - Failure: >15 pp

### Test F: Policy Output Backtest
- Gross cost gap:
  - Acceptable: <=15%
  - Caution: >15% and <=30%
  - Failure: >30%
- Net cost gap:
  - Acceptable: <=20%
  - Caution: >20% and <=35%
  - Failure: >35%
- Program-interaction component sign consistency:
  - Acceptable: all major components same sign
  - Caution: 1 major sign flip
  - Failure: >=2 major sign flips

### Test G: Sensitivity and Robustness
- ORG gross cost stability across variants:
  - Acceptable: range <=20% of central estimate
  - Caution: >20% and <=35%
  - Failure: >35%
- Top-10 state membership stability:
  - Acceptable: >=8 retained
  - Caution: 6-7 retained
  - Failure: <=5 retained

## 3. Critical Failure Checks (Auto-Red)
- Federal floor misapplied (anything other than $7.25 in harmonized test)
- Weight denominator error (`n_months` not based on unique year-month)
- Missing-month handling incorrectly hardcodes divide-by-12 with 11 observed months

## 4. Pre-Draft Report Scaffold

### Executive Summary
- Overall rating: TBD
- Pass/Caution/Failure counts: TBD
- Recommendation: TBD

### Inputs and Reproducibility
- Commit hash: TBD
- Input files and hashes: TBD
- Run timestamp: TBD

### Results by Test
- Test A: TBD
- Test B: TBD
- Test C: TBD
- Test D: TBD
- Test E: TBD
- Test F: TBD
- Test G: TBD

### Root-Cause Notes
- TBD

### Release Decision
- TBD

### Appendix
- Full metric tables: TBD
- State tables: TBD
- Distribution tables/plots: TBD
- Command log: TBD

## 5. Validation Results (Run 2026-03-08)

- Overall rating: **Red**
- Status counts: Acceptable=4, Caution=0, Failure=13
- Target wage used: $16.80/hr
- Eligible workers: ORG=23.65M, ASEC-proxy=34.95M
- Policy costs: ORG gross/net=$100.89B/$66.78B, ASEC-proxy gross/net=$292.30B/$193.80B

### Metrics

- Test A | national_worker_gap_pct = 32.3365 -> Failure
- Test A | state_median_gap_pct = 24.0622 -> Failure
- Test A | large_state_max_gap_pct = 66.5432 -> Failure
- Test B | wage_quantile_gap_max_pct = 65.5172 -> Failure
- Test B | weighted_ks = 0.3570 -> Failure
- Test C | median_baseline_income_gap_pct = 24.2222 -> Failure
- Test C | decomposition_residual_pct = 0.4879 -> Acceptable
- Test D | eligible_count_gap_pct = 32.3365 -> Failure
- Test D | eligible_share_gap_pp = 15.4754 -> Failure
- Test D | state_rank_spearman = 0.9582 -> Acceptable
- Test E | family_bucket_max_gap_pp = 9.6738 -> Failure
- Test E | family_total_abs_dev_pp = 19.7680 -> Failure
- Test F | gross_cost_gap_pct = 65.4848 -> Failure
- Test F | net_cost_gap_pct = 65.5426 -> Failure
- Test F | major_component_sign_flips_score = 0.0000 -> Acceptable
- Test G | gross_cost_range_pct_of_central = 60.5844 -> Failure
- Test G | min_top10_overlap = 10.0000 -> Acceptable

### Artifacts

- Manifest: `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_vs_asec_20260308/manifest.json`
- Metrics: `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_vs_asec_20260308/metrics.csv`
- State compare: `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_vs_asec_20260308/state_workers_org_vs_asec.csv`
- Family compare: `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_vs_asec_20260308/family_shares_org_vs_asec.csv`
- Program interactions compare: `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_vs_asec_20260308/program_interactions_org_vs_asec.csv`
- Sensitivity: `C:/Users/Research/Documents/GitHub/eig-wagesubsidy-policy-sim/WORKSPACE/output/validation/org_vs_asec_20260308/sensitivity.csv`

### Method Caveats

- ASEC side uses `employment_income_before_lsr / (weekly_hours_worked_before_lsr * 52)` as legacy wage proxy.
- `is_tax_unit_head` and exact marital status were not materialized in cached H5; used person-level proxy via marital unit size and own-children count.
- This validation is consistency-focused, not identity matching across ORG and ASEC records.
