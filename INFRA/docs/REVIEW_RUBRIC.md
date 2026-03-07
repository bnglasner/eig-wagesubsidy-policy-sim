# Review Rubric (Shared Standard)

Use this rubric for all substantive review outputs across Claude and Codex.

## Severity Levels (3)

### Critical

- Definition: likely to cause materially incorrect conclusions, invalid policy interpretation, or reproducibility failure.
- Typical examples: claim/result mismatch, wrong variable construction in main outcome, invalid identification logic, broken/undocumented core pipeline assumptions.
- Expected action: must fix before merge/publication.

### Medium

- Definition: meaningful quality issue that does not invalidate the core conclusion but could mislead, reduce trust, or weaken reproducibility.
- Typical examples: missing caveat, ambiguous specification choice, inconsistent labeling, incomplete robustness evidence.
- Expected action: should fix before final release.

### Optional

- Definition: improvement that increases clarity, maintainability, or presentation quality without changing core validity.
- Typical examples: wording clarity, additional visualization, cleaner code organization, non-blocking documentation improvements.
- Expected action: nice to have.

## Confidence Bands

- `High`: strong direct evidence from `WORKSPACE/code/` and `WORKSPACE/output/` artifacts.
- `Medium`: evidence is plausible but partially inferential.
- `Low`: weak evidence; flag as tentative and ask for validation.

## Required Finding Fields

Each finding should include:

1. Severity (`Critical`, `Medium`, `Optional`)
2. Confidence (`High`, `Medium`, `Low`)
3. Issue (what is wrong)
4. Evidence (where and how it appears)
5. Risk (impact if unresolved)
6. Recommended fix (specific and feasible)
7. Verification step (how to confirm resolution)

## Ordering Rule

- Present findings in this order: `Critical` -> `Medium` -> `Optional`.
- Within each severity, sort by risk and confidence strength.

## No-Finding Case

If no issues are found:

- State explicitly: `No critical, medium, or optional findings.`
- Note residual risks or testing gaps, if any.



