# CPS ASEC 2025 (IPUMS-CPS Annual Social and Economic Supplement) — variable documentation

- **Dataset:** Current Population Survey, Annual Social and Economic Supplement (March 2025 sample; March Basic + ASEC), IPUMS-CPS microdata.
- **Registry id:** `cps` (variables appended to the curated `template` entry at `verification: parsed`). This doc complements `cps_org_2025-2026.md`, which documents the basic-monthly ORG variable set; this file documents the **ASEC-specific** variables requested by `code/01_data_preparation/01c_asec_pull.R` and consumed by `01d_asec_preprocess.py` / `01e_match_org_to_asec.py`.
- **Vintage documented:** IPUMS CPS ASEC 2025 (March 2025 sample; income reference year 2024), IPUMS CPS v13.0 DDI 2.5 (DOI 10.18128/D030.V13.0, produced 2026-03-09), extract `cps_00305`.
- **Consumers:** `code/01_data_preparation/01c_asec_pull.R` (extract request), `01d_asec_preprocess.py` (primary-earner household records: spouse income, children's ages), `01e_match_org_to_asec.py` (nearest-neighbor statistical match of ORG eligible workers to ASEC households, currently scoped to the **employed** low-wage population only).
- **Origin note:** this pass was written as part of the data-feasibility read for `Infrastructure/specs/2026-07-08_entry-from-nonemployment-remodel.md` (item 1, net-of-transfer reservation / household context). `data/external/asec_persons_2025.parquet` was not materialized in this repo checkout at the time of writing (only the raw IPUMS download directory `data/external/asec_2025_raw/` and its DDI `cps_00305.xml` are present); all facts below come from that in-repo DDI, not from inspecting extract rows.

## Sources and authority tier

**Tier 1 — Authoritative in-repo IPUMS DDI.** `data/external/asec_2025_raw/cps_00305.xml`, cataloged at `Infrastructure/references/literature/data_dictionaries/2025_cps-asec_dictionary.xml` (same artifact already used for `cps_org_2025-2026.md`'s Tier 1 variables — no new fetch was made). All variables below appear in this DDI under the requested `ASEC_VARS` list in `01c_asec_pull.R`.

> Observed facts are stated plainly from the DDI text; anything not stated is marked `[unverified: ...]`. No universe, definition, or coding was inferred from a variable name.

---

### INCWAGE — Wage and salary income (previous calendar year)
- **Definition (DDI):** "Each respondent's total pre-tax wage and salary income — that is, money received as an employee — for the previous calendar year." For ASEC 1988+, derived from a Census recode combining `OINCWAGE` and (when applicable) `INCLONGJ`.
- **Coding:** `99999999` = N.I.U.; `99999998` = Missing (1962–1966 only). Nominal dollars as reported; DDI advises CPI adjustment for real comparisons.
- **Topcoding:** DDI states the Census Bureau applies disclosure-avoidance topcoding/swap-value methods that vary across time; exact 2025 threshold `[unverified: not stated in the DDI text itself — see linked Census documentation]`.
- **Consumer use:** `01d_asec_preprocess.py` uses `INCWAGE > 0` as an earner-candidate filter and computes `hourly_wage_asec = INCWAGE / annual_hours_asec`; also captures `spouse_incwage` (INCWAGE of the RELATE==202 household member) as household context.

### INCTOT — Total personal income (previous calendar year)
- **Definition (DDI):** "Each respondent's total pre-tax personal income or losses from all sources for the previous calendar year."
- **Coding:** `999999999` = N.I.U.; `999999998` = Missing (1962–1964 only). Values can be negative.
- **Topcoding:** same Census disclosure-avoidance caveat as INCWAGE; exact threshold `[unverified]`.
- **Consumer use:** retained by `01d` as a diagnostic/QC field; not currently used in matching or fiscal calculations.

### WKSWORK2 — Weeks worked last year, intervalled
- **Definition (DDI):** Number of weeks worked for profit, pay, or as an unpaid family worker during the preceding calendar year, reported in six intervals.
- **Coding:** `0` NIU; `1` 1–13 weeks; `2` 14–26; `3` 27–39; `4` 40–47; `5` 48–49; `6` 50–52; `9` Missing.
- **Consumer use:** `01d` maps codes to interval midpoints (`WKSWORK2_MIDPOINTS`: 7.0, 20.0, 33.0, 43.5, 48.5, 51.0 weeks) to construct `wks_worked` and, with `UHRSWORKLY`, `annual_hours_asec`.

### UHRSWORKLY — Usual hours worked per week (last year)
- **Definition (DDI):** Usual weekly hours for respondents who worked (or did any temporary/part-time/seasonal work) during the previous calendar year.
- **Coding:** 2-digit numeric; `99` = 99+ hours; `999` = NIU.
- **Consumer use:** `01d` requires `UHRSWORKLY > 0` for earner-candidate status; combined with `wks_worked` to build `annual_hours_asec` and `hourly_wage_asec`.

### FAMUNIT — Family unit membership
- **Definition (DDI):** IPUMS-derived indicator of which family group within the household each person belongs to; primary families/individuals are coded `1`, secondary family groups receive higher codes. Distinct from the Census Bureau's own family/subfamily enumeration (see DDI text for FTYPE/FAMKIND/FAMREL cross-references).
- **Coding:** `01` 1st family in household/group quarters; `02`, `03`, … successive family groups.
- **Consumer use:** requested in the extract (`01c_asec_pull.R`) but **not read** by `01d_asec_preprocess.py`, which instead identifies the primary earner and household roster via `SERIAL` + `RELATE` directly. `[unverified: whether FAMUNIT would change household-roster construction for multi-family households; not exercised by current code]`.

### ASECWT — Annual Social and Economic Supplement weight (person)
- **Definition (DDI):** Person-level weight for individual-level analyses of ASEC supplement data. DDI explicitly warns: use `WTFINL` (not ASECWT) for non-ASEC person-level analyses, `EARNWT` for the small set of earner-study variables, and `ASECWTH` for household-level ASEC analyses.
- **Consumer use:** requested in the extract; `01d_asec_preprocess.py`'s `out_cols` retains ASECWT, but the primary-earner matching/aggregation in `01d`/`01e` as read does not visibly apply it as an analysis weight — flagged here per methodology rule MR-VU1/DA9 territory, **not resolved by this data-feasibility pass** (out of scope; see `methodology-reviewer`).
- **Already documented at the top level:** the curated `cps` template `weights` list already carries ASEC person/household weights generically (`asecwt` / `MARSUPWT`/`ASECWT`); this entry adds the DDI-sourced per-variable detail for this project's specific 2025 vintage.

### ASECWTH — Annual Social and Economic Supplement weight (household)
- **Definition (DDI):** Household-level weight for ASEC household statistics; must be used (not `HWTFINL`) for unbiased ASEC household-level estimates.
- **Consumer use:** requested in the extract; not visibly used downstream in the examined consumers (`01d`, `01e` operate at the person/primary-earner level). `[unverified: whether a household-level use is planned]`.

---

## Relevance to the entry-from-nonemployment remodel spec (context, not a new fact)

`01e_match_org_to_asec.py` already performs a nearest-neighbor statistical match from **employed** ORG eligible workers to ASEC primary-earner households (weighted on `wage_decile`, `marital_binary`, `nchild_bin`, `age_bin`, `sex_binary`, `educ_group`; state is an exact constraint), producing `asec_spouse_income`, `asec_n_children` (actual count, not the 0/2c bucket), and `asec_children_ages` per matched ORG worker. This machinery is not currently run against `data/processed/nonemployed_pool.parquet` (the non-employed pool built by `01h`). Extending it to the non-employed pool — substituting the imputed MPL's within-state decile for the (unobserved) actual wage decile — would be a **straightforward reuse of existing code and already-pulled ASEC data**, not a new dataset acquisition, and is the most direct path to giving non-employed persons the same richer household context (actual child count/ages, spouse earnings) that employed workers already receive. This is an assessment note for the spec's evaluation routing, not a new codebook fact.

## Handoff notes

- `methodology-reviewer`: ASECWT/ASECWTH exist on the extract per the DDI but are not visibly applied as survey weights in `01d`/`01e`'s primary-earner selection and matching; flag if income/composition statistics computed from the ASEC-matched sample are presented as population-representative without weighting.
- `code-reviewer` / `ai-skeptic`: INCWAGE, INCTOT, WKSWORK2, UHRSWORKLY, FAMUNIT, ASECWT, ASECWTH are confirmed present in `01c_asec_pull.R`'s `ASEC_VARS` request and in the in-repo DDI; names are not fabricated.
- **Vintage risk:** all facts here are from the ASEC 2025 (v13.0) DDI already cataloged for the ORG doc. If a later ASEC vintage is pulled (`01c_asec_pull.R`'s `TARGET_YEARS` fallback logic), re-verify definitions/topcoding against that vintage's own DDI before treating this doc as current.
