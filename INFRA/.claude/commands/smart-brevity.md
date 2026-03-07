# /smart-brevity

Rewrite a passage using the Smart Brevity six-step framework for maximum clarity and impact.

## Usage

```
/smart-brevity [passage to rewrite]
```

**Examples:**
```
/smart-brevity "In recent years, there has been growing interest among policymakers, researchers, and the business community in understanding the nature of geographic inequality across the United States, particularly as it relates to economic opportunity and the diverging fortunes of different communities."

/smart-brevity [paste any paragraph or section]
```

## Instructions

When this command is invoked:

1. **Read** $ARGUMENTS as the input passage.
2. **Identify** the core finding or news angle buried in the passage.
3. **Apply** all six Smart Brevity steps (see below).
4. **Output** the rewritten passage in the structure below.
5. **Annotate** each change with a brief note explaining why.

## Smart Brevity Six-Step Framework

### Step 1: Lead with what's new or most important
- Ask: What would the audience most want to know?
- Put that first. Cut any buildup or context that precedes the key point.

### Step 2: Write a one-sentence lede
- The opening sentence must be a single, complete thought.
- No "In recent years," "Historically," or "Researchers have long known…"
- No compound sentences in the lede.

### Step 3: State "Why it matters"
- The second element must explicitly tell the reader why this matters to them.
- Use language like: "Why it matters: …" or "The bottom line: …" or "This means…"

### Step 4: Use bullets, not paragraphs, for lists
- Any list of three or more items becomes bulleted.
- Each bullet is a complete thought.
- **Bold the first phrase** of each bullet to aid skimming.

### Step 5: Cut ruthlessly
- Delete every sentence that merely restates something already said.
- Delete filler phrases: "It is important to note that…," "As mentioned above…," "In conclusion…"
- Delete hedges unless they reflect genuine uncertainty: "somewhat," "relatively," "in some ways."

### Step 6: Strong verbs, active voice
- Replace weak nominalizations with strong verbs: "The decline of wages" → "Wages declined."
- Eliminate passive voice where active is possible.
- Replace "went up/down" with specific verbs: surged, contracted, outpaced, lagged, concentrated.

## Output Format

```
## Smart Brevity Rewrite

**Original:**
[The original passage]

**Rewritten:**

**[Suggested headline — ≤10 words, sentence case]**

[One-sentence lede.]

**Why it matters:** [One sentence on significance.]

[Body — short paragraphs (2–3 sentences max) or bullets as appropriate]

- **[Bold first phrase.]** Supporting detail.
- **[Bold first phrase.]** Supporting detail.

---

**Changes made:**
- [Specific change 1 and reason]
- [Specific change 2 and reason]
- ...

**Word count:** [Original] → [Rewritten]
```

## EIG-Specific Rules (Apply in Addition to Smart Brevity)

- "Percent" in body text (not %)
- Numbers one through nine spelled out; 10+ as numerals
- Oxford comma in all lists
- No contractions
- COVID-19 (not Covid-19 or COVID19)
- One word per concept — no elegant variation
- "data are" (plural)
