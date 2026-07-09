# Project Profile

Single source of project context. The AI agent reads this first every session.

## Research Project Title
- The 80-80 Rule: A Wage Subsidy Proposal for American Workers

## Research Question
- Who is eligible for the Economic Innovation Group's 80-80 Rule wage subsidy, what is the subsidy worth to each worker, what does it cost the government gross and net of tax recapture and safety-net responses, and how are those effects distributed across the workforce?

The 80-80 Rule is a direct-to-worker transfer that fills 80 percent of the gap between a worker's employer-paid wage and a target set at 80 percent of the national median hourly wage (a roughly $16.80 per hour target against a roughly $21.00 median in the current run).

## Data in Scope

| Data Source | Type | Owner/Location | Time Coverage | Access Notes |
|---|---|---|---|---|
| CPS Outgoing Rotation Group (ORG) | Public microdata (IPUMS-CPS, `*2` era) | **Internalized in-repo** (2026-07-07) via the vendored EIG-Wage-Figure build in `code/00_ingest/` (upstream `EIG-Wage-Figure-Explain-Everything` @ `33bbcb7`); raw → `data/raw/cps_org/`, gated panel → `data/intermediate/cps_org_panel/`. No longer depends on the sibling repo at run time (`EIG_ORG_RAW_DIR` optional override for the companion comparison). | Most recent 12 complete monthly samples (currently 2025m5–2026m5) | Wage-rate identification. EIG SWA sample gate + seeded `ranger` RF hours imputation. `EARNWT` (ORG earnings weight) for employed-earner wage/eligibility/cost; `WTFINL` for the non-employed pool (`01h`). See `docs/org_ingestion_internalized.md` and `Infrastructure/specs/2026-07-07_org-wage-internalization.md`. |
| CPS ASEC | Public microdata (IPUMS API) | `data/external/` | 2025 vintage | Spouse income and child ages for matched households. The 2025 vintage changed RELATE codes: spouse is 202, children are 301. |
| PolicyEngine-US | Microsimulation model (Python package) | Pre-computed household income schedules in `output/data/intermediate_results/` | 2026 policy year | Tax and safety-net interactions. `household_net_income` excludes ACA Premium Tax Credits and Medicaid by default; corrected in post-processing. |

For each in-scope dataset, run `/document-data` to acquire its vintage-correct codebook and document the relevant variables in the dataset registry (`Infrastructure/references/datasets/registry.yaml`).

## Deliverables
- Interactive Streamlit simulation, live at eig-wage-subsidy.streamlit.app (entrypoint `app/app.py`).
- Blog post and policy brief presenting eligibility, cost, and distributional findings.
- Public methodology documentation (`docs/pipeline_methodology_public.md`).

## Constraints
- Primary language is Python; project scope tier 1 (descriptive and interactive tool). R and Stata stage runners exist from the template baseline but are not the active pipeline.
- The app is deployed on Streamlit Cloud. The deployment entrypoint must point at `app/app.py`.
- All written outputs and figures follow EIG communications and brand standards (`Infrastructure/style/docs/README.md`).
- No hardcoded absolute paths; credentials are never committed (use `.Renviron` or local secret tooling; see `.Renviron.example`).

## Additional Context (Open Notes)

Pipeline language profile (active values):
- Pipeline entrypoint: `code/run_all.py` (run with `python code/run_all.py`).
- Bootstrap config: `code/00_setup/00_config.py`.
- Stage script convention: `.py`, organized in numbered stages `01`–`05` under `code/`.

Two-source design: CPS ORG identifies who is eligible, at what wage, and for how many hours; PolicyEngine-US pre-computed household schedules supply the tax and safety-net responses. ORG and ASEC/PolicyEngine are not a common panel and do not support defensible one-to-one linkage, so the two modeling tasks are kept separate and combined at the aggregation step.

Authors: Benjamin Glasner and Adam Ozimek (Economic Innovation Group).
