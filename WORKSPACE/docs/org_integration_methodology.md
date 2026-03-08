# ORG Data Integration Methodology
## EIG Wage Subsidy Policy Simulation — Worker Identification via CPS Outgoing Rotation Group

**Status:** Active — DDI codes confirmed March 2026; pipeline running on CPS ORG data
**Last updated:** 2026-03-07
**Authors:** EIG Research / Claude Code

---

## 1. Purpose and Motivation

The original pipeline identified eligible workers using PolicyEngine's `Microsimulation`
class, which loads the enhanced CPS (Annual Social and Economic Supplement, ASEC) microdata
(`enhanced_cps_2024.h5`). While the ASEC provides rich household-level income data suitable
for tax and transfer calculations, it contains a critical flaw for hourly wage identification:
it does not expose a `weeks_worked_last_year` variable, forcing the pipeline to approximate
annual hours as `weekly_hours_worked × 52`.

This assumption systematically misclassifies high-wage part-year workers as low-wage workers:
a California worker who earned $30/hr but only worked 20 weeks reports `employment_income`
of $24,000. Divided by 40 hrs × 52 wks = 2,080, this yields an implied wage of $11.54/hr —
falsely putting them in the $7.25–$16.80 eligible range.

The CPS Outgoing Rotation Group (ORG) supplement solves this problem at the source: it
directly reports the respondent's **usual hourly wage** (for paid-hourly workers) or
**usual weekly earnings** (for all workers). These are point-in-time wage rate measures,
not annual income divided by assumed hours. The same $30/hr California worker reports
`hourwage = $30.00` and is immediately excluded.

This document describes the full methodology for replacing ASEC-based worker identification
with ORG-based worker identification while preserving the PolicyEngine safety-net
interaction schedule infrastructure unchanged.

---

## 2. Architecture Overview: Two-Source Design

The pipeline uses two fundamentally different data sources for two fundamentally different
purposes. They are never merged at the individual record level.

```
CPS ORG microdata (real-wages-generations-ipums repo)
  └─ EPI wage construction (01b_build_org_panel.R)
       └─ org_panel.parquet (with STATEFIP, NCHILD, FAMUNIT, RELATE, WKSTAT)
            └─ 01a_data_ingest.py
                 ├─ Eligibility: hourly_wage_epi in [$7.25, target_wage)
                 ├─ Annual hours: hours_epi × WKSTAT weeks multiplier
                 ├─ Family type: MARST + NCHILD → family_type_key
                 ├─ State: STATEFIP → state abbreviation
                 └─ hourly_workers.parquet  ←── same schema as before
                          │
                          ▼
PolicyEngine pre-computed income schedules (individual_schedules/)
  └─ Built by 01b_precompute_individual.py using PE Simulation (NOT Microsimulation)
       └─ 204 parquets: {family_type_key}_{state_code}.parquet
            └─ 02a_descriptive_stats.py
                 └─ Interpolates safety-net deltas for each worker
                      └─ 5 population output parquets (unchanged)
```

**Key principle:** The ORG data determines *who is eligible and at what wage*. The PE
schedules determine *how taxes and transfers respond to the subsidy*. These are orthogonal
questions answered by the best available tool for each.

---

## 3. CPS ORG vs CPS ASEC — What Each Measures

Understanding why each source is used for its respective role requires understanding
what each survey actually measures.

### CPS ASEC (Annual Social and Economic Supplement)
- Conducted each March; asks about the **prior calendar year**
- `employment_income`: total wages and salaries received in the prior year
- `weekly_hours_worked`: usual hours per week (during the prior year)
- `weeks_worked_last_year` (WKSWORK1): **not exposed by PolicyEngine's enhanced_cps_2024.h5**
- Rich household composition, all income sources (capital, transfers, retirement)
- Used by PolicyEngine for tax and benefit simulation because it has annual totals
- Limitation: annual income / assumed 52 weeks = wage proxy that is contaminated by
  part-year work histories

### CPS ORG (Outgoing Rotation Group, Basic Monthly CPS)
- Conducted every month; asks about the **current week / current job**
- `EARNWEEK` / `EARNWEEK2`: usual weekly earnings before deductions, from the primary job
- `HOURWAGE` / `HOURWAGE2`: hourly wage rate (paid-hourly workers only)
- `UHRSWORKORG` / `UHRSWORK1`: usual weekly hours
- `PAIDHOUR`: whether the respondent is paid by the hour
- No annual income totals; no prior-year work history; no multi-source income decomposition
- Covers only respondents in rotation months 4 and 8 (MISH 4/8), roughly 1/4 of all
  basic monthly CPS respondents each month
- Strength: measures the **current wage rate** directly, immune to part-year contamination

### Why ORG for eligibility, ASEC for safety-net schedules
The PE safety-net schedules (built by `01b_precompute_individual.py`) are parametric grids:
for a synthetic household of a given family type in a given state, what do taxes and
transfers look like at each annual income level from $0 to ~$80,000? These were computed
using PE's `Simulation` class with constructed household situations — no ASEC microdata
is involved. The only input from the worker record into the schedule lookup is:
`(family_type_key, state_code, baseline_income_annual)`. All three are available from ORG.

