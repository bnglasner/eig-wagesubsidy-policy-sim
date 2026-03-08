# EIG Wage Subsidy Simulation: Public Methodology Guide

## 1. Purpose and scope

This project estimates the fiscal and distributional effects of the Economic Innovation Group (EIG) wage subsidy proposal (the "80-80 Rule") for US workers.

The pipeline is designed to answer three core policy questions:

1. How many workers are eligible under the wage rule?
2. What is the gross transfer cost of the subsidy?
3. What is the net fiscal cost after tax and means-tested program responses?

The architecture deliberately separates wage identification from fiscal-response modeling:

- Wage eligibility and subsidy sizing are identified from CPS ORG microdata.
- Tax-transfer responses are modeled using precomputed PolicyEngine-US schedules.

This document is written for a technically literate audience and is intended to be directly reproducible from the codebase.

---

## 2. Policy rule and notation

The implemented policy is parameterized by four scalars:

- `base_wage` = federal minimum wage floor (`$7.25`)
- `target_pct` = target-wage share of the median (`0.80`)
- `subsidy_pct` = subsidy share of the wage gap (`0.80`)
- `M` = weighted median paid-hourly wage in the ORG estimation sample (dynamic)

Define:

- `T = target_pct * M`
- `w_i^raw` = EPI-constructed hourly wage (`hourly_wage_epi`) for worker `i`
- `w_i = max(w_i^raw, base_wage)`

Hourly subsidy for worker `i`:

`subsidy_hr_i = subsidy_pct * max(0, T - w_i)`

Annual subsidy:

`subsidy_ann_i = subsidy_hr_i * h_i`

where `h_i` is annual hours (derived from ORG hours and WKSTAT mapping; see Section 7).

Key implication: workers at or above `T` receive zero subsidy; workers below `T` receive a linear phaseout transfer with slope `-subsidy_pct` in employer wage space.

---

## 3. Identification strategy: why two data sources

The central methodological choice is a two-source design.

### 3.1 Source A: CPS ORG for wage-rate identification

ORG is used to identify the distribution of hourly wages and employment intensity for active workers. This is the preferred source for wage-rate analysis because it directly captures current pay and work status variables used in EPI wage construction.

### 3.2 Source B: PolicyEngine schedules for fiscal interactions

PolicyEngine schedules encode how household taxes and program entitlements change as annual earnings vary, conditional on stylized family-state profiles.

### 3.3 Why sources are not linked record-to-record

ORG and ASEC/PolicyEngine inputs are not a common panel and do not support defensible one-to-one linkage at the individual level in this setup. The pipeline therefore uses:

- ORG for worker-level eligibility and subsidy amounts
- PolicyEngine schedule interpolation for conditional fiscal deltas

This avoids spurious pseudo-matching while preserving interpretability of each modeling layer.

---

## 4. Data assets and file contracts

## 4.1 ORG export step

Script:

- `WORKSPACE/code/01_data_preparation/00_export_org_data.py`

Behavior:

- Reads `org_panel_*.parquet` from companion repo `real-wages-generations-ipums`.
- Selects the most recent two files (or one if only one exists).
- Exports trimmed columns to `WORKSPACE/data/external/org_workers_{max_year}.parquet`.

Exported variables include:

- time/sample: `year`, `month`, `mish`
- weights/demographics: `earnwt`, `age`, `statefip`, `nchild`, `marst`, `wkstat`, `classwkr`
- wage variables: `paid_hourly`, `hours_epi`, `hours_epi_valid`, `hourly_wage_epi`, `hourly_wage_epi_valid`, `weekly_earn_epi`
- EPI sample flag: `epi_sample_eligible`

## 4.2 PolicyEngine schedule step

Script:

- `WORKSPACE/code/01_data_preparation/01b_precompute_individual.py`

Behavior:

- Constructs annual-income schedules by `(family_type_key, state_code)`.
- Stores component values over an income grid in:
  - `WORKSPACE/output/data/intermediate_results/individual_schedules/{family}_{state}.parquet`

These schedules are later interpolated (not re-simulated live) during population aggregation.

---

## 5. Wage measurement and sample eligibility (ORG / EPI variables)

The ingest pipeline relies on EPI-constructed wage variables in ORG.

Primary variables:

- `hourly_wage_epi`
- `hourly_wage_epi_valid`
- `paid_hourly`
- `hours_epi`
- `weekly_earn_epi`
- `epi_sample_eligible`

