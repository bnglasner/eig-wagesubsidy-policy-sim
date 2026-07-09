# Replication Targets — Pre-change baseline for the entry-remodel implementation

**Date:** 2026-07-08 · **Captured before any code change in the rev2 implementation session.**
**Environment note:** the validated local Python env (requirements.txt, 2026-03-07) was absent from this machine; recreated as `.venv` with pinned pandas 2.3.3 / numpy 2.4.2 / pyarrow 23.0.1 + statsmodels ≥0.14.5 / scipy ≥1.13. Baselines below were read from the on-disk outputs produced by the last validated run (not re-generated), so they are the authoritative pre-change targets.

## Non-employed pool (`data/processed/nonemployed_pool.parquet`, 01h output)

- Rows: **181,960** · population **59.28M** weighted
- MPL p25/p50/p75 = **$15.53 / $21.00 / $28.18** (median == employed median — the known ST-7 red flag)
- Share MPL < $16.80 target: **30.9%**
- Population by cell (M): men **24.69**, other_women **30.74**, single_mothers **3.85**
- Baseline induced entry (gross gate `y + s(y) ≥ r`, central): **0.935M** total — men **0.088**, other_women **0.778**, single_mothers **0.069**
- ST-10 artifact diagnostic: viable-share among reachable, by state, ranges **0.032 (CT) – 0.074 (VT)**, median 0.053

## 02d matching simulation (`matching_simulation.parquet`)

| scenario | beta | induced_M | incumbent Δwage % | gross $B | net $B | firm capture $B (% of gross) |
|---|---|---|---|---|---|---|
| rigid-central | 0.5 | 0.94 | 0.0 | 102.0 | 78.4 | 6.1 (6.0%) |
| rigid-measured | 0.7 | 0.94 | 0.0 | 101.4 | 77.7 | 3.5 (3.5%) |
| rigid-rigid | 0.3 | 0.94 | 0.0 | 102.3 | 78.8 | 8.8 (8.6%) |
| flex-central | 0.5 | 0.94 | −12.1 | 143.2 | 122.0 | 59.3 (41.4%) |
| flex-measured | 0.7 | 0.94 | −6.6 | 123.1 | 100.8 | 31.5 (25.6%) |
| flex-rigid | 0.3 | 0.94 | −18.9 | 169.0 | 149.8 | 94.7 (56.0%) |

Entry wage p15 = $10.00/hr in all rows; entrant_source = ORG pool.

## 02b behavioral scenarios (`behavioral_scenarios.parquet`) — NOT expected to change (parity anchor)

| scenario | gross $B | net $B | workers M | induced M (sm / ow / men) |
|---|---|---|---|---|
| static | 89.75 | 72.12 | 20.81 | 0.00 |
| lower | 92.33 | 73.57 | 21.15 | 0.35 (0.11 / 0.24 / 0.00) |
| central | 96.86 | 76.12 | 21.53 | 0.72 (0.19 / 0.43 / 0.10) |
| upper | 103.88 | 77.86 | 22.09 | 1.28 (0.26 / 0.75 / 0.27) |

## Expected direction of post-change deltas (to be attributed in the delta note)

1. **ST-7 conditional-Mills imputation**: pool MPL falls → larger g, more of pool below target → pushes calibrated entry **up** (and per-entrant subsidy up).
2. **ST-11 saturated person-level target**: replaces linear eps×mean(g) → pushes calibrated entry **down**, most in high-εg cells (single_mothers).
3. **Net calibration/gate + net stimulus basis**: direction ambiguous by cell (EMTRs shrink net gains, most for benefit-receiving family types).
4. **Band values (W2c)**: central anchors unchanged by decision; edges move.
5. 02b table and `tests/test_behavioral_static_parity.py`: **must not change** (any drift = regression).
