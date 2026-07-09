# EIG Style Review: Re-centered wage-subsidy drafts (blog/brief + technical appendix)

Scope: EIG writing, citation, and figure-style compliance for the two 1.25M-recentered drafts.
Remit is style/citation/figure only — not the numbers. Figure findings are limited to
doc-level labeling and to what the figure-generation code bakes into each image; the R suite
sources the canonical EIG theme + tokens (`eig_fig_utils.R` → `eig_theme_ggplot`, `eig_load_tokens`)
and stamps the canonical `Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.`
line, so brand palette/typography compliance is handled in code and is not re-litigated below.

Documents reviewed:
- A. `drafts/2026-07-08_wage-subsidy-impact-cost-summary.md` (blog/brief)
- B. `drafts/2026-07-09_technical-appendix.md` (companion technical appendix)

---

# Draft A — Blog/brief (`2026-07-08_wage-subsidy-impact-cost-summary.md`)

## Numbers And Percentages

- `ERROR` Line 158 ("contribute about **three percent** of modeled entrants"): a number preceding a unit of measurement (percent) must be a numeral, even below 10 (writing-style §1 and §10). -> "contribute about **3 percent** of modeled entrants."
- `ERROR` Line 239 ("careful studies measure offers falling nearly **one percent** per month out of work"): same rule — percentages always take numerals. -> "falling nearly **1 percent** per month."
- `ERROR` Line 130 ("Roughly **seven million** are unemployed… About **ten million** report… and **nine million** describe themselves as retired"): millions/billions take numerals + word form (writing-style §1), and the sentence is internally inconsistent (it already uses "34 million" and "10 to 15 million"). -> "Roughly **7 million**… About **10 million**… and **9 million**…"
- `SUGGESTION` Table 2 header (lines 53–54) uses `Share of recipients (%)` / `Share of the group's workers (%)`: the `%` symbol is correct inside a table column header (charts/tables exception), so no change needed — flagged only to confirm this is intentional and not to be "corrected" to "percent."
- `SUGGESTION` Internal "Evidence" block, Line 289 ("status-differentiated **~10%** penalty"): `%` appears in prose-style text. The block is marked "strip before publication," so this is low priority, but if any of it survives into published prose, convert `%` → "percent."

## Punctuation

- `SUGGESTION` Line 239 (footnote marker `...per month out of work[^8]).`): the marker sits inside the closing parenthesis and period. EIG places footnote markers outside the closing punctuation of the sentence. -> move to sentence end: "…per month out of work).[^8]"
- `SUGGESTION` Internal "Evidence" block, Lines 279, 290, 304 use spaced em dashes (" — "). EIG em dashes take no surrounding spaces. Strip-before-publication, so low priority; fix if retained.

## Capitalization

- No errors. Digital headline (Line 1) is correctly sentence case; figure captions (Lines 12, 43, 86, 103, 109, 126, 150, 154, 170, 188, 202, 216, 222, 228, 243, 247, 253) and table titles are sentence case with the "Figure N." / "Table N." prefix.

## Spelling And Word Form

- No errors. No contractions found. `COVID-19` / `homeownership` not applicable. "PolicyEngine-US" (Lines 266, 282) is a product name, not adjectival "US," so it is compliant.

## Voice And Style

- `SUGGESTION` "the evidence-central" used as a bare noun (Lines 148, 239, and echoed in the bottom line): "we headline the evidence-central," "the evidence-central corrects that one choice." Reads awkwardly and breaks EIG voice. Keep the label as a modifier. -> "the evidence-central estimate" / "we lead with the evidence-central estimate."
- `SUGGESTION` Line 6 (lede) is a single ~65-word sentence carrying three quantities plus a nested parenthetical. It satisfies the one-sentence-lede rule technically but strains Smart Brevity ("one complete thought, no throat-clearing"). Consider tightening the parenthetical floor aside into the "Why it matters" or a following sentence.
- `SUGGESTION` "headline" as a verb (Lines 148, 239) is informal; acceptable in blog voice but flagged for consistency with the appendix, which uses it too.

## Smart Brevity And Structure

- No errors. One-sentence lede present (Line 6); "**Why it matters:**" framing present and early (Line 8); bulleted lists bold their first phrase (Lines 115–118, 238–241); "**The bottom line:**" close (Line 261).