Conceptually, EPI wage construction combines paid-hourly reports with imputed hourly wages for non-hourly workers from weekly earnings and hours, subject to eligibility and cleaning rules. In this project, those variables are treated as upstream inputs rather than recomputed.

Operational eligibility in `01a_data_ingest.py` requires:

- `epi_sample_eligible == True`
- `hourly_wage_epi_valid == True`
- `16 <= age <= 64`
- `earnwt > 0`
- `employer_wage < TARGET_WAGE` after federal floor

This ensures the subsidy applies to valid wage observations in the intended working-age domain.

---

## 6. Dynamic median and target wage construction

The target wage is not fixed ex ante. It is recomputed from the ORG extract used in the run.

Estimator sample for the median:

- paid-hourly workers only (`paid_hourly == True`)
- EPI-eligible and valid-wage observations
- positive ORG earnings weights

Let `x_j` be hourly wages and `omega_j` be `earnwt` within this estimator sample. The weighted median `M` is computed by sorting `x_j`, forming cumulative weight `C_k = sum_{j<=k} omega_j`, and selecting the first `x_k` with `C_k >= 0.5 * C_total`.

Implemented target:

- `TARGET_WAGE = round(target_pct * M, 2)`

Rounding to cents is intentional and matches downstream wage comparisons.

---

## 7. Annual hours construction and weighting logic

Annual hours are derived from current weekly-equivalent hours (`hours_epi`) and labor-force status (`wkstat`).

## 7.1 WKSTAT to annual weeks mapping

`01a_data_ingest.py` applies the confirmed mapping:

- `11 -> 52`
- `12 -> 48`
- `13 -> 52`
- `14 -> 40`
- `15 -> 48`
- `21 -> 40`
- `22 -> 40`
- `41 -> 48`
- `42 -> 48`
- default for unmapped codes: `52`

Annual hours:

`h_i = hours_epi_i * weeks_multiplier(wkstat_i)`

If `h_i` is missing or non-positive after mapping, fallback is `cfg['ws_hours_per_year']` (default `2000`).

## 7.2 Population weighting in pooled ORG months

Because ORG records are monthly and pooled across multiple `(year, month)` groups, final analysis weight is:

`weight_i = earnwt_i / N_ym`

where `N_ym` is the number of unique `(year, month)` groups present in the eligible sample.

This converts monthly weights into an annual-average equivalent over the pooled period and avoids overcounting by naive summation across months.

## 7.3 Missing-month handling

If a month is absent in a given year (for example, October 2025 in the current extract), `N_ym` reflects observed groups only. This preserves internal consistency of weighting for the realized sample.

---

## 8. Household-type and geography mapping

Two categorical mappings are required for schedule lookup.

## 8.1 State mapping

- `statefip -> state_code` via fixed FIPS-to-abbreviation dictionary.
- Unmapped FIPS records are dropped with warning.

## 8.2 Family-type key mapping

From ORG marital status and children counts:

- prefix: `married` if `marst in {1,2}`, else `single`
- suffix: `2c` if `nchild >= 1`, else `0c`

Final key in:

- `single_0c`, `single_2c`, `married_0c`, `married_2c`

Note: this is a stylized household typing designed to align with schedule files, not a full household reconstruction.

---

## 9. Safety-net and tax response model

Script:

- `WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.py`

For each eligible worker `i`:

1. Baseline labor income:
   - `Y0_i = employer_wage_i * annual_hours_i`
2. Subsidized labor income:
   - `Y1_i = Y0_i + subsidy_ann_i`
3. Load schedule for `(family_type_key_i, state_code_i)`
4. Interpolate each schedule component at `Y0_i` and `Y1_i`
5. Compute component delta:
   - `Delta c_i = c(Y1_i) - c(Y0_i)`

If an exact schedule is unavailable, fallback order is:

1. `single_0c` in same state
2. same family type in `TX`
3. `single_0c` in `TX`
4. if still missing, zeros

This fallback policy is explicit and logged.

Covered components include transfers and taxes represented in `_SCHEDULE_COLS` (plus analytic wage subsidy handled separately).

---

## 10. Fiscal accounting identities

Define weights `w_i` (analysis weights), subsidy `S_i = subsidy_ann_i`, and schedule net-income delta `Delta NI_i`.

