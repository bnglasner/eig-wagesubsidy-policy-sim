# Skill: /review-code

Runs the code error review only. Executes the RA's pipeline, discovers all source files in the target project, spawns the `code-reviewer` sub-agent, and writes `code-error-report.html` to the `review-reports/` subdirectory of the target directory.

---

## Trigger

User runs `/review-code <target_dir>`

Example: `/review-code ~/ra-project`

---

## Execution Steps

### Step 1 — Parse target directory

Extract `target_dir` from the command argument. Expand `~` to the full home directory path.

If no argument is provided, stop and respond:

> Usage: `/review-code <path-to-project>`
> Example: `/review-code ~/ra-project`

Verify that `target_dir` exists and is a directory. If not:

> `<target_dir>` does not exist or is not a directory. Check the path and try again.

**Stop.**

### Step 2 — Detect and run the pipeline

Run the shared pipeline-detection procedure in `.codex/rules/review-pipeline-runner.md`, substituting `<review-type>` = "code review".

If the pipeline fails, **stop and do not proceed to the review.** If it succeeds ("Pipeline completed successfully."), continue to Step 3.

### Step 3 — Discover files

Recursively find all files matching these extensions inside `target_dir`:
- `*.py`
- `*.R`
- `*.Rmd`
- `*.qmd`
- `*.do`
- `*.ado`

Exclude files under these subdirectories (relative to `target_dir`):
- `.git/`

Collect the full absolute path of each discovered file.

If zero files are found, stop and respond:

> No reviewable source files found in `<target_dir>`. Expected `.py`, `.R`, `.Rmd`, `.qmd`, `.do`, or `.ado` files.

### Step 4 — Report discovery

List the discovered files, grouped by language:

> Found **N** files to review in `<target_dir>`:
>
> **Python (n):** `path/to/file.py`, …
> **R (n):** `path/to/file.R`, …
> **Stata (n):** `path/to/file.do`, …
>
> Proceeding with code error review.

### Step 5 — Create output directory

Create the output directory `<target_dir>/review-reports/` if it does not already exist:

```
mkdir -p <target_dir>/review-reports
```

### Step 6 — Spawn the code-reviewer sub-agent

Spawn the `code-reviewer` sub-agent with the following context:

```
Agent: code-reviewer
Target directory: <target_dir>
Files to review: [full list of absolute file paths]
Rules: .codex/rules/code-quality-rules.md
Template: .codex/templates/code-error-report.md
Output: <target_dir>/review-reports/code-error-report.html
```

The sub-agent will read each file, apply the checklists, and write the HTML report into `<target_dir>/review-reports/`.

### Step 7 — Wait and monitor

Wait for the sub-agent to complete. If the sub-agent reports an error (file unreadable, template missing, write failure), surface the error to the user with the specific message.

### Step 8 — Confirm output and summarize

Verify that `<target_dir>/review-reports/code-error-report.html` exists and is non-empty.

Report to the user:

> Code review complete. Report written to `<target_dir>/review-reports/code-error-report.html`.
>
> **Summary:** N findings — X CRITICAL, X HIGH, X MEDIUM, X LOW, X INFO

If CRITICAL or HIGH findings are present, add:

> ⚑ **Attention:** [X] CRITICAL and [X] HIGH severity errors were found. Review these before running the analysis.

If no findings:

> No definitive code errors found across all N files.
