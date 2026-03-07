# eig-wagesubsidy-policy-sim

**EIG Wage Subsidy Policy Simulation**
Authors: Ben Glasner and Adam Ozimek (EIG)
Tier 1 — Interactive tool + blog post

This repository models the EIG "80-80 Rule" wage subsidy proposal using the PolicyEngine-US microsimulation engine. It produces an interactive Streamlit simulation and supporting blog-post content.

## The Policy

The EIG wage subsidy has three components:

1. **Target wage** — 80% of national median hourly wage ($16/hr in 2024)
2. **Subsidy** — 80% × (target_wage − employer_wage), for workers earning ≥ federal minimum wage
3. **Base wage** — Federal minimum wage ($7.25/hr), the minimum employer-paid wage to qualify

Workers at $7.25/hr → $14.25 take-home. Workers at $12/hr → $15.20 take-home. Zero subsidy at $16/hr+.

## Two-Zone Structure

- `WORKSPACE/` — code, data, output, and the interactive app
- `INFRA/` — docs, style guides, brand assets, agent config

## Quick Start

```bash
# 1. Activate virtual environment (see INFRA/docs/START_HERE.md for setup)
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 2. Run the interactive app
streamlit run WORKSPACE/app/app.py

# 3. Run the data pipeline (pre-computes population impacts)
python WORKSPACE/code/run_all.py
```

## If You Are A Human Researcher

Start here: `INFRA/docs/START_HERE.md`

Work in:
- `WORKSPACE/app/` — Streamlit interactive simulation
- `WORKSPACE/code/` — data pipeline scripts
- `WORKSPACE/output/` — charts and tables for blog post

## If You Are An AI Agent

Start here: `INFRA/docs/AI_START.md` and `INFRA/docs/PROJECT_INTAKE.md`

## Document Map

| Purpose | Canonical File |
|---------|----------------|
| Project intake / decisions | `INFRA/docs/PROJECT_INTAKE.md` |
| Architecture overview | `INFRA/docs/ARCHITECTURE.md` |
| Pipeline language and entrypoint | `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` |
| Style system | `INFRA/style/` |
| Interactive app | `WORKSPACE/app/app.py` |
| Pipeline entrypoint | `WORKSPACE/code/run_all.py` |