## Figure Labels And Source Lines

- `ERROR` Table 3 source line (Line 101) and Table 4 source line (Line 146) read `Source: EIG 80-80 wage subsidy simulation, 2026.` while Table 1 (Line 39) and Table 2 (Line 82) read `Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.` The figure-style source-line rule requires the organization name spelled out in full in the source line ("Economic Innovation Group" is three words). This is also elegant variation of the source attribution. -> standardize all four to "Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026."
- `SUGGESTION` Every embedded PNG bakes its own "Figure N." title into the image (e.g., `05c_core_figures.R` sets `title = "Figure 5. Average annual subsidy per eligible worker by state."`), and the draft repeats the identical "**Figure N.**" caption in the markdown body (e.g., Line 109). This double-labels the figure number. Per figure-style §3 ("Many EIG figures include the title in the surrounding document text rather than in the figure itself — confirm with the layout designer"), pick one home for the "Figure N." title. Recommendation for a web/blog embed: keep the caption in the document text and drop the baked-in title (or vice versa), consistently.
- `SUGGESTION` Draft figure captions end with a period (e.g., Line 12); the figure-style examples do not. Not a violation, but confirm the house convention and apply it uniformly (all figure captions here are consistent, so this is cosmetic).

## Citations

- `ERROR` Footnotes 6, 7, and 8 (Lines 270–272) format journal articles in Chicago "Volume, no. Issue (Year): pages" style with the year in parentheses and a colon before the page range — e.g., `*American Economic Review* 103, no. 5 (2013): 1797–1829`. EIG format is `Journal, Volume (Issue), Year, pages.` with no parentheses around the year and a comma (not a colon) before pages, and a comma after the journal name (citation-style §1–2). -> `*American Economic Review*, 103 (5), 2013, 1797–1829.`; apply the same fix to Grogger `85, no. 2 (2003): 394–408` → `85 (2), 2003, 394–408.`; Schmieder et al. `106, no. 3 (2016): 739–777` → `106 (3), 2016, 739–777.`; Krueger and Mueller `8, no. 1 (2016): 142–179` → `8 (1), 2016, 142–179.`
- `ERROR` (`[TO VERIFY]` placeholders — must resolve before publication) Footnotes 1, 3, 4, and 5 (Lines 265, 267, 268, 269) carry unresolved `[TO VERIFY]` items:
  - `[^1]` — missing the required publication year/date and URL. The EIG format requires the year after the author names; this citation has none. Resolve date + URL and hyperlink the title.
  - `[^3]` — `[TO VERIFY: publication month]` for the SRDC report.
  - `[^4]` — `[TO VERIFY: NYC publication month]` for the MDRC NYC report.
  - `[^5]` — is a placeholder, not a citation: "as cited in the first post (NBER, American Economic Association, and Peterson Institute…) [TO VERIFY: carry over the exact citations…]." A published brief needs the actual per-job-cost citations, not a pointer.
  (The internal Evidence block, Line 292, already acknowledges these are open citation details; this finding is the actionable list.)
- `SUGGESTION` URLs are presented as bare URLs in footnotes 3, 4, 6, 7, and 8 rather than hyperlinked to the title. Citation-style §1 asks that the title be the hyperlinked text where the work is online. In this markdown draft, wrap the title in a link: `["Article Title"](URL)`.
- `SUGGESTION` Access-date inconsistency: footnotes 3 and 4 use "accessed July 8, 2026"; footnotes 6 and 7 use "accessed July 9, 2026." Reconcile to a single access date (or confirm the dates genuinely differ).
- `SUGGESTION` Simulation-name capitalization drifts between the footnote and the source lines: `[^2]` (Line 266) writes "80-80 Wage Subsidy Simulation" (title case) while table source lines write "80-80 wage subsidy simulation" (lowercase). Pick one form.

---

# Draft B — Technical appendix (`2026-07-09_technical-appendix.md`)

## Numbers And Percentages

- `ERROR` Line 69 ("roughly **three percent** are disabled or retired"): number before "percent" must be a numeral. -> "roughly **3 percent**."
- `ERROR` Line 81 ("a **one percent** rise in the net return raises… by eps percent"): -> "a **1 percent** rise…" ("eps percent" is a variable placeholder and is fine.)
- `ERROR` Line 97 ("and under **one percent** when the worker's bargaining share is high"): -> "under **1 percent**."

