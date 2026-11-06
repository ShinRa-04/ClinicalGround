"""Plan and run official grading from immutable deferred actor snapshots.

Planning is read-only and does not contact Docker. The execution path verifies
every actor world is stopped before invoking the pinned official verifier.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
from typing import Any, Callable, Protocol

from . import batch


class DeferredGradingError(RuntimeError):
    """A deferred run is incomplete, changed, or unsafe to grade."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _read_manifest(run_dir: Path, *, allow_experimental: bool = False) -> dict[str, Any]:
    run_root = Path(run_dir).resolve(strict=True)
    runs_root = Path(__file__).resolve().parents[1] / "runs"
    if not run_root.is_relative_to(runs_root.resolve()):
        raise DeferredGradingError("run_dir must be inside ignored HealthHarnessCodex/runs")
    path = run_root / "batch.manifest.json"
    if path.is_symlink() or not path.is_file():
        raise DeferredGradingError("batch manifest is missing or linked")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise DeferredGradingError("batch manifest is invalid") from None
    frozen = manifest.get("frozen_config") if isinstance(manifest, dict) else None
    if not isinstance(frozen, dict) or frozen.get("defer_grading") is not True:
        raise DeferredGradingError("batch was not frozen in deferred-grading mode")
    simulator = frozen.get("simulator")
    if not allow_experimental and isinstance(simulator, dict) and simulator.get("backend") in batch.SPOOL_BACKENDS:
        raise DeferredGradingError("experimental simulator runs are not eligible for official grading")
    return manifest


def plan_deferred_grading(run_dir: Path, dataset_root: Path, *, allow_experimental: bool = False) -> dict[str, Any]:
    """Read-only validation of the complete selected batch and snapshot hashes."""
    run_root = Path(run_dir).resolve(strict=True)
    manifest = _read_manifest(run_root, allow_experimental=allow_experimental)
    frozen = manifest.get("frozen_config")
    records = manifest.get("tasks")
    if not isinstance(frozen, dict) or not isinstance(records, list) or not records:
        raise DeferredGradingError("batch manifest has no selected tasks")
    domain_keys = frozen.get("domains")
    if (not isinstance(domain_keys, list) or not domain_keys or
            any(domain not in batch.CANONICAL_DOMAINS for domain in domain_keys)):
        raise DeferredGradingError("frozen domains are invalid")
    planned: list[dict[str, Any]] = []
    expected_task_hashes = frozen.get("task_instruction_sha256")
    if not isinstance(expected_task_hashes, dict):
        raise DeferredGradingError("frozen public instruction hashes are missing")
    seen: set[tuple[str, str]] = set()
    for task in records:
        if not isinstance(task, dict):
            raise DeferredGradingError("batch task record is invalid")
        domain, task_id = task.get("domain"), task.get("task_id")
        key = (domain, task_id)
        if (not isinstance(domain, str) or domain not in domain_keys or
                not isinstance(task_id, str) or not task_id or task_id in {".", ".."} or
                any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for ch in task_id) or
                key in seen):
            raise DeferredGradingError("batch contains an invalid or duplicate task identity")
        seen.add(key)
        public_dir = (Path(dataset_root).resolve(strict=True) /
                      batch.CANONICAL_DOMAINS[domain] / "tasks" / task_id)
        if not public_dir.resolve(strict=True).is_relative_to(Path(dataset_root).resolve(strict=True)):
            raise DeferredGradingError("selected task path escaped the public dataset root")
        instruction = public_dir / "instruction.md"
        if instruction.is_symlink() or not instruction.is_file():
            raise DeferredGradingError("a selected public task instruction is missing or linked")
        actual_hash = batch._sha256_file(instruction)
        hash_key = f"{domain}/{task_id}"
        if (actual_hash != task.get("instruction_sha256") or
                expected_task_hashes.get(hash_key) != actual_hash):
            raise DeferredGradingError("a selected public task instruction changed")
        attempts = task.get("attempts")
        expected_count = frozen.get("attempts")
        if not isinstance(attempts, list) or len(attempts) != expected_count or not attempts:
            raise DeferredGradingError("selected task attempts are incomplete")
        planned_attempts = []
        attempt_numbers: set[int] = set()
        for attempt in attempts:
            if not isinstance(attempt, dict) or attempt.get("status") != "deferred_ready":
                raise DeferredGradingError("every selected actor attempt must be settled and deferred-ready")
            number = attempt.get("attempt")
            if (not isinstance(number, int) or isinstance(number, bool) or
                    number < 1 or number > expected_count or number in attempt_numbers):
                raise DeferredGradingError("selected actor attempts must have unique frozen numbers")
            attempt_numbers.add(number)
            if attempt.get("grading_status") != "pending" or attempt.get("official_score") is not None:
                raise DeferredGradingError("deferred attempt grading state is invalid")
            if attempt.get("container_stopped") is not True:
                raise DeferredGradingError("every selected actor world must be recorded stopped")
            snapshot = batch._verify_deferred_attempt(run_root, task, attempt, frozen)
            planned_attempts.append({
                "attempt": number,
                "container_name": attempt["container_name"],
                "snapshot": snapshot.relative_to(run_root).as_posix(),
                "snapshot_manifest_sha256": attempt["deferred_snapshot"]["manifest_sha256"],
            })
        planned.append({"domain": domain, "task_id": task_id, "attempts": planned_attempts})
    try:
        frozen_keys = {tuple(value.split("/", 1)) for value in expected_task_hashes
                       if isinstance(value, str) and value.count("/") == 1}
    except (TypeError, ValueError):
        raise DeferredGradingError("frozen task hash keys are invalid") from None
    if len(frozen_keys) != len(expected_task_hashes) or seen != frozen_keys:
        raise DeferredGradingError("selected task set differs from the frozen instruction hash set")
    return {"status": "plan_only", "run_dir": str(run_root),
            "source_commit": frozen.get("source_commit"),
            "source_fingerprint": frozen.get("source_fingerprint"),
            "model": frozen.get("model"), "reasoning_effort": frozen.get("reasoning_effort"),
            "selected_tasks": len(planned),
            "selected_attempts": sum(len(task["attempts"]) for task in planned),
            "tasks": planned,
            "no_docker_no_inference_no_grading": True}


