# Session Log — Companion Slide Deck (2026-07-09)

## Goal
Build a PowerPoint companion deck for `drafts/2026-07-09_combined-brief-and-appendix`, EIG-brand + Tufte compliant.

## Decisions
- Scope confirmed via clarifying questions: full deck (~22), 16:9, embed figures with native takeaway headlines.
- Attempted title/source auto-cropping of figures; auto-crop was unreliable across the 18 figures. **User directed: skip cropping, use PNGs as-is.** Final approach embeds `output/figures/main/*.png` unmodified (they already carry EIG-compliant titles + source lines) and layers a native EIG-styled takeaway headline on each figure slide.
- Palette drawn only from 2022 primary tokens (teal900 `#024140` for title/dividers/closing + table headers; blue800, green700, gold600 accents). Fonts: Source Serif Pro (headlines) / Open Sans (body). Native tables use teal header + horizontal rules only (`#D9D9D9`).

## Build
- Generator: `scratchpad/deckbuild/generate.js` (pptxgenjs 4.0.1). Output: `output/slides/2026-07-09_80-80-companion-deck.pptx` (29 slides: title, 5 section dividers, 18 figure slides, 3 native tables, 2 stat/text slides, closing). Speaker notes on every slide.

## Verification
- Rendered to PDF (LibreOffice) → 29 JPEGs; fresh-eyes subagent visual QA of all slides.
- Fixed: slide 2 stat number "$45–48B" wrapped/collided with caption → reduced 58→40pt; re-rendered and confirmed clean.
- Placeholder scan: none. File 2.4 MB, non-empty.

## Follow-up (2026-07-09, same session)
- **fig03 source fix:** title was clipping on the right ("…who qualif[y]"). Fixed at source in `code/05_figures_tables/05c_core_figures.R:345` by wrapping the title to two lines (`\n`); AR unchanged (2160x1920). Regenerated via a temp driver alongside the script (skips the sf/tigris map). Both PNG and SVG refreshed; brief and deck now show the full title.
- **Narrative refinements (user-approved, all three applied):** deck 29 → 32 slides.
  1. Moved the Bottom Line to close the argument *before* the appendix (appendix is now backup).
  2. Added two section dividers for previously orphaned mini-acts and renumbered acts: 01 cost, 02 who, 03 work, **04 Is it worth it? (capture + cost-per-job)**, 05 safety net, **06 How sure are you?**, appendix "A". Kickers on fig09/fig10 relabeled to "Is it worth it?".
  3. Added a dedicated "What about men?" stat/text slide (~180K central) inside the work act, restoring the brief's honest male-entry beat.
- Verified changed slides (9, 18, 19, 26, 29, 30) by render; no overlap/overflow.

## Slide-native figure subsystem (2026-07-09, new effort — /orchestrate)
Spec: `Infrastructure/specs/2026-07-09_slide-native-figures.md`; plan: `Infrastructure/plans/2026-07-09_slide-native-figures.md` (APPROVED, full per-figure assessment).
- **Decisions:** parallel `output/figures/slides/`; strip title+source from figures (slide supplies native headline + one-line annotation + source); per-figure Tufte/EIG written critique + fixes.
- **W1 harness (done):** `eig_save_fig(target="slide")` → `output/figures/slides/`; `eig_load_slide_spec()` + `eig_slide_dims()` read `code/05_figures_tables/slide_figures.json` (single source of truth for dims + slide text). 05c and 05d drivers guarded by `EIG_FIG_NO_RUN`. New driver `code/05_figures_tables/05e_slide_figures.R` calls every fig with `slide=TRUE`.
- **W1 pilot (done, pattern locked):** fig02 (WIDE) + fig03 (TWOCOL) converted and rendered clean. Pattern — WIDE: `ts=1.9, bs=17`; TWOCOL: `ts≈1.35, bs≈14`, drop redundant value axis, wider export (~AR 1.3). Both strip title/caption, scale in-plot text by `ts`, save via spec dims.
- **W2 in progress:** two `eig-style-guide-agent` subagents authoring the remaining 16 (Agent A = 05c: fig01/fig05-map/fig10/fig12; Agent B = 05d: 12 figures), file-scoped to avoid edit conflicts.
- **Next:** regenerate all via 05e, eyeball 18, integrate into deck (native headline+annotation+source, read from JSON), then fan out 18 independent per-figure Tufte/EIG assessments → remediate.

