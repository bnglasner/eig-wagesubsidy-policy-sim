#!/usr/bin/env python3
"""Validate the canonical dataset registry structure and entry metadata.

The dataset registry (Infrastructure/references/datasets/registry.yaml) is the
single source of truth consumed by methodology-reviewer (weights + pitfalls),
code-reviewer (data currency), ai-skeptic (variable-name fabrication), and the
data-dictionary-agent (which appends project-layer variable documentation).

This validator enforces the schema and the two-layer governance model:

  - layer `template`  -> curated, reusable knowledge; verification MUST be `verified`.
  - layer `project`   -> agent-acquired, vintage-pinned docs; verification MUST be `parsed`.

Per-variable entries carry their own `verification` (default `parsed`) so a
project may append `parsed` variables under a `verified` template dataset
without downgrading the dataset's curated metadata.

Loader mirrors validate_literature_catalog.py: try PyYAML, fall back to Ruby.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

DATASET_REQUIRED_FIELDS = {"id", "name", "layer", "verification"}
ALLOWED_LAYERS = {"template", "project"}
ALLOWED_VERIFICATION = {"verified", "parsed"}
ALLOWED_KINDS = {"survey", "administrative", "aggregate"}
ALLOWED_SEVERITY = {"HIGH", "MEDIUM", "LOW"}
# Per-variable required fields. Vintage and source are mandatory because the
# registry's value over a plain codebook is that every documented variable is
# pinned to the vintage it describes and to an authoritative source. An
# unconfirmed value is recorded as a "[unverified: ...]" string, not omitted.
VARIABLE_REQUIRED_FIELDS = {"name", "vintage", "source"}


def _load_with_pyyaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is not installed") from exc

    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_with_ruby(path: Path) -> Any:
    cmd = [
        "ruby",
        "-rjson",
        "-ryaml",
        "-rdate",
        "-e",
        (
            "data = YAML.safe_load("
            "File.read(ARGV[0]), permitted_classes: [Date, Time], aliases: true"
            "); puts JSON.generate(data)"
        ),
        str(path),
    ]
    try:
        output = subprocess.check_output(cmd, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Ruby is not available") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Ruby YAML parse failed: {exc}") from exc
    return json.loads(output)


def load_registry(path: Path) -> Any:
    try:
        return _load_with_pyyaml(path)
    except RuntimeError:
        try:
            return _load_with_ruby(path)
        except RuntimeError as exc:
            raise RuntimeError(
                "Unable to parse YAML registry. Install PyYAML (`pip install pyyaml`) "
                "or run with Ruby available."
            ) from exc


def is_iso_date(value: Any) -> bool:
    if isinstance(value, dt.date):
        return True
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _is_unverified(value: Any) -> bool:
    """A '[unverified: ...]' marker satisfies presence requirements."""
    return isinstance(value, str) and value.strip().lower().startswith("[unverified")


def validate_weights(label: str, weights: Any, errors: list[str]) -> None:
    if weights == "not_applicable":
        return
    if not isinstance(weights, list):
        errors.append(
            f"{label}: `weights` must be a list of weight mappings or the string "
            f"`not_applicable`."
        )
        return
    for w_index, weight in enumerate(weights, start=1):
        w_label = f"{label} weight #{w_index}"
        if not isinstance(weight, dict):
            errors.append(f"{w_label}: each weight must be a mapping.")
            continue
        if not isinstance(weight.get("context"), str) or not weight.get("context", "").strip():
            errors.append(f"{w_label}: `context` must be a non-empty string.")
        has_name = any(
            isinstance(weight.get(k), str) and weight.get(k, "").strip()
            for k in ("name", "ipums_name", "census_name")
        )
        if not has_name:
            errors.append(
                f"{w_label}: must specify at least one of `name`, `ipums_name`, "
                f"or `census_name`."
            )


def validate_pitfalls(label: str, pitfalls: Any, errors: list[str]) -> None:
    if not isinstance(pitfalls, list):
        errors.append(f"{label}: `pitfalls` must be a list (use [] if none).")
        return
    seen_ids: set[str] = set()
    for p_index, pitfall in enumerate(pitfalls, start=1):
        p_label = f"{label} pitfall #{p_index}"
        if not isinstance(pitfall, dict):
            errors.append(f"{p_label}: each pitfall must be a mapping.")
            continue
        pid = pitfall.get("id")
        if not isinstance(pid, str) or not pid.strip():
            errors.append(f"{p_label}: `id` must be a non-empty string.")
        else:
            if pid in seen_ids:
                errors.append(f"{p_label}: duplicate pitfall `id` `{pid}` within dataset.")
            seen_ids.add(pid)
        if not isinstance(pitfall.get("description"), str) or not pitfall.get("description", "").strip():
            errors.append(f"{p_label}: `description` must be a non-empty string.")
        if pitfall.get("severity") not in ALLOWED_SEVERITY:
            errors.append(
                f"{p_label}: `severity` must be one of: {', '.join(sorted(ALLOWED_SEVERITY))}."
            )


def validate_variables(label: str, variables: Any, repo_root: Path, errors: list[str]) -> None:
    if not isinstance(variables, list):
        errors.append(f"{label}: `variables` must be a list (use [] if none).")
        return
    seen_names: set[str] = set()
    for v_index, var in enumerate(variables, start=1):
        v_label = f"{label} variable #{v_index}"
        if not isinstance(var, dict):
            errors.append(f"{v_label}: each variable must be a mapping.")
            continue
        name = var.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{v_label}: `name` must be a non-empty string.")
        else:
            if name in seen_names:
                errors.append(f"{v_label}: duplicate variable `name` `{name}` within dataset.")
            seen_names.add(name)
            v_label = f"{label} variable `{name}`"
        for field in ("vintage", "source"):
            value = var.get(field)
            present = (isinstance(value, str) and value.strip()) or _is_unverified(value)
            if not present:
                errors.append(
                    f"{v_label}: `{field}` is required (use a value or an explicit "
                    f"`[unverified: ...]` marker). Project variables must be vintage-pinned "
                    f"and sourced."
                )
        verification = var.get("verification", "parsed")
        if verification not in ALLOWED_VERIFICATION:
            errors.append(
                f"{v_label}: `verification` must be one of: "
                f"{', '.join(sorted(ALLOWED_VERIFICATION))} (default `parsed`)."
            )


def validate_docs(label: str, docs: Any, repo_root: Path, errors: list[str]) -> None:
    if not isinstance(docs, list):
        errors.append(f"{label}: `docs` must be a list of repository-relative file paths (use [] if none).")
        return
    for d_index, doc in enumerate(docs, start=1):
        d_label = f"{label} doc #{d_index}"
        if not isinstance(doc, str) or not doc.strip():
            errors.append(f"{d_label}: each doc path must be a non-empty string.")
            continue
        if doc.startswith("/"):
            errors.append(f"{d_label}: doc path must be repository-relative, not absolute: `{doc}`.")
            continue
        path_obj = (repo_root / doc).resolve()
        if not path_obj.exists():
            errors.append(f"{d_label}: doc path does not exist: `{doc}`.")
        elif path_obj.is_dir():
            errors.append(f"{d_label}: doc path points to a directory, expected a file: `{doc}`.")


def validate_registry(registry: Any, repo_root: Path) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(registry, dict):
        return ["Registry root must be a YAML mapping."], warnings, 0

    if not isinstance(registry.get("version"), int):
        errors.append("Top-level `version` must be an integer.")
    if not is_iso_date(registry.get("last_updated")):
        errors.append("Top-level `last_updated` must be an ISO date (`YYYY-MM-DD`).")

    datasets = registry.get("datasets")
    if datasets is None:
        errors.append("Top-level `datasets` key is missing.")
        return errors, warnings, 0
    if not isinstance(datasets, list):
        errors.append("Top-level `datasets` must be a list.")
        return errors, warnings, 0

    seen_ids: set[str] = set()

    for index, ds in enumerate(datasets, start=1):
        label = f"dataset #{index}"
        if not isinstance(ds, dict):
            errors.append(f"{label}: dataset must be a mapping.")
            continue

        missing = DATASET_REQUIRED_FIELDS - set(ds.keys())
        if missing:
            errors.append(f"{label}: missing required keys: {', '.join(sorted(missing))}.")

        ds_id = ds.get("id")
        if not isinstance(ds_id, str) or not ds_id.strip():
            errors.append(f"{label}: `id` must be a non-empty string.")
            ds_id = None
        else:
            if ds_id in seen_ids:
                errors.append(f"{label}: duplicate dataset `id` `{ds_id}`.")
            seen_ids.add(ds_id)
            label = f"dataset `{ds_id}`"

        if not isinstance(ds.get("name"), str) or not ds.get("name", "").strip():
            errors.append(f"{label}: `name` must be a non-empty string.")

        layer = ds.get("layer")
        if layer not in ALLOWED_LAYERS:
            errors.append(f"{label}: `layer` must be one of: {', '.join(sorted(ALLOWED_LAYERS))}.")

        verification = ds.get("verification")
        if verification not in ALLOWED_VERIFICATION:
            errors.append(
                f"{label}: `verification` must be one of: {', '.join(sorted(ALLOWED_VERIFICATION))}."
            )

        # Two-layer governance: template => verified, project => parsed.
        if layer == "template" and verification == "parsed":
            errors.append(
                f"{label}: a `template` dataset must be `verified`. Curated, reusable "
                f"knowledge is human-verified; promote it or move it to a project entry."
            )
        if layer == "project" and verification == "verified":
            errors.append(
                f"{label}: a `project` dataset must be `parsed`. An agent never writes "
                f"`verified`; promotion is a human step."
            )

        kind = ds.get("kind")
        if kind is not None and kind not in ALLOWED_KINDS:
            errors.append(f"{label}: `kind` (if present) must be one of: {', '.join(sorted(ALLOWED_KINDS))}.")

        if "weights" in ds:
            validate_weights(label, ds["weights"], errors)
        if "pitfalls" in ds:
            validate_pitfalls(label, ds["pitfalls"], errors)
        if "variables" in ds:
            validate_variables(label, ds["variables"], repo_root, errors)
        if "docs" in ds:
            validate_docs(label, ds["docs"], repo_root, errors)

    if not datasets:
        warnings.append("Registry has no datasets yet.")

    return errors, warnings, len(datasets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the canonical dataset registry.")
    parser.add_argument(
        "--registry",
        default="Infrastructure/references/datasets/registry.yaml",
        help="Repository-relative path to the registry YAML.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root path. Defaults to script-derived root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_root = Path(__file__).resolve().parents[2]
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_root
    registry_path = (repo_root / args.registry).resolve()

    if not registry_path.exists():
        print(f"ERROR: registry file does not exist: {registry_path}", file=sys.stderr)
        return 1

    try:
        registry = load_registry(registry_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors, warnings, dataset_count = validate_registry(registry, repo_root)

    if errors:
        print(
            f"Dataset registry validation failed with {len(errors)} error(s) "
            f"and {len(warnings)} warning(s).",
            file=sys.stderr,
        )
        for err in errors:
            print(f"- ERROR: {err}", file=sys.stderr)
        for warn in warnings:
            print(f"- WARNING: {warn}", file=sys.stderr)
        return 1

    print(
        f"Dataset registry validation passed for {dataset_count} dataset"
        f"{'' if dataset_count == 1 else 's'} with {len(warnings)} warning(s)."
    )
    for warn in warnings:
        print(f"- WARNING: {warn}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
