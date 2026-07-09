# EIG Style Docs Index

## Purpose

Central index for EIG style guidance used by researchers and AI agents.

## Visual Style Core (read in order)

1. Design specification: `agent-01-design-spec.md`
2. R implementation: `agent-02-r-implementation.md`
3. Stata implementation: `agent-03-stata-implementation.md`
4. Python implementation: `agent-04-python-implementation.md`
5. Legacy palette policy: `eig-legacy-palette-policy.md`
6. Design signoff checklist: `eig-design-signoff-checklist.md`

## Graphical Quality Layer (design excellence)

Applied by the `eig-tufte-critique` skill and Pass 2 of `eig-style-review`. Complements —
does not replace — brand compliance.

1. Tufte principles: `tufte-principles.md` (data-ink, lie factor, chartjunk, small multiples, density)
2. Analytical design: `tufte-analytical-design.md` (six principles, sparklines, layering, range-frames, causality)

## Editorial And Publication Style

- Writing style: `eig-writing-style.md`
- Citation style: `eig-citation-style.md`
- Document process: `eig-document-process.md`
- Brand guidelines: `eig-brand-guidelines.md`
- Figure standards: `eig-figure-style.md`

## Datawrapper Workflow Docs

1. Integration contract: `datawrapper-integration.md`
2. Downstream adoption checklist: `datawrapper-downstream-adoption-checklist.md`
3. CI template: `ci/datawrapper-compliance.workflow.template.yml`
4. Root handoff entrypoint: `../DATAWRAPPER_PIPELINE_AGENT_HANDOFF.md`

## Validation Commands

```bash
python3 Infrastructure/style/scripts/compliance/check_datawrapper_manifest.py <manifest_path>
python3 Infrastructure/style/scripts/compliance/check_legacy_metadata.py <metadata_json_path>
```

## Related Canonical AI Files

- Agents: `Infrastructure/agents/eig-style-guide-agent.md` (figure-code production plus token-style audit, including Datawrapper), `Infrastructure/agents/eig-reviewer.md`, `Infrastructure/agents/eig-writer.md`
- Skills: `Infrastructure/style/skills/eig-style-apply.md`, `eig-style-review.md`, `eig-style-datawrapper.md`, `eig-tufte-critique.md` (graphical-quality ideation and critique)
- Commands: `Infrastructure/commands/review-style.md`, `Infrastructure/commands/cite.md`, `Infrastructure/commands/cover-sheet.md`, `Infrastructure/commands/smart-brevity.md`
- Rules: `Infrastructure/rules/style-writing-rules.md`, `Infrastructure/rules/style-citation-rules.md`, `Infrastructure/rules/style-figure-rules.md`, `Infrastructure/rules/style-datawrapper-rules.md`
- Templates: `Infrastructure/templates/style-review-report.md`, `Infrastructure/templates/style-cover-sheet.md`, `Infrastructure/templates/style-citation-output.md`, `Infrastructure/templates/smart-brevity-output.md`
