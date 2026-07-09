# Orchestration Plan — Dynamic Cost Modeling & Behavioral Responses

Status: APPROVED (depth + scope confirmed by user 2026-06-25)

## Objective

Open a new analytical angle for the 80-80 Rule wage subsidy: dynamic cost modeling that
incorporates behavioral responses (labor supply entry and hours changes). Begin with a
thorough literature scout covering (A) extensive- and intensive-margin labor-supply
elasticity estimates relevant to a wage subsidy, and (B) the dynamic/behavioral cost-modeling
literature for comparable transfer programs (EITC, CTC, NIT, active labor-supply policies).

## Workstreams

| Workstream | Route (Agent/Command) | Dependency | Status |
|---|---|---|---|
| W1. Literature scout — elasticities + dynamic cost modeling | `literature-scout` (thorough sweep) | none (runs upstream of analysis) | In progress |
| W2. Methodology design — integrate elasticities into gross/net cost model | `methodology-reviewer` + planning | W1 research gap | Blocked by W1 |
| W3. Implementation — dynamic cost layer in pipeline | code (Python, `code/`) + `/review-code` | W2 approved design | Blocked by W2 |
| W4. Numerical verification of dynamic estimates | `/review-numbers` | W3 + pipeline success | Blocked by W3 |

## Execution Waves

1. **Wave 1 (now):** W1 literature scout — single comprehensive agent. Two-part scope:
   - Thread A: extensive (participation) + intensive (hours) elasticities — Saez, Chetty,
     Hoynes, Eissa, Meyer, Rothstein, Blundell, Keane; CBO labor-supply elasticity review;
     EITC, CTC, NIT experiments.
   - Thread B: dynamic cost / behavioral fiscal scoring — CBO/JCT dynamic scoring; MVPF
     (Hendren & Sprung-Keyser); EITC incidence / wage pass-through (Rothstein); ALMP and
     employment-subsidy evidence (Card/Kluve/Weber meta-analyses).
   - Four confirmed cost-model angles: elasticity→revenue feedback; MVPF/welfare; incidence
     & wage pass-through; ALMP/employment-program evidence.
2. **Wave 2 (after W1):** Translate the research gap into a methodology design for layering
   behavioral responses onto the existing gross/net cost framework. Plan + spec.
3. **Wave 3 (finalization):** Implement, verify numbers, document.

## Performance/Cost Tier Notes
- Highest expected tier this wave: Tier 2-3 (thorough multi-wave snowball).
- Long-run safeguards: single scout (no parallel catalog writes); saturation-based stopping;
  all citations flagged `[unverified: ...]` where not corroborated; entries written at
  `status: parsed` only.

## Completion Criteria
- W1: tiered annotated bibliography + researcher landscape + research gap; `catalog.yaml`
  entries (parsed) validated by `validate_literature_catalog.py`; summaries saved.

## Next Action
- Run W1 scout; on return, re-plan Wave 2 from the research-gap section.
