# fig10_cost_per_job — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Log-scale honesty is handled well: the x-axis title reads "Cost per job (log scale)," breaks are clean powers of ten ($10K/$100K/$1M), and *every* point carries an explicit dollar label — so the visual compression inherent to a log axis cannot mislead a reader about the ~170x spread.
- Emphasis is correct and restrained: the two EIG entries use token colors (marginal green `eig_green_700`, fully-loaded gold `eig_gold_600`) against neutral-gray alternatives, so the eye lands on the comparison the headline makes.
- Very high data-ink ratio — no chartjunk, no box border, no baked-in title/source (slide=TRUE nulls both title and caption; layout supplies kicker/headline/source). Labels legible at ts=1.9.
- Ordering is intentional and defended in code (ascending cost via `reorder()` + pinned `scale_y_discrete(limits=...)`, lines 461–462, 513), placing the cheapest EIG option at the bottom and the most expensive alternative on top.

**Issues:**
- `- [MEDIUM] "floor" label sits on the RIGHT (highest-cost, $47K) dot while "high scenario" sits on the LEFT (lowest-cost, $13K) dot — "floor" reads as a minimum but here marks the most expensive per-job outcome, a genuine comprehension trap. → Relabel for clarity, e.g. "$47K conservative" / "$13K optimistic," in full_pts lab (lines 482–484).`
- `- [LOW] "other" series color is a hardcoded net-new hex "#9AA0A6" (line 491), not token-derived (non-negotiable #2). No exact neutral-gray exists in the 2022 primary palette, so the choice is defensible, but it is undocumented. → Add a neutral token or a short comment noting no palette equivalent exists.`
- `- [LOW] No gridlines at all: theme blanks major.x (line 84) and the figure blanks major.y (line 528). On a log dot plot, faint vertical guides at the labeled breaks would speed value-reading — but every point is labeled and brand default is no vertical gridlines, so this is acceptable as-is; keep only if labels are ever dropped.`

**Integration:**
- Log-scale honesty: strong. The scale is named in the axis title and reinforced by per-point value labels; readers are not misled about magnitude. This is the figure's main risk surface and it passes.
- Label clipping: the long left-hand policy labels (esp. "80-80 subsidy (marginal, per entrant)") clear the panel edge — the slide branch adds `plot.margin` l=26 (line 533) and neither the PNG nor slide-21 shows truncation. Headline ("undercuts the job-creation policies we already run") matches the chart (both EIG entries fall below all alternatives). Annotation is additive and accurate ($5.3K / $32K / $154K+ / $900K); omitting the $106K–$196K state/local band is fine. Hierarchy (kicker → headline → annotation → chart → source) is clean.

**Top 3 prioritized:**
1. [MEDIUM] Fix the "floor" vs "high scenario" left/right naming inversion (lines 482–484).
2. [LOW] Document or tokenize the `#9AA0A6` neutral gray (line 491).
3. [LOW] Optional faint log-break gridlines — only if value labels are ever removed.
