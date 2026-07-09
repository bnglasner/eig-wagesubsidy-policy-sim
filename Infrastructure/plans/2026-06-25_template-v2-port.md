# Plan: Port EIG template v2 into eig-wagesubsidy-policy-sim

Date: 2026-06-25. Status: executed on branch `feature/template-v2-port` (uncommitted; diff left for review).

## Objective
Replace the legacy `INFRA/` baseline-shell scaffolding with the updated EIG AI-assisted research template (`eig-template-version2`): canonical `Infrastructure/` brain, generated adapter trees, `Makefile` generation model, and the flat `code/ data/ drafts/ output/` layout — while preserving all research work and the live app.

## Decisions (confirmed with user)
1. Adopt the full flat layout (move `WORKSPACE/*` to repo root).
2. Adopt the full generation model (`make brain-sync` + `make maintenance-check`).
3. Migrate the useful legacy docs; drop superseded boilerplate.

## Steps
1. Safety branch; verify tooling (`make`, `python3`, `pyyaml`).
2. Install `Infrastructure/`, `.claude` / `.codex` / `.agents`, `Makefile`, root instructions, `drafts/`, `.gitattributes`; remove old root adapters; run `template-reset`.
3. Flatten: `WORKSPACE/{code,data,output}` to root; `app`, `docs` to root; `explorations` into `Infrastructure/`.
4. Migrate identity to `PROJECT.md`; carry `.Renviron.example` and historical logs/plan; remove `INFRA/`.
5. Rewire paths: config root-detection + constants (`.py/.R/.do`), `Path(__file__).parents[N]` indices, quoted `"WORKSPACE"` segments, `eig_style` `INFRA`->`Infrastructure`, `app.py`, `.streamlit`, `.gitignore`, markdown.
6. `make brain-sync`; `make maintenance-check` to green.
7. Verify config + app path resolution; byte-compile; log; report.

## Verification gates
- `make maintenance-check`: 8/8 pass.
- All `.py` byte-compile; `00_config.py` resolves repo root; every relocated path constant resolves to a real directory.

## Out of scope / follow-ups
- Streamlit Cloud entrypoint update (`app/app.py`) — dashboard setting, not in-repo.
- End-to-end live run (`streamlit run`, `python code/run_all.py`) — requires the project virtualenv.