class OfflineGrader(Protocol):
    def __call__(self, snapshot: Path, task: dict[str, Any], attempt: dict[str, Any],
                 work_dir: Path) -> dict[str, Any]: ...


class DockerWorldStateCheck:
    """Read-only Docker check. It never starts, stops, or changes a world."""

    def __init__(self, docker: str = "docker"):
        self.docker = docker

    def __call__(self, container_name: str) -> bool:
        try:
            result = subprocess.run(
                [self.docker, "inspect", "--format", "{{.State.Running}}", container_name],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=15, check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0 and result.stdout.strip().casefold() == "false"


class DockerOfflineGrader:
    """Run the unchanged official verifier with only its export transport replaced."""

    def __init__(self, *, docker: str, env_file: Path, allow_network: bool):
        self.docker = docker
        self.env_file = env_file
        self.allow_network = allow_network

    def command(self, task: dict[str, Any], work_dir: Path) -> list[str]:
        logs_dir = work_dir / "logs"
        container_hash = hashlib.sha256((str(work_dir.resolve()) + task["task_id"]).encode("utf-8")).hexdigest()[:12]
        container_name = f"bigdata-health-codex-grade-{container_hash}"
        return [self.docker, "run", "--name", container_name, "--network", "bridge",
                "--label", f"com.bigdata.workspace={batch.ROOT_LABEL}",
                "--label", "com.bigdata.ownedcase=1",
                "--mount", f"type=bind,source={logs_dir.resolve()},target=/logs",
                "--env-file", str(self.env_file),
                "--env", f"CHI_BENCH_TASK_ID={task['task_id']}",
                "--env", "CHI_BENCH_TASKS_ROOT=/opt/chi-bench/tasks",
                "--env", "CHI_BENCH_JUDGE_MODEL=claude-opus-4-7",
                "--env", "CHI_BENCH_JUDGE_NUM_VOTES=1",
                "--entrypoint", "/workspace/.venv/bin/python",
                batch.RUNTIME_IMAGE_SHA256, "-c", self._script(task["task_id"])]

    @staticmethod
    def _script(task_id: str) -> str:
        # Captured stdout/stderr and private verifier outputs stay in ignored runs.
        return r'''import contextlib,hashlib,io,json,pathlib,sys
from chi_bench.verifier import task_runtime as tr
saved=pathlib.Path('/logs/deferred_snapshot/exported_state.json')
expected='http://127.0.0.1:8023/export'
def fixed_export(url,timeout=5.0):
 if url!=expected: raise RuntimeError('unexpected_export_url')
 value=json.loads(saved.read_text(encoding='utf-8'))
 if not isinstance(value,dict): raise RuntimeError('snapshot_export_not_object')
 return value
tr.fetch_json=fixed_export
root=pathlib.Path('/opt/chi-bench/tasks')/TASK/'fixtures'/'expectations.json'
out=pathlib.Path('/logs/late_grade')
out.mkdir(parents=True,exist_ok=True)
private=io.StringIO()
try:
 with contextlib.redirect_stdout(private),contextlib.redirect_stderr(private):
  code=tr.run_verifier(expectations_path=root,reward_path=out/'reward.json',scorecard_path=out/'scorecard.json',exported_state_path=out/'exported_state.json',verifier_context_path=out/'verifier_context.json',verifier_host='127.0.0.1',verifier_port=8023)
except Exception as e:
 code=None
 private.write(type(e).__name__)
(out/'verifier.private.log').write_text(private.getvalue(),encoding='utf-8')
names=('reward.json','scorecard.json','exported_state.json','verifier_context.json')
print(json.dumps({'returncode':code,'artifacts':{n:{'exists':(out/n).is_file(),'bytes':(out/n).stat().st_size if (out/n).is_file() else None,'sha256':hashlib.sha256((out/n).read_bytes()).hexdigest() if (out/n).is_file() else None} for n in names}}))
'''.replace("TASK", json.dumps(task_id))

    def __call__(self, snapshot: Path, task: dict[str, Any], attempt: dict[str, Any],
                 work_dir: Path) -> dict[str, Any]:
        if not self.allow_network or not self.env_file.is_file():
            raise DeferredGradingError("direct judge requires explicit network access and local Runner/.env")
        logs_dir = work_dir / "logs"
        logs_dir.mkdir(parents=True)
        shutil.copytree(snapshot / "logs", logs_dir, dirs_exist_ok=True, symlinks=False)
        if (logs_dir / "late_grade").exists() or (logs_dir / "late_grade").is_symlink():
            raise DeferredGradingError("grade output path already exists in copied actor logs")
        payload = logs_dir / "deferred_snapshot"
        payload.mkdir()
        shutil.copy2(snapshot / "exported_state.json", payload / "exported_state.json")
        command = self.command(task, work_dir)
        container_name = command[command.index("--name") + 1]
        existing = subprocess.run([self.docker, "inspect", container_name], capture_output=True,
                                  text=True, encoding="utf-8", errors="replace", timeout=10, check=False,
                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        if existing.returncode == 0:
            raise DeferredGradingError("grade container name is already in use; preserving it")
        result = None
        launch_error: Exception | None = None
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=900, check=False,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
        except (OSError, subprocess.TimeoutExpired) as exc:
            launch_error = exc
        finally:
            # Docker may keep a paid judge process alive after its CLI times out.
            try:
                cleanup = subprocess.run([self.docker, "rm", "--force", container_name],
                                          capture_output=True, timeout=30, check=False,
                                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
                cleanup_confirmed = cleanup.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                cleanup_confirmed = False
        if launch_error is not None:
            return {"status": "ungraded", "reason": f"offline_verifier_{type(launch_error).__name__}",
                    "grader_container_cleanup_confirmed": cleanup_confirmed}
        if not cleanup_confirmed:
            return {"status": "ungraded", "reason": "grader_container_cleanup_unconfirmed",
                    "grader_container_cleanup_confirmed": False}
        try:
            assert result is not None
            report = json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            return {"status": "ungraded", "reason": "offline_verifier_protocol_error",
                    "grader_container_cleanup_confirmed": cleanup_confirmed}
        status, grade = batch._official_grade(logs_dir, "late_grade", report.get("returncode"))
        return {"status": status, "official_score": grade.get("reward") if status == "graded" else None,
                "returncode": report.get("returncode"), "grade": grade,
                "transport": "offline_snapshot_export_transport",
                "grade_output": "late_grade", "grader_container_cleanup_confirmed": cleanup_confirmed}


class OpenRouterOfflineGrader(DockerOfflineGrader):
    """Benchmark verifier and WorkspaceJudge with explicitly alternate transport."""

    def __init__(self, *, max_budget_usd: float = 0.50, key_limit_enforced: bool = False, **kwargs):
        super().__init__(**kwargs)
        if not 0 < max_budget_usd <= 0.50:
            raise DeferredGradingError("OpenRouter budget must be positive and at most $0.50")
        self.max_budget_usd = max_budget_usd
        self.key_limit_enforced = key_limit_enforced

    def command(self, task, work_dir):
        command = super().command(task, work_dir)
        index = command.index("--entrypoint")
        code_root = Path(__file__).resolve().parents[1]
        command[index:index] = ["--mount", f"type=bind,source={code_root},target=/adapter,readonly"]
        original = command[-1]
        injection = '''sys.path.insert(0,'/adapter')
from health_harness_codex.openrouter_judge import OpenRouterJudgeRunner
runner=OpenRouterJudgeRunner(pathlib.Path('/logs/openrouter_judge'),max_budget_usd=BUDGET,key_limit_enforced=KEY_LIMIT)
original_collect=tr.collect_all_verifier_checks
def with_openrouter(*args,**kwargs):
 kwargs['judge']=runner
 return original_collect(*args,**kwargs)
tr.collect_all_verifier_checks=with_openrouter
'''.replace("BUDGET", repr(self.max_budget_usd)).replace("KEY_LIMIT", repr(self.key_limit_enforced))
        command[-1] = original.replace("tr.fetch_json=fixed_export", "tr.fetch_json=fixed_export\n" + injection)
        return command

    def __call__(self, *args, **kwargs):
        output = super().__call__(*args, **kwargs)
        score = output.pop("official_score", None)
        output.update(transport="openrouter_opus_4_7_workspace_runner",
                      official_score=None, evaluator_score=score,
                      competition_acceptance="not established for alternate transport")
        if output["status"] == "graded":
            output["status"] = "evaluated"
        return output


def _runner_command_preview(docker: str, env_file: Path, logs_root: Path, task_id: str) -> list[str]:
    returner = DockerOfflineGrader(docker=docker, env_file=env_file, allow_network=True)
    return returner.command({"task_id": task_id}, logs_root)


def _validate_env_file(path: Path, allow_network: bool) -> Path:
    if not allow_network:
        raise DeferredGradingError("--grade-later requires explicit --allow-benchmark-network")
    if path is None:
        raise DeferredGradingError("--grade-later requires the ignored local Runner/.env file")
    original = Path(path)
    if original.is_symlink():
        raise DeferredGradingError("benchmark environment file must not be a symlink")
    try:
        resolved = original.resolve(strict=True)
    except OSError:
        raise DeferredGradingError("benchmark environment file is unavailable") from None
    expected = batch.PROJECT_ROOT / "Runner" / ".env"
    if resolved != expected.resolve() or resolved.name != ".env" or not resolved.is_file():
        raise DeferredGradingError("direct judge environment must be ignored local Runner/.env")
    return resolved


def _grade_artifact_inventory(work_dir: Path) -> dict[str, Any]:
    logs = work_dir / "logs" / "late_grade"
    if not logs.is_dir():
        return {"files": []}
    return batch._tree_inventory(logs)


def run_grade_later(run_dir: Path, dataset_root: Path, *, plan_only: bool = True,
                    offline_grader: OfflineGrader | None = None,
                    container_state_check: Callable[[str], bool] | None = None,
                    docker: str = "docker", env_file: Path | None = None,
                    allow_network: bool = False, judge_transport: str = "direct",
                    max_budget_usd: float = 0.50, budget_mode: str = "reservation") -> dict[str, Any]:
    """Validate the full batch first, then grade each saved actor export once."""
    if judge_transport not in {"direct", "openrouter"}:
        raise DeferredGradingError("unknown judge transport")
    if budget_mode not in {"reservation", "key-limit"}:
        raise DeferredGradingError("unknown budget enforcement mode")
    alternate = judge_transport == "openrouter"
    plan = plan_deferred_grading(run_dir, dataset_root, allow_experimental=alternate)
    plan["judge_transport"] = judge_transport
    if alternate and plan["selected_attempts"] != 1:
        raise DeferredGradingError("bounded OpenRouter evaluation currently supports exactly one attempt")
    if plan_only:
        return plan
    manifest = _read_manifest(run_dir, allow_experimental=alternate)
    frozen = manifest["frozen_config"]
    run_root = Path(run_dir).resolve(strict=True)
    env_path = _validate_env_file(env_file, allow_network) if offline_grader is None else None
    state_check = container_state_check or DockerWorldStateCheck(docker)
    # Check all worlds and the image before starting any judge process.
    for task in manifest["tasks"]:
        for attempt in task["attempts"]:
            if not state_check(attempt["container_name"]):
                raise DeferredGradingError("a selected actor world is active or its stopped state is unverified")
    if offline_grader is None:
        image_check = subprocess.run([docker, "image", "inspect", "--format", "{{.Id}}", batch.RUNTIME_IMAGE],
                                     capture_output=True, text=True, encoding="utf-8", errors="replace",
                                     timeout=15, check=False)
        if image_check.returncode != 0 or image_check.stdout.strip() != batch.RUNTIME_IMAGE_SHA256:
            raise DeferredGradingError("pinned runtime image identity check failed")
        grader: OfflineGrader = (OpenRouterOfflineGrader(docker=docker, env_file=env_path,
            allow_network=True, max_budget_usd=max_budget_usd,
            key_limit_enforced=budget_mode == "key-limit") if alternate else
            DockerOfflineGrader(docker=docker, env_file=env_path, allow_network=True))
    else:
        grader = offline_grader
    grade_root = run_root / "late_grades"
    if grade_root.exists() and any(grade_root.iterdir()):
        raise DeferredGradingError("late grading already started for this actor batch; preserving existing grade records")
    grade_root.mkdir(exist_ok=True)
    execution_dir = grade_root / f"grade-run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    execution_dir.mkdir()
    if offline_grader is None:
        commands = []
        for task in manifest["tasks"]:
            for attempt in task["attempts"]:
                item_id = f"{task['domain']}__{task['task_id']}__attempt-{attempt['attempt']}"
                commands.append(grader.command(task, execution_dir / item_id))
        from decimal import Decimal, ROUND_HALF_UP
        sessions = Decimal(plan["selected_attempts"])
        estimate = lambda per_session: str((Decimal(per_session) * sessions).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP))
        print(json.dumps({"direct_judge_commands": commands,
                          "scope_attempts": plan["selected_attempts"],
                          "estimate_not_measured": {
                              "scope_scenarios": {"low": f"${estimate('0.15')}",
                                                  "middle": f"${estimate('0.375')}",
                                                  "high": f"${estimate('0.75')}"},
                              "per_session_scenarios": ["$0.15 (20k input + 2k output)",
                                                         "$0.375 (50k input + 5k output)",
                                                         "$0.75 (100k input + 10k output)"],
                              "limitations": "not a spending cap; judge usage, retries and tool turns may vary"}},
                   ensure_ascii=False), flush=True)
    entries: list[dict[str, Any]] = []
    partial_manifest_path = execution_dir / "grade-manifest.partial.json"

    def checkpoint(status: str = "grading") -> None:
        batch._atomic_json(partial_manifest_path, {
            "schema_version": 1, "created_at": _utc_now(),
            "actor_manifest_sha256": batch._sha256_file(run_root / "batch.manifest.json"),
            "frozen_source_commit": frozen.get("source_commit"),
            "grading_mode": ("openrouter_workspace_judge" if alternate else "official_direct_judge") if offline_grader is None else "injected_test_runner",
            "status": status, "grades": entries,
        })
    try:
        for task in manifest["tasks"]:
            for attempt in task["attempts"]:
                attempt_dir = run_root / attempt["attempt_dir"]
                snapshot = batch._verify_deferred_attempt(run_root, task, attempt, frozen)
                item_id = f"{task['domain']}__{task['task_id']}__attempt-{attempt['attempt']}"
                work_dir = execution_dir / item_id
                work_dir.mkdir()
                entries.append({"domain": task["domain"], "task_id": task["task_id"],
                                "attempt": attempt["attempt"],
                                "actor_snapshot_manifest_sha256": attempt["deferred_snapshot"]["manifest_sha256"],
                                "status": "grading", "official_score": None,
                                "transport": "offline_snapshot_export_transport" if offline_grader is None
                                else "synthetic_test_runner"})
                checkpoint()
                output = grader(snapshot, task, attempt, work_dir)
                if not isinstance(output, dict):
                    output = {"status": "ungraded", "reason": "grader_returned_invalid_result"}
                entries[-1].update(status=output.get("status", "ungraded"),
                                   evaluator_score=output.get("evaluator_score"),
                                   official_score=output.get("official_score") if output.get("status") == "graded" else None,
                                   transport=output.get("transport", entries[-1]["transport"]),
                                   output=output, grade_artifacts=_grade_artifact_inventory(work_dir))
                checkpoint()
        result = {"schema_version": 1, "created_at": _utc_now(),
                  "actor_manifest_sha256": batch._sha256_file(run_root / "batch.manifest.json"),
                  "frozen_source_commit": frozen.get("source_commit"),
                  "grading_mode": ("openrouter_workspace_judge" if alternate else "official_direct_judge") if offline_grader is None else "injected_test_runner",
                  "no_actor_replay": True, "grades": entries}
        batch._atomic_json(execution_dir / "grade-manifest.json", result)
        partial_manifest_path.unlink(missing_ok=True)
        return {"status": "grade_finished", "grade_manifest": str(execution_dir / "grade-manifest.json"),
                "grades": len(entries), "results": [{"domain": item["domain"], "task_id": item["task_id"],
                                                     "attempt": item["attempt"], "status": item["status"],
                                                     "official_score": item["official_score"],
                                                     "evaluator_score": item.get("evaluator_score")}
                                                    for item in entries]}
    except Exception:
        # Leave the append-only directory as a recoverable partial record.
        checkpoint("interrupted")
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan or execute grading from frozen actor snapshots")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--grade-later", action="store_true",
                        help="execute the official verifier after all snapshots/worlds validate")
    parser.add_argument("--allow-benchmark-network", action="store_true")
    parser.add_argument("--benchmark-env-file", type=Path)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--judge-transport", choices=("direct", "openrouter"), default="direct")
    parser.add_argument("--max-budget-usd", type=float, default=0.50)
    parser.add_argument("--budget-mode", choices=("reservation", "key-limit"), default="reservation",
                        help="key-limit requires a verified non-resetting OpenRouter key cap within --max-budget-usd")
    args = parser.parse_args(argv)
    try:
        result = run_grade_later(args.run_dir, args.dataset_root,
                                 plan_only=not args.grade_later, docker=args.docker,
                                 env_file=args.benchmark_env_file,
                                 allow_network=args.allow_benchmark_network,
                                 judge_transport=args.judge_transport,
                                 max_budget_usd=args.max_budget_usd, budget_mode=args.budget_mode)
    except Exception as exc:
        print(json.dumps({"status": "rejected", "error_type": type(exc).__name__, "reason": str(exc)},
                         ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