## Slide-native figure subsystem — COMPLETED (2026-07-09)
- **W2 build:** two `eig-style-guide-agent` subagents authored the remaining 16 figures (05c: 4, 05d: 12); all 18 build via `05e_slide_figures.R` into `output/figures/slides/` (PNG+SVG, chrome-stripped, projection-legible). Agent B fixed a `bs` name collision in fig13_cost_band and repositioned a fig11b annotation.
- **W3 integrate:** deck generator re-pointed to `output/figures/slides/`; each figure slide now renders a native EIG headline + one-line italic annotation dek + native source, read from `slide_figures.json`. Deck = 32 slides.
- **W4 assess (independent, per-figure):** 18 `eig-style-guide-agent` critiques → `output/figures/slides/assessments/*.md`. Verdicts: 17 Minor fixes, 1 Ship as-is (fig12), 0 Needs work. Consolidated in `_REMEDIATION.md`.
- **W5 remediate (applied + re-verified):**
  - Deck: **fig05** was mis-dispatched as WIDE (map centered, bullets missing) → switched to `figTwoCol` (real bug the review caught); **fig06** annotation rewritten (pool claim → threshold mechanic); **fig07b** headline corrected (bars show non-participants 64% > unemployed 33%); **fig08** headline reframed to the below-target comparison the chart shows.
  - Figures: fig01 "No subsidy" label; fig02 slide-asterisk + "−0.0" fixes; fig03 highlight now Female/16–24/<HS (matches headline); fig04 interior labels dark-on-gold; fig07 precedent labels enlarged; fig09 bargaining bars ordered ascending; fig10 endpoints labeled with entrant counts; fig11b gray vs green lines + crossover marker; fig13 x-limit tightened; fig15 redundant axis dropped.
  - Regenerated + rebuilt + re-rendered; spot-verified fig05/fig11b/fig02/fig04/fig10/fig13/fig15 clean.
- **Accepted as-is (documented in `_REMEDIATION.md`):** neutral grays (palette has no gray token; `style-figure-rules` permits neutral gray); fig11 y-truncation (net-income level chart; gaps drawn line-to-line so not inflated); fig14 density; fig12 ship as-is. Minor known nit: fig11b vertical "Subsidy hours cap" label slightly clipped at plot top (LOW).
- **Deliverable:** `output/slides/2026-07-09_80-80-companion-deck.pptx` (2.35 MB) now built entirely on the slide-native figure set.

## Notes
- `output/figures/main/` (document/brief figures) left untouched throughout, except two shared-root-cause co-fixes to source code that will only change the brief figures on a future doc rebuild: fig03 title-wrap and the fig01 "No subsidy" label (both improvements; flagged).
- Assessment conclusion: base ordering was already sound (mirrors the brief's Q&A arc and respects the cost-per-job → entry-count dependency); the changes were structural consistency + completeness, not a reordering of the argument.

## Evidence
- Sources: `drafts/2026-07-09_combined-brief-and-appendix.md`; `output/figures/main/`; `Infrastructure/style/tokens/eig-style-tokens.v1.json`.
- Confidence: High that deck numbers/figures mirror the brief (copied from the same draft). Medium on font fidelity in non-EIG viewers (brand fonts substitute; EIG PowerPoint has them).
- Assumptions: brand fonts installed in the user's PowerPoint; deck is a communication artifact downstream of the stabilized brief (no pipeline rerun).