---

## 4. EPI Wage Construction Methodology

The `real-wages-generations-ipums` repository constructs two hourly wage metrics from the
raw CPS ORG microdata. This pipeline uses the **EPI metric** (`hourly_wage_epi`), which
is the more methodologically rigorous of the two. The construction logic lives in
`code/01_data/01b_build_org_panel.R`.

### 4.1 Sample Frame

Only respondents in rotation months 4 or 8 (`MISH %in% c(4, 8)`) are retained.
These are the "outgoing" rotation groups who receive the earnings supplement questions.

### 4.2 Weekly Earnings Construction

Raw nominal weekly earnings are built from two IPUMS-harmonized variables:

| Variable | Description | Sentinel / missing code |
|---|---|---|
| `EARNWEEK2` | Rounded harmonized weekly earnings (post-1994, preferred) | ≥ 999,999.99 |
| `EARNWEEK` | Legacy weekly earnings variable (pre-1994) | ≥ 9,999.99 |

Preference order: `EARNWEEK2` if positive and non-missing, else `EARNWEEK`. Values at or
above the sentinel threshold are treated as missing.

`EARNWEEK` represents **usual weekly earnings before taxes and deductions from the primary
job**. It includes base pay and any tips, commissions, or overtime that the respondent
considers part of their usual pay — but it does NOT include bonuses, irregular payments,
or earnings from secondary jobs.

### 4.3 Usual Weekly Hours Construction

Hours are built from two variables with preference for `UHRSWORK1`:

| Variable | Description | Special codes |
|---|---|---|
| `UHRSWORK1` | Usual hours per week at main job (basic monthly) | ≥ 997 = invalid |
| `UHRSWORKORG` | Usual hours, ORG supplement version | 997 = hours vary; 998/999 = invalid |

When `UHRSWORKORG == 997`, the respondent's hours vary week to week
(`hours_vary = TRUE`). This triggers the hours-vary imputation step (see §4.5).

Hours above 99 per week are treated as hard outliers and set to missing.

### 4.4 Paid-Hourly Indicator

`PAIDHOUR == 2` indicates the respondent is paid by the hour. This determines the
wage construction path:

- **Paid hourly:** use directly reported hourly wage (`HOURWAGE2` preferred, `HOURWAGE`
  fallback)
- **Not paid hourly (salaried/commission/other):** impute as `weekly_earn / hours_epi`

### 4.5 EPI-Specific Processing

The following steps distinguish the EPI metric from the simpler EIG metric:

**E1. EPI sample eligibility**
Workers must be age 16+ and not self-employed (`CLASSWKR` codes 10–14 = self-employed,
excluded). Self-employment exclusion is methodologically important: self-employed workers
have earnings determined by business profits, not market wages, and the 80-80 Rule does
not apply to them.

**E2. Hours-vary imputation**
For workers flagged as `hours_vary = TRUE` who have valid weekly earnings but no reported
hours, hours are imputed via OLS regression within each calendar month:

```
hours ~ age + age² + sex + education_level
```

Fitted values are constrained to [1, 99]. This avoids discarding variable-hours workers
who have valid earnings data. Approximately a few thousand records per year are imputed.

**E3. EPI hours (`hours_epi`)**
Final hours used in wage construction:
- If `hours_vary` and imputed hours available: use imputed hours
- Else if valid reported hours: use `hours_usual_weekly`
- Else: missing (record excluded from EPI wage calculation)

**E4. Pareto topcode adjustment (pre-April 2023)**
Before April 2023, `EARNWEEK` was topcoded at a fixed threshold that varied by sex
(approximately $2,884.61/week for men, lower for women in older years). Workers at the
topcode are assigned the Pareto-imputed mean above the threshold, computed separately by
sex within each calendar month. This corrects the downward bias in average wages caused
by censoring high earners.

**E5. Phase-in harmonization (April 2023 – March 2024)**
Beginning April 2023, BLS changed the topcode methodology to a dynamic cap. However,
respondents in MISH 8 during this transition period still had the old topcode applied
because their first interview (MISH 4) occurred under the old regime. The pipeline
detects these cases and adjusts MISH 8 topcoded records to match the mean earnings of
MISH 4 respondents above the old threshold in the same month.

**E6. EPI hourly wage (`hourly_wage_epi`)**
Final wage construction:
```
if not epi_sample_eligible:           → NA
if paid_hourly and HOURWAGE2 valid:   → HOURWAGE2
if paid_hourly and HOURWAGE valid:    → HOURWAGE
if not paid_hourly and earn + hours valid: → weekly_earn_epi / hours_epi
else:                                 → NA
```

`hourly_wage_epi_valid = TRUE` only when a non-missing, positive, finite wage is produced
and the record is EPI-eligible.

### 4.6 What hourly_wage_epi Is — and Is Not

`hourly_wage_epi` measures the **current market wage rate** for the worker's current
primary job as of the survey reference week. It is:

- **Not** derived from annual income divided by assumed hours (the ASEC proxy)
- **Not** affected by how many weeks the worker worked last year
- **Correct for part-year workers**: a seasonal worker at $30/hr reports `hourly_wage_epi
  = $30.00` regardless of how few weeks they worked
