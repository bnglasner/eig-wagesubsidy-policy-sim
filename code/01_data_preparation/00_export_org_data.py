"""
00_export_org_data.py — RETIRED (2026-07-07).

ORG wage ingestion is now internalized in this repo. The employed-worker panel
is produced by the vendored EIG-Wage-Figure R stages under code/00_ingest/
(00a -> 01a -> 01b), which write data/intermediate/cps_org_panel/. The Python
consumer 01a_data_ingest.py reads that panel directly and derives the EIG
nominal hourly wage; 01h_nonemployed_pool.py reads the raw partitions under
data/raw/cps_org/.

This script previously read a processed org_panel from the sibling
real-wages-generations-ipums repo (now defunct) and is no longer part of the
pipeline. It is retained as a stub only to give a clear pointer if invoked.

See Infrastructure/specs/2026-07-07_org-wage-internalization.md.
"""
import sys

_MSG = (
    "00_export_org_data.py is RETIRED. ORG ingestion is internalized:\n"
    "  1) Rscript code/00_ingest/00a_download-ipums-cps.R\n"
    "  2) Rscript code/00_ingest/01a_load-ipums-cps.R\n"
    "  3) Rscript code/00_ingest/01b_build-org-panel.R\n"
    "Then run code/01_data_preparation/01a_data_ingest.py.\n"
    "See Infrastructure/specs/2026-07-07_org-wage-internalization.md."
)

if __name__ == "__main__":
    print(_MSG)
    sys.exit(0)
