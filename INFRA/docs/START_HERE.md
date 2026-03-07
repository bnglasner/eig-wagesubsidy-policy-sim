# Start Here — eig-wagesubsidy-policy-sim

This is an active project repository, not the template. You are in the right place.

## Python Environment Setup (Do This First)

This project requires **Python 3.12** (PolicyEngine-US does not yet support Python 3.14).
Your machine currently has Python 3.14 installed. Follow these steps:

### Step 1 — Install Python 3.12

Download and install from: https://www.python.org/downloads/release/python-3129/
- Choose "Windows installer (64-bit)"
- Check "Add python.exe to PATH" during install
- After install, verify: `py -3.12 --version`

### Step 2 — Create the virtual environment

From the project root (`eig-wagesubsidy-policy-sim/`):

```bash
py -3.12 -m venv .venv
```

### Step 3 — Activate and install dependencies

```bash
# Activate (Windows)
.venv\Scripts\activate

# Install all dependencies (~5-10 minutes; policyengine-us is large)
python -m pip install -r requirements.txt
```

### Step 4 — Verify the install

```bash
python -c "from policyengine_us import Microsimulation; print('PolicyEngine OK')"
```

### Step 5 — Run the app

```bash
streamlit run WORKSPACE/app/app.py
```

---

## Project Overview

- **Policy**: EIG "80-80 Rule" wage subsidy — 80% of gap to 80% of national median wage
- **Primary output**: Interactive Streamlit simulation (embeddable in HTML)
- **Secondary output**: Blog post write-up with figures
- **Pipeline**: `python WORKSPACE/code/run_all.py` (pre-computes population impacts)

## Working in This Project

Work in:
- `WORKSPACE/app/` — Streamlit interactive simulation
- `WORKSPACE/code/` — data pipeline scripts (stages 00, 01, 02, 05)
- `WORKSPACE/output/` — figures and tables for blog post

Do not modify:
- `INFRA/` — infrastructure, style system, brand assets
- `requirements.txt` — without updating `.python-version` and testing install

## Non-Negotiable Rules

1. Keep all paths relative to the project root.
2. Never store credentials in repository files.
3. All scripts must import `00_config.py` for shared paths and policy parameters.
4. Every chart or table in the blog post must have a corresponding producing script.
5. The `.venv/` directory is gitignored — do not commit it.
