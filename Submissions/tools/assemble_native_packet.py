"""Assemble a private χ-Bench packet from one validated HealthHarness pilot.

This producer never runs an actor or verifier. It copies recorded run results
and official files, and exports the saved native engine messages as a clearly
identified non-ATIF transcript using chi-bench's JSONL+zstd packer.
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
import sqlite3
import sys
import tempfile
from typing import Any, Callable


TASK_ID = "pa_t012_t012_o001_p01_triage_payer"
EXPECTED_SOURCE_PREFIX = "03c845d"
RUNTIME_IMAGE = "sha256:420d28d0f15af56241c8ca212dcdea63acea1d9113a5fbbb5189368964684f66"
PACKET_SCHEMA = "chi-bench/submission/v1"
DATASET_VERSION = "chi-bench-v1.0.0"
TRIALS = ("trial-1", "trial-2", "trial-3")
CSV_FIELDS = ("benchmark", "dataset_version", "submission_id", "team", "agent", "model",
              "domain", "pass_at_1", "n_trials", "n_tasks", "mean_cost_usd",
              "mean_walltime_s", "submitted_at")
ALLOWED_FILES = {
    "submission.json", "results.csv", "sub.yaml", "provenance.json", "README.md",
    *(f"trials/pa_um/{trial}/{rel}" for trial in TRIALS for rel in (
        "result.json", "verifier/reward.json", "verifier/scorecard.json", "agent/trajectory.jsonl.zst")),
}


class PacketError(ValueError):
    """Inputs do not support a safe, reproducible packet."""


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
        raise PacketError(f"{label} is missing or invalid JSON") from None
    if not isinstance(value, dict):
        raise PacketError(f"{label} must be a JSON object")
    return value


def _load_aggregator() -> Any:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "HealthHarnessCodex" / "evaluations" / "aggregate_official_pilot.py"
    spec = importlib.util.spec_from_file_location("health_harness_pilot_aggregator", path)
    if spec is None or spec.loader is None:
        raise PacketError("the local pilot validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _utc(ts: Any, label: str) -> str:
    if isinstance(ts, bool) or not isinstance(ts, (int, float)):
        raise PacketError(f"recorded {label} time is missing")
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _recorded_run_times(events_path: Path) -> tuple[str, str]:
    starts: list[float] = []
    finishes: list[float] = []
    try:
        rows = events_path.read_text(encoding="utf-8").splitlines()
        for row in rows:
            event = json.loads(row)
            if not isinstance(event, dict):
                continue
            kind, timestamp = event.get("kind"), event.get("time")
            if kind in {"run_started", "run_finished"} and isinstance(timestamp, (int, float)) and not isinstance(timestamp, bool):
                (starts if kind == "run_started" else finishes).append(float(timestamp))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise PacketError("recorded event timestamps are missing or invalid") from None
    if len(starts) != 1 or len(finishes) != 1 or finishes[0] < starts[0]:
        raise PacketError("each trial must have one ordered recorded run start and finish")
    return _utc(starts[0], "start"), _utc(finishes[0], "finish")


def _extract_native_messages(snapshot: Path) -> list[dict[str, Any]]:
    before_hash = _sha256(snapshot)
    uri = "file:" + snapshot.resolve().as_posix().replace("?", "%3F") + "?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise PacketError("state snapshot failed SQLite integrity_check")
            rows = connection.execute("SELECT state_json FROM cases").fetchall()
            if len(rows) != 1:
                raise PacketError("state snapshot must contain exactly one case")
            state = json.loads(rows[0][0])
        finally:
            connection.close()
    except PacketError:
        raise
    except (sqlite3.Error, json.JSONDecodeError, TypeError, OSError):
        raise PacketError("state snapshot cannot be read as a native case state") from None
    if _sha256(snapshot) != before_hash:
        raise PacketError("read-only state snapshot changed during extraction")
    messages = state.get("messages") if isinstance(state, dict) else None
    if not isinstance(messages, list) or not messages or not all(isinstance(message, dict) for message in messages):
        raise PacketError("state snapshot has no faithful native message list")
    return messages


def _default_packer(src: Path, dst: Path) -> None:
    try:
        from chi_bench.experiment.trajectory_pack import pack_trajectory_to_jsonl_zst
    except ImportError:
        raise PacketError("chi-bench trajectory packer is unavailable in this runtime") from None
    pack_trajectory_to_jsonl_zst(src, dst)


def _write_trajectory(snapshot: Path, destination: Path, trial_name: str,
                      packer: Callable[[Path, Path], None]) -> int:
    messages = _extract_native_messages(snapshot)
    payload = {
        "schema_version": "health-harness/native-transcript/v1",
        "session_id": f"sqlite-sha256:{_sha256(snapshot)}",
        "agent": {"name": "HealthHarnessCodex"},
        "steps": messages,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{trial_name}-trajectory-") as temp_dir:
        source = Path(temp_dir) / "native-transcript.json"
        source.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        packer(source, destination)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise PacketError("trajectory packer did not create a non-empty compressed transcript")
    return len(messages)


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _write_sub_yaml(path: Path, submission_id: str, team: str, contact: str, model: str,
                    fixed: dict[str, Any]) -> None:
    path.write_text(
        "schema: health-harness/native-packet-export/v1\n"
        "submission:\n"
        f"  id: {_yaml_string(submission_id)}\n"
        f"  team: {_yaml_string(team)}\n"
        f"  contact: {_yaml_string(contact)}\n"
        "  agent: HealthHarnessCodex\n"
        f"  model: {_yaml_string(model)}\n"
        "  notes: Derived native run export; not the original chi-bench submission configuration.\n"
        f"  reasoning_effort: {_yaml_string(fixed['reasoning_effort'])}\n"
        f"  task_id: {_yaml_string(fixed['task_id'])}\n"
        f"  source_commit: {_yaml_string(fixed['source_commit'])}\n"
        f"  composition: {_yaml_string(fixed['composition'])}\n"
        f"run:\n  n_trials: 3\n  execution: native standalone Codex harness\n"
        f"  budgets: {json.dumps(fixed['budgets'], ensure_ascii=False)}\n"
        "dataset:\n  version: chi-bench-v1.0.0\n  domains: [pa_um]\n",
        encoding="utf-8")


def _copy_source(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    if _sha256(src) != _sha256(dst):
        raise PacketError(f"verbatim copy failed for {src.name}")


def _source_record(root: Path, path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "sha256": _sha256(path), "bytes": path.stat().st_size}


def _write_csv(path: Path, manifest: dict[str, Any]) -> None:
    sub, dataset, results = manifest["submission"], manifest["dataset"], manifest["results"]
    rows = []
    for domain, score in [("overall", results["overall"]), *results["per_domain"].items()]:
        rows.append({"benchmark": dataset["name"], "dataset_version": dataset["version"],
                     "submission_id": sub["id"], "team": sub["team"], "agent": sub["agent"],
                     "model": sub["model"], "domain": domain,
                     "pass_at_1": score["pass_at_1"], "n_trials": score["n_trials"],
                     "n_tasks": score["n_tasks"], "mean_cost_usd": "",
                     "mean_walltime_s": score.get("mean_walltime_s"),
                     "submitted_at": sub["submitted_at"]})
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def assemble_packet(pilot_root: Path, output_root: Path, submission_id: str = "submission_1",
                    submission_date: str = "2026-10-20", team: str | None = None,
                    contact: str | None = None, allow_unconfirmed_identity: bool = False,
                    packer: Callable[[Path, Path], None] | None = None) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", submission_id):
        raise PacketError("submission id must be a lowercase slug")
    try:
        packet_date = date.fromisoformat(submission_date)
    except ValueError:
        raise PacketError("submission date must be YYYY-MM-DD") from None
    if packet_date > datetime.now(timezone.utc).date():
        raise PacketError("submission date cannot be in the future")
    if not allow_unconfirmed_identity and (not team or not contact):
        raise PacketError("team and contact are required unless the packet is explicitly marked unconfirmed")
    identity_confirmed = bool(team and contact)
    team = team or "not provided"
    contact = contact or "not provided"

    root = Path(pilot_root).resolve(strict=True)
    aggregator = _load_aggregator()
    try:
        aggregate = aggregator.aggregate_pilot(root)
    except aggregator.PilotAggregationError as exc:
        raise PacketError(f"pilot validation failed: {exc}") from None
    fixed = aggregate["fixed_configuration"]
    if fixed.get("task_id") != TASK_ID or not str(fixed.get("source_commit", "")).startswith(EXPECTED_SOURCE_PREFIX):
        raise PacketError("pilot does not match the requested frozen UM task and source version")
    official = aggregate["trials"]
    if len(official) != 3 or any(t["official_reward"] != 1 or t["scorecard"] != {
            "passed": 21, "failed": 0, "not_applicable": 0, "non_na": 21, "total": 21,
            "failed_check_names": []} for t in official):
        raise PacketError("packet requires three official 21/21 strict passes")

    out_base = Path(output_root).resolve()
    target = out_base / f"{packet_date.isoformat()}-{submission_id}"
    out_base.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise PacketError("packet destination already exists; refusing overwrite")
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    packer = packer or _default_packer
    stage = Path(tempfile.mkdtemp(prefix=f".{submission_id}-staging-", dir=out_base))
    try:
        trial_records = []
        walltimes = []
        for index, trial_name in enumerate(TRIALS, start=1):
            trial_source = root / trial_name
            attempt = trial_source / "attempt-1"
            eval_path = attempt / "evaluation.json"
            run_path = attempt / "run.result.json"
            state_path = attempt / "state.snapshot.sqlite"
            events_path = attempt / "events.jsonl"
            receipt = _read_json(trial_source / "official-evaluation-receipt.json", "official receipt")
            verifier_dir = trial_source / Path(receipt["verifier_dir"])
            reward_path, scorecard_path = verifier_dir / "reward.json", verifier_dir / "scorecard.json"
            evaluation = _read_json(eval_path, "evaluation")
            metadata = evaluation["metadata"]
            local_status = evaluation["harness_status"]
            run_start, run_finish = _recorded_run_times(events_path)
            run_result = _read_json(run_path, "run result")
            elapsed = run_result.get("elapsed_seconds")
            if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or elapsed < 0:
                raise PacketError(f"{trial_name} has no recorded owner-loop duration")
            walltimes.append(float(elapsed))

            rel_trial = Path("trials") / "pa_um" / trial_name
            _copy_source(run_path, stage / rel_trial / "result.json")
            _copy_source(reward_path, stage / rel_trial / "verifier" / "reward.json")
            _copy_source(scorecard_path, stage / rel_trial / "verifier" / "scorecard.json")
            message_count = _write_trajectory(state_path, stage / rel_trial / "agent" / "trajectory.jsonl.zst",
                                              trial_name, packer)
            artifact_paths = [eval_path, run_path, events_path, state_path,
                              trial_source / "official-evaluation-receipt.json",
                              reward_path, scorecard_path, verifier_dir / "verifier_context.json"]
            trial_records.append({
                "trial_id": trial_name,
                "official_reward": 1,
                "scorecard": {k: aggregate["trials"][index - 1]["scorecard"][k]
                              for k in ("passed", "failed", "not_applicable", "total")},
                "local_harness_status": local_status,
                "model_calls": aggregate["trials"][index - 1]["model_calls"],
                "engine_tool_calls": aggregate["trials"][index - 1]["engine_tool_calls"],
                "owner_loop_seconds": float(elapsed),
                "recorded_run_started_at": run_start,
                "recorded_run_finished_at": run_finish,
                "native_message_count": message_count,
                "source_artifacts": {p.relative_to(root).as_posix(): _source_record(root, p)
                                     for p in artifact_paths},
                "trajectory_sha256": _sha256(stage / rel_trial / "agent" / "trajectory.jsonl.zst"),
            })

        pass_score = aggregate["one_task_pilot_metrics"]
        mean_walltime = sum(walltimes) / len(walltimes)
        overall = {"pass_at_1": pass_score["pass_at_1"], "n_trials": 3, "n_tasks": 1,
                   "pass_at_3": pass_score["pass_at_3"], "pass_power_3": pass_score["pass_power_3"],
                   "mean_walltime_s": mean_walltime,
                   "scope_note": "One public UM development task, three fresh worlds; not full-benchmark performance."}
        submission = {
            "id": submission_id, "team": team, "contact": contact,
            "agent": "HealthHarnessCodex", "model": fixed["model"],
            "reasoning_effort": fixed["reasoning_effort"], "submitted_at": stamp,
            "notes": "Private local packet draft; one-task development pilot, not a full-benchmark result.",
            "publication_ready": False,
        }
        manifest = {
            "schema": PACKET_SCHEMA,
            "submission": submission,
            "dataset": {"name": "chi-bench", "version": DATASET_VERSION, "domains": ["pa_um"]},
            "results": {"overall": overall, "per_domain": {"pa_um": dict(overall)}},
            "provenance": {},
        }
        _write_csv(stage / "results.csv", manifest)
        (stage / "submission.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _write_sub_yaml(stage / "sub.yaml", submission_id, team, contact, fixed["model"], fixed)
        provenance = {
            "chi_bench_git_sha": "4444a07fa68a4f1623f841a292a54e284fc8e7f7",
            "image_digest": RUNTIME_IMAGE,
            "judge_model": "not_applicable:deterministic-verifier",
            "harness_version": f"HealthHarnessCodex@{fixed['source_commit']}",
            "producer_script_sha256": _sha256(Path(__file__).resolve()),
            "actor_source_commit": fixed["source_commit"],
            "actor_source_fingerprint": fixed["source_fingerprint"],
            "task_id": fixed["task_id"],
            "model": fixed["model"],
            "reasoning_effort": fixed["reasoning_effort"],
            "budgets": fixed["budgets"],
            "composition": fixed["composition"],
            "configuration_source": "Comparable frozen configuration fields copied from each validated trial evaluation metadata.",
            "runtime_image_digest": RUNTIME_IMAGE,
            "judge_execution": "No judge checks were present in the three official scorecards; no judge inference was run.",
            "identity_confirmed": identity_confirmed,
            "publication_ready": False,
            "publication_limitations": [
                "Team/contact identity is unconfirmed." if not identity_confirmed else "Public submission has not been authorized.",
                "This is one development task, not held-out or full-benchmark validation.",
                "Acceptance of a one-task partial submission within a domain is not confirmed by the public packet docs.",
                "Cost was not measured; mean_cost_usd is intentionally omitted.",
            ],
            "trajectory": {
                "schema_version": "health-harness/native-transcript/v1",
                "source": "messages field from the integrity-checked, read-only state.snapshot.sqlite cases.state_json",
                "steps": "Faithful original engine message objects; no per-step timestamps.",
                "session_id": "Derived transcript artifact ID sqlite-sha256:<snapshot SHA-256>; not a provider or Harbor session ID.",
                "derived_from_snapshot_sha256": True,
                "not_provider_session_id": True,
                "encoding": "chi_bench.experiment.trajectory_pack.pack_trajectory_to_jsonl_zst, zstd level 19",
                "not_atif_or_harbor": True,
            },
            "timing_scope": "Recorded run_started/run_finished UTC event times; owner-loop elapsed_seconds excludes setup and official grading.",
            "packaging_time_utc": stamp,
            "submission_date": packet_date.isoformat(),
            "pilot_root_name": root.name,
            "pilot_metrics": pass_score,
            "trials": trial_records,
        }
        (stage / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest["provenance"] = provenance
        (stage / "submission.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        readme = (
            f"# {submission_id} local packet\n\n"
            "This packet contains three official passes for one public UM development task. "
            "It is a private local draft, not a full-benchmark estimate or clinical certification.\n\n"
            f"- Official pass@1: {overall['pass_at_1']:.3f} (3/3)\n"
            f"- Official pass@3: {overall['pass_at_3']}\n- Official pass^3: {overall['pass_power_3']}\n"
            f"- Mean owner-loop time: {mean_walltime:.3f} seconds (setup/grading excluded)\n"
            "- Cost: unknown; omitted from results.\n"
            f"- Local statuses: {', '.join(record['local_harness_status'] for record in trial_records)}.\n"
            f"- Publication ready: no. Team/contact identity confirmed: {str(identity_confirmed).lower()}.\n"
            "- One-task partial-domain acceptance is not confirmed by the public packet contract.\n\n"
            "The compressed trajectory is a HealthHarness native-message transcript, not a strict ATIF or Harbor session. "
            "Its session_id is a derived SQLite snapshot hash, not a provider/Harbor session identifier; "
            "maintainer acceptance of this native trajectory export is unconfirmed. "
            "Each `result.json` is copied verbatim from the recorded native run result; reward and scorecard files "
            "are copied verbatim from the receipt-selected official verifier directory.\n"
        )
        (stage / "README.md").write_text(readme, encoding="utf-8")
        actual_files = {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()}
        if actual_files != ALLOWED_FILES:
            raise PacketError("packet output file set differs from the public allowlist")
        try:
            stage.rename(target)
        except FileExistsError:
            raise PacketError("packet destination appeared during assembly; refusing overwrite") from None
    finally:
        if stage.exists():
            if stage.is_symlink() or stage.resolve().parent != out_base.resolve():
                raise PacketError("temporary staging directory escaped the output root; refusing cleanup")
            shutil.rmtree(stage)
    return target


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build a private packet from a validated three-trial UM pilot")
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path,
                        default=repo / "Submissions" / "submission_1_2026-10-20" / "packet")
    parser.add_argument("--submission-id", default="submission_1")
    parser.add_argument("--date", default="2026-10-20", dest="submission_date")
    parser.add_argument("--team")
    parser.add_argument("--contact")
    parser.add_argument("--allow-unconfirmed-identity", action="store_true")
    args = parser.parse_args(argv)
    try:
        target = assemble_packet(args.pilot_root, args.output_root, args.submission_id,
                                 args.submission_date, args.team, args.contact,
                                 args.allow_unconfirmed_identity)
    except (PacketError, OSError) as exc:
        print(json.dumps({"status": "rejected", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"status": "assembled", "packet_path": str(target)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
