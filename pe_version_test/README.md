# PolicyEngine Version Comparison Test

## What this tests

**Question 1:** Does passing `hourly_wage` into a PolicyEngine situation dict change any tax/benefit outputs?
- If yes: we can pass workers' actual hourly rates into pre-computed schedules for better accuracy.
- If no: the new variable is currently a data-only stub with no downstream formulas (expected for now).

**Question 2:** How much did 40 versions of PE changes (1.592.4 → 1.632.2) affect the schedules?
- Checks EITC, SNAP, Medicaid/CHIP, ACA PTC, CTC, SSI, TANF, federal/state/payroll taxes, net income.
- Flags any variable with a max deviation > $1,000 at any income point.

## How to run

```bash
cd pe_version_test/
./run_comparison.sh
```

That's it. The script will:
1. Create two Python 3.12 venvs (`.venv_pe_old`, `.venv_pe_new`) — ~150 MB each
2. Install policyengine-us 1.592.4 and 1.632.2 respectively
3. Run 131 income points × 3 combos × 2 hourly_wage modes in each version (~5–10 min)
4. Print a comparison report

## Test combos

| Key | State | Family |
|---|---|---|
| `single_0c_TX` | Texas | Single adult, no children |
| `single_2c_CA` | California | Single adult, 2 children (ages 8, 3) |
| `married_2c_NY` | New York | Married couple, 2 children (ages 8, 3) |

These three span the main sources of variation: state tax rules, benefit generosity,
and family-size-driven program interactions (EITC phase-out, CTC, CCDF, school meals).

## Output

Results are saved as JSON in `results/`:
- `pe_results_1.592.4.json`
- `pe_results_1.632.2.json`

The diff report prints directly to stdout. Large deviations (> $1,000) are flagged with `◄ LARGE`.

## Re-running a single version

```bash
# Just the old version
RESULTS_DIR=./results .venv_pe_old/bin/python pe_compare.py --mode single

# Just the new version
RESULTS_DIR=./results .venv_pe_new/bin/python pe_compare.py --mode diff
```
