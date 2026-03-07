# /cover-sheet

Generate a filled EIG publication cover sheet from a project description.

## Usage

```
/cover-sheet [project description]
```

**Examples:**
```
/cover-sheet A research report analyzing wage growth by income quintile using CPS data from 2000â€“2023, led by Ben Glasner, targeting policymakers and journalists, planned release in Q2 2025.

/cover-sheet Policy brief on the geographic concentration of startup activity in U.S. metros. Co-authored with Kenan Institute. Target audience: venture capital community and congressional staff. National scope, 2010â€“2022 data.
```

## Instructions

When this command is invoked:

1. **Parse** $ARGUMENTS for any explicitly stated fields (author, title, audience, date, scope, data sources, partners, etc.).
2. **Infer** reasonable placeholder values for any fields not explicitly stated, marking them `[TO FILL]`.
3. **Generate** the complete EIG cover sheet as a filled markdown table, using the template from `INFRA/docs/eig-document-process.md`.
4. **Flag** any field that requires human judgment as `[TO FILL]`.

## Cover Sheet Template (from eig-document-process.md)

Output the following table, filled in as completely as possible:

```markdown
## EIG Publication Cover Sheet

| Field | Entry |
|-------|-------|
| **Document Title** | [Working title or TO FILL] |
| **Document Type** | [Inferred type or TO FILL] |
| **Primary Author(s)** | [From input or TO FILL] |
| **Assisting Researcher(s)** | [From input or TO FILL] |
| **Project Lead** | [From input or TO FILL] |
| **Date Initiated** | [Today's date or TO FILL] |
| **Target Release Date** | [From input or TO FILL] |
| **Target Audience** | [From input or inferred] |
| **Core Finding / Thesis** | [Inferred from description or TO FILL] |
| **Key Data Sources** | [From input or TO FILL] |
| **Related EIG Projects** | [TO FILL] |
| **External Partners** | [From input or None] |
| **Embargo / Release Restrictions** | [None unless stated] |
| **Geographic Scope** | [From input or TO FILL] |
| **Time Period** | [From input or TO FILL] |
| **Planned Outputs** | [Inferred: main report PDF, press release, blog post â€” adjust as needed] |
| **Communications Lead** | [TO FILL] |
| **Legal / Compliance Review Needed?** | [No unless indicated] |
| **Current Status** | Pre-draft |
| **Notes** | [Any caveats or dependencies from the input] |
```

## After the Cover Sheet

Also output:

### Pre-Draft Questions
List any pre-draft questions from `INFRA/docs/eig-document-process.md` that are unanswered based on the input â€” so the project lead knows what still needs to be resolved before drafting begins.

### Next Steps
A brief 3â€“5 bullet checklist of immediate next steps based on the cover sheet status:
- Fill in [TO FILL] fields
- Confirm data availability
- Confirm review chain participants
- Set milestone dates
- etc.

