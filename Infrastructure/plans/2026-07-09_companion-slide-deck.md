# Orchestration Plan — Companion Slide Deck

**Status:** COMPLETED 2026-07-09 — deck at `output/slides/2026-07-09_80-80-companion-deck.pptx` (32 slides, 16:9). Includes fig03 source fix + approved narrative refinements (bottom-line-before-appendix, two added dividers with 6-act renumber, dedicated "What about men?" slide). See session log for details.

## Objective
- Produce a PowerPoint (`.pptx`) companion deck for `drafts/2026-07-09_combined-brief-and-appendix`, compliant with EIG brand tokens (2022 palette, Source Serif Pro / Open Sans, teal table headers) and the Tufte graphical-quality layer.
- Confirmed scope: **full deck (~22 slides)** covering the main brief narrative *and* the appendix/methodology section; **16:9 widescreen**; figures **embedded from `output/figures/main/` with figure titles and source lines restyled as native, token-styled slide text**.

## Workstreams

| Workstream | Route (Agent/Command) | Dependency | Status |
|---|---|---|---|
| W1 Narrative distillation (slide spine, EIG voice) | Direct (brief prose is already EIG-compliant) | none | Done (in-plan) |
| W2 Style spec (palette map, type scale, layout motif) from tokens | Direct, per `eig-style-guide-agent` conventions + `style-figure-rules.md` | none | Done (in-plan) |
| W3 Deck build (`pptxgenjs`, embed figures, native titles/notes) | pptx skill | W1, W2 | Pending |
| W4 Visual QA (fresh-eyes render inspection) | subagent (mandated by pptx skill) | W3 | Pending |
| W5 EIG style/consistency spot-check + number match vs brief | Direct + optional `eig-reviewer` | W3 | Pending |

## Execution Waves
1. **Wave 1 (now):** W1 + W2 folded into the build design (content already stabilized in the brief; no upstream pipeline dependency — this is a downstream communication artifact).
2. **Wave 2:** W3 build the generator script → `output/slides/2026-07-09_80-80-companion-deck.pptx`.
3. **Wave 3 (finalization):** W4 visual QA via subagent → fix defects → W5 confirm numbers/titles match the brief, confirm token colors/fonts.

## Performance/Cost Tier Notes
- Highest expected tier: **Tier 1** (deck generation + LibreOffice render, <2 min). No pipeline rerun; figures already exist. No Tier 3/4 gating needed.

## Completion Criteria
- `.pptx` opens, renders without overflow/overlap defects (subagent-verified).
- Every embedded figure resolves; every headline number matches the brief.
- Colors drawn only from the 2022 primary token palette; fonts are the EIG brand stack.
- Source line on figure slides; EIG attribution present.

## Next Action
- Build the generator and produce the deck (Wave 2).