- **Primary job only**: earnings from a second job are excluded
- **Usual pay only**: irregular bonuses, one-time payments not included
- **Tipped workers**: `EARNWEEK` is supposed to capture usual total pay including tips
  if regularly received, but respondent reporting of variable tip income is imprecise

---

## 5. Variables Added to the IPUMS Extract

The following variables were added to `variable_list_requested` in
`code/01_data/01a_ipums_extract_define_download.R` in the `real-wages-generations-ipums`
repository. The extract re-submission was triggered by the changed variable list detected
at runtime.

| IPUMS Variable | Type | Purpose in EIG pipeline |
|---|---|---|
| `STATEFIP` | Integer (FIPS code) | Geographic unit for state-level aggregation and PE safety-net schedule lookup. Mapped to two-letter abbreviation in the ingest script. |
| `NCHILD` | Integer (0–9) | Number of own children under 18 in household. Used with `MARST` to derive `family_type_key`. |
| `FAMUNIT` | Integer | Family unit number within household. Enables optional "one primary earner per family unit" filter consistent with the PE tax-unit-head approach. |
| `RELATE` | Categorical | Relationship to household reference person. Identifies the household reference person and other family unit members. |
| `WKSTAT` | Categorical | Work status: full-time, part-time for economic reasons, part-time for non-economic reasons, at work with variable schedule. Used to assign the annual weeks multiplier. |

**Note:** `SERIAL` (household serial number) was already present in the raw extract.
`FAMUNIT` and `RELATE` together with `SERIAL` allow family unit grouping when needed.

**Pending:** Exact integer codes for `WKSTAT` and `RELATE` must be verified against the
DDI codebook accompanying the new IPUMS extract. Code values have shifted across CPS
history and are recorded in IPUMS harmonized form. Update this document with confirmed
codes once the extract has downloaded.

---

## 6. Eligibility Determination

### 6.1 Federal Minimum Wage Floor

Before any eligibility check, each worker's reported wage is floored at the federal
minimum wage ($7.25/hr):

```python
FEDERAL_MIN_WAGE = 7.25  # USD per hour

employer_wage = max(hourly_wage_epi, FEDERAL_MIN_WAGE)
```

This floor is applied **universally and unconditionally**, prior to the eligibility filter
and subsidy calculation. It is a policy assumption, not a data cleaning step:

- **Rationale:** The 80-80 Rule sets the federal minimum as the absolute wage floor.
  A worker whose reported `hourly_wage_epi` falls below $7.25 — most commonly a tipped
  worker legally paid at the federal tipped minimum ($2.13/hr base) — is treated by this
  policy as earning $7.25 for subsidy purposes.
- **Effect:** These workers are not excluded. They are included at the floored wage and
  receive the maximum subsidy (`0.80 × ($16.80 − $7.25) = $7.64/hr`).
- **State minimums are not used as floors.** A tipped worker in California who legally
  earns below the state's $16/hr minimum is still floored only at the federal $7.25,
  not at the California minimum. The policy does not override state tipped wage
  carve-outs — it simply asserts a federal floor for the subsidy formula.
- `hourly_wage_epi` values below zero or implausibly low (measurement error) are handled
  separately: records with `hourly_wage_epi_valid == False` are excluded before this
  floor is applied.

### 6.2 Eligibility Filter

After the floor is applied, a worker is eligible if:

```python
employer_wage < TARGET_WAGE         # floored wage below target (upper bound)
epi_sample_eligible == True         # age 16+, not self-employed
hourly_wage_epi_valid == True       # non-missing, positive, finite (pre-floor check)
age >= 16 and age <= 64             # working-age filter; 65+ excluded as SS proxy
not (relate == 301 and age < 19)    # tax-dependent exclusion
```

The `age <= 64` ceiling serves as a proxy exclusion for Social Security recipients; the CPS ORG does not collect income-by-source, so true SS receipt cannot be identified directly. The dependent exclusion removes workers who are a child of the household head (`relate == 301`) and under 19 years old — the standard qualifying-child dependent definition. Note that qualifying *relative* dependents (any age, income below IRS threshold) cannot be identified from ORG data alone.

Note: the lower bound check (`employer_wage >= BASE_WAGE`) is automatically satisfied
after flooring — no worker survives to this step with `employer_wage < $7.25`.

`TARGET_WAGE` is computed dynamically from the same ORG dataset (see §10).

No filter to "household head" is applied. The 80-80 Rule is a per-worker wage subsidy:
every eligible worker receives the subsidy regardless of their household position. The
PE Microsimulation approach filtered to `is_tax_unit_head` because PE's entity structure
models one representative earner per tax unit. With ORG microdata, all eligible workers
are retained. This is the methodologically correct treatment of a per-worker subsidy.

An optional `FAMUNIT`-based primary earner filter is documented in §11 as a sensitivity
check for cost estimate comparability with the original PE approach.

---

## 7. Annual Hours Calculation via WKSTAT

The ORG does not contain `weeks_worked_last_year` (an ASEC-only variable). Annual hours
must therefore be approximated as `hours_epi × weeks_multiplier(WKSTAT)`.

