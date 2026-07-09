# CPS ORG wage ingestion — internalized (2026-07-07)

The CPS Outgoing Rotation Group wage build is now produced **inside this repo**. It previously depended on a sibling repository at run time. This note records what changed, how to run it, and how to keep it in sync with upstream.

## Source of truth

- Canonical repo: **`EIG-Wage-Figure-Explain-Everything`**, commit **`33bbcb7`**.
- Vendored stages (config + annotated inert-guards only) under **`code/00_ingest/`**:
  - `00a_download-ipums-cps.R` — IPUMS API extract (define/submit/download).
  - `01a_load-ipums-cps.R` — load, sentinels, uppercase names, year partitions.
  - `01b_build-org-panel.R` — EPI SWA sample gate, wage sentinels, seeded `ranger` RF "hours-vary" imputation, sex-separate Pareto topcode, 2023m4–2024m12 rotation-group bridge.
- Pristine upstream copies at that SHA are kept at `code/00_ingest/.upstream_33bbcb7/` for diffing and drift control.

## Scope of the vendoring edits

Only two classes of change from upstream are allowed, and every change is one of them:

- `# EIG-VENDOR-CONFIG:` — configuration: recent-12-sample slice, `*2`-only wage variables, added `NCHILD`/`RELATE`/`WKSTAT`, output paths, run flags.
- `# EIG-VENDOR-GUARD:` — inert-guards making legacy-era code safe when legacy `HOURWAGE`/`EARNWEEK` are absent (R's `dplyr::if_else` evaluates both branches eagerly).

`01b_build-org-panel.R` is **byte-identical** to upstream. Verify with:

```bash
bash Infrastructure/scripts/check_org_vendor_drift.sh
```

## Function-by-function crosswalk (recent-only / `*2` / nominal window)

| Upstream step | Disposition | Notes |
|---|---|---|
| `00a` sample discovery + variable list | config | keep last 12 samples; drop legacy `HOURWAGE`/`EARNWEEK`; add `NCHILD`/`RELATE`/`WKSTAT`. |
| `01a` load / partition / canonical wage seam | verbatim + inert-guard | for a 2025–2026 window all rows are `*2` (legacy rows = 0), so the seam picks `*2`; the legacy branch is guarded and never selected. |
| `01b` sample gate, wage sentinels, RF hours imputation | verbatim | `epi_sample_eligible` = panel membership; RF produces `uhrsworkorg_used_num` + `hours_imputed_flag`. |
| `01b` legacy topcode lookup, sex-separate Pareto, rotation bridge | verbatim, **inert** | window years > 2024 → Pareto skipped; bridge months (2023–2024) absent; legacy topcode unused. Carried faithfully as no-ops. |
| `02a` nominal hourly-wage routing (`PAIDHOUR` split) | reproduced in Python `01a` | deterministic transform of EIG columns; identical value. |
| `02a` PCE deflation, real wages, EPI $0.50/$200 bounds | **out of scope** | nominal subsidy. A $0.50/hr **nominal** floor approximates the EPI $0.50 (1989 PCE) low-end clean; the $200 upper bound is irrelevant to a <$16.80 population. |

## R → Python handoff contract

- **Raw partitions** `data/raw/cps_org/year=YYYY/part-0.parquet` (consumed by `01h_nonemployed_pool.py`): all rotations, UPPERCASE IPUMS names, `haven` labels zapped; includes `WTFINL`, `EMPSTAT`, `NCHILD`, `RELATE`, `HOURWAGE_CANON_NUM`, `EARNWEEK_CANON_NUM`, `UHRSWORK1`, `UHRSWORKORG`, `PAIDHOUR`, `WKSTAT`, demographics, `STATEFIP`, RF features, Q-flags.
- **Gated panel** `data/intermediate/cps_org_panel/year=YYYY/part-0.parquet` (consumed by `01a_data_ingest.py`): gate-passing rows plus `uhrsworkorg_used_num`, `nominal_weekly_wage_num`, `hours_imputed_flag`, `pareto_topcode_imputed_flag`.
- `01a_data_ingest.py::_load_and_adapt_org_panel()` maps EIG-native columns → the internal names the eligibility/cost logic uses; the output `data/processed/hourly_workers.parquet` schema is **unchanged**.

## How to run

```bash
# 1) R ingestion (needs IPUMS_API_KEY in ~/.Renviron or ./.Renviron)
Rscript code/00_ingest/00a_download-ipums-cps.R   # submits/downloads (IPUMS-cache-guarded)
Rscript code/00_ingest/01a_load-ipums-cps.R
Rscript code/00_ingest/01b_build-org-panel.R
# 2) Python pipeline (or `python code/run_all.py`, which now runs the R stage first)
python code/01_data_preparation/01a_data_ingest.py
python code/01_data_preparation/01h_nonemployed_pool.py
```

`run_all.py` wires the R stage in via `RUN_00_INGEST_ORG` (subprocess `Rscript`), ahead of `01a`.

## Dependencies

- **R (dev/pipeline only):** `ipumsr, arrow, dplyr, haven, fs, here, tibble, stringr, readr, ranger` (loader: `code/_utils/00_packages.R`). The Streamlit app deployment stays Python-only; `requirements.txt` is unchanged.
- **IPUMS key:** `IPUMS_API_KEY` in `.Renviron` (see `.Renviron.example`). Submitting an extract is outward-facing and consumes the account quota — human-gate it.

## Drift control

`code/00_ingest/.upstream_33bbcb7/` holds the pinned upstream. `Infrastructure/scripts/check_org_vendor_drift.sh` asserts the vendored files differ from upstream only by blank/comment/`EIG-VENDOR-*` lines (01b byte-identical) and warns if the canonical repo has advanced past `33bbcb7`. To re-sync: re-copy the canonical files into `.upstream_33bbcb7/`, re-apply the whitelisted edits, bump the recorded SHA here and in the script, and re-run the check + the method-fidelity gate.

## Known caveats

- **RF hours on truncated years.** The `ranger` hours imputation is fit per calendar year. On a partial calendar year (e.g. the current 2025 with 7 of its months in the window), the fit sees fewer rows than a full-history run, so the imputed hours for the ~2.4% "hours-vary" rows differ slightly (mean |Δ| ≈ 1.3 weekly hours). All non-imputed rows and all deterministic fields are bit-identical. See `Infrastructure/session_logs/2026-07-07_replication_report.md`.
- **`NCHILD` universe.** The retired export doc described `NCHILD` as "under 18"; the IPUMS DDI defines it as own children in the household of **any age**. Family typing (`nchild >= 1`) uses the IPUMS definition. Flagged by the data-dictionary pass; reconfirm against the ORG basic-monthly DDI in a later authoritative fetch.
