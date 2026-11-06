"""Build a private full-domain packet from one integrity-checked 75-task batch.

This is a packet producer only. It does not run actors, grading, or publication.
Native results and official reward/scorecard files are copied without edits;
trajectories are faithful saved engine messages under a disclosed custom schema.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Callable


DOMAINS = ("pa_provider", "pa_um", "cm")
TASK_COUNTS = {"pa_provider": 25, "pa_um": 25, "cm": 25}
CHI_BENCH_COMMIT = "4444a07fa68a4f1623f841a292a54e284fc8e7f7"
PACKET_SCHEMA = "chi-bench/submission/v1"
DATASET_VERSION = "chi-bench-v1.0.0"
CSV_FIELDS = ("benchmark", "dataset_version", "submission_id", "team", "agent", "model",
              "domain", "pass_at_1", "n_trials", "n_tasks", "mean_cost_usd",
              "mean_walltime_s", "submitted_at")


class BatchPacketError(ValueError):
    """The batch is incomplete, tampered, incomparable, or not packet-ready."""


def _load_helpers():
    path = Path(__file__).resolve().parent / "assemble_native_packet.py"
    spec = importlib.util.spec_from_file_location("native_packet_helpers", path)
    if spec is None or spec.loader is None:
        raise BatchPacketError("native trajectory helpers are unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise BatchPacketError(f"{label} is missing or invalid JSON") from None
    if not isinstance(value, dict):
        raise BatchPacketError(f"{label} must be a JSON object")
    return value


def _utc_package_time() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_batch_module():
    repo = Path(__file__).resolve().parents[2]
    path = repo / "HealthHarnessCodex" / "health_harness_codex" / "batch.py"
    spec = importlib.util.spec_from_file_location("batch_packet_validator", path)
    if spec is None or spec.loader is None:
        raise BatchPacketError("batch integrity validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _validate_full_batch(batch_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    batch_mod = _load_batch_module()
    manifest_path = batch_root / "batch.manifest.json"
    manifest = _read_json(manifest_path, "batch manifest")
    frozen = manifest.get("frozen_config")
    tasks = manifest.get("tasks")
    summary = manifest.get("summary")
    if not isinstance(frozen, dict) or not isinstance(tasks, list) or not isinstance(summary, dict):
        raise BatchPacketError("batch manifest is incomplete")
    if frozen.get("attempts") != 1 or tuple(frozen.get("domains", ())) != DOMAINS:
        raise BatchPacketError("packet requires the frozen all-domain, one-attempt batch configuration")
    if (frozen.get("runtime_image_sha256") != "sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66" or
            not isinstance(frozen.get("source_commit"), str) or
            not isinstance(frozen.get("source_fingerprint"), str) or len(frozen["source_fingerprint"]) != 64):
        raise BatchPacketError("batch source or runtime image provenance is incomplete")
    if (len(tasks) != 75 or summary.get("full_dataset_coverage_complete") is not True or
            summary.get("full_domain_coverage_complete") != {domain: True for domain in DOMAINS}):
        raise BatchPacketError("packet requires 75 graded first attempts with full dataset coverage")

    counts = {domain: 0 for domain in DOMAINS}
    seen_task_ids: set[str] = set()
    packet_rows: list[dict[str, Any]] = []
    helpers = _load_helpers()
    for task in tasks:
        if not isinstance(task, dict):
            raise BatchPacketError("batch task row is malformed")
        domain, task_id = task.get("domain"), task.get("task_id")
        if domain not in counts or not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", task_id):
            raise BatchPacketError("batch contains an unknown domain or unsafe task ID")
        if task_id in seen_task_ids:
            raise BatchPacketError("batch contains duplicate task IDs that cannot be represented unambiguously")
        seen_task_ids.add(task_id)
        counts[domain] += 1
        instruction_key = f"{domain}/{task_id}"
        instruction_hash = frozen.get("task_instruction_sha256", {}).get(instruction_key)
        if not isinstance(instruction_hash, str) or len(instruction_hash) != 64:
            raise BatchPacketError("frozen configuration lacks a public instruction hash")
        attempts = task.get("attempts")
        if not isinstance(attempts, list) or len(attempts) != 1:
            raise BatchPacketError("each full-benchmark task must contain exactly one first attempt")
        attempt = attempts[0]
        if not isinstance(attempt, dict) or attempt.get("status") != "graded" or attempt.get("official_score") not in (0, 1):
            raise BatchPacketError("every first attempt must have an actual strict official reward of 0 or 1")
        relative = f"{domain}/{task_id}/attempt-1"
        if attempt.get("attempt_dir") != relative:
            raise BatchPacketError("batch attempt path differs from the task/domain identity")
        try:
            batch_mod._verify_completed_attempt(batch_root, task, attempt, frozen)
        except Exception as exc:
            raise BatchPacketError(f"completed batch attempt integrity check failed ({type(exc).__name__})") from None

        attempt_dir = batch_root / relative
        receipt = _read_json(attempt_dir / "official-evaluation-receipt.json", "official receipt")
        if receipt.get("attempt") != 1 or receipt.get("selected_output") not in {"official_1", "official_2", "official_3"}:
            raise BatchPacketError("official receipt does not select a completed first-attempt verifier output")
        artifact_hashes = receipt.get("artifacts")
        required_artifacts = {"reward", "scorecard", "exported_state", "verifier_context"}
        if not isinstance(artifact_hashes, dict) or not required_artifacts.issubset(artifact_hashes):
            raise BatchPacketError("official receipt must hash all four verifier artifacts")
        verifier_dir = attempt_dir / "container_logs" / receipt["selected_output"]
        if not verifier_dir.is_dir():
            raise BatchPacketError("receipt-selected verifier output directory is missing")
        for key, filename in {"reward": "reward.json", "scorecard": "scorecard.json",
                              "exported_state": "exported_state.json", "verifier_context": "verifier_context.json"}.items():
            file_path = verifier_dir / filename
            expected = artifact_hashes[key]
            if (not file_path.is_file() or file_path.is_symlink() or not isinstance(expected, dict) or
                    _sha256(file_path) != expected.get("sha256") or file_path.stat().st_size != expected.get("bytes")):
                raise BatchPacketError(f"receipt-selected {filename} is missing or hash-invalid")
        grade = batch_mod._official_grade(verifier_dir.parent, verifier_dir.name,
                                          receipt.get("grader_runs", [{}])[-1].get("returncode"))
        if grade[0] != "graded" or grade[1].get("reward") != attempt["official_score"]:
            raise BatchPacketError("official scorecard/reward/judge state is inconsistent with batch manifest")

        result_path = attempt_dir / "run.result.json"
        evaluation_path = attempt_dir / "evaluation.json"
        events_path = attempt_dir / "events.jsonl"
        snapshot_path = attempt_dir / "state.snapshot.sqlite"
        result = _read_json(result_path, "native run result")
        evaluation = _read_json(evaluation_path, "native evaluation")
        metadata = evaluation.get("metadata")
        if not isinstance(metadata, dict):
            raise BatchPacketError("native evaluation has no metadata")
        expected_identity = {
            "source_commit": frozen.get("source_commit"),
            "source_fingerprint": frozen.get("source_fingerprint"),
            "model": frozen.get("model"),
            "reasoning_effort": frozen.get("reasoning_effort"),
            "task_instruction_sha256": instruction_hash,
        }
        if any(metadata.get(key) != value for key, value in expected_identity.items()):
            raise BatchPacketError("native evaluation metadata differs from frozen batch configuration")
        if metadata.get("task_id", metadata.get("task")) != task_id:
            raise BatchPacketError("native evaluation task identity does not match the batch row")
        if result.get("task") != task_id or result.get("task_instruction_sha256") != instruction_hash:
            raise BatchPacketError("verbatim native run result identity differs from the frozen public task")
        local = result.get("local_harness")
        if not isinstance(local, dict):
            raise BatchPacketError("native run result lacks local_harness status")
        if attempt.get("local_status") != local.get("status"):
            raise BatchPacketError("batch local status differs from the original native run result")
        if evaluation.get("harness_status") != local.get("status"):
            raise BatchPacketError("native evaluation and native result statuses disagree")
        owner_seconds = result.get("elapsed_seconds")
        if isinstance(owner_seconds, bool) or not isinstance(owner_seconds, (int, float)) or owner_seconds < 0:
            owner_seconds = None
        run_start, run_finish = helpers._recorded_run_times(events_path)
        if not snapshot_path.is_file() or not result_path.is_file():
            raise BatchPacketError("required native run artifact is missing")
        trajectory = {"source": _sha256(snapshot_path)}
        packet_rows.append({
            "domain": domain, "task_id": task_id, "attempt": attempt, "attempt_dir": attempt_dir,
            "verifier_dir": verifier_dir, "result_path": result_path,
            "reward_path": verifier_dir / "reward.json", "scorecard_path": verifier_dir / "scorecard.json",
            "snapshot_path": snapshot_path, "evaluation_path": evaluation_path, "events_path": events_path,
            "receipt_path": attempt_dir / "official-evaluation-receipt.json",
            "reward": grade[1]["reward"], "checks": grade[1]["checks"],
            "semantic_evaluation": grade[1]["semantic_evaluation"],
            "local_status": local.get("status"), "owner_loop_seconds": owner_seconds,
            "recorded_run_started_at": run_start, "recorded_run_finished_at": run_finish,
            "trajectory_source_sha256": trajectory["source"],
        })
    if counts != TASK_COUNTS or len(packet_rows) != 75:
        raise BatchPacketError("full packet requires exactly 25 graded tasks in each canonical domain")
    return manifest, packet_rows, frozen


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _write_native_sub_yaml(path: Path, submission_id: str, team: str, contact: str,
                           frozen: dict[str, Any]) -> None:
    path.write_text(
        "schema: health-harness/native-batch-export/v1\n"
        "submission:\n"
        f"  id: {_yaml_string(submission_id)}\n"
        f"  team: {_yaml_string(team)}\n"
        f"  contact: {_yaml_string(contact)}\n"
        "  agent: HealthHarnessCodex\n"
        f"  model: {_yaml_string(frozen['model'])}\n"
        f"  reasoning_effort: {_yaml_string(frozen['reasoning_effort'])}\n"
        "  notes: Derived frozen native batch export; not a cb submission execution config.\n"
        "run:\n  n_trials: 75\n  n_tasks: 75\n  execution: native standalone HealthHarnessCodex\n"
        f"  budgets: {json.dumps(frozen['budgets'], ensure_ascii=False)}\n"
        f"  source_commit: {_yaml_string(frozen['source_commit'])}\n"
        f"  source_fingerprint: {_yaml_string(frozen['source_fingerprint'])}\n"
        f"  composition: {_yaml_string(frozen.get('composition', 'unknown'))}\n"
        "dataset:\n  version: chi-bench-v1.0.0\n  domains: [pa_provider, pa_um, cm]\n",
        encoding="utf-8")


def _write_results_csv(path: Path, manifest: dict[str, Any]) -> None:
    sub, dataset, results = manifest["submission"], manifest["dataset"], manifest["results"]
    rows = []
    for domain, score in [("overall", results["overall"]), *results["per_domain"].items()]:
        rows.append({"benchmark": dataset["name"], "dataset_version": dataset["version"],
                     "submission_id": sub["id"], "team": sub["team"], "agent": sub["agent"],
                     "model": sub["model"], "domain": domain, "pass_at_1": score["pass_at_1"],
                     "n_trials": score["n_trials"], "n_tasks": score["n_tasks"],
                     "mean_cost_usd": "", "mean_walltime_s": score.get("mean_walltime_s"),
                     "submitted_at": sub["submitted_at"]})
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def assemble_full_batch_packet(batch_root: Path, output_root: Path, submission_id: str,
                               submission_date: str, team: str, contact: str,
                               packer: Callable[[Path, Path], None] | None = None) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", submission_id):
        raise BatchPacketError("submission id must be a lowercase slug")
    try:
        packet_date = date.fromisoformat(submission_date)
    except ValueError:
        raise BatchPacketError("submission date must be YYYY-MM-DD") from None
    if packet_date > datetime.now(timezone.utc).date():
        raise BatchPacketError("submission date cannot be in the future")
    if not team or not contact:
        raise BatchPacketError("team and contact are required")
    root = Path(batch_root).resolve(strict=True)
    _load_batch_module()
    required_runs_root = Path(__file__).resolve().parents[2] / "HealthHarnessCodex" / "runs"
    if not root.is_relative_to(required_runs_root.resolve()):
        raise BatchPacketError("batch root must be inside ignored HealthHarnessCodex/runs")
    try:
        batch_manifest, packet_rows, frozen = _validate_full_batch(root)
    except BatchPacketError:
        raise
    except Exception as exc:
        raise BatchPacketError(f"batch validation failed ({type(exc).__name__})") from None

    output_base = Path(output_root).resolve()
    target = output_base / f"{packet_date.isoformat()}-{submission_id}"
    output_base.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise BatchPacketError("packet destination already exists; refusing overwrite")
    stamp = _utc_package_time()
    if packer is None:
        packer = _load_helpers()._default_packer
    stage = Path(tempfile.mkdtemp(prefix=f".{submission_id}-stage-", dir=output_base))
    try:
        trial_records = []
        domain_totals = {domain: {"reward": 0, "seconds": [], "count": 0} for domain in DOMAINS}
        for row in packet_rows:
            domain, task_id = row["domain"], row["task_id"]
            attempt_name = f"{task_id}__attempt_1"
            destination = Path("trials") / domain / attempt_name
            helper = _load_helpers()
            _copy = helper._copy_source
            _copy(row["result_path"], stage / destination / "result.json")
            _copy(row["reward_path"], stage / destination / "verifier" / "reward.json")
            _copy(row["scorecard_path"], stage / destination / "verifier" / "scorecard.json")
            message_count = helper._write_trajectory(row["snapshot_path"],
                stage / destination / "agent" / "trajectory.jsonl.zst", attempt_name, packer)
            total = domain_totals[domain]
            total["reward"] += row["reward"]
            total["count"] += 1
            if row["owner_loop_seconds"] is not None:
                total["seconds"].append(float(row["owner_loop_seconds"]))
            source_files = [row[key] for key in ("result_path", "reward_path", "scorecard_path",
                                                  "snapshot_path", "evaluation_path", "events_path", "receipt_path")]
            source_hashes = {path.relative_to(root).as_posix(): {
                "sha256": _sha256(path), "bytes": path.stat().st_size} for path in source_files}
            receipt = _read_json(row["receipt_path"], "official receipt")
            verifier_files = {name: {"sha256": _sha256(path), "bytes": path.stat().st_size}
                              for name, path in (("reward.json", row["reward_path"]),
                                                 ("scorecard.json", row["scorecard_path"]),
                                                 ("exported_state.json", row["verifier_dir"] / "exported_state.json"),
                                                 ("verifier_context.json", row["verifier_dir"] / "verifier_context.json"))}
            trajectory_path = stage / destination / "agent" / "trajectory.jsonl.zst"
            trial_records.append({
                "domain": domain, "task_id": task_id, "attempt": 1,
                "official_reward": row["reward"], "scorecard": row["checks"],
                "semantic_evaluation": row["semantic_evaluation"],
                "local_status": row["local_status"], "owner_loop_seconds": row["owner_loop_seconds"],
                "recorded_run_started_at": row["recorded_run_started_at"],
                "recorded_run_finished_at": row["recorded_run_finished_at"],
                "native_message_count": message_count,
                "receipt_selected_output": receipt["selected_output"],
                "actor_and_receipt_sha256": source_hashes,
                "official_artifact_sha256": verifier_files,
                "trajectory_sha256": _sha256(trajectory_path),
            })

        overall_passes = sum(item["reward"] for item in domain_totals.values())
        mean_walltime = [seconds for item in domain_totals.values() for seconds in item["seconds"]]
        overall = {"pass_at_1": overall_passes / 75, "n_trials": 75, "n_tasks": 75,
                   "scope_note": "All 75 public tasks, one first attempt each; not clinical certification."}
        if mean_walltime:
            overall["mean_walltime_s"] = sum(mean_walltime) / len(mean_walltime)
        per_domain = {}
        for domain in DOMAINS:
            totals = domain_totals[domain]
            per_domain[domain] = {"pass_at_1": totals["reward"] / 25, "n_trials": 25, "n_tasks": 25}
            if totals["seconds"]:
                per_domain[domain]["mean_walltime_s"] = sum(totals["seconds"]) / len(totals["seconds"])
        identity_confirmed = bool(team and contact)
        submission = {"id": submission_id, "team": team, "contact": contact,
                      "agent": "HealthHarnessCodex", "model": frozen["model"],
                      "reasoning_effort": frozen["reasoning_effort"], "submitted_at": stamp,
                      "notes": "Full 75-task native batch; publication format acceptance remains under review.",
                      "publication_ready": False}
        manifest = {"schema": PACKET_SCHEMA, "submission": submission,
                    "dataset": {"name": "chi-bench", "version": DATASET_VERSION, "domains": list(DOMAINS)},
                    "results": {"overall": overall, "per_domain": per_domain}, "provenance": {}}
        _write_results_csv(stage / "results.csv", manifest)
        _write_native_sub_yaml(stage / "sub.yaml", submission_id, team, contact, frozen)

        packet_helper = _load_helpers()
        producer_digest = _sha256(Path(__file__).resolve())
        provenance = {
            "chi_bench_git_sha": CHI_BENCH_COMMIT,
            "image_digest": frozen["runtime_image_sha256"],
            "judge_model": "official-runtime-verifier",
            "configured_grader": "chi_bench.verifier.task_runtime.verify",
            "judge_execution": "No judge model identity is asserted; per-trial scorecard/context availability is recorded below.",
            "harness_version": f"HealthHarnessCodex@{frozen['source_commit']}",
            "producer_script_sha256": _sha256(Path(__file__).resolve()),
            "producer_script_sha256": producer_digest,
            "actor_source_commit": frozen["source_commit"],
            "actor_source_fingerprint": frozen["source_fingerprint"],
            "model": frozen["model"], "reasoning_effort": frozen["reasoning_effort"],
            "budgets": frozen["budgets"], "composition": frozen.get("composition"),
            "runtime_image": frozen["runtime_image"], "runtime_image_sha256": frozen["runtime_image_sha256"],
            "domains": list(DOMAINS), "n_tasks": 75, "n_trials": 75,
            "cost": "unknown; omitted from results", "mean_walltime_scope":
                "Recorded standalone owner-loop elapsed seconds; setup and official grading excluded; no CI estimate at one run per task.",
            "identity_confirmed": identity_confirmed, "publication_ready": False,
            "publication_limitations": [
                "Native HealthHarness transcript/result export has not been accepted by maintainers as Harbor/ATIF output.",
                "No public validation or publication was performed.",
                "Cost was not measured; mean_cost_usd is intentionally omitted.",
            ],
            "trajectory": {
                "schema_version": "health-harness/native-transcript/v1",
                "source": "messages from integrity-checked read-only state.snapshot.sqlite cases.state_json",
                "steps": "Faithful original engine message objects; no per-step timestamp synthesis.",
                "session_id": "sqlite-sha256:<snapshot digest>; derived export ID, not a provider/Harbor session.",
                "encoding": "Upstream chi_bench trajectory_pack.pack_trajectory_to_jsonl_zst, zstd level 19.",
                "not_atif_or_harbor": True,
            },
            "batch_manifest": {"path": "batch.manifest.json", "sha256": _sha256(batch_root / "batch.manifest.json"),
                               "bytes": (batch_root / "batch.manifest.json").stat().st_size},
            "frozen_batch_config": frozen,
            "trial_rows": trial_records,
        }
        manifest["provenance"] = provenance
        (stage / "submission.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "README.md").write_text(
            f"# {submission_id} full-domain native batch packet\n\n"
            "This packet covers all 75 public PA/provider, UM, and CM tasks with one independently graded first attempt each. "
            "Reward-zero failures are retained as measured results; no ungraded task is encoded as zero.\n\n"
            f"- Overall strict pass@1: {overall['pass_at_1']:.3f} ({overall_passes}/75).\n"
            + "\n".join(f"- {domain}: {per_domain[domain]['pass_at_1']:.3f} "
                         f"({domain_totals[domain]['reward']}/25)." for domain in DOMAINS) + "\n"
            "- Cost: unknown; omitted.\n- Publication ready: no; native transcript compatibility remains unconfirmed.\n\n"
            "Each result.json is copied byte-for-byte from the native run. Official reward and scorecard files are copied "
            "byte-for-byte from receipt-selected verifier outputs. The trajectory schema is HealthHarness native messages, "
            "not strict ATIF or Harbor; header identifiers are derived from SQLite snapshot hashes. No fixture, expectation, "
            "solution or verifier context body is included in the packet.\n", encoding="utf-8")

        expected_files = {"submission.json", "results.csv", "sub.yaml", "provenance.json", "README.md"}
        for row in packet_rows:
            trial_root = Path("trials") / row["domain"] / f"{row['task_id']}__attempt_1"
            expected_files.update({(trial_root / "result.json").as_posix(),
                                   (trial_root / "verifier" / "reward.json").as_posix(),
                                   (trial_root / "verifier" / "scorecard.json").as_posix(),
                                   (trial_root / "agent" / "trajectory.jsonl.zst").as_posix()})
        actual_files = {path.relative_to(stage).as_posix() for path in stage.rglob("*") if path.is_file()}
        if actual_files != expected_files:
            raise BatchPacketError("packet file tree differs from the exact public allowlist")
        try:
            stage.rename(target)
        except FileExistsError:
            raise BatchPacketError("packet destination appeared during build; refusing overwrite") from None
    finally:
        if stage.exists():
            if stage.is_symlink() or stage.resolve().parent != output_base.resolve():
                raise BatchPacketError("staging directory escaped output root; refusing cleanup")
            shutil.rmtree(stage)
    return target


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Assemble a private packet from one complete validated 75-task batch")
    parser.add_argument("--batch-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path,
                        default=repo / "Submissions" / "submission_full_2026-10-20" / "packet")
    parser.add_argument("--submission-id", required=True)
    parser.add_argument("--date", dest="submission_date", required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--contact", required=True)
    args = parser.parse_args(argv)
    try:
        path = assemble_full_batch_packet(args.batch_root, args.output_root, args.submission_id,
                                          args.submission_date, args.team, args.contact)
    except Exception as exc:
        print(json.dumps({"status": "rejected", "error_type": type(exc).__name__, "reason": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(json.dumps({"status": "assembled", "packet_path": str(path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