This differs from the original `weekly_hours × 52` flat assumption in one critical way:
the wage rate used for eligibility (`hourly_wage_epi`) is now correct regardless of weeks
worked. The WKSTAT-based weeks multiplier improves the annual income proxy used for
safety-net schedule lookup, but it does not affect eligibility determination.

### 7.1 WKSTAT Weeks Multiplier Mapping

**Note:** The WKSTAT code values below are conceptual groupings. Exact IPUMS integer
codes must be verified against the new DDI extract. This table will be updated once
codes are confirmed.

| WKSTAT conceptual group | BLS definition | Weeks multiplier | Rationale |
|---|---|---|---|
| **Full-time** | Usually works 35+ hours/week; at work during reference week | **52** | Year-round FT employment is the norm for most retail, food service, healthcare support workers in the target wage range |
| **Part-time, economic reasons** | Involuntary: slack work, business conditions, could not find full-time work | **40** | Involuntary part-time workers are more likely to have gaps in employment; underemployment correlates with seasonal and irregular work patterns |
| **Part-time, non-economic reasons** | Voluntary: student, caregiver, industry where full-time is < 35 hrs | **48** | Most voluntary part-time workers maintain year-round employment; slight discount applied for scheduling gaps |
| **At work, not usual schedule** | At work during reference week but not usual hours (vacation, holiday, illness, weather) | **48** | Treated identically to PT non-economic per project design decision; these are predominantly usually-full-time workers whose reference-week hours are temporarily reduced |

**Hours calculation:**
```python
annual_hours = hours_epi * weeks_multiplier(wkstat)
```

Workers with missing or unclassifiable WKSTAT default to the full-time multiplier (52)
with a diagnostic warning. This is conservative (overestimates annual income for
uncertain-schedule workers) rather than dropping records.

### 7.2 Annual Income Proxy

All downstream calculations use `employer_wage` (the floored wage from §6.1), not the
raw `hourly_wage_epi`, to ensure consistency between eligibility, income proxies, and
subsidy amounts:

```python
baseline_income = employer_wage * annual_hours
               = employer_wage * hours_epi * weeks_multiplier(wkstat)
```

For the cost calculation:
```python
subsidy_hr     = max(0, TARGET_WAGE - employer_wage) * SUBSIDY_PCT
subsidy_annual = subsidy_hr * annual_hours
```

**Limitations of this proxy (documented for transparency):**

1. **Weeks-worked assumption remains approximate.** WKSTAT captures current full/part-time
   status, not prior-year weeks worked. A worker who is currently full-time but took a
   leave earlier in the year will have their annual income overstated.

2. **Primary job only.** `hourly_wage_epi` and `hours_epi` reflect the primary job.
   Multiple job holders' total annual employment income is understated, shifting their
   safety-net schedule lookup to a lower income point (overstating benefits, understating
   taxes).

3. **Usual vs actual hours.** `hours_epi` is usual weekly hours, not last-week hours.
   Workers with high volatility (gig workers, on-call retail) may report a "usual" figure
   that does not reflect their realized annual pattern.

4. **Direction of residual bias.** For part-year workers who are incorrectly assigned
   a full weeks multiplier, baseline income is overstated → safety-net schedule lookup
   is at a higher income point → benefits understated, taxes overstated. The net cost
   estimate will therefore tend to slightly underestimate safety-net offsets and
   slightly overestimate tax revenue, resulting in a modest upward bias in net program
   cost for this subgroup.

These limitations are second-order relative to the primary improvement: eligibility
classification is now based on the actual current wage rate, eliminating the systematic
part-year contamination present in the ASEC-based approach.

---

## 8. Family Type Key Derivation

The PE pre-computed schedules cover four household archetypes used as the basis for
safety-net interaction lookups:

| family_type_key | Description |
|---|---|
| `single_0c` | Single adult, no children |
| `single_2c` | Single adult, with children |
| `married_0c` | Married couple, no children |
| `married_2c` | Married couple, with children |

These are derived from two ORG variables:

### 8.1 Marital Status (MARST)

| MARST code | Label | Mapping |
|---|---|---|
| 1 | Married, spouse present | `married` |
| 2 | Married, spouse absent | `married` |
| 3 | Separated | `single` |
| 4 | Divorced | `single` |
| 5 | Widowed | `single` |
| 6 | Never married / single | `single` |

MARST codes 1–2 are treated as married because both may file jointly for tax purposes.
The PE household simulations model joint filers as a married couple with one working
adult and one non-working spouse.

### 8.2 Children (NCHILD)

`NCHILD` = number of own children under 18 present in the household.

```python
has_children = NCHILD >= 1
```

Workers with 1 or more children are assigned to the `_2c` schedule. This matches the
PE simulation convention where the "2 children" schedule is used as the closest available
approximation for any household with dependents.

### 8.3 Key Construction

```python
prefix = "married" if MARST in {1, 2} else "single"
suffix = "2c" if NCHILD >= 1 else "0c"
family_type_key = f"{prefix}_{suffix}"
```

---

## 9. State Code Mapping

