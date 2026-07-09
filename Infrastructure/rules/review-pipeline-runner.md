# Review Pipeline Runner (shared procedure)

This is the single source of truth for the **pipeline-detection-and-run** step shared by the pipeline-gated review commands: `/review-code`, `/review-methodology`, `/review-numbers`, `/review-consistency`, and `/full-review`. Each of those command playbooks references this procedure instead of restating it. (`/review-ai` and `/review-style` do **not** run the pipeline and do not use this procedure.)

When a command says "run the shared pipeline-detection procedure," perform exactly the steps below, substituting `<review-type>` with that command's review name (e.g., "code review", "methodology review", "number verification review", "document–code consistency review", "full review").

---

## Detect and run the pipeline

Search for a runall script at the **top level** of `target_dir` only (not recursively). Match these filenames exactly (case-insensitive), in priority order:

| Priority | Filename(s) | Interpreter |
|----------|-------------|-------------|
| 1 | `runall.sh`, `run_all.sh` | `bash <script>` |
| 2 | `runall.do`, `run_all.do` | `stata -b do <script>` |
| 3 | `runall.R`, `run_all.R` | `Rscript <script>` |
| 4 | `runall.py`, `run_all.py` | `python <script>` |

If no matching file is found, stop and respond:

> No runall script found in `<target_dir>`. Expected one of:
> `runall.sh`, `run_all.sh`, `runall.do`, `run_all.do`, `runall.R`, `run_all.R`, `runall.py`, `run_all.py`
>
> Add a runall script and try again.

**Stop.**

Tell the user which script was found and is being executed:

> Found `<script_name>`. Running pipeline…

Execute the script using its interpreter, with `target_dir` as the working directory. Capture stdout and stderr.

**If the script exits with a non-zero exit code:**

> Pipeline failed (exit code N).
>
> ```
> [last 50 lines of combined stdout/stderr]
> ```
>
> Fix the pipeline errors before running a `<review-type>`.

**Stop. Do not proceed to the review.** (For `/full-review`, additionally: **do not spawn any sub-agents.**)

If the script succeeds (exit code 0):

> Pipeline completed successfully.
