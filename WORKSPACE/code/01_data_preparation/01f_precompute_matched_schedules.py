"""
01f_precompute_matched_schedules.py
Pre-compute PolicyEngine income schedules for matched ASEC household configs.

For each unique discretised household configuration that appears in the
ORG–ASEC matches, this script runs PolicyEngine across 131 income grid points
($0–$65,000 in $500 steps) and saves a schedule parquet.  The schedule is
keyed by a config string that encodes all PE-relevant household inputs:
    {n_adults}a_{n_children}c_{child_ages_repr}_{spouse_bucket}_{state}.parquet

Discretisation
--------------
  Spouse income  → 10 representative buckets (0, 5k, 10k, 15k, 20k, 25k,
                   32.5k, 45k, 62.5k, 87.5k)
  Child ages     → 4 broad age bands per child
                   (0-2 → 1, 3-5 → 4, 6-12 → 9, 13-17 → 15)

Compute estimate gate
---------------------
  Before any PE calls the script prints:
    - number of unique configs
    - estimated runtime at 0.5s/call with MAX_WORKERS
  The user can abort (Ctrl-C) or reduce MAX_CONFIGS to cap the run.
  If unique configs exceed MAX_CONFIGS the script clusters them with k-means
  and uses cluster centroids as representative configs.

Output
------
  WORKSPACE/output/data/intermediate_results/matched_schedules/
    {config_key}_{state}.parquet
      index  : annual_income (0, 500, ..., 65000)
      columns: eitc, child_tax_credit, snap, medicaid_chip, aca_ptc, ssi,
               tanf, housing, ccdf, wic, school_meals, liheap, other_benefits,
               federal_tax, state_tax, payroll_tax, net_income

Usage
-----
    python WORKSPACE/code/01_data_preparation/01f_precompute_matched_schedules.py
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE        = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[3]
EXTERNAL_DIR = PROJECT_ROOT / "WORKSPACE" / "data" / "external"
APP_DIR      = PROJECT_ROOT / "WORKSPACE" / "app"
OUTPUT_DIR   = (
    PROJECT_ROOT
    / "WORKSPACE" / "output" / "data" / "intermediate_results" / "matched_schedules"
)

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# ── Configuration ─────────────────────────────────────────────────────────────

INCOME_POINTS: list[int] = list(range(0, 65_001, 500))   # 131 points

MAX_WORKERS  = 16      # parallel processes (tune to your core count)
MAX_CONFIGS  = 5_000   # soft cap: if unique configs exceed this, k-means cluster

# Spouse income bucket boundaries and representative midpoints (annual $)
SPOUSE_BUCKET_BOUNDS = [0, 1, 7_500, 12_500, 17_500, 22_500, 27_500, 37_500, 52_500, 72_500]
SPOUSE_BUCKET_REPRS  = [0, 5_000, 10_000, 15_000, 20_000, 25_000, 32_500, 45_000, 62_500, 87_500]

# Child age representative values (PE-relevant cutoffs at 0-2, 3-5, 6-12, 13-17)
def _discretise_child_age(age: int) -> int:
    if age <= 2:  return 1
    if age <= 5:  return 4
    if age <= 12: return 9
    return 15


def _discretise_spouse_income(income: float) -> float:
    """Map raw spouse income to nearest representative bucket midpoint."""
    income = max(0.0, income)
    for i in range(len(SPOUSE_BUCKET_BOUNDS) - 1, -1, -1):
        if income >= SPOUSE_BUCKET_BOUNDS[i]:
            return float(SPOUSE_BUCKET_REPRS[i])
    return 0.0


def _config_key(n_adults: int, n_children: int, children_ages_repr: tuple[int, ...], spouse_bucket: float) -> str:
    """Serialisable string key for one household configuration (without state)."""
    ages_str = "_".join(map(str, children_ages_repr)) if children_ages_repr else "none"
    spouse_k = int(spouse_bucket // 1000)
    return f"{n_adults}a_{n_children}c_{ages_str}_s{spouse_k}k"


# ── Worker function (top-level for multiprocessing) ───────────────────────────

def _compute_and_save(
    config_key: str,
    n_adults: int,
    n_children: int,
    children_ages: list[int],
    spouse_income: float,
    state_code: str,
) -> tuple[str, str, float]:
    """
    Run PolicyEngine for all income grid points for one matched household config.
    Returns (config_key, state_code, elapsed_seconds).
    """
    t0 = time.time()

    from utils.household_sim import compute_income_point_matched  # noqa: E402

    rows = []
    for income in INCOME_POINTS:
        row = compute_income_point_matched(
            annual_income=float(income),
            n_adults=n_adults,
            n_children=n_children,
            children_ages=children_ages,
            spouse_annual_income=spouse_income,
            state_code=state_code,
        )
        row["annual_income"] = income
        rows.append(row)

    df = pd.DataFrame(rows).set_index("annual_income")
    out_file = OUTPUT_DIR / f"{config_key}_{state_code}.parquet"
    df.to_parquet(out_file)

    return config_key, state_code, round(time.time() - t0, 1)


# ── Extract unique configs from matches ───────────────────────────────────────

def _extract_configs(matches: pd.DataFrame) -> list[dict]:
    """
    Extract unique discretised (n_adults, n_children, children_ages_repr,
    spouse_bucket, state_code) from the matched ORG-ASEC frame.
    Returns a list of config dicts.
    """
    import json

    records = []
    for _, row in matches.iterrows():
        n_adults    = 2 if row.get("marital_binary", 0) == 1 else 1
        spouse_raw  = float(row.get("asec_spouse_income", 0.0) or 0.0)
        spouse_buck = _discretise_spouse_income(spouse_raw)

        ages_raw  = row.get("asec_children_ages", "[]")
        if isinstance(ages_raw, str):
            try:
                ages_raw = json.loads(ages_raw)
            except Exception:
                ages_raw = []
        ages_raw = [int(a) for a in ages_raw if 0 <= int(a) < 18][:3]

        n_children    = len(ages_raw)
        ages_repr     = tuple(sorted(_discretise_child_age(a) for a in ages_raw))
        state         = str(row.get("state_code", ""))

        records.append({
            "n_adults":      n_adults,
            "n_children":    n_children,
            "children_ages": ages_repr,
            "spouse_income": spouse_buck,
            "state_code":    state,
            "config_key":    _config_key(n_adults, n_children, ages_repr, spouse_buck),
        })

    configs_df = pd.DataFrame(records).drop_duplicates(
        subset=["n_adults", "n_children", "children_ages",
                "spouse_income", "state_code"]
    )
    out = configs_df.to_dict(orient="records")
    for c in out:
        c["children_ages"] = list(c["children_ages"])
    return out


# ── K-means clustering for config reduction ───────────────────────────────────

def _cluster_configs(configs: list[dict], k: int) -> list[dict]:
    """
    If len(configs) > MAX_CONFIGS, reduce to k representative configs using
    k-means on a numeric encoding of the config space.  Each cluster is
    represented by the config closest to its centroid.
    """
    from sklearn.cluster import MiniBatchKMeans

    print(f"  Clustering {len(configs):,} configs -> {k} representatives via k-means ...")

    # Numeric encoding for clustering
    rows = []
    for c in configs:
        ages = list(c["children_ages"]) + [0] * (3 - len(c["children_ages"]))
        rows.append([
            c["n_adults"],
            c["n_children"],
            ages[0], ages[1], ages[2],
            c["spouse_income"] / 87_500,   # normalise
        ])
    X = np.array(rows, dtype=float)

    km = MiniBatchKMeans(n_clusters=k, random_state=42, n_init=3)
    labels = km.fit_predict(X)

    # For each cluster pick the actual config nearest the centroid
    representatives = []
    for cluster_id in range(k):
        mask  = labels == cluster_id
        if not mask.any():
            continue
        cluster_X = X[mask]
        centroid  = km.cluster_centers_[cluster_id]
        dists     = np.linalg.norm(cluster_X - centroid, axis=1)
        best_idx  = np.where(mask)[0][dists.argmin()]
        representatives.append(configs[best_idx])

    print(f"  Reduced to {len(representatives):,} representative configs.")
    return representatives


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load matches ──────────────────────────────────────────────────────────
    matches_path = EXTERNAL_DIR / "org_asec_matches.parquet"
    if not matches_path.exists():
        raise FileNotFoundError(
            f"{matches_path} not found. Run 01e_match_org_to_asec.py first."
        )
    print(f"Loading matches: {matches_path.name} ...")
    matches = pd.read_parquet(matches_path)
    print(f"  {len(matches):,} matched ORG workers")

    # ── Extract unique household configs ──────────────────────────────────────
    print("Extracting unique discretised household configurations ...")
    all_configs = _extract_configs(matches)
    print(f"  {len(all_configs):,} unique configs before caching check")

    # Skip already-computed configs
    tasks = [
        c for c in all_configs
        if not (OUTPUT_DIR / f"{c['config_key']}_{c['state_code']}.parquet").exists()
    ]
    skipped = len(all_configs) - len(tasks)
    print(f"  {skipped:,} already computed (skipping), {len(tasks):,} to run")

    # ── Compute estimate gate ──────────────────────────────────────────────────
    pe_calls       = len(tasks) * len(INCOME_POINTS)
    secs_per_call  = 0.5            # conservative estimate per PE call
    est_secs       = pe_calls * secs_per_call / max(MAX_WORKERS, 1)
    est_mins       = est_secs / 60
    est_hrs        = est_mins / 60

    print(f"\nCompute estimate:")
    print(f"  Configs to run : {len(tasks):,}")
    print(f"  Income points  : {len(INCOME_POINTS)}")
    print(f"  Total PE calls : {pe_calls:,}  (at 0.5s each, {MAX_WORKERS} workers)")
    if est_hrs < 1:
        print(f"  Estimated time : {est_mins:.0f} minutes")
    else:
        print(f"  Estimated time : {est_hrs:.1f} hours")

    if len(tasks) > MAX_CONFIGS:
        print(
            f"\n  [!] {len(tasks):,} configs exceeds MAX_CONFIGS={MAX_CONFIGS:,}.\n"
            f"      Clustering to {MAX_CONFIGS:,} representative households ...\n"
            f"      Edit MAX_CONFIGS at the top of this script to change the cap."
        )
        tasks = _cluster_configs(tasks, k=MAX_CONFIGS)
        pe_calls  = len(tasks) * len(INCOME_POINTS)
        est_mins  = pe_calls * secs_per_call / max(MAX_WORKERS, 1) / 60
        print(f"  Revised estimate: {len(tasks):,} configs, ~{est_mins:.0f} min")

    if not tasks:
        print("\nNothing to do — all schedules already exist.")
        return

    print(f"\nStarting pre-computation ({MAX_WORKERS} workers) ...")
    print("  Press Ctrl-C to abort cleanly (completed configs are saved).\n")

    # ── Parallel pre-computation ───────────────────────────────────────────────
    completed_n = 0
    failed: list[tuple] = []
    wall_start  = time.time()

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_map = {
            pool.submit(
                _compute_and_save,
                c["config_key"],
                c["n_adults"],
                c["n_children"],
                c["children_ages"],
                c["spouse_income"],
                c["state_code"],
            ): c
            for c in tasks
        }

        for future in as_completed(future_map):
            cfg = future_map[future]
            try:
                _, _, elapsed = future.result()
                completed_n += 1
                pct   = 100 * completed_n / len(tasks)
                eta_s = (
                    (time.time() - wall_start) / completed_n * (len(tasks) - completed_n)
                )
                print(
                    f"  [{completed_n:>5}/{len(tasks)}  {pct:5.1f}%]  "
                    f"{cfg['config_key']} / {cfg['state_code']}  ({elapsed}s)  "
                    f"ETA {eta_s/60:.1f} min",
                    flush=True,
                )
            except Exception as exc:
                failed.append((cfg["config_key"], cfg["state_code"], str(exc)))
                print(f"  FAILED: {cfg['config_key']} / {cfg['state_code']} — {exc}")

    wall_elapsed = round(time.time() - wall_start, 1)
    print(
        f"\nDone. {completed_n} succeeded, {len(failed)} failed "
        f"in {wall_elapsed}s ({wall_elapsed/60:.1f} min)."
    )
    if failed:
        print("Failed configs:")
        for key, state, err in failed:
            print(f"  {key} / {state}: {err}")

    print(
        f"\nSchedules written to:\n  {OUTPUT_DIR}\n"
        "\nNext step: update household_sim.py to route matched workers through "
        "these schedules (run_from_matched_precomputed)."
    )


if __name__ == "__main__":
    main()
