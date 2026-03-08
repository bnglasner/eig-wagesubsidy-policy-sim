# Deployment Guide: EIG Wage Subsidy Simulator

> Target audience: EIG staff deploying the app for the first time, or updating it after a pipeline run.

---

## Quick start (deploy in 5 minutes)

**Platform: Streamlit Community Cloud (recommended)**

1. Push this repo (including data files) to GitHub — see [Data artifacts](#data-artifacts) below.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
3. Click **New app**.
4. Fill in:
   - **Repository:** `your-org/eig-wagesubsidy-policy-sim`
   - **Branch:** `master`
   - **Main file path:** `WORKSPACE/app/app.py`
5. Click **Deploy**. First build takes ~3–5 minutes.
6. Share the URL (format: `https://your-org-eig-wagesubsidy.streamlit.app`).

No secrets or environment variables are required for the default configuration.

---

## Platform comparison

| | Streamlit Cloud | Render | Railway |
|---|---|---|---|
| **Cost** | Free (public repos) | Free tier (sleeps) | $5/mo credit |
| **Setup effort** | Minimal (GUI) | Medium (Dockerfile) | Medium |
| **RAM** | 1 GB | 512 MB (free) | 512 MB (free) |
| **Sleep on idle** | No (public apps) | Yes (15 min) | No |
| **Custom domain** | No (free tier) | Yes | Yes |
| **Best for** | This app | Docker-based setups | Long-running services |

**Recommendation: Streamlit Community Cloud.**
The app data is 7.5 MB pre-computed parquets committed to the repo. PolicyEngine is installed but not called at runtime (all schedules pre-computed). RAM usage stays well under 1 GB in normal operation.

---

## Data artifacts

The app requires three sets of pre-computed parquet files. These are **committed to the repo** (gitignore has explicit exceptions — see `.gitignore` lines 74–79):

| Path | Size | Description |
|------|------|-------------|
| `WORKSPACE/data/processed/hourly_workers.parquet` | ~330 KB | Eligible workers (output of `01a_data_ingest.py`) |
| `WORKSPACE/output/data/intermediate_results/population/*.parquet` | ~40 KB | 5 population-level summary files (output of `02a_descriptive_stats.py`) |
| `WORKSPACE/output/data/intermediate_results/individual_schedules/*.parquet` | ~3.7 MB | 204 PolicyEngine budget schedules (4 family types × 51 states) |

**Total: ~7.5 MB** — well within GitHub's 100 MB file limit and Streamlit Cloud's 1 GB repo limit.

### When to regenerate data

Re-run the pipeline after:
- CPS ORG data is updated (new IPUMS extract)
- Policy parameters change (e.g., new median wage, different subsidy %)
- PolicyEngine version is updated (re-run `01b_precompute_individual.py` for new schedules)

Pipeline steps:
```bash
# From repo root
.venv/Scripts/python.exe WORKSPACE/code/01_data_preparation/01a_data_ingest.py
.venv/Scripts/python.exe WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.py
# Then commit the updated parquets and push
```

### Individual schedules

The 204 individual schedules in `individual_schedules/` are pre-computed by `01b_precompute_individual.py` (uses live PolicyEngine calls — slow, ~30–60 min). They only need to be regenerated when:
- PolicyEngine version changes significantly (benefit calculation logic updates)
- State-specific policy parameters change in a way that affects baseline schedules

---

## Required environment variables

**None required** for the default public deployment.

The app is fully self-contained: all data is in the repo, no external API calls at runtime.

If you add user authentication or analytics in the future, document secrets here and add them to Streamlit Cloud's **Secrets** manager (Settings → Secrets).

---

## Local development

```bash
# Clone the repo
git clone https://github.com/your-org/eig-wagesubsidy-policy-sim.git
cd eig-wagesubsidy-policy-sim

# Create virtual environment (Python 3.12)
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt  # Mac/Linux

# Run the app
streamlit run WORKSPACE/app/app.py
```

---

## Updating data and redeploying

1. Re-run pipeline scripts locally (see [When to regenerate data](#when-to-regenerate-data)).
2. Commit the updated parquet files:
   ```bash
   git add WORKSPACE/data/processed/hourly_workers.parquet
   git add WORKSPACE/output/data/intermediate_results/population/
   git add WORKSPACE/output/data/intermediate_results/individual_schedules/
   git commit -m "Update pipeline outputs: [date] [brief description]"
   git push
   ```
3. Streamlit Cloud redeploys automatically on push (no manual action needed).

---

## Troubleshooting

### App loads but Population tab shows "data not found"
The population parquets are missing. Check that the `population/` directory contents are committed to git:
```bash
git ls-files WORKSPACE/output/data/intermediate_results/population/
```
Expected output: 5 `.parquet` files. If empty, run step 2 of the pipeline and commit.

### "ModuleNotFoundError: pyarrow" on Streamlit Cloud
`pyarrow` is now pinned in `requirements.txt`. If this error appears, confirm `requirements.txt` at repo root contains `pyarrow==23.0.1`.

### "ModuleNotFoundError: policyengine_us" at import time
PolicyEngine is only imported inside functions (`compute_income_point`, `_run_live`) when live simulation is triggered. If all 204 schedule parquets exist, this code path is never reached. Confirm schedules are committed:
```bash
git ls-files WORKSPACE/output/data/intermediate_results/individual_schedules/ | wc -l
```
Expected: 204. If fewer, individual schedules are missing.

### App is very slow on first load
Streamlit Cloud cold-starts can take 30–60 seconds when the Python environment is being rebuilt. Subsequent loads are fast. If the app is consistently slow, check if PolicyEngine live fallback is being triggered (schedules missing).

### PolicyEngine version mismatch warning
If PolicyEngine emits deprecation warnings about variable names, check `household_sim.py` — it uses `_try_vars()` to probe multiple variable name patterns across PE-US versions. Update the variable name lists if new PE-US versions rename variables.

### Memory error on Streamlit Cloud (1 GB limit)
Normal operation uses ~200–400 MB. If memory exceeds 1 GB, the likely cause is PolicyEngine being loaded into memory. Ensure all 204 schedules are present so the live fallback is never triggered. If PolicyEngine itself is the issue at install time, consider the slim deployment option (see below).

### Slim deployment (no PolicyEngine)
If policyengine-us causes install failures on the target platform, create `requirements-slim.txt`:
```
streamlit==1.55.0
pandas==2.3.3
numpy==2.4.2
plotly==5.24.1
pyarrow==23.0.1
```
In `household_sim.py`, the live fallback (`_run_live`) will raise an `ImportError` if PolicyEngine is missing, but the pre-computed path will still work for all 204 state/family combinations. The calculator tab will show an error only if the user selects a combination without a pre-computed schedule (which cannot happen with the full set).

---

## File checklist before deploying

Run this to confirm all required files are present and committed:
```bash
# All 5 population files
git ls-files WORKSPACE/output/data/intermediate_results/population/

# All 204 individual schedules (should print 204)
git ls-files WORKSPACE/output/data/intermediate_results/individual_schedules/ | wc -l

# Eligible workers file
git ls-files WORKSPACE/data/processed/hourly_workers.parquet

# Requirements and config
git ls-files requirements.txt .streamlit/config.toml .python-version
```
