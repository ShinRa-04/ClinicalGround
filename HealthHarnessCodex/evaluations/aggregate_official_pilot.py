"""Aggregate exactly three comparable, independently graded pilot trials."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from typing import Any


TRIAL_NAMES = ("trial-1", "trial-2", "trial-3")
COMPARABILITY_FIELDS = (
    "source_commit", "source_fingerprint", "task_id", "task_instruction_sha256",
    "model", "reasoning_effort", "budgets", "initial_state_fingerprint",
    "allowed_instruction_source_sha256", "composition",
)
OFFICIAL_FILES = ("reward.json", "scorecard.json", "verifier_context.json")
MAX_JSON_BYTES = 20_000_000


class PilotAggregationError(ValueError):
    """Pilot inputs are incomplete, incomparable, or internally inconsistent."""


def aggregate_pilot(pilot_root: Path) -> dict[str, Any]:
    root = Path(pilot_root).resolve(strict=True)
    if not root.is_dir():
        raise PilotAggregationError("pilot root must be a directory")
    ignored_runs_root = Path(__file__).resolve().parents[1] / "runs"
    if not root.is_relative_to(ignored_runs_root):
        raise PilotAggregationError("pilot root must be inside ignored HealthHarnessCodex/runs/")
    numbered_trials = {path.name for path in root.iterdir()
                       if path.is_dir() and re.fullmatch(r"trial-\d+", path.name)}
    if numbered_trials != set(TRIAL_NAMES):
        raise PilotAggregationError("pilot root must contain exactly trial-1, trial-2, and trial-3")

    trials = []
    baseline_metadata: dict[str, Any] | None = None
    for trial_name in TRIAL_NAMES:
        trial_root = root / trial_name
        if trial_root.is_symlink() or not trial_root.resolve(strict=True).is_relative_to(root):
            raise PilotAggregationError(f"{trial_name} must remain inside the pilot root and cannot be a symlink")
        attempt = trial_root / "attempt-1"
        try:
            attempt_resolved = attempt.resolve(strict=True)
        except OSError:
            raise PilotAggregationError(f"{trial_name}/attempt-1 is missing") from None
        if attempt.is_symlink() or not attempt_resolved.is_relative_to(trial_root.resolve()):
            raise PilotAggregationError(f"{trial_name}/attempt-1 must remain inside its trial directory")
        evaluation = _read_json(_regular_file(attempt / "evaluation.json"), "evaluation.json")
        run_result = _read_json(_regular_file(attempt / "run.result.json"), "run.result.json")
        metadata = evaluation.get("metadata")
        if not isinstance(metadata, dict):
            raise PilotAggregationError(f"{trial_name} evaluation has no metadata object")
        _validate_comparability_metadata(metadata, trial_name)
        if baseline_metadata is None:
            baseline_metadata = metadata
        else:
            _validate_same_configuration(baseline_metadata, metadata, trial_name)

        local = run_result.get("local_harness")
        if not isinstance(local, dict):
            raise PilotAggregationError(f"{trial_name} run result has no local_harness result")
        local_status = local.get("status")
        if local_status not in {"complete", "unresolved", "exhausted", "error", "blocked",
                                "runtime_failure", "setup_failure"}:
            raise PilotAggregationError(f"{trial_name} does not have a settled local run result")
        if evaluation.get("harness_status") != local_status:
            raise PilotAggregationError(f"{trial_name} evaluation and run result local statuses disagree")
        if run_result.get("task") != metadata["task_id"]:
            raise PilotAggregationError(f"{trial_name} run result task differs from its evaluation metadata")

        receipt = _read_json(_regular_file(trial_root / "official-evaluation-receipt.json"),
                             "official-evaluation-receipt.json")
        verifier_dir = _resolve_verifier_dir(trial_root, receipt.get("verifier_dir"))
        artifact_hashes = _verify_official_artifacts(verifier_dir, trial_root, receipt)
        reward_file = _read_json(verifier_dir / "reward.json", "reward.json")
        scorecard = _read_json(verifier_dir / "scorecard.json", "scorecard.json")
        verifier_context = _read_json(verifier_dir / "verifier_context.json", "verifier_context.json")

        reward = _extract_binary_reward(reward_file)
        checks = _summarize_scorecard(scorecard)
        scorecard_binary = 1 if checks["failed"] == 0 and checks["non_na"] > 0 else 0
        if reward != scorecard_binary:
            raise PilotAggregationError(f"{trial_name} reward.json disagrees with scorecard check results")
        for key in ("success", "passed", "binary_success"):
            if isinstance(scorecard.get(key), bool) and int(scorecard[key]) != scorecard_binary:
                raise PilotAggregationError(f"{trial_name} scorecard {key} disagrees with check results")
        scorecard_reward = _optional_scorecard_reward(scorecard)
        if scorecard_reward is not None and scorecard_reward != reward:
            raise PilotAggregationError(f"{trial_name} reward.json disagrees with scorecard reward")
        semantic = _validate_semantic_status(receipt, scorecard, verifier_context, checks["check_names"])

        metrics = evaluation.get("metrics")
        if not isinstance(metrics, dict):
            raise PilotAggregationError(f"{trial_name} evaluation has no metrics object")
        dispatches = metrics.get("tool_dispatch_attempts")
        if not isinstance(dispatches, dict):
            raise PilotAggregationError(f"{trial_name} evaluation has no tool dispatch counts")
        not_dispatched = metrics.get("tool_dispatch_not_dispatched", {})
        if not isinstance(not_dispatched, dict):
            raise PilotAggregationError(f"{trial_name} known-not-dispatched counts must be an object")
        not_dispatched_counts = {}
        for name, count in not_dispatched.items():
            if not isinstance(name, str) or name not in dispatches:
                raise PilotAggregationError(f"{trial_name} known-not-dispatched count names an unknown tool")
            count = _dispatch_count(count)
            attempts = _dispatch_count(dispatches[name])
            if count > attempts:
                raise PilotAggregationError(f"{trial_name} known-not-dispatched count exceeds tool attempts")
            not_dispatched_counts[name] = count
        model_calls = metrics.get("model_calls_observed_this_segment", metrics.get("model_calls"))
        engine_calls = metrics.get("tool_calls")
        if not _nonnegative_number(model_calls) or not _nonnegative_number(engine_calls):
            raise PilotAggregationError(f"{trial_name} model/engine call counts are missing or invalid")
        actor_tool_attempts = sum(_dispatch_count(count) for name, count in dispatches.items()
                                  if isinstance(name, str) and name.startswith("mcp_"))
        actor_not_dispatched = sum(count for name, count in not_dispatched_counts.items()
                                   if name.startswith("mcp_"))
        actor_dispatches = actor_tool_attempts - actor_not_dispatched
        workspace_dispatches = sum(_dispatch_count(count) for name, count in dispatches.items()
                                   if isinstance(name, str) and name.startswith("workspace."))
        elapsed = metrics.get("elapsed_seconds")
        usage = metrics.get("reported_usage_this_segment", metrics.get("reported_usage"))
        trials.append({
            "trial": trial_name,
            "official_reward": reward,
            "scorecard": {"passed": checks["passed"], "failed": checks["failed"],
                          "not_applicable": checks["not_applicable"], "non_na": checks["non_na"],
                          "total": checks["total"], "failed_check_names": checks["failed_check_names"]},
            "local_harness_status": local_status,
            "model_calls": model_calls,
            "engine_tool_calls": engine_calls,
            "actor_tool_attempts": actor_tool_attempts,
            "actor_mcp_dispatches": actor_dispatches,
            "workspace_dispatches": workspace_dispatches,
            "elapsed_seconds": elapsed if _nonnegative_number(elapsed) else None,
            "reported_usage": usage if isinstance(usage, dict) else None,
            "cost_estimate": None,
            "semantic_evaluation": semantic,
            "verified_artifact_sha256": artifact_hashes,
        })

    rewards = [item["official_reward"] for item in trials]
    passed = sum(rewards)
    return {
        "schema_version": 1,
        "pilot_scope": {"task_id": baseline_metadata["task_id"], "trial_count": 3,
                        "fixed_source_commit": baseline_metadata["source_commit"],
                        "fixed_source_fingerprint": baseline_metadata["source_fingerprint"]},
        "fixed_configuration": {key: baseline_metadata[key] for key in COMPARABILITY_FIELDS},
        "trials": trials,
        "one_task_pilot_metrics": {
            "pass_at_1": passed / 3,
            "pass_at_3": int(passed > 0),
            "pass_power_3": int(passed == 3),
            "successful_trials": passed,
            "trial_count": 3,
            "scope_note": "These metrics describe only this three-trial, single-task pilot; they are not full-benchmark rates.",
        },
        "cost_estimate": None,
    }


def _validate_comparability_metadata(metadata: dict[str, Any], trial: str) -> None:
    missing = [key for key in COMPARABILITY_FIELDS if key not in metadata or metadata[key] is None]
    if missing:
        raise PilotAggregationError(f"{trial} is missing required comparison metadata: {', '.join(missing)}")


def _validate_same_configuration(reference: dict[str, Any], current: dict[str, Any], trial: str) -> None:
    for key in COMPARABILITY_FIELDS:
        if _canonical(reference[key]) != _canonical(current[key]):
            raise PilotAggregationError(f"{trial} is incomparable: {key} differs")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _resolve_verifier_dir(trial_root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise PilotAggregationError("official receipt must name a verifier_dir relative to its trial root")
    relative = Path(value)
    if relative.is_absolute() or any(part == ".." for part in relative.parts):
        raise PilotAggregationError("official verifier directory must remain inside its trial root")
    candidate = trial_root / relative
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        raise PilotAggregationError("official verifier directory is missing") from None
    if not resolved.is_dir() or not resolved.is_relative_to(trial_root.resolve()):
        raise PilotAggregationError("official verifier directory must remain inside its trial root")
    cursor = trial_root.resolve()
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise PilotAggregationError("official verifier directory cannot traverse symlinks")
    return resolved


def _regular_file(path: Path) -> Path:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
            raise PilotAggregationError(f"required pilot artifact is missing, linked, or oversized: {path.name}")
    except OSError:
        raise PilotAggregationError(f"required pilot artifact is unavailable: {path.name}") from None
    return path


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise PilotAggregationError(f"{label} is missing or invalid JSON") from None
    if not isinstance(data, dict):
        raise PilotAggregationError(f"{label} must be a JSON object")
    return data


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_official_artifacts(verifier_dir: Path, trial_root: Path, receipt: dict[str, Any]) -> dict[str, str]:
    expected = receipt.get("artifact_sha256")
    if not isinstance(expected, dict):
        raise PilotAggregationError("official receipt is missing artifact_sha256")
    relative_dir = verifier_dir.relative_to(trial_root.resolve())
    verified = {}
    for name in OFFICIAL_FILES:
        path = _regular_file(verifier_dir / name)
        digest = _sha256_file(path)
        keys = (str(relative_dir / name), name)
        supplied = [expected[key] for key in keys if key in expected]
        if not supplied or any(not isinstance(value, str) or value.lower() != digest for value in supplied):
            raise PilotAggregationError(f"official receipt hash mismatch for {name}")
        verified[name] = digest
    return verified


def _extract_binary_reward(reward_data: dict[str, Any]) -> int:
    value = reward_data.get("reward")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value not in (0, 1, 0.0, 1.0):
        raise PilotAggregationError("official reward must be the binary numeric value 0 or 1")
    return int(value)


def _optional_scorecard_reward(scorecard: dict[str, Any]) -> int | None:
    present = [(key, scorecard[key]) for key in ("reward", "binary_reward") if key in scorecard]
    values = []
    for key, value in present:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value not in (0, 1, 0.0, 1.0):
            raise PilotAggregationError(f"scorecard {key}, when present, must be binary")
        values.append((key, int(value)))
    if len({value for _, value in values}) > 1:
        raise PilotAggregationError("scorecard reward and binary_reward disagree")
    if not values:
        return None
    return values[0][1]


def _scorecard_check_entries(scorecard: dict[str, Any]) -> list[tuple[str, Any]]:
    raw = scorecard.get("checks", scorecard.get("check_results"))
    if isinstance(raw, list):
        entries = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise PilotAggregationError("scorecard checks must contain objects")
            name = item.get("name", item.get("id", item.get("check_name", item.get("check"))))
            if not isinstance(name, str) or not name:
                raise PilotAggregationError(f"scorecard check {index} has no name")
            entries.append((name, item))
        return entries
    if isinstance(raw, dict):
        return [(name, item) for name, item in raw.items() if isinstance(name, str) and name]
    raise PilotAggregationError("scorecard has no check list/map")


def _check_result(name: str, entry: Any) -> str:
    if isinstance(entry, bool):
        return "passed" if entry else "failed"
    if isinstance(entry, str):
        normalized = entry.strip().casefold().replace("-", "_").replace(" ", "_")
        if normalized in {"na", "n_a", "n/a", "not_applicable"}:
            return "not_applicable"
        if normalized in {"pass", "passed", "success", "ok"}:
            return "passed"
        if normalized in {"fail", "failed", "failure", "error"}:
            return "failed"
        raise PilotAggregationError(f"scorecard check {name} has an unknown result state")
    if not isinstance(entry, dict):
        raise PilotAggregationError(f"scorecard check {name} has no result state")
    if entry.get("applicable") is False or entry.get("is_applicable") is False or entry.get("not_applicable") is True:
        return "not_applicable"
    status = entry.get("status", entry.get("result"))
    if isinstance(status, str):
        normalized = status.strip().casefold().replace("-", "_").replace(" ", "_")
        if normalized in {"na", "n_a", "n/a", "not_applicable"}:
            return "not_applicable"
        if normalized in {"pass", "passed", "success", "ok"}:
            return "passed"
        if normalized in {"fail", "failed", "failure", "error"}:
            return "failed"
    passed = entry.get("passed")
    if isinstance(passed, bool):
        return "passed" if passed else "failed"
    if isinstance(status, bool):
        return "passed" if status else "failed"
    raise PilotAggregationError(f"scorecard check {name} has an unknown result state")


def _summarize_scorecard(scorecard: dict[str, Any]) -> dict[str, Any]:
    entries = _scorecard_check_entries(scorecard)
    names = [name for name, _ in entries]
    if len(set(names)) != len(names):
        raise PilotAggregationError("scorecard has duplicate check names")
    statuses = {name: _check_result(name, entry) for name, entry in entries}
    counts = {key: sum(value == key for value in statuses.values())
              for key in ("passed", "failed", "not_applicable")}
    counts["non_na"] = counts["passed"] + counts["failed"]
    counts["total"] = len(statuses)
    failed_names = sorted(name for name, value in statuses.items() if value == "failed")
    _validate_declared_scorecard_counts(scorecard, counts, statuses)
    if counts["non_na"] == 0:
        raise PilotAggregationError("scorecard has no applicable non-N/A checks")
    counts["check_names"] = list(statuses)
    counts["failed_check_names"] = failed_names
    return counts


def _validate_declared_scorecard_counts(scorecard: dict[str, Any], counts: dict[str, Any],
                                        statuses: dict[str, str]) -> None:
    containers = [scorecard]
    for key in ("counts", "summary", "check_counts", "totals"):
        if isinstance(scorecard.get(key), dict):
            containers.append(scorecard[key])
    aliases = {
        "passed": {"passed", "passed_count", "pass_count", "checks_passed", "passed_checks"},
        "failed": {"failed", "failed_count", "fail_count", "checks_failed"},
        "not_applicable": {"not_applicable", "not_applicable_count", "not_applicable_checks", "na", "n_a", "na_count", "checks_na"},
        "non_na": {"non_na", "applicable", "applicable_count", "applicable_checks", "total_checks"},
        "total": {"total", "checks_total", "check_count"},
    }
    for container in containers:
        for key, value in container.items():
            normalized = str(key).casefold().replace("-", "_").replace(" ", "_")
            for category, names in aliases.items():
                if normalized in names and isinstance(value, int) and not isinstance(value, bool):
                    if value != counts[category]:
                        raise PilotAggregationError(f"scorecard declared {category} count is inconsistent")
            if normalized == "failed_checks":
                if isinstance(value, list):
                    declared_names = sorted(_check_name(item) for item in value)
                    if declared_names != sorted(name for name, status in statuses.items() if status == "failed"):
                        raise PilotAggregationError("scorecard failed_checks list is inconsistent")
                elif isinstance(value, int) and not isinstance(value, bool) and value != counts["failed"]:
                    raise PilotAggregationError("scorecard failed_checks count is inconsistent")
            if normalized in {"passed_checks", "checks_passed_names"} and isinstance(value, list):
                declared_names = sorted(_check_name(item) for item in value)
                if declared_names != sorted(name for name, status in statuses.items() if status == "passed"):
                    raise PilotAggregationError("scorecard passed_checks list is inconsistent")
            if normalized in {"not_applicable_checks", "na_checks", "checks_na_names"} and isinstance(value, list):
                declared_names = sorted(_check_name(item) for item in value)
                if declared_names != sorted(name for name, status in statuses.items() if status == "not_applicable"):
                    raise PilotAggregationError("scorecard not_applicable_checks list is inconsistent")


def _check_name(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        name = value.get("name", value.get("id", value.get("check_name")))
        if isinstance(name, str):
            return name
    raise PilotAggregationError("scorecard declares an invalid check name")


def _validate_semantic_status(receipt: dict[str, Any], scorecard: dict[str, Any],
                              verifier_context: dict[str, Any], check_names: list[str]) -> dict[str, Any]:
    reason_values: list[Any] = []
    indicator_seen = False

    reason_keys = {
        "semanticdegradedreason", "semanticunavailablereason",
        "judgedegradedreason", "judgeunavailablereason",
    }

    def walk(value: Any, semantic_or_judge_parent: bool = False) -> None:
        nonlocal indicator_seen
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = re.sub(r"[^a-z]", "", str(key).casefold())
                semantic_scope = semantic_or_judge_parent or "semantic" in normalized
                judge_scope = semantic_or_judge_parent or "judge" in normalized
                if normalized in reason_keys or (
                    semantic_scope and ("degrad" in normalized or "unavail" in normalized) and "reason" in normalized
                ):
                    indicator_seen = True
                    reason_values.append(child)
                if normalized == "degradedrubricids":
                    indicator_seen = True
                    if child not in (None, [], {}):
                        reason_values.append(child)
                if normalized == "judgesessionmetadata":
                    indicator_seen = True
                if (semantic_scope or judge_scope) and normalized in {"status", "state"} and isinstance(child, str):
                    if child.casefold() in {"degraded", "unavailable", "skipped", "failed"}:
                        reason_values.append(child)
                walk(child, semantic_scope or judge_scope)
        elif isinstance(value, list):
            for child in value:
                walk(child, semantic_or_judge_parent)

    for value in (receipt, scorecard, verifier_context):
        walk(value)
    non_null = [value for value in reason_values if value is not None]
    if non_null:
        raise PilotAggregationError("native semantic evaluation is degraded or unavailable")
    judge_checks = [name for name in check_names if name.casefold().startswith("judge.") or
                    ("judge" in name.casefold() and "semantic" in name.casefold())]
    if judge_checks and not indicator_seen:
        raise PilotAggregationError("judge checks are present but semantic availability status is missing")
    if indicator_seen:
        return {"status": "reason_none", "judge_checks_present": bool(judge_checks)}
    return {"status": "not_applicable_no_judge_checks", "judge_checks_present": False}


def _dispatch_count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PilotAggregationError("tool dispatch counts must be nonnegative integers")
    return value


def _nonnegative_number(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0)


def render_markdown(report: dict[str, Any]) -> str:
    pilot = report["one_task_pilot_metrics"]
    rows = ["| Trial | Official reward | Checks passed/failed/N/A | Local status | Model calls | Engine calls | Actor attempts | Actor MCP dispatched | Workspace | Seconds |",
            "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|"]
    for trial in report["trials"]:
        check = trial["scorecard"]
        rows.append(f"| {trial['trial']} | {trial['official_reward']} | {check['passed']}/{check['failed']}/{check['not_applicable']} | "
                    f"{trial['local_harness_status']} | {trial['model_calls']} | {trial['engine_tool_calls']} | "
                    f"{trial['actor_tool_attempts']} | {trial['actor_mcp_dispatches']} | "
                    f"{trial['workspace_dispatches']} | {trial['elapsed_seconds']} |")
    return ("# One-task official pilot\n\n" + "\n".join(rows) + "\n\n" +
            f"pass@1: {pilot['pass_at_1']:.3f} ({pilot['successful_trials']}/3)\n\n" +
            f"pass@3: {pilot['pass_at_3']}\n\n" + f"pass^3: {pilot['pass_power_3']}\n\n" +
            "Cost estimate: unknown. These rates describe only this fixed-version, single-task three-trial pilot. "
            "Local harness status and official reward are reported separately.\n")


def write_reports(pilot_root: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    root = Path(pilot_root).resolve(strict=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + f"-{time.time_ns() % 1_000_000_000:09d}Z"
    json_path = root / f"official-pilot-aggregate-{stamp}.json"
    markdown_path = root / f"official-pilot-aggregate-{stamp}.md"
    try:
        with json_path.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        with markdown_path.open("x", encoding="utf-8") as stream:
            stream.write(render_markdown(report))
    except FileExistsError:
        raise PilotAggregationError("aggregate output filename already exists; rerun for a unique filename") from None
    return json_path, markdown_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate exactly three comparable official pilot trials")
    parser.add_argument("--pilot-root", type=Path, required=True,
                        help="ignored root containing trial-1, trial-2, and trial-3")
    args = parser.parse_args(argv)
    try:
        report = aggregate_pilot(args.pilot_root)
        json_path, markdown_path = write_reports(args.pilot_root, report)
    except PilotAggregationError as exc:
        print(json.dumps({"status": "rejected", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"status": "aggregated", "json_path": str(json_path),
                      "markdown_path": str(markdown_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