Gross subsidy cost:

`Gross = sum_i w_i * S_i`

Net fiscal cost (implementation):

`Net = sum_i w_i * Delta NI_i`

Program-level interaction table is built from weighted means and totals of `Delta c_i` for each component `c` in schedules; wage subsidy is added as a contextual row with 100% of gross cost.

Interpretation convention:

- Positive transfer deltas increase government cost.
- Negative transfer deltas reduce government cost.
- Tax components are stored as worker-negative values in schedules; their deltas are carried through consistently in net-income accounting.

---

## 11. Output products and schema

Population outputs are written to:

- `WORKSPACE/output/data/intermediate_results/population/`

Files:

- `summary.parquet`: one-row macro metrics (`gross_cost_bn`, `net_cost_bn`, `n_workers_mn`, `avg_annual_subsidy`, `n_records_raw`)
- `by_state.parquet`: state workers/cost/subsidy summaries
- `by_wage_bracket.parquet`: worker distribution and average subsidy over wage bins
- `by_family_type.parquet`: four family-type aggregates
- `program_interactions.parquet`: per-program average and total deltas plus share of gross cost

These files are consumed directly by the interactive population tab.

---

## 12. Validation framework and decision thresholds

Validation is implemented in:

- `WORKSPACE/code/04_robustness_heterogeneity/04b_org_validation_framework.py`
- `WORKSPACE/docs/org_validation_framework.md`

Framework dimensions:

1. Internal coherence checks
2. External moment calibration (ORG vs ASEC-compatible aggregates)
3. Sensitivity bounds under alternative assumptions
4. Stability checks across time windows / month exclusions

Outputs include machine-readable manifests and graded status flags (for example Green/Yellow/Red style interpretation) to distinguish model uncertainty from implementation failure.

---

## 13. Reproducibility instructions

## 13.1 Environment and repositories

Required:

- this repository: `eig-wagesubsidy-policy-sim`
- companion repository: `real-wages-generations-ipums`
- Python environment with `pandas`, `pyarrow`, `policyengine_us`, `streamlit`, and project dependencies

## 13.2 Execution sequence

From repository root:

```powershell
# 1) Export recent ORG panel subset
.\.venv\Scripts\python.exe WORKSPACE\code\01_data_preparation\00_export_org_data.py

# 2) Build eligible ORG worker analysis file
.\.venv\Scripts\python.exe WORKSPACE\code\01_data_preparation\01a_data_ingest.py

# 3) Build population aggregates with schedule interpolation
.\.venv\Scripts\python.exe WORKSPACE\code\02_descriptive_analysis\02a_descriptive_stats.py

# 4) Optional: run validation framework
.\.venv\Scripts\python.exe WORKSPACE\code\04_robustness_heterogeneity\04b_org_validation_framework.py

# 5) Launch interactive app
.\.venv\Scripts\streamlit.exe run WORKSPACE\app\app.py --server.port 8501
```

## 13.3 Primary artifacts to verify

- `WORKSPACE/data/external/org_workers_{max_year}.parquet`
- `WORKSPACE/data/processed/hourly_workers.parquet`
- population outputs in `WORKSPACE/output/data/intermediate_results/population/`
- validation outputs in `WORKSPACE/output/validation/`

---

## 14. Identification assumptions and limitations

1. ORG is strong for wage-rate identification but not a complete annual household-resource survey.
2. Annual hours are modeled using current-hours plus WKSTAT-based week multipliers, not observed prior-year weeks.
3. Tax-transfer responses are approximated from stylized schedule interpolation by family-state type, not full household microsimulation per ORG record.
4. Eligibility floor uses federal `$7.25` by design; state minimum wages are not imposed in the baseline policy implementation.
5. Estimates should be interpreted as model-based policy simulations with uncertainty bands, not administrative totals.

These limitations are explicit design tradeoffs, not hidden deficiencies.

---

## 15. Why this framework is policy-informative

Despite unavoidable data constraints, the framework is analytically strong for comparative policy analysis because it combines:

- empirically grounded wage-rate eligibility from ORG,
- transparent and parameterized subsidy mechanics,
- consistent tax-transfer response estimation,
- replicable and inspectable output artifacts,
- explicit validation, sensitivity, and stability diagnostics.

For policy design iteration, this structure is typically superior to single-source shortcuts that weaken either wage measurement or fiscal interaction realism.
