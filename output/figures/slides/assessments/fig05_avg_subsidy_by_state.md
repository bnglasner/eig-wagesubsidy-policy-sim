# fig05_avg_subsidy_by_state — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Cream→gold single-hue sequential fill is token-derived (`eig_cream_100`→`eig_gold_600`, lines 83–84) and colorblind-safe: it varies primarily in luminance, so the order survives deuteran/protan vision. The distressed South (TX/LA/MS) reads darkest, which matches the "lagging labor markets" headline.
- Clean Tufte data-ink: white 0.15 borders, no panel box, no graticule or gridlines, AK/HI inset via `shift_geometry` (line 71), no chartjunk.
- Correct figure/deck separation: `title = NULL` and `caption = NULL` for the slide (lines 112–113), so no baked-in title/source; the slide template carries the headline and the "Source: Economic Innovation Group…" line.
- DC pinpoint is preserved with a point + leader + label (lines 91–110) rather than dropped, and the "D.C." shortening reads cleanly and clears the panel's right edge — the right editorial call, since DC is a high-wage outlier that would otherwise undercut the "lagging labor markets" framing.

**Issues:**
- `- [HIGH] The rendered slide (slide-11.jpg) shows no right-column bullets and the map is centered, not left-aligned — the TWOCOL layout is not realized, so the viewer gets no state names/values (the map alone cannot label them). → Confirm the deck template actually injects the LA/MS/CA/eligible-count bullets into the right column; if this JPG is the composed output, the bullets are the whole point of TWOCOL and must be restored.`
- `- [MEDIUM] The map+legend render small (~41% of slide width) and centered, so at projection the $2,500–$4,500 colorbar labels are hard to read despite the slide-only legend bump (barwidth 1.1 / barheight 8, lines 87–88; legend text size 10, line 128). → Enlarge the map within the left column and/or increase legend text so the color scale reads at distance.`
- `- [MEDIUM] The saved PNG carries heavy internal whitespace — the US map occupies only ~60% of the canvas width — which compounds the smallness when placed in a column. → Tighten the saved extent/aspect (crop margins; the far-left and top/bottom dead space) via eig_slide_dims / plot.margin so the twocol column is not wasted.`
- `- [LOW] The DC marker/leader use eig_teal_900 (line 92), off the gold sequential scale; as a non-data annotation this is acceptable, but a reader could briefly read teal as a category. Keeping it as a labeled pinpoint (not a fill) is the right compromise — no change required.`

**Integration:** In the artifact provided, the two-column design is not delivered: the map sits centered with an empty right column and no bullets, so the map's key weakness (a choropleth cannot name its top/bottom states) goes uncompensated. As specified, the bullets do complement the map well — they name LA ($4,981)/MS ($4,990) as the darkest states, CA ($2,392) as a light-fill contrast, and add eligible-worker counts the fill cannot show — but that value only lands if they render. Headline and annotation fit and are sentence-case; source line is present and correct. Once bullets are confirmed in the right column and the map is enlarged/left-aligned, balance and legibility resolve.

**Top 3 (prioritized):** (1) Verify/restore the right-column bullets and left-align the map — HIGH. (2) Enlarge map + legend so the colorbar reads at projection — MEDIUM. (3) Crop the figure's internal whitespace so the column is used efficiently — MEDIUM.