`STATEFIP` is a numeric FIPS code (1–56, with gaps for territories and unnumbered entries).
The PE safety-net schedules use two-letter state abbreviations as filenames
(`{family_type_key}_{state_code}.parquet`). The mapping is applied in the ingest script.

Full FIPS-to-abbreviation lookup table (to be implemented in `01a_data_ingest.py`):

```python
FIPS_TO_STATE = {
    1: "AL",  2: "AK",  4: "AZ",  5: "AR",  6: "CA",  8: "CO",  9: "CT",
   10: "DE", 11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL",
   18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD",
   25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
   32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND",
   39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD",
   47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV",
   55: "WI", 56: "WY",
}
```

Records with STATEFIP codes not in this table (e.g., territories: 72 = Puerto Rico)
are excluded from the analysis with a warning. The PE schedules cover the 50 states
plus DC only.

---

## 10. Dynamic Median Wage and Target Wage

The current `00_config.py` hardcodes `ws_median_hourly_wage = 21.00`. With ORG data
available through 2025, this should be computed dynamically at ingest time.

**Definition:** Weighted median of `hourly_wage_epi` among paid-hourly
(non-salaried), EPI-eligible, employed workers in the most recent 12 months of ORG data.

**2025–2026 result (12 pooled year-months):**
- Weighted median, paid-hourly workers: **$21.00/hr**
- Pooled across 2025 (11 months — October absent from extract) and 2026 (partial year); ingest uses unique `(year, month)` groups for `n_months` so weighting remains internally consistent regardless of missing months.

**Computation in `01a_data_ingest.py`:**
```python
# Most recent 12 months of valid paid-hourly workers
recent = org[
    (org["year"] >= recent_year_start) &
    (org["hourly_wage_epi_valid"]) &
    (org["paid_hourly"] == True) &
    (org["epi_sample_eligible"])
]
wages  = recent["hourly_wage_epi"].values
weights = recent["earnwt"].values
# Weighted median
sort_idx = np.argsort(wages)
cumw = np.cumsum(weights[sort_idx])
median_wage = wages[sort_idx][np.searchsorted(cumw, cumw[-1] * 0.5)]

TARGET_WAGE = round(median_wage * SUBSIDY_PCT, 2)  # 80% of median
```

The dynamic median replaces the hardcoded value in config and propagates into all
downstream calculations automatically.

---

## 11. Weighting Methodology

This is the most consequential methodological difference between the ASEC-based and
ORG-based approaches. Incorrect weighting produces wrong population totals and cost
estimates.

### 11.1 Weight Variables Available in CPS

| Weight variable | Source | Calibration target | When to use |
|---|---|---|---|
| `EARNWT` | ORG supplement | Civilian wage/salary workers in employment, reference month | **Use for all ORG wage analysis** |
| `WTFINL` | Basic monthly CPS | Civilian non-institutional population, reference month | Labor force participation, unemployment analysis |
| `ASECWT` / `ASECWTH` | CPS ASEC | Civilian non-institutional population, prior calendar year | ASEC (prior-year income) analysis only |
| `person_weight` (PE) | enhanced_cps_2024 | PE's internal CPS ASEC calibration | PE Microsimulation only — do not use with ORG data |

**For all EIG wage subsidy analysis using ORG data: use `EARNWT` exclusively.**

`EARNWT` is specifically designed for the earner study and is calibrated to the wage-
earning employed population. It is the weight recommended by IPUMS and used by EPI, BLS,
and all standard ORG wage analyses.

`WTFINL` is inappropriate for wage analysis because it is calibrated to the entire
civilian non-institutional population (including unemployed, out-of-labor-force persons).
Using `WTFINL` for wage statistics would misrepresent the population of wage earners.

### 11.2 The Monthly Pooling Problem

The ORG is a monthly cross-section: each month's `EARNWT` values sum to approximately
the total civilian wage-earning employed population for that month (~130–140 million
workers in recent years).

When pooling N months of ORG data:

**DO NOT** sum `earnwt` directly across months for population counts. Doing so overstates
the population by a factor of N.

**CORRECT approach for population-weighted cost estimates:**

```python
# If pooling N months (e.g., 12 months of 2025):
n_months = len(df["month"].unique())
df["earnwt_monthly"] = df["earnwt"] / n_months

# Gross annual cost
gross_cost_annual = (df["subsidy_annual"] * df["earnwt_monthly"]).sum()

# Eligible worker count (annual average)
n_workers = df["earnwt_monthly"].sum()
```

This yields the monthly-average population of eligible workers, which represents the
steady-state stock of workers who qualify at any given time. For an annual cost estimate,
`subsidy_annual = subsidy_hr × hours_epi × weeks_multiplier` already accounts for the
full year of subsidy payments per worker, so no further annual scaling is needed.

**CORRECT approach for weighted statistics (medians, means, distributions):**

For ratio statistics (medians, percentiles, weighted means of wage rates, subsidy
amounts), `earnwt` can be used directly without division — the denominators cancel:

```python
# Weighted mean subsidy (earnwt or earnwt/N both give same result)
avg_subsidy = np.average(df["subsidy_annual"], weights=df["earnwt"])
```

### 11.3 Comparison with PE ASEC Approach

