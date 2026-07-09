# Skill: /review-numbers

Runs the document number verification review. Executes the RA's pipeline, discovers all source and document files in the target project, spawns the `data-consistency-reviewer` sub-agent, and writes `doc-number-report.html` to the `review-reports/` subdirectory of the target directory.

---

## Trigger

User runs `/review-numbers <target_dir>` or `/review-numbers <target_dir> <document_path>`

Examples:
- `/review-numbers ~/ra-project`
- `/review-numbers ~/ra-project ~/ra-project/paper/manuscript.tex`

---

## Execution Steps

### Step 1 — Parse arguments

Extract `target_dir` from the first argument. Expand `~` to the full home directory path.

If no argument is provided, stop and respond:

> Usage: `/review-numbers <path-to-project> [path-to-document]`
> Example: `/review-numbers ~/ra-project`
> Example: `/review-numbers ~/ra-project ~/ra-project/paper/manuscript.tex`

Verify that `target_dir` exists and is a directory. If not:

> `<target_dir>` does not exist or is not a directory. Check the path and try again.

**Stop.**

If a second argument is provided, treat it as the document path. Verify the file exists. If not:

> `<document_path>` does not exist. Check the path and try again.

**Stop.**

### Step 2 — Detect and run the pipeline

Run the shared pipeline-detection procedure in `.codex/rules/review-pipeline-runner.md`, substituting `<review-type>` = "number verification review".

If the pipeline fails, **stop and do not proceed to the review.** If it succeeds ("Pipeline completed successfully."), continue to Step 3.

### Step 3 — Discover source code files

Recursively find all files matching these extensions inside `target_dir`:
- `*.py`
- `*.R`
- `*.Rmd`
- `*.qmd`
- `*.do`
- `*.ado`

Exclude files under `.git/`.

Collect the full absolute path of each discovered file.

### Step 4 — Discover or confirm document files

**If a document path was provided in Step 1:** use that file as the document to review.

**If no document path was provided:** search for document files in `target_dir` (recursively). Match these extensions:
- `*.tex`
- `*.md` (excluding files named `README.md`, `CHANGELOG.md`, `LICENSE.md`, and any files inside `.claude/` or `.codex/`)
- `*.qmd`
- `*.Rmd`
- `*.pdf` (excluding `doc-number-report.pdf`, `doc-consistency-report.pdf`)

Exclude files under `.git/`, `.claude/`, and `.codex/`.

Also exclude the `review-reports/` directory.

If zero document files are found, stop and respond:

> No document files found in `<target_dir>`. Expected `.tex`, `.md`, `.qmd`, `.Rmd`, or `.pdf` files.
>
> Specify the document path explicitly: `/review-numbers <target_dir> <document_path>`

**Stop.**

If one document file is found, use it automatically.

If multiple document files are found, list them and ask the user to select:

> Found multiple document files in `<target_dir>`:
>
> 1. `path/to/manuscript.tex`
> 2. `path/to/appendix.tex`
> 3. `path/to/paper.qmd`
>
> Which document(s) should I review? (Enter numbers separated by commas, or "all")

Wait for the user's response.

### Step 5 — Report discovery

List the discovered files:

> **Document(s) to verify:** `manuscript.tex` (and any others selected)
>
> Found **N** source code files in `<target_dir>`:
>
> **Python (n):** `path/to/file.py`, …
> **R (n):** `path/to/file.R`, …
> **Stata (n):** `path/to/file.do`, …
>
> Proceeding with number verification review.

### Step 6 — Create output directory

Create the output directory `<target_dir>/review-reports/` if it does not already exist:

```
mkdir -p <target_dir>/review-reports
```

### Step 7 — Spawn the data-consistency-reviewer sub-agent

Spawn the `data-consistency-reviewer` sub-agent with the following context:

```
Agent: data-consistency-reviewer
Target directory: <target_dir>
Document files: [list of document file paths]
Code files to review: [full list of source code file paths]
Rules: .codex/rules/doc-number-rules.md
Template: .codex/templates/doc-number-report.md
Output: <target_dir>/review-reports/doc-number-report.html
```

The sub-agent will read the document(s) and code, extract numbers, trace and verify them, and write the HTML report into `<target_dir>/review-reports/`.

### Step 8 — Wait and monitor

Wait for the sub-agent to complete. If the sub-agent reports an error (file unreadable, template missing, write failure), surface the error to the user with the specific message.

### Step 9 — Confirm output and summarize

Verify that `<target_dir>/review-reports/doc-number-report.html` exists and is non-empty.

Report to the user:

> Number verification review complete. Report written to `<target_dir>/review-reports/doc-number-report.html`.
>
> **Summary:** N numbers extracted — X verified, X flagged
> **Findings:** X CRITICAL, X HIGH, X MEDIUM, X LOW, X INFO

If CRITICAL or HIGH findings are present, add:

> ⚑ **Attention:** [X] CRITICAL and [X] HIGH severity number mismatches were found. Review these before submission — the document may contain incorrect statistics.

If no findings:

> All N numbers verified successfully. No mismatches found.
