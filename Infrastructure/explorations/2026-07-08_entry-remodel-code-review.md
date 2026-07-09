# Code Review — Entry-from-Nonemployment Remodel (2026-07-08)

**Scope:** `code/01_data_preparation/01i_household_links.py` (new), `code/01_data_preparation/01h_nonemployed_pool.py` (overhauled), `code/02_descriptive_analysis/02d_matching_simulation.py` (overhauled), `code/00_setup/00_config.py` (`eps_ext_band`), reviewed against their callers (`run_all.py`, `02b_behavioral_scenarios.py`).
**Standard:** `.claude/rules/code-quality-rules.md` — definitive errors + material efficiency/readability suggestions only. No code changes made.
**Verified facts taken as given:** clean end-to-end run (01i → 01h → 02b → 02d), byte-identical 01h rerun, parity test passing, 02b baseline unchanged, calibration realized == target.

**Summary:** No CRITICAL findings. One HIGH (01i missing from the pipeline runner while 01h now hard-requires its output), one MEDIUM (latent positional misalignment in `_entrants_from_pool`'s `weight_override` contract), two LOW, five SUGGESTIONs. The core numerical mechanics — links merge alignment, 3-column household key, `get_indexer` position math, hash-rank calibration, band monotonicity assertions, pay-up grid masking — all check out (see "Verified clean" at the end).

---

## CE-001 — HIGH — 01i is not registered in `run_all.py`, but 01h now hard-fails without its output

**Files:** `code/run_all.py:276-301` (steps 01a → 01b → 01h; no 01i step, no `RUN_01I_*` flag) and `code/01_data_preparation/01h_nonemployed_pool.py:436-438`.

**Problematic code** (`01h_nonemployed_pool.py:436-438`):

```python
links_path = PATH_DATA_PROCESSED / "household_links.parquet"
if not links_path.exists():
    raise FileNotFoundError(f"{links_path} not found. Run 01i_household_links.py first.")
```

and `run_all.py:79` (now-stale comment):

```python
RUN_01H_NONEMPLOYED_POOL = True        # ORG non-employed pool for 02d (needs widened export; no-op if absent)
```

**Why it's wrong:** The remodel made `household_links.parquet` a hard prerequisite of 01h (a deliberate `raise`, not a soft skip), but the canonical pipeline runner has no step that produces it. The clean end-to-end run this session succeeded only because 01i was invoked manually (or the file already existed in `data/processed/`). On a fresh checkout — or after `data/processed` is cleaned — `python code/run_all.py` crashes at 01h with `FileNotFoundError`. The `run_all.py:79` comment ("no-op if absent") also no longer describes 01h's behavior: it is a no-op only when the *raw partitions* are absent; with raw data present and links absent it raises. This is exactly the failure class the verification protocol targets (reproducibility of the documented entry point).

**Fix:** Register 01i in `run_all.py` immediately before 01h:

```python
RUN_01I_HOUSEHOLD_LINKS = True

run_script(
    script_id="01i",
    stage="01",
    script_path="code/01_data_preparation/01i_household_links.py",
    label="Household links (spouse pairing + child flags) — 01h prerequisite",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01I_HOUSEHOLD_LINKS,
)
```

and update the `RUN_01H_NONEMPLOYED_POOL` comment to state the hard dependency. (Ordering note: 01i must precede 01h; both are no-ops when the raw ORG dir is absent, so the fallback behavior on machines without raw data is preserved — 01i prints-and-returns, 01h prints-and-returns before reaching the `raise`.)

---

## CE-002 — MEDIUM — `_entrants_from_pool` filters rows *after* accepting a positionally-aligned `weight_override`

**File:** `code/02_descriptive_analysis/02d_matching_simulation.py:184-195` (function) and `:315-320` (caller).

**Problematic code:**

```python
def _entrants_from_pool(pool, beta, target, edge="central", weight_override=None):
    ...
    pool = pool.dropna(subset=[c for c in need if c in pool.columns])
    pool = pool[pool["weight"] > 0]
    ...
    wt = pool["weight"].to_numpy(float) if weight_override is None \
        else np.asarray(weight_override, float)
```

Caller (`main`, lines 315-320) builds the override on the **unfiltered** pool:

```python
wov = pool["weight"].to_numpy(float) * np.where(sp.to_numpy(), factor, 1.0)
ge, ne, fce, ind, by_cell, det = _entrants_from_pool(
    pool, beta_c, target, edge="central", weight_override=wov)
```

**Why it's wrong:** The override array is positional over the full pool, but the function drops rows (`dropna` + `weight > 0`) *before* adopting it, while `y`, `h`, `req`, `viable`, etc. are extracted from the filtered frame. Today no row is dropped — 01h guarantees `WTFINL > 0` and every `need` column is non-NaN — so lengths coincide and the sensitivity numbers are correct (consistent with the clean run). But the function's own defensive filters guarantee misalignment the moment they act: every downstream aggregate (`wt * viable`, `wt[payup]`) then either crashes on a length mismatch or — if a caller ever passes a same-length array built from a differently-filtered pool — silently weights the wrong persons. A concrete trigger path exists inside this codebase: the 01h cell-median fallback can emit NaN `mpl` (see CE-003), which would make `dropna` bite. This is a definitive interface bug in the new `weight_override` contract, currently benign by luck of the data.

**Fix:** Apply the override before filtering, keeping alignment index-based rather than positional:

```python
def _entrants_from_pool(pool, beta, target, edge="central", weight_override=None):
    pool = pool.copy()
    if weight_override is not None:
        pool["weight"] = np.asarray(weight_override, float)   # aligned to the caller's pool
    pool = pool.dropna(subset=[c for c in need if c in pool.columns])
    pool = pool[pool["weight"] > 0]
    ...
    wt = pool["weight"].to_numpy(float)
```

(If zero-weight sensitivity rows must be *kept* rather than filtered, use `pool["weight"] >= 0` with the override present — with `we = wt * viable`, zeroed rows contribute nothing either way, but note the current `pool["weight"] > 0` filter would silently drop factor-0.0 rows under this fix; that is the correct economics for "zeroed entrants" but should be a conscious choice.)

---

## CE-003 — LOW — `_cellmedian_fallback`'s `or`-chain cannot fall back from a NaN cell median (NaN is truthy)

**File:** `code/01_data_preparation/01h_nonemployed_pool.py:265-266`.

**Problematic code:**

```python
out = np.array([cell.get(f"{s}|{e}|{a}") or sexm.get(s) or overall
                for s, e, a in zip(pool["sex_label"], pool["educ_group"], pool["age_bin"])], float)
```

**Why it's wrong:** `wmed()` returns `np.nan` when a group has no valid `(obs_wage, EARNWT>0)` pair (line 259: `if ok.sum() == 0: return np.nan`). But `float('nan')` is truthy in Python, so `nan or sexm.get(s) or overall` evaluates to `nan` — the fallback ladder never engages for exactly the degenerate cells it was written to handle. A NaN then flows into `mpl`, `entry_hours` ranking, and the band, and finally gets `dropna`'d in 02d (triggering the CE-002 misalignment). It only matters on the Heckman-failure path *and* with a cell whose weights are all invalid — hence LOW — but the guard is definitively non-functional for the NaN case it exists for.

**Fix:**

```python
def _first_valid(*vals):
    for v in vals:
        if v is not None and np.isfinite(v):
            return v
    return np.nan

out = np.array([_first_valid(cell.get(f"{s}|{e}|{a}"), sexm.get(s), overall)
                for s, e, a in zip(pool["sex_label"], pool["educ_group"], pool["age_bin"])], float)
```

---

## CE-004 — LOW — `hh_other_nonemployed_adult` is wrong for employed persons, and the inline comment claims the opposite

**File:** `code/01_data_preparation/01i_household_links.py:135-137`.

**Problematic code:**

```python
out["hh_other_nonemployed_adult"] = (
    n_nonemp_adult.reindex(idx).fillna(0).to_numpy() - 1 > 0)  # excluding self if non-employed;
# conservative: for employed persons this over-counts by 0, for non-employed by self-exclusion.
```

**Why it's wrong:** `n_nonemp_adult` counts non-employed 16–64 adults per household. The `- 1` self-exclusion is only valid when the row's own person is in that count — i.e., for non-employed rows. For an **employed** person in a household with exactly one non-employed adult, the truth is "another non-employed adult exists" (count of others = 1) but the formula gives `1 - 1 > 0 = False`: an under-count, not the "over-counts by 0" the comment asserts (the comment has it backwards). For the pool's own use the logic is correct — pool rows are non-employed by construction, self is always in the count, and subtracting 1 exactly removes self. And the column is currently written but consumed nowhere (`01h` merges only `spouse_is_employed`, `own_child_under5`, `hh_child_under5`, `spouse_linkable`), so no result is affected today. But `household_links.parquet` is a persisted person-level artifact covering *all* persons 16–64; any future consumer using it on employed rows (e.g., as a selection-equation shifter in the estimation sample, its plausible next use) inherits a silently miscoded flag.

**Fix:** Subtract self only when self is non-employed:

```python
cnt = n_nonemp_adult.reindex(idx).fillna(0).to_numpy()
self_nonemp = (~out["EMPSTAT... (carry EMPSTAT into `out`)"].isin(list(_EMPLOYED_EMPSTAT))).to_numpy()
out["hh_other_nonemployed_adult"] = (cnt - self_nonemp.astype(int)) > 0
```

(Carry `EMPSTAT` into `out` at line 107 to support this.) At minimum, correct the comment so the employed-row semantics are disclosed accurately.

---

## CE-005 — SUGGESTION — Raw ORG partitions are read full-width twice per pipeline run (01i, then 01h)

**Files:** `code/01_data_preparation/01i_household_links.py:152-153` and `code/01_data_preparation/01h_nonemployed_pool.py:415-416`.

```python
parts = sorted(raw_dir.glob("year=*/part-0.parquet"))[-2:]
org = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
```

Both stages materialize ~1.1M rows × every column in the extract, back to back. 01i uses at most 10 columns (`cols + ew_col`, line 76-78); 01h uses ~20. `pd.read_parquet(p, columns=[...])` is a one-line change per script that cuts I/O and peak memory several-fold (Parquet is columnar; unread columns cost nothing). If the raw extract widens further (the queued SPLOC/NCHLT5 re-pull), the full-width double load grows with it. A larger refactor (01i persisting a slim roster for 01h to reuse) is optional; the `columns=` pruning is the material, low-risk win.

## CE-006 — SUGGESTION — 02d re-reads `nonemployed_pool.parquet` six times per run

**File:** `code/02_descriptive_analysis/02d_matching_simulation.py:124-129` inside `simulate()`.

```python
pool_path = PATH_DATA_PROCESSED / "nonemployed_pool.parquet"
if pool_path.exists():
    ...
    ge, ne, fce, induced_M, ind_by_cell, detail = _entrants_from_pool(
        pd.read_parquet(pool_path), beta, target)
```

`simulate()` is called 6 times (2 wage modes × 3 betas), each re-reading and re-parsing the same file; the band block then reads it a 7th time (line 302). Read once in `main()` and pass the DataFrame (or `pool_path`-loaded frame) into `simulate()` — `_entrants_from_pool` already treats its argument read-only apart from the reassigned local. Removes ~6 redundant parquet parses of a several-hundred-thousand-row file per run.

## CE-007 — SUGGESTION — `_net_gain_at` re-derives schedule groupings every call and evaluates settled rows

**File:** `code/02_descriptive_analysis/02d_matching_simulation.py:202-225` with `_entrant_fiscal` (`:153-164`).

Each `_entrants_from_pool` invocation calls `_net_gain_at` up to 9 times (once at `w_e` + 8 grid steps), and each call rebuilds the `(family_type_key, state)` DataFrame, re-runs the groupby, re-resolves schedules (cached, but the group/position bookkeeping is not), and interpolates **all** pool rows — including rows already settled (`~remaining`) and rows that were never `viable`, whose results are masked out or zero-weighted. With 11 invocations per run (6 `simulate` + 3 edges + 2 sensitivity variants) this is ~100 full-pool groupby+interp passes. 01h already has the right pattern: precompute a `_NetIncome`-style `(schedule, positions)` list once per invocation and reuse it; additionally, inside the grid loop evaluate only `remaining` rows (`w_try[remaining]` against the cached group positions intersected with `remaining`). Correctness is unaffected (the masking already guarantees that); this is purely the dominant avoidable compute in the new entrant path.

## CE-008 — SUGGESTION — Row-wise `.apply`/comprehensions over ~1.1M rows in 01h `main()`

**File:** `code/01_data_preparation/01h_nonemployed_pool.py:425-429`.

```python
org["educ_group"] = org["EDUC"].apply(lambda c: _EDUC_MAP.get(int(c), "Less than HS"))
org["educ_fine"] = org["EDUC"].apply(lambda c: _EDUC_FINE_MAP.get(int(c), "primary_or_less"))
org["age_bin"] = org["AGE"].apply(_age_bin)
org["family_type_key"] = [_family_key(m, n) for m, n in zip(org["MARST"], org["NCHILD"])]
org["mcell"] = [_assign_matching_cell(s, f) for s, f in zip(org["sex_label"], org["family_type_key"])]
```

Five Python-level per-row passes over ~1.1M rows. Vectorized equivalents: `org["EDUC"].map(_EDUC_MAP).fillna("Less than HS")` (ditto fine map), `pd.cut(org["AGE"], [15, 24, 34, 44, 54, 64], labels=[...])` for `age_bin`, and boolean/`np.where` construction for `family_type_key`/`mcell` (02b's `assign_cell` already does the latter vectorized — reusing it also removes a duplicated cell definition). Order-of-magnitude faster and one canonical definition instead of two.

## CE-009 — SUGGESTION — Python-lambda groupby aggregations over the full household roster in 01i

**File:** `code/01_data_preparation/01i_household_links.py:83-88`.

```python
hh_any_under5 = hh["AGE"].agg(lambda a: bool((a < 5).any()))
hh_own_child_under5 = roster[roster["RELATE"] == 301].groupby(_HH_KEY)["AGE"].agg(
    lambda a: bool((a < 5).any()))
```

Per-group Python lambdas over several hundred thousand households are the slow path in pandas. Vectorized equivalents compute the flag once, then use the cythonized `any`:

```python
hh_any_under5 = (roster["AGE"] < 5).groupby([roster[k] for k in _HH_KEY]).any()
hh_own_child_under5 = (roster.loc[roster["RELATE"] == 301, "AGE"] < 5) \
    .groupby([roster.loc[roster["RELATE"] == 301, k] for k in _HH_KEY]).any()
```

(Or `roster.assign(u5=roster["AGE"] < 5).groupby(_HH_KEY)["u5"].any()`.) Same results, materially faster on the full roster.

---

## Verified clean (checked, no finding)

- **01h links merge alignment** (`01h:440-445`): key casts to `int64` on both sides before an exact-key left merge; all subsequent computation is column-based (no pre-merge positional arrays reused post-merge). The `astype("boolean").fillna(False)` pattern is correct for both the fully-matched (plain `bool`) and hypothetical unmatched (`object`-with-NaN) cases.
- **Household key** — `(YEAR, MONTH, SERIAL)` is the grouping/join/reindex key *everywhere* in 01i (`hh` aggregates, `heads`/`spouses` set_index + join, `reindex(idx)`), so concatenating two year partitions cannot collide SERIALs across YEAR or MONTH. `_partner_frame`'s join is on deduplicated unique indexes on both sides; `linked` cannot carry duplicate `(hhkey, PERNUM)` because heads (RELATE 101) and spouses (201/202/203) are disjoint and deduped.
- **Multi-spouse dedup guard** (`01i:93-95`): `~index.duplicated(keep="first")` silently keeps one record, but the extract was verified to contain none, and the guard prevents a merge fan-out (which *would* be a bug) — acceptable as written.
- **`_NetIncome` / `_entrant_fiscal` / `_ni_cost` group positions**: each builds its key frame fresh with a RangeIndex (or `index=w.index`, unique), so `key.index.get_indexer(idx)` returns correct positions into the positionally-extracted numpy arrays, including after 02d's internal filtering (arrays are extracted from the already-filtered frame).
- **Hash-ranked u** (`01h:360-373`): `hash_pandas_object` over 4 int64 keys gives 64-bit values; `rank(method="first")` ties (the only file-order-dependent path) require exact 64-bit hash collisions — negligible at pool size, and byte-identical rerun confirms determinism.
- **Band assertion direction** (`01h:404-405`): lower eps → lower target → smaller λ → larger markups → `reservation_wage_lower ≥ central ≥ upper`. Assertions match; shared `u` guarantees pointwise monotonicity; tolerances are on the correct side.
- **02d viability gate** (`02d:200`): `req <= gnb*(1+gnet)*(1+1e-9)` is algebraically identical to 01h's calibration condition `m ≤ g_net` (both use the stored floored/clipped `g_net` and `net_gain_base`), with the tolerance on the permissive side to absorb float roundtrip — non-reachable rows (m=100) can never pass since `g_net ≤ 3`.
- **Pay-up grid** (`02d:216-225`): `_net_gain_at(np.where(remaining, w_try, w_final))` evaluates settled rows at their final wage, but `newly = remaining & (...)` masks them out — no corruption (only wasted compute; see CE-007). Grid ordering takes the lowest clearing wage; unresolved rows correctly fall back to `w=y`, consistent with the calibration-identical max-package gate.
- **Zero-weighted non-viable rows**: `s_e`, `subsidy_annual_e`, `dens` are computed for all rows but every aggregate multiplies by `we = wt * viable`; `wt[payup]` equals the `we` mass on `payup` since `payup ⊆ viable`. Harmless.
- **Reconciliation `.iloc[0]` guards** (`02d:338-346`): the `band_edge=="central" & variant=="as-modeled"` row is unconditionally created by the loop; the 02b read is wrapped in try/except with a NaN fallback that formats safely.
- **`eps_ext_band` config** (`00_config.py:216-220`): keys match 01h's `band[e][c]` and 02d's synthetic-path lookup exactly; edge ordering (lower ≤ central ≤ upper per cell) is consistent with the monotonicity assertions.