The PE Microsimulation used `person_weight` (derived from `ASECWT`) over 43,236 annual
ASEC person records. The ASEC weight is calibrated to represent the prior-year annual
population — it already accounts for full-year coverage since ASEC is conducted once per
year.

The ORG approach uses `earnwt / n_months` over ~300,000 total records per year (roughly
25,000 ORG-eligible persons per month × 12 months). The division by `n_months` is
necessary to match the ASEC's annual population accounting.

**Expected result:** Both approaches should yield comparable eligible worker counts
(approximately 25–30M workers nationally). The 2024 ORG estimate with EARNWT/12 gives
~28M eligible workers vs the PE ASEC estimate of 26.87M — consistent agreement at
roughly 5% difference, attributable to the wage measurement improvement.

### 11.4 Within-Year Duplicate Observations

CPS respondents appear in the ORG supplement twice during their 16-month panel tenure:
once in MISH 4 and once in MISH 8, approximately 8–12 months apart. Within a single
calendar year, some respondents will contribute both a MISH 4 and a MISH 8 observation.

The `EARNWT/n_months` approach inherently accounts for this through the averaging: if a
person appears twice in 2025 (say March and November), their MISH 4 observation
contributes to the March monthly average and their MISH 8 observation contributes to
the November monthly average. Both observations have separate `EARNWT` values calibrated
to their respective reference months, and dividing by 12 ensures neither is
double-counted at the annual level.

For wage distribution statistics (medians, percentiles), the duplicate observations add
precision without introducing bias, since `EARNWT` weights each observation to its
reference month's population.

---

## 12. Integration with PE Safety-Net Schedules

### 12.1 What the PE Schedules Contain

Each of the 204 pre-computed parquet files (`{family_type_key}_{state_code}.parquet`
in `individual_schedules/`) contains a grid of annual employment income values indexed
from $0 to approximately $80,000, with columns for each income/benefit component:

```
index: annual_employment_income (e.g., 0, 500, 1000, ..., 80000)
columns: eitc, child_tax_credit, snap, medicaid_chip, aca_ptc, ssi, tanf,
         housing, ccdf, wic, school_meals, liheap, other_benefits,
         federal_tax, state_tax, payroll_tax, net_income
```

These were computed by running PolicyEngine's `Simulation` on a synthetic household
(one working adult, specified family type, zero other income sources) at each income
level for each state. They represent the tax and transfer environment for a representative
household, not any individual CPS respondent.

### 12.2 The Lookup Operation

For each worker in `hourly_workers.parquet`:

```python
# 1. Find the matching schedule
schedule = load_schedule(family_type_key, state_code)
# fallback chain: single_0c(same state) → exact key(TX) → single_0c(TX)

# 2. Interpolate at baseline income and subsidy income
baseline_income = hourly_wage_epi * annual_hours
subsidy_income  = baseline_income + subsidy_annual

for col in SCHEDULE_COLS:
    baseline_v = np.interp(baseline_income, income_axis, schedule[col])
    subsidy_v  = np.interp(subsidy_income,  income_axis, schedule[col])
    delta[col] = subsidy_v - baseline_v  # change due to subsidy
```

### 12.3 What the Integration Assumes

The schedule lookup maps each ORG worker to a representative PE household. This mapping
assumes:

1. The worker's only employment income source is their ORG-derived annual income proxy
   (`hourly_wage_epi × annual_hours`). Other income sources (spouse, capital, other jobs)
   are not modeled.
2. The family structure (married/single, has_children) is correctly classified from
   MARST and NCHILD.
3. The state-specific tax and transfer rules encoded in the PE schedule are representative
   for the worker's actual situation.

These assumptions were already present in the original pipeline (which also used the
pre-computed schedules). Switching to ORG data for worker identification does not change
these assumptions — it only changes the income level at which the worker enters the
schedule, using a more accurate wage rate.

---

## 13. Process Flow — End to End

