# /cite

Format a citation in EIG style from natural-language source information.

## Usage

```
/cite [natural-language description of source]
```

**Examples:**
```
/cite David Autor, David Dorn, and Gordon Hanson, The China Syndrome, American Economic Review, vol 103 issue 6, 2013, pages 2121-2168, doi 10.1257/aer.103.6.2121

/cite Economic Innovation Group, press release, EIG Releases New Distressed Communities Index, February 7 2023, https://eig.org/news/...

/cite Anne Case and Angus Deaton, Deaths of Despair and the Future of Capitalism, Princeton University Press, 2020

/cite webpage: John Lettieri, The Geography of Opportunity, Economic Innovation Group, March 14 2022, https://eig.org/geography (accessed February 1 2024)
```

## Instructions

When this command is invoked:

1. **Parse** $ARGUMENTS for the following fields:
   - Authors (last name, first name; or organization name)
   - Title (article/post vs. book/report â€” infer from context)
   - Publication/Journal/Website name (if applicable)
   - Volume, issue, page range (for journal articles)
   - Organization (for reports, press releases)
   - Year (and month/day if available)
   - URL (if provided)
   - Date of access (for webpages, if provided)

2. **Determine the source type** from context clues:
   - Journal/volume/issue â†’ Article
   - "press release" â†’ Press Release
   - "book" / publisher name â†’ Book
   - "report" / "working paper" â†’ Report
   - URL + date accessed â†’ Webpage
   - "podcast" / "episode" â†’ Podcast
   - Law/statute â†’ Law

3. **Format** using the correct EIG citation template from `INFRA/docs/eig-citation-style.md`.

4. **Output:**
   - The formatted citation
   - The source type identified
   - Any missing fields that would be needed for a complete citation (flagged as [MISSING])

## Citation Templates (Quick Reference)

**Article:** `Last, First, "Title," Journal, Vol (Issue), Year, pages. URL.`
**Webpage:** `Last, First, "Title," Site, Month Day, Year. URL (accessed Month Day, Year).`
**Report:** `Last, First, Report Title, Organization, Month Year. URL.`
**Book:** `Last, First, Book Title, Publisher, Year.`
**Press release:** `Organization, "Title," Month Day, Year. URL.`

## EIG Citation Rules (Apply Always)

- End with a period
- No parentheses around the year
- Article/post titles in quotation marks; book/report titles italicized (use *asterisks* in markdown)
- Hyperlink the title in digital documents (note this requirement if URL is provided)
- Four or more authors: first author + "et al."
- Webpage: always include "accessed [date]" if provided
- No "Retrieved from" language

## Output Example

```
**Formatted citation:**
Autor, David, David Dorn, and Gordon Hanson, "The China Syndrome: Local Labor Market Effects of Import Competition in the United States," *American Economic Review*, 103 (6), 2013, 2121â€“2168. https://doi.org/10.1257/aer.103.6.2121.

**Source type:** Journal article
**Missing fields:** None
```

