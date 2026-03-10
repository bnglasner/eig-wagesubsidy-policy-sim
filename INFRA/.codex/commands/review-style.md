# /review-style

Audit a document or passage against all EIG writing, citation, and style rules. Returns a structured list of errors and suggestions with corrections.

## Usage

```
/review-style [file path or pasted text]
```

**Examples:**
```
/review-style drafts/chapter1.md
/review-style "Workers in the US saw wages rise 4% last year, but homeownership rates didn't keep pace."
```

## Instructions

When this command is invoked, act as the **eig-reviewer** agent (see `INFRA/.claude/agents/eig-reviewer.md`).

1. **If $ARGUMENTS is a file path:** Read the file at that path.
2. **If $ARGUMENTS is pasted text:** Use that text directly as the input.
3. Apply every rule in the EIG Reviewer Agent checklist (numbers, punctuation, capitalization, spelling, voice, Smart Brevity, figures, citations).
4. Return the full structured review report in the format specified in the eig-reviewer agent file.

## Output Format

```
## EIG Style Review: [Document or excerpt description]

### Numbers & Percentages
- [ERROR/SUGGESTION] [Location]: [Issue] â†’ [Correction]

### Punctuation
...

### Summary
[X] errors, [Y] suggestions.
```

Include corrected text for every ERROR. For SUGGESTIONs, provide the improved version as well where a clear improvement exists.

## Notes

- If the input is very long (>2,000 words), review the first 500 words thoroughly and summarize patterns observed in the rest.
- Always review figure captions and source lines if any figures are described or embedded.
- Always review all citations if any footnotes or endnotes are present.