```
Step 1: IPUMS Extract (real-wages repo, R)
   01a_ipums_extract_define_download.R
   Variables: YEAR, MONTH, MISH, CPSID, CPSIDP, EARNWT, WTFINL, AGE, SEX,
              RACE, HISPAN, MARST, EDUC, EMPSTAT, PAIDHOUR, HOURWAGE, HOURWAGE2,
              EARNWEEK, EARNWEEK2, UHRSWORKORG, UHRSWORK1, CLASSWKR,
              STATEFIP [NEW], NCHILD [NEW], SERIAL, FAMUNIT [NEW],
              RELATE [NEW], WKSTAT [NEW]
   Output: data/raw/ipums/cps_by_year/cps_raw_{YYYY}.parquet

Step 2: ORG Panel Build (real-wages repo, R)
   01b_build_org_panel.R
   - Filter to MISH 4/8
   - Construct weekly_earn_nominal, hours_usual_weekly, paid_hourly
   - EPI steps E1–E6: eligibility, hours imputation, Pareto topcode,
     phase-in harmonization, hourly_wage_epi
   - Pass-through of new variables (statefip, nchild, famunit, relate, wkstat)
   Output: data/processed/org_panel_by_year/org_panel_{YYYY}.parquet
           data/processed/org_panel.parquet (monolithic, backward-compatible)

Step 3: Data Export to EIG Repo (Python, manual or scripted)
   - Read most recent year's org_panel parquet from real-wages repo
   - Filter columns to EIG-relevant subset
   - Save to WORKSPACE/data/external/org_workers_{YYYY}.parquet in EIG repo

Step 4: Worker Identification (EIG repo, Python)
   WORKSPACE/code/01_data_preparation/01a_data_ingest.py  [REWRITTEN]
   - Read org_workers_{YYYY}.parquet
   - Compute dynamic median wage → TARGET_WAGE
   - Filter: epi_sample_eligible, valid wage, age 16–64 (65+ excluded as SS proxy)
   - Exclude tax dependents: relate == 301 and age < 19
   - Apply federal minimum wage floor: employer_wage = max(hourly_wage_epi, $7.25)
   - Filter: employer_wage < TARGET_WAGE (upper bound eligibility)
   - Map STATEFIP → state abbreviation
   - Derive family_type_key from MARST + NCHILD
   - Assign annual_hours via WKSTAT weeks multiplier
   - Compute baseline_income, subsidy_hr, subsidy_annual
   - Weight = earnwt / n_months
   Output: WORKSPACE/data/processed/hourly_workers.parquet

Step 5: Population Aggregation (EIG repo, Python) — UNCHANGED
   WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.py
   - Loads hourly_workers.parquet
   - Looks up PE safety-net schedules by (family_type_key, state_code)
   - Interpolates deltas at baseline_income and subsidy_income
   - Aggregates with weights to produce 5 population output parquets

Step 6: Verification (EIG repo, Python) — UNCHANGED
   WORKSPACE/code/05_figures_tables/05a_main_outputs.py
```

---

## 14. Assumptions and Limitations Inventory

| # | Assumption | Direction of bias | Severity |
|---|---|---|---|
| A1 | Annual hours = hours_epi × weeks_multiplier(WKSTAT) | Overstates annual income for workers who did not work all weeks | Moderate — affects safety-net lookup, not eligibility |
| A2 | WKSTAT weeks multipliers (52 / 48 / 40) are reasonable priors for annual work weeks by FT/PT status | Unknown; based on CPS ASEC cross-section evidence | Low-moderate |
| A3 | Wage subsidy is treated as fully taxable employment income in PE schedules | Correct per policy design — subsidy is taxable income | None — intentional |
| A4 | Family type from MARST + NCHILD maps well to the PE household archetypes | May misclassify complex households (cohabitating couples, extended family) | Low — broad categories |
| A5 | PE schedule assumes only employment income for the worker | Ignores spouse income, capital income, transfers already received | Pre-existing; same in original pipeline |
| A6 | EARNWEEK reflects usual pay including tips and commissions | Variable-pay workers (commission sales, tipped service) may have noisy EARNWEEK | Low — affected workers tend to be near median, not in low-wage range |
| A9 | Tipped workers with hourly_wage_epi below $7.25 are floored to $7.25 and included as eligible | Policy design assumption; may slightly overstate eligible worker count relative to a strict exclusion approach | Low — tipped workers below $7.25 are a small share of total eligibles; flooring effect on cost is bounded (max subsidy = $7.64/hr) |
| A7 | No secondary job earnings included | Understates total income for multiple job holders | Low — rare in target wage range |
| A8 | earnwt / n_months correctly annualizes ORG monthly weights | Assumes stable population composition across months in the year | Low — population is stable month-to-month |

---

## 15. Verification Status — Variable Codes and Universe Checks

### 15.1 Confirmed from `01b_build_org_panel.R` source code

The following codes are used directly in the R pipeline and are confirmed correct:

| Variable | Code | Confirmed value | Source |
|---|---|---|---|
| `MARST` | Married (spouse present or absent) | 1, 2 | R code lines 232–239 |
| `MARST` | Separated | 3 | R code |
| `MARST` | Divorced | 4 | R code |
| `MARST` | Widowed | 5 | R code |
| `MARST` | Never married | 6 | R code |
| `CLASSWKR` | Self-employed (excluded from EPI sample) | 10–14 | R code lines 262–263 |
| `PAIDHOUR` | Paid by the hour | 2 | R code line 150 |
| `UHRSWORKORG` | Hours vary week to week | 997 | R code line 110 |
| `UHRSWORKORG` | Invalid/not in universe | >= 997 → NA | R code line 111 |

### 15.2 Pass-through variables — present in org panel parquets, codes unverified

The `01b_build_org_panel.R` script does not process the five EIG-specific variables.
They pass through from the raw CPS parquets via `arrow::read_parquet() %>% janitor::clean_names()`
and are retained in the org panel output with their raw IPUMS integer values under
lowercase column names:

| Raw IPUMS name | Column in org panel parquet | Status |
|---|---|---|
| `STATEFIP` | `statefip` | Present; FIPS integer codes are standard and stable — lookup table in §9 is correct |
| `NCHILD` | `nchild` | Present; integer count 0–9 confirmed from IPUMS documentation |
| `FAMUNIT` | `famunit` | Present; integer family unit number within household |
| `RELATE` | `relate` | Present; integer codes unverified — see §15.3 |
| `WKSTAT` | `wkstat` | Present; integer codes unverified — see §15.3 |

