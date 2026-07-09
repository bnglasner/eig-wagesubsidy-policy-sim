# EIG Style Review

Use this skill when auditing outputs/code for EIG style compliance.

## Source Priority

1. `Infrastructure/style/docs/agent-01-design-spec.md`
2. `Infrastructure/style/docs/eig-legacy-palette-policy.md`
3. `Infrastructure/style/tokens/eig-style-tokens.v1.json`
4. `Infrastructure/style/docs/eig-design-signoff-checklist.md`
5. Language implementation references under `Infrastructure/style/docs/agent-0{2,3,4}-*.md`

## Review Workflow

A complete figure review has two passes. Pass 1 confirms the output is on-brand; Pass 2
confirms it is a good display of the data.

### Pass 1 — Brand compliance

1. Identify artifact type: figure, table, dashboard, or mixed output set.
2. Check color usage against style tokens.
3. Check typography/layout against style baseline.
4. Confirm legacy-palette usage has required justification.
5. Report concrete findings with path-specific fixes.

### Pass 2 — Graphical quality (design-quality layer)

6. Run the Tufte test against `Infrastructure/style/docs/tufte-principles.md`:
   lie factor ≈ 1, data-ink maximized (eraser test), zero chartjunk (collision test),
   comparison enabled ("compared to what?"), appropriate data density.
7. For dense/results/dashboard outputs, also walk the six analytical-design principles in
   `Infrastructure/style/docs/tufte-analytical-design.md`.
8. Apply the color-count reconciliation: EIG palette governs which hues; prefer the fewest
   encoded colors (1–2 + neutral gray). Flag — do not silently resolve — any genuine
   conflict between a Tufte preference and an EIG brand non-negotiable.
9. For deeper ideation or a standalone design critique, hand off to the `eig-tufte-critique`
   skill, which owns this layer in full.

## Required Findings Format

1. Severity (`Critical`, `Medium`, `Optional`)
2. Evidence (path + relevant code/output element)
3. Risk
4. Recommended fix
5. Verification step
