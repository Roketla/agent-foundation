#!/usr/bin/env python3
"""Aggregate bounded, evidence-pointer-only v0.3 evaluation records."""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


MAX_INPUT_BYTES = 2 * 1024 * 1024
METRICS = ("duration_seconds", "input_tokens", "cached_input_tokens", "output_tokens", "human_interventions")
OUTCOMES = {"accepted", "failed", "blocked"}
VARIANTS = {"baseline", "candidate"}


class ValidationError(ValueError):
    pass


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _fail(path, message):
    raise ValidationError(f"{path}: {message}")


def _validate_metric(value, path, integer=False):
    if value is None:
        return
    valid = _is_int(value) if integer else isinstance(value, (int, float)) and not isinstance(value, bool)
    if not valid or not math.isfinite(value) or value < 0:
        _fail(path, "must be a non-negative number or null")


def validate_input(payload):
    if not isinstance(payload, dict) or type(payload.get("schema_version")) is not int or payload["schema_version"] != 1:
        _fail("input", "must be an object with schema_version 1")
    runs = payload.get("runs")
    if not isinstance(runs, list):
        _fail("input.runs", "must be a list")
    seen = set()
    for index, run in enumerate(runs):
        path = f"runs[{index}]"
        if not isinstance(run, dict):
            _fail(path, "must be an object")
        for key in ("run_id", "case_id", "environment", "requested_model"):
            if not _nonempty_string(run.get(key)):
                _fail(f"{path}.{key}", "must be a non-empty string")
        if run["run_id"] in seen:
            _fail(f"{path}.run_id", "duplicates an earlier run_id")
        seen.add(run["run_id"])
        if not isinstance(run.get("variant"), str) or run["variant"] not in VARIANTS:
            _fail(f"{path}.variant", "must be baseline or candidate")
        if not isinstance(run.get("outcome"), str) or run["outcome"] not in OUTCOMES:
            _fail(f"{path}.outcome", "must be accepted, failed, or blocked")
        if not _is_int(run.get("attempts")) or run["attempts"] < 1:
            _fail(f"{path}.attempts", "must be an integer of at least 1")
        observed, evidence = run.get("observed_model"), run.get("model_evidence")
        if observed is not None and not _nonempty_string(observed):
            _fail(f"{path}.observed_model", "must be a non-empty string or null")
        if evidence is not None and not _nonempty_string(evidence):
            _fail(f"{path}.model_evidence", "must be a non-empty string or null")
        if observed is not None and evidence is None:
            _fail(f"{path}.model_evidence", "is required when observed_model is present")
        checks = run.get("checks")
        if not isinstance(checks, list):
            _fail(f"{path}.checks", "must be a list")
        for check_index, check in enumerate(checks):
            check_path = f"{path}.checks[{check_index}]"
            if not isinstance(check, dict) or not _nonempty_string(check.get("name")) or not isinstance(check.get("passed"), bool) or not _nonempty_string(check.get("evidence")):
                _fail(check_path, "must have non-empty name/evidence and boolean passed")
        if run["outcome"] == "accepted" and (not checks or not all(check["passed"] for check in checks)):
            _fail(f"{path}.checks", "accepted runs require one or more passing checks")
        for metric in METRICS:
            _validate_metric(run.get(metric), f"{path}.{metric}", metric != "duration_seconds")
        if run.get("cached_input_tokens") is not None and run.get("input_tokens") is None:
            _fail(f"{path}.cached_input_tokens", "requires input_tokens")
        if run.get("cached_input_tokens") is not None and run["cached_input_tokens"] > run["input_tokens"]:
            _fail(f"{path}.cached_input_tokens", "cannot exceed input_tokens")
        refs = run.get("evidence")
        if not isinstance(refs, list) or not refs or not all(_nonempty_string(ref) for ref in refs):
            _fail(f"{path}.evidence", "must be a list of non-empty reference strings")
    return runs


def _metric_summary(runs, metric):
    values = [run[metric] for run in runs if run.get(metric) is not None]
    return {"total": sum(values) if values else None, "observed_runs": len(values), "missing_runs": len(runs) - len(values)}


def _variant_summary(runs):
    outcomes = {outcome: sum(run["outcome"] == outcome for run in runs) for outcome in sorted(OUTCOMES)}
    observed = sorted({run["observed_model"] for run in runs if run.get("observed_model") is not None})
    return {
        "sample_count": len(runs),
        "outcomes": outcomes,
        "acceptance_rate": outcomes["accepted"] / len(runs) if runs else None,
        "attempts_total": sum(run["attempts"] for run in runs),
        "metrics": {metric: _metric_summary(runs, metric) for metric in METRICS},
        "model_observation": {"observed_models": observed, "unobserved_runs": len(runs) - sum(run.get("observed_model") is not None for run in runs)},
    }


def _comparison(baseline, candidate):
    result = {}
    for metric in METRICS:
        left = _metric_summary(baseline, metric)
        right = _metric_summary(candidate, metric)
        complete = left["missing_runs"] == 0 and right["missing_runs"] == 0
        result[metric] = {
            "complete": complete,
            "difference_candidate_minus_baseline": right["total"] - left["total"] if complete else None,
        }
    return result


def build_report(payload):
    runs = validate_input(payload)
    groups = defaultdict(lambda: {"baseline": [], "candidate": []})
    for run in runs:
        groups[(run["case_id"], run["environment"])][run["variant"]].append(run)
    cases, unmatched = [], []
    for (case_id, environment), group in sorted(groups.items()):
        baseline, candidate = group["baseline"], group["candidate"]
        paired = bool(baseline and candidate)
        entry = {
            "case_id": case_id,
            "environment": environment,
            "baseline": _variant_summary(baseline),
            "candidate": _variant_summary(candidate),
            "comparison": {"status": "paired" if paired else "unmatched", "metrics": _comparison(baseline, candidate) if paired else None},
        }
        cases.append(entry)
        if not paired:
            unmatched.append({"case_id": case_id, "environment": environment, "missing_variant": "baseline" if not baseline else "candidate"})
    return {
        "schema_version": 1,
        "input_schema_version": 1,
        "record_count": len(runs),
        "paired_case_count": sum(case["comparison"]["status"] == "paired" for case in cases),
        "unmatched": unmatched,
        "cases": cases,
        "caveats": [
            "Cases are compared only when case_id and environment match.",
            "Metric totals include accepted, failed, and blocked runs; null means no observation.",
            "cached_input_tokens is a subset of input_tokens and is not added to token volume.",
            "Token figures are volume, not cost. One sample does not establish improvement.",
            "Differences are raw totals; unequal sample counts do not support per-run efficiency claims.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_subparsers(dest="command", required=True)
    report = command.add_parser("report", help="validate records and emit an aggregate JSON report")
    report.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.stat().st_size > MAX_INPUT_BYTES:
            raise ValidationError(f"input exceeds {MAX_INPUT_BYTES} bytes")
        with args.input.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        print(json.dumps(build_report(payload), indent=2, sort_keys=True, allow_nan=False))
    except (OSError, ValueError, OverflowError) as error:
        print(f"evaluate.py: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
