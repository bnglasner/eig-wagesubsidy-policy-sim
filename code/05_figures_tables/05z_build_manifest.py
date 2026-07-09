"""
05z_build_manifest.py — Build the intermediate-outputs manifest.

Single answer to "what analysis-consumable tables exist and what is in each." Scans
output/data/intermediate_results/population/ (the canonical home for analysis tables) and
data/processed/ for the pool + diagnostics, and writes a _manifest.csv describing each:
file, produced_by, rows, columns, description, role.

role ∈ {analysis-table, diagnostic, deprecated}. Descriptions/producers/roles come from the
registry below (hand-curated, so the manifest carries human context, not just schema). Any
parquet found without a registry entry is still listed with role "unregistered" so nothing is
silently invisible.

Consumers use code/_utils/intermediates.py (list_intermediates / load) to grab by stem.
Run after the pipeline (wired into run_all.py after the figure stage).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg = importlib.util.module_from_spec(_cfg_spec); _cfg_spec.loader.exec_module(_cfg)
POP = _cfg.PATH_OUTPUT_INTERMEDIATE / "population"
PROCESSED = _cfg.PATH_DATA_PROCESSED

# stem -> (produced_by, role, description)
_REGISTRY = {
    "summary": ("02a", "analysis-table", "Headline totals: gross/net cost, eligible workers, avg subsidy."),
    "by_sex": ("02a", "analysis-table", "Eligible workers, cost, avg subsidy by sex."),
    "by_age_bin": ("02a", "analysis-table", "By 10-year age band."),
    "by_education": ("02a", "analysis-table", "By education group."),
    "by_race_ethnicity": ("02a", "analysis-table", "By race/ethnicity."),
    "by_family_type": ("02a", "analysis-table", "By married/single x children."),
    "by_wage_bracket": ("02a", "analysis-table", "By employer-wage band; avg subsidy (progressivity)."),
    "by_state": ("02a", "analysis-table", "By state: workers, gross/net cost, avg subsidy (choropleth source)."),
    "take_up_by_group": ("02e", "analysis-table", "Take-up rate: share of each group's hourly workers eligible."),
    "behavioral_scenarios": ("02b", "analysis-table", "Reduced-form EITC/CBO-benchmark cost band + induced entry by cell."),
    "matching_simulation": ("02d", "analysis-table", "Structural sim, 6 rows (wage_mode x beta): cost, firm capture, induced by cell, cliff pay-up, entry hours."),
    "entry_margin_band": ("02d", "analysis-table", "Extensive-margin band (lower/central/upper) + household-coordination sensitivity rows."),
    "entry_reconciliation": ("02d", "analysis-table", "02b-vs-02d central induced-entry wedge attribution."),
    "mpl_imputation_band": ("02f", "analysis-table", "MPL uncertainty, four axes: imputation variants (converged); offer-dispersion lambda {0.5,0.75,1.0}; uniform wage-penalty {0,10,20%}; status-mixture (left-skewed) penalties."),
    "incumbent_hours_margin": ("02d", "analysis-table", "E5 intensive margin: added hours/FTE/cost for eligible incumbents below 40 hrs/wk over the eps_int band {0.05/0.20/0.33}."),
    "entrant_hours_sensitivity": ("02d", "analysis-table", "PI-3: entry FTE, entrant gross/net, marginal $/job under 3 entrant-hours mappings (rank / independent / median), central edge."),
    "entry_scenario_grid": ("02g", "analysis-table", "Joint 27-cell decomposition of induced entry: penalty {0/10/20%} x offer-dispersion lambda {0.5/0.75/1.0} x eps edge {lower/central/upper}."),
    "entry_headline_scenarios": ("02g", "analysis-table", "Three jointly-specified entry bundles: conservative floor (0.83M), evidence-central (status-differentiated ~10% penalty), high joint corner."),
    "entry_central_composition": ("02g", "analysis-table", "Evidence-central entrants by prior labor-force status (fig07b source); reflects the headline, not the floor."),
    "entry_central_stress": ("02g", "analysis-table", "Coordination/take-up stress tests computed on the evidence-central pool (spouse-employed zeroed; take-up 0.80)."),
    "incidence_by_segment": ("02c", "deprecated", "Band-clearing incidence — 02c superseded by 02d; not regenerated."),
    "incidence_decomposition": ("02c", "deprecated", "Band-clearing incidence decomposition — 02c superseded by 02d."),
    "program_interactions": ("02a", "analysis-table", "Per-program tax/transfer deltas (waterfall source)."),
    "nonemployed_pool": ("01h", "analysis-table", "Non-employed pool: MPL, g_net, reservation band, entry hours, household flags, person keys."),
    "nonemployed_pool_diagnostics": ("01h", "diagnostic", "Heckman + band-calibration audit trail (JSON): IMR coef, MPL percentiles by variant, per-cell/edge target vs realized, g_net guards."),
    "household_links": ("01i", "analysis-table", "In-ORG spouse links (employment/earnings) + child-under-5 flags, by person key."),
}


def _describe(path: Path, stem: str) -> dict:
    produced_by, role, desc = _REGISTRY.get(stem, ("?", "unregistered", ""))
    row = {"file": path.name, "stem": stem, "produced_by": produced_by, "role": role,
           "rows": "", "columns": "", "description": desc}
    if path.suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
            sch = pq.read_schema(path)
            row["rows"] = pq.read_metadata(path).num_rows
            row["columns"] = ";".join(sch.names)
        except Exception:  # noqa: BLE001
            try:
                df = pd.read_parquet(path)
                row["rows"] = len(df); row["columns"] = ";".join(map(str, df.columns))
            except Exception:  # noqa: BLE001
                pass
    elif path.suffix == ".json":
        row["rows"] = ""; row["columns"] = "(json diagnostics)"
    return row


def main() -> None:
    rows = []
    for p in sorted(POP.glob("*.parquet")):
        rows.append(_describe(p, p.stem))
    for name in ("nonemployed_pool.parquet", "nonemployed_pool_diagnostics.json",
                 "household_links.parquet"):
        p = PROCESSED / name
        if p.exists():
            rows.append(_describe(p, p.stem))
    man = pd.DataFrame(rows, columns=["file", "stem", "produced_by", "role", "rows",
                                      "columns", "description"])
    out = POP / "_manifest.csv"
    man.to_csv(out, index=False)
    by_role = man["role"].value_counts().to_dict()
    print(f"05z | Wrote {out} | {len(man)} intermediates | roles: {by_role}")


if __name__ == "__main__":
    main()