### 15.3 Confirmed — WKSTAT codes from DDI and data inspection

**Source:** Online IPUMS DDI codebook for extract #304 (CPS Basic Monthly, WKSTAT variable,
start position 145, width 2). Confirmed against `wkstat.value_counts()` on
`org_panel_2025.parquet` (n=296,369 records).

| Code | DDI Label | 2025 count | Weeks multiplier | Rationale |
|------|-----------|-----------|-----------------|-----------|
| 11 | Full-time hours (35+), usually full-time | 102,226 | **52** | Core FT workforce |
| 12 | Part-time for non-economic reasons, usually full-time | 8,045 | **48** | Usually FT but currently reduced hours voluntarily |
| 13 | **Not at work**, usually full-time | 3,518 | **52** | On leave/holiday; FT worker, not a PT worker |
| 14 | Full-time hours, usually part-time for **economic** reasons | 125 | **40** | Usual status is involuntary PT; drives annual weeks |
| 15 | Full-time hours, usually part-time for **non-economic** reasons | 690 | **48** | Usual status is voluntary PT |
| 21 | Part-time for economic reasons, usually full-time | 1,327 | **40** | Involuntary PT this week |
| 22 | Part-time hours, usually part-time for economic reasons | 2,600 | **40** | Chronically involuntary PT |
| 41 | Part-time hours, usually part-time for non-economic reasons | 20,139 | **48** | Voluntary PT (students, caregivers) |
| 42 | Not at work, usually part-time | 1,527 | **48** | On leave; PT worker |
| 50 | Unemployed, seeking full-time work | 4,468 | — | Filtered: no valid wage |
| 60 | Unemployed, seeking part-time work | 1,103 | — | Filtered: no valid wage |
| 99 | NIU, blank, or not in labor force | 150,601 | — | Filtered: no valid wage |

**Implementation in `01a_data_ingest.py`:**
```python
WKSTAT_WEEKS = {
    11: 52,   # FT hours, usually FT → full year
    12: 48,   # PT non-economic, usually FT → slight discount
    13: 52,   # Not at work, usually FT → on leave; FT worker
    14: 40,   # FT this week, usually PT economic → usual status drives
    15: 48,   # FT this week, usually PT non-economic → usual status drives
    21: 40,   # PT economic, usually FT → involuntary PT
    22: 40,   # PT, usually PT for economic reasons → chronic involuntary PT
    41: 48,   # PT, usually PT for non-economic reasons → voluntary PT
    42: 48,   # Not at work, usually PT → PT worker on leave
}
DEFAULT_WEEKS = 52  # fallback for unclassified codes (conservative)
```

**Note on codes 10/20/40:** These are aggregate summary codes in the DDI but do not appear
in the 2025 data (or any post-2000 data). The detailed codes (11–42) are always populated
for employed respondents. The `DEFAULT_WEEKS = 52` fallback handles any future edge cases.

**RELATE reference-person code:** Confirmed as **101** from 2025 data
(`relate.value_counts()` shows 101 as the dominant code with 125,057 records).
Needed only for the optional FAMUNIT-based primary-earner sensitivity filter (§11).

**NCHILD in basic monthly CPS:** Confirmed populated. The 2025 org panel shows
`nchild` ranging from 0–9 with 82,084 workers (28%) reporting at least one child.
No systematic zero-inflation observed. The variable is valid for family type derivation.

---

## 16. Key Differences from Original PE Microsimulation Approach

| Dimension | Original (PE ASEC) | New (CPS ORG) |
|---|---|---|
| **Wage measure** | `employment_income / (weekly_hours × 52)` | `hourly_wage_epi` (directly reported or `weekly_earn / hours`) |
| **Part-year workers** | Misclassified as low-wage (systematic upward bias in eligibles) | Correctly identified at actual wage rate |
| **Annual income proxy** | `employment_income` (actual prior-year total) | `hourly_wage_epi × hours_epi × weeks_multiplier(WKSTAT)` |
| **Self-employment** | Filtered via `is_tax_unit_head`; self-employed may be included | Explicitly excluded via `CLASSWKR` (EPI sample eligibility) |
| **Worker unit** | One per tax unit (tax-unit head filter) | All eligible workers |
| **Weight** | `person_weight` from ASEC (annual calibration, 43k records) | `EARNWT / n_months` (monthly calibration, ~300k records/year) |
| **State resolution** | Expanded from household level via `nb_persons()` | Direct from `STATEFIP` per record |
| **Children** | Expanded from tax-unit level via `nb_persons()` | Direct from `NCHILD` per record |
| **Wage floor** | $7.25 applied as lower eligibility bound (exclusion) | $7.25 applied as policy floor before subsidy calculation (inclusion at floor) |
| **Tipped workers below $7.25** | Excluded from eligible population | Included at floored wage of $7.25; receive maximum subsidy |
| **Median wage** | Hardcoded $21.00/hr in config | Computed dynamically from ORG data |
| **Target wage** | Hardcoded $16.80/hr | Computed as 80% of dynamic median |
| **PE role** | Worker identification + safety-net schedules | Safety-net schedules only |
