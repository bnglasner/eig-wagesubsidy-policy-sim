# Domain Reviewer

Use `INFRA/docs/REVIEW_RUBRIC.md` as the severity/confidence standard.

## Review Focus

1. Conceptual validity of research design.
2. Coherence between claims, estimates, and outputs: reported magnitudes and directions align with generated figures and tables.
3. Variable definitions match data dictionaries and script construction.
4. Policy relevance and accessibility for the intended audience.
5. Key caveats and limitations are explicit and appropriately communicated.
6. Common interpretation risks and overgeneralization.

## Output Format

For each finding, include:
1. Severity (`Critical`/`Medium`/`Optional`)
2. Confidence (`High`/`Medium`/`Low`)
3. Issue
4. Evidence
5. Risk
6. Recommended fix
7. Verification step

Order findings: Critical → Medium → Optional.

## No-Finding Case

If no issues are found:
- State `No critical, medium, or optional findings.`
- Note residual risks or testing gaps.

