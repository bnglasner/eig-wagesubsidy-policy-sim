"""
intermediates.py — one easy way to grab pipeline intermediate outputs.

The full analysis-consumable output set lives in
output/data/intermediate_results/population/ (analysis tables) plus data/processed/ (the
non-employed pool + its diagnostics), described by a hand-curated manifest
(_manifest.csv, built by code/05_figures_tables/05z_build_manifest.py). This module lets
figures, tables, and numeric analyses grab an intermediate by its stem instead of
hard-coding paths.

    from code._utils.intermediates import list_intermediates, load, manifest
    manifest()                      # -> DataFrame: file, stem, produced_by, role, rows, cols, desc
    list_intermediates(role="analysis-table")   # -> list of stems
    by_state = load("by_state")     # -> DataFrame (parquet) or dict (json diagnostics)

Path-independent: resolves the repo root by walking up to code/run_all.py, so it works from
any cwd and from R via reticulate if needed.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _repo_root(start: Path | None = None) -> Path:
    cur = (start or Path(__file__)).resolve()
    for _ in range(12):
        if (cur / "code" / "run_all.py").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError("Could not locate repo root (code/run_all.py).")


def _search_dirs() -> list[Path]:
    root = _repo_root()
    return [root / "output" / "data" / "intermediate_results" / "population",
            root / "data" / "processed"]


def _find(stem: str) -> Path:
    for d in _search_dirs():
        for ext in (".parquet", ".json"):
            p = d / f"{stem}{ext}"
            if p.exists():
                return p
    raise FileNotFoundError(
        f"No intermediate named '{stem}' in {[str(d) for d in _search_dirs()]}. "
        f"Available: {', '.join(list_intermediates())}")


def manifest() -> pd.DataFrame:
    """The intermediates manifest as a DataFrame (built by 05z). Falls back to a directory
    scan if the manifest CSV has not been generated yet."""
    man = _search_dirs()[0] / "_manifest.csv"
    if man.exists():
        return pd.read_csv(man)
    return pd.DataFrame({"stem": list_intermediates()})


def list_intermediates(role: str | None = None) -> list[str]:
    """Stems of available intermediates. Optionally filter by manifest role
    (analysis-table | diagnostic | deprecated | unregistered)."""
    if role is not None:
        man = _search_dirs()[0] / "_manifest.csv"
        if man.exists():
            m = pd.read_csv(man)
            return sorted(m.loc[m["role"] == role, "stem"].tolist())
    stems = set()
    for d in _search_dirs():
        if d.exists():
            for p in list(d.glob("*.parquet")) + list(d.glob("*.json")):
                stems.add(p.stem)
    return sorted(stems)


def load(stem: str):
    """Load an intermediate by stem: parquet -> DataFrame, json -> dict."""
    p = _find(stem)
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    return json.loads(p.read_text())
