# EIG Wage Subsidy Policy Simulation

**Authors:** Benjamin Glasner and Adam Ozimek (Economic Innovation Group)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://eig-wage-subsidy.streamlit.app/)

---

## Overview

This repository models the Economic Innovation Group's **80-80 Rule** wage subsidy proposal — a direct-to-worker transfer that fills 80% of the gap between a worker's employer-paid wage and a target set at 80% of the national median hourly wage. The project estimates who is eligible, what the subsidy is worth to each worker, what it costs the government gross and net of tax and safety-net responses, and how those effects are distributed across the workforce.

The interactive app is live at **[eig-wage-subsidy.streamlit.app](https://eig-wage-subsidy.streamlit.app/)**.

---

## The Policy: The 80-80 Rule

The subsidy is defined by four parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `base_wage` | $7.25 | Federal minimum wage floor — minimum employer-paid wage to qualify |
| `target_pct` | 0.80 | Target wage as share of median paid-hourly wage |
| `subsidy_pct` | 0.80 | Fraction of the wage gap filled by the subsidy |
| `M` | Dynamic | Weighted median paid-hourly wage from CPS ORG (current run: ~$21.00/hr) |

**Mechanics:**

- Target wage `T = 0.80 × M` (current run: ~$16.80/hr)
- Hourly subsidy = `0.80 × max(0, T − employer_wage)`
- Annual subsidy = hourly subsidy × annual hours worked
- Workers at or above `T` receive zero subsidy; subsidy phases out linearly as wages rise toward `T`

**Illustrative examples** (current parameterization):

| Employer wage | Hourly subsidy | Full-time annual subsidy |
|---------------|---------------|--------------------------|
| $7.25/hr | $7.64/hr | ~$15,890 |
| $10.00/hr | $5.44/hr | ~$11,320 |
| $13.00/hr | $3.04/hr | ~$6,320 |
| $16.80/hr | $0.00 | $0 |

All four parameters are adjustable in the interactive app.

---

## Key Findings (Current Run)

Estimates are based on pooled 2025–2026 CPS Outgoing Rotation Group (ORG) microdata:

| Metric | Value |
|--------|-------|
| Eligible workers | **21.4 million** |
| Average annual subsidy | **$4,417** |
| Gross annual cost | **$94.4B** |
| Net annual cost (after tax recapture and safety-net offsets) | **$73.2B** |

**Scale in context:** The gross cost is comparable to the Earned Income Tax Credit (~$70–75B/year, ~23M claimant households), but the two programs differ fundamentally. The EITC is assessed against household income and strongly shaped by household composition. The 80-80 Rule targets the employer-paid wage rate directly, making eligibility a function of the job rather than household circumstances — extending coverage to single workers and secondary earners who receive little or no EITC. For additional context, [Bartik (2020)](https://research.upjohn.org/cgi/viewcontent.cgi?article=1034&context=up_policypapers) estimates governments already spend roughly $80B per year on job creation, most of it in large-business tax breaks with limited evidence of effectiveness in distressed communities.

---

## Architecture: Two-Source Design

The pipeline deliberately separates two modeling tasks that require different data:

```
CPS ORG microdata
    └── Wage identification (who is eligible, at what wage, for how many hours)
            └── hourly_workers.parquet

PolicyEngine-US pre-computed household schedules
    └── Safety-net and tax interactions (how taxes and transfers respond to higher earnings)
            └── {family_type}_{state}.parquet  [204 files, 4 types × 51 states]

Combined in 02a_descriptive_stats.py
    └── Population-level aggregates, cost estimates, distributional breakdowns
```

**Why two sources?** ORG and ASEC/PolicyEngine inputs are not a common panel and do not support defensible one-to-one linkage. ORG is the preferred source for wage-rate identification; PolicyEngine schedules provide consistent tax-transfer response modeling by household type and state.

---

## Repository Structure

```
eig-wagesubsidy-policy-sim/
├── WORKSPACE/
│   ├── app/                          # Streamlit interactive application
│   │   ├── app.py                    # Entry point
│   │   ├── tabs/
│   │   │   ├── calculator.py         # Individual wage calculator tab
│   │   │   ├── population.py         # Population-level impacts tab
│   │   │   └── methods.py            # Methodology documentation tab
│   │   └── utils/
│   │       ├── household_sim.py      # Schedule interpolation and simulation logic
│   │       ├── subsidy.py            # Subsidy math helpers
│   │       ├── states.py             # State code utilities
│   │       └── eig_style.py          # Brand colors and Plotly layout defaults
│   ├── code/
│   │   ├── 00_setup/                 # Config and environment setup
│   │   │   └── 00_config.py          # Paths, parameters, defaults
│   │   ├── 01_data_preparation/
│   │   │   ├── 00_export_org_data.py # Export CPS ORG subset from companion repo
│   │   │   ├── 01a_data_ingest.py    # Build eligible worker analysis file
│   │   │   └── 01b_precompute_individual.py  # Pre-compute 204 household schedules
│   │   ├── 02_descriptive_analysis/
│   │   │   └── 02a_descriptive_stats.py  # Population aggregates and distributional output
│   │   └── 04_robustness_heterogeneity/
│   │       └── 04b_org_validation_framework.py  # Validation and sensitivity checks
│   ├── data/
│   │   ├── external/                 # org_workers_{year}.parquet (from ORG export)
│   │   └── processed/                # hourly_workers.parquet (eligible workers)
│   ├── output/
│   │   └── data/intermediate_results/
│   │       ├── population/           # summary, by_state, by_wage_bracket, etc.
│   │       └── individual_schedules/ # 204 pre-computed household income schedules
│   └── docs/
│       └── pipeline_methodology_public.md  # Full public methodology reference
└── INFRA/                            # Internal docs, style guides, agent config
```

---

## Data Pipeline

### Prerequisites

- Python virtual environment with `pandas`, `pyarrow`, `policyengine_us`, `streamlit`
- Companion repository [`real-wages-generations-ipums`](https://github.com/bnglasner/real-wages-generations-ipums) at the same directory level (provides `org_panel_{year}.parquet` files)

### Execution Sequence

```powershell
# 1. Export recent CPS ORG panel subset
.\.venv\Scripts\python.exe WORKSPACE\code\01_data_preparation\00_export_org_data.py

# 2. Build eligible worker analysis file (wage identification, hours, family type)
.\.venv\Scripts\python.exe WORKSPACE\code\01_data_preparation\01a_data_ingest.py

# 3. Pre-compute 204 household income schedules (one-time, slow; ~30-60 min)
.\.venv\Scripts\python.exe WORKSPACE\code\01_data_preparation\01b_precompute_individual.py

# 4. Build population aggregates with schedule interpolation
.\.venv\Scripts\python.exe WORKSPACE\code\02_descriptive_analysis\02a_descriptive_stats.py

# 5. Optional: run validation framework
.\.venv\Scripts\python.exe WORKSPACE\code\04_robustness_heterogeneity\04b_org_validation_framework.py

# 6. Launch interactive app
.\.venv\Scripts\streamlit.exe run WORKSPACE\app\app.py --server.port 8501
```

Step 3 only needs to be re-run if PolicyEngine-US is updated or household type/state coverage changes. Steps 1–2 and 4 should be re-run when new ORG data becomes available.

---

## Interactive Application

The Streamlit app has three tabs:

### Individual Wage Calculator
Enter an employer-paid wage, state, and household type to see:
- Hourly and annual subsidy amount
- Full budget constraint chart — income by source across all hours-worked levels, comparing Baseline vs. With Subsidy scenarios
- Difference table showing the change in every income component at four reference hours levels (0, 20, 40, 60 hrs/week)
- Tax and transfer interactions at part-time and full-time hours

The program selection panel lets users toggle which safety-net programs appear in the figure and affect the net income calculation.

### Population-Level Impacts
Aggregate effects across all eligible workers:
- **Headline metrics:** eligible workers, gross cost, net cost, average annual subsidy
- **Geographic distribution:** choropleth map with four metrics — share of state workers receiving the subsidy (default), workers (thousands), gross cost, average annual subsidy
- **By wage bracket:** worker distribution and average subsidy across $2 hourly wage bins
- **Program interactions:** how EITC, SNAP, Medicaid, taxes, and other programs change on average per worker and in aggregate
- **By family type:** single/married × with/without children
- **Demographic breakdowns:** by sex, race/ethnicity, education, and age group — with both share-of-recipients and share-of-group-receiving metrics

### Methodology
Full documentation of the data sources, eligibility rules, wage measurement, annual hours construction, household-type mapping, schedule interpolation, and fiscal accounting identities.

---

## Methodology Notes

**Wage identification:** Uses EPI-constructed hourly wages (`hourly_wage_epi`) from CPS ORG. The weighted median is computed from paid-hourly workers only, using ORG earnings weights. The target wage is rounded to the nearest cent.

**Eligibility sample:** Workers age 16–64 with valid EPI wage observations, positive earnings weights, and employer wages below the target wage. Workers 65+ are excluded as a proxy for Social Security recipient status. Tax dependents (children of household head, age < 19) are excluded.

**Annual hours:** Current weekly hours (`hours_epi`) × WKSTAT-based annual weeks multiplier (full-time year-round = 52 weeks; part-year and part-time codes mapped to 40–52 weeks).

**Population weights:** `earnwt / N_ym` where `N_ym` is the number of unique (year, month) groups in the eligible sample, converting monthly ORG weights to an annual-average equivalent.

**Safety-net interactions:** Interpolated from pre-computed PolicyEngine-US 2026 household income schedules by (family type × state). Four family types: single/married × 0/2+ children. 51 states including DC. Income grid: $0–$65,000 in $500 steps. Net income includes ACA Premium Tax Credits and Medicaid, which PolicyEngine's `household_net_income` excludes by default (as non-cash in-kind benefits), corrected in post-processing.

**Net cost accounting:** `Net cost = Σ_i weight_i × ΔNet_income_i` where ΔNet income is the change in comprehensive household net income (wages + subsidy + all transfers − taxes) interpolated at baseline and subsidized annual earnings.

Full methodology: [`WORKSPACE/docs/pipeline_methodology_public.md`](WORKSPACE/docs/pipeline_methodology_public.md)

---

## Identification Assumptions and Limitations

1. ORG is strong for wage-rate identification but is a monthly survey, not a complete annual household resource survey.
2. Annual hours are modeled from current hours and WKSTAT status, not observed prior-year weeks worked.
3. Safety-net responses use stylized household types (4 categories), not full per-record household microsimulation.
4. Eligibility uses the federal minimum wage floor ($7.25); state minimum wages are not imposed in the baseline.
5. Social Security exclusion uses age 65+ as a proxy; SSDI recipients under 65 cannot be identified in ORG.
6. Tax-dependent exclusion covers qualifying children identifiable in ORG; qualifying relative dependents (any age) cannot be identified without tax-return data.

These are explicit design tradeoffs, documented in the methodology guide.

---

## Citation

Glasner, Benjamin and Adam Ozimek. "The 80-80 Rule: A Wage Subsidy Proposal for American Workers." Economic Innovation Group, 2025.

Interactive simulation: [eig-wage-subsidy.streamlit.app](https://eig-wage-subsidy.streamlit.app/)