## Punctuation

- `ERROR` Line 126 ("SRDC **—** the Canadian Self-Sufficiency Project… MDRC **—** Paycheck Plus…"): spaced em dashes. EIG em dashes take no surrounding spaces. -> "SRDC—the Canadian Self-Sufficiency Project… MDRC—Paycheck Plus…" (four occurrences on this line).

## Capitalization

- No errors. Section headers and the digital-style title reference are consistent.

## Spelling And Word Form

- No errors. No contractions. "PolicyEngine-US" (Line 21) is a product name, compliant.

## Voice And Style

- `SUGGESTION` "**evidence-central**" used as a bare noun (Line 57: "We headline the evidence-central rather than the floor"). Same awkwardness as Draft A. -> "the evidence-central estimate."
- `SUGGESTION` Heavy use of bold inline lead-ins ("**The wage model.**", "**Offers are distributions, not points.**", etc.) is on-brand for an appendix, but several run-in paragraphs exceed the 2–4 sentence blog target. Acceptable for a technical appendix; flagged only for awareness.

## Smart Brevity And Structure

- No errors for the appendix format (it is not a Smart Brevity artifact; the one-sentence-lede / "Why it matters" rules do not apply to a methods appendix).

## Figure Labels And Source Lines

- Not applicable — the appendix embeds no figures of its own; it cross-references the main piece's figures (e.g., Line 65, Line 99). No source-line issues.

## Citations

- `ERROR` (structural, self-disclosed) The entire appendix uses author-date, parenthetical in-text citations — e.g., "(Krueger and Mueller 2016)" (Line 38), "(Heckman 1979)" (Line 49), "(Maestas, Mullen, and Strand 2013)" (Line 40), "(Schmieder, von Wachter, and Bender 2016)" (Line 57). EIG publications use footnotes and do **not** put author names or years in parentheses in running text (citation-style §1, §3). The draft acknowledges this at Line 144 ("Citation formatting is author-date prose style; convert to EIG footnote format at publication if this appendix ships publicly"). Action: if the appendix is published, convert every parenthetical author-date reference to an EIG footnote; if it stays internal, no change.
- `ERROR` "Key sources" list (Lines 124–136) parenthesizes years throughout — e.g., "Card and Hyslop (2005), *Econometrica*", "Miller et al. (2018), MDRC". EIG forbids parentheses around the year and these are not full citations (no titles, no full publication data). -> either convert to full EIG-format footnote citations, or clearly retain as an internal shorthand index that is stripped/replaced before publication.
- `SUGGESTION` `et al.` usage is correct where present (e.g., "Michalopoulos et al.", "Miller et al." — 4+ authors). No change; confirmed compliant.
- `SUGGESTION` The "Evidence (internal, strip before publication)" block (Lines 140–144) contains `%` and shorthand notation; this is fine as internal-strip content, but ensure it is removed before any public release.

---

## Summary

- Errors: 12
  - Draft A: 6 (three number/percent-and-million, one table source-line, one citation-format for footnotes 6–8, one `[TO VERIFY]` placeholder cluster covering footnotes 1/3/4/5).
  - Draft B: 6 (three number/percent, one spaced-em-dash, two citation-family: author-date in-text + "Key sources" parenthesized years).
- Suggestions: 13 (footnote-marker placement, bare-URL hyperlinking, access-date/name-capitalization consistency, "evidence-central" as a bare noun in both drafts, lede tightening, double figure-number labeling, and internal-strip-block cleanups).
- Overall assessment: The re-centered drafts are largely EIG-compliant in voice, structure, and figure branding (the R figure suite is theme/token-driven and correctly stamps the canonical source line). The load-bearing fixes are (1) spelled-out numbers before "percent" and before "million" that must become numerals, (2) the four table/figure source lines and the footnote 6–8 journal citations that must adopt EIG citation format (no parenthesized years, org name spelled out), and (3) resolving the `[TO VERIFY]` footnote placeholders before publication. The appendix's biggest citation task is the acknowledged, one-time conversion from author-date prose to EIG footnotes if it ships publicly.
