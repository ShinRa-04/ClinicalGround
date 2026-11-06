"""Local operations around the unchanged official run/submission tools."""

from __future__ import annotations

import importlib.metadata
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/runner')
BENCH = ROOT / 'chi-bench'
LEADERBOARD = ROOT / 'leaderboard'
DATASET = Path('/dataset')
DATA = DATASET / 'chi-bench'
PUBLIC_REPO = 'actava/chi-bench'
PUBLIC_REVISION = 'chi-bench-v1.0.0'
HANDBOOK_REPO = 'actava/managed-care-operations-handbook'
HANDBOOK = DATA / 'skills/managed-care-operations-handbook/SKILL.md'
RUNTIME_IMAGE = 'bigdata-chi-bench:runtime-4444a07'
RUNTIME_NODE_MAJOR = '22'
RUNTIME_CLAUDE_CLI = '2.1.302'


def call(args: list[str], cwd: Path = BENCH) -> int:
    return subprocess.run(args, cwd=cwd, check=False).returncode


def receipt(name: str, details: dict) -> None:
    folder = (DATASET / 'receipts' if name in
              ('public-data-download.json', 'handbook-download.json') else ROOT / 'logs')
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(details, indent=2) + '\n', encoding='utf-8')


def download(handbook: bool = False) -> int:
    from huggingface_hub import HfApi, get_token, snapshot_download

    repo = HANDBOOK_REPO if handbook else PUBLIC_REPO
    token = get_token() if handbook else False
    if handbook and not token:
        print('Handbook download needs approved access and local login. Run: .\\toolkit.ps1 hf auth login', file=sys.stderr)
        return 2
    revision = 'main' if handbook else PUBLIC_REVISION
    info = HfApi(token=token).dataset_info(repo, revision=revision)
    destination = DATA / 'skills' if handbook else DATA
    snapshot_download(repo, repo_type='dataset', revision=info.sha,
                      local_dir=destination, token=token, max_workers=8)
    if handbook:
        if not HANDBOOK.is_file():
            raise RuntimeError('Downloaded handbook layout is missing its expected SKILL.md.')
    else:
        (DATA / '.chi-bench-version').write_text(PUBLIC_REVISION + '\n', encoding='utf-8')
    details = {'repository': repo, 'revision': revision, 'resolved_commit': info.sha,
               'destination': str(destination), 'files': len(info.siblings)}
    receipt('handbook-download.json' if handbook else 'public-data-download.json', details)
    print(json.dumps(details, indent=2))
    return 0


def doctor() -> int:
    from huggingface_hub import get_token

    engine = subprocess.run(['docker', 'info', '--format', '{{.ServerVersion}}'],
                            capture_output=True, text=True)
    runtime = subprocess.run(['docker', 'image', 'inspect', 'chi-bench:latest',
                             '--format', '{{.Id}}'], capture_output=True, text=True)
    pin = DATA / '.chi-bench-version'
    counts = {domain: len(list((DATA / domain / 'tasks').glob('*/instruction.md')))
              for domain in ('prior_auth_provider', 'prior_auth_um', 'care_management')}
    details = {
        'chi_bench_version': importlib.metadata.version('chi-bench'),
        'harbor_version': importlib.metadata.version('harbor'),
        'python': sys.version.split()[0],
        'docker_engine': engine.stdout.strip() if engine.returncode == 0 else None,
        'dataset_pin': pin.read_text().strip() if pin.is_file() else None,
        'dataset_root': str(DATA),
        'public_task_counts': counts,
        'handbook_present': HANDBOOK.is_file(),
        'huggingface_login_present': bool(get_token()),
        'provider_keys_present': {name: bool(os.environ.get(name)) for name in
                                  ('ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY', 'OPENROUTER_API_KEY')},
        'runtime_image_present': runtime.returncode == 0,
        'runtime_image_id': runtime.stdout.strip() if runtime.returncode == 0 else None,
    }
    print(json.dumps(details, indent=2))
    receipt('doctor.json', details)
    return 0 if engine.returncode == 0 else 2


def prepare_runtime() -> int:
    if not HANDBOOK.is_file():
        print('Runtime build needs the approved handbook. Request access, log in, then run download-handbook.', file=sys.stderr)
        return 2
    if not (DATA / '.chi-bench-version').is_file():
        print('Run download-public first.', file=sys.stderr)
        return 2
    current = subprocess.run(['docker', 'image', 'inspect', 'chi-bench:latest',
                              '--format', '{{index .Config.Labels "com.bigdata.workspace"}}'],
                             capture_output=True, text=True)
    if current.returncode == 0 and current.stdout.strip() != 'BigData/Runner':
        print('An unrelated chi-bench:latest image already exists; it was left unchanged.', file=sys.stderr)
        return 2
    for command in ([sys.executable, 'scripts/repair_pa_t035.py', '--data-dir', str(DATA)],
                    [sys.executable, 'scripts/regenerate_payer_request_forms.py', '--data-dir', str(DATA)],
                    ['chi-bench', 'data', 'verify', '--data-dir', str(DATA)]):
        result = call(command)
        if result:
            return result
    # The pinned upstream recipe uses Node 20 with an unpinned Claude CLI.
    # The current CLI requires Node >=22. Keep the checkout unchanged and
    # generate a narrowly scoped, reproducible compatibility override locally.
    upstream = (BENCH / 'docker/Dockerfile').read_text(encoding='utf-8')
    if upstream.count('setup_20.x') != 1 or upstream.count('@anthropic-ai/claude-code@latest') != 1:
        raise RuntimeError('Upstream runtime recipe changed; review compatibility overrides before building.')
    corrected = upstream.replace('setup_20.x', f'setup_{RUNTIME_NODE_MAJOR}.x').replace(
        '@anthropic-ai/claude-code@latest', f'@anthropic-ai/claude-code@{RUNTIME_CLAUDE_CLI}'
    )
    # BuildKit reads the separately mounted dataset as a named build context.
    # No copy, junction, or data directory inside the official checkout is needed.
    if upstream.count('COPY data/') != 10:
        raise RuntimeError('Upstream dataset COPY instructions changed; review the named context mapping.')
    corrected = corrected.replace('COPY data/', 'COPY --from=chi_data ')
    recipe = ROOT / '.cache/Dockerfile.runtime'
    recipe.parent.mkdir(exist_ok=True)
    recipe.write_text(corrected, encoding='utf-8')
    receipt('runtime-build-recipe.json', {
        'upstream_dockerfile_sha256': hashlib.sha256(upstream.encode()).hexdigest(),
        'local_dockerfile_sha256': hashlib.sha256(corrected.encode()).hexdigest(),
        'node_major': RUNTIME_NODE_MAJOR,
        'claude_code_version': RUNTIME_CLAUDE_CLI,
        'generated_dockerfile': str(recipe),
        'dataset_build_context': str(DATA),
    })
    return 0


def build_runtime() -> int:
    result = prepare_runtime()
    if result:
        return result
    recipe = ROOT / '.cache/Dockerfile.runtime'
    result = call(['docker', 'build', '-f', str(recipe), '--target', 'runtime',
                   '--build-context', f'chi_data={DATA}',
                   '--label', 'com.bigdata.workspace=BigData/Runner', '-t', RUNTIME_IMAGE, '.'])
    return result or call(['docker', 'tag', RUNTIME_IMAGE, 'chi-bench:latest'])


def main() -> int:
    os.environ.setdefault('GIT_CONFIG_GLOBAL', str(ROOT / '.cache/gitconfig'))
    args = sys.argv[1:] or ['doctor']
    action, rest = args[0], args[1:]
    if action == 'doctor':
        return doctor()
    if action == 'download-public':
        return download()
    if action == 'download-handbook':
        return download(handbook=True)
    if action == 'build-runtime':
        return build_runtime()
    if action == 'prepare-runtime':
        return prepare_runtime()
    if action == 'validate-packet':
        return call([sys.executable, 'scripts/validate.py', *rest], LEADERBOARD)
    if action in ('cb', 'hf', 'gh', 'docker', 'python'):
        command = {'cb': 'chi-bench', 'python': sys.executable}.get(action, action)
        if action == 'cb' and rest[:2] in (['data', 'verify'], ['data', 'download']):
            if not any(arg == '--data-dir' or arg.startswith('--data-dir=') for arg in rest):
                rest = [*rest, '--data-dir', str(DATA)]
        # Explicit local auth should use the saved token, while public downloads stay anonymous.
        if action in ('hf', 'gh'):
            os.environ.pop('HF_HUB_DISABLE_IMPLICIT_TOKEN', None)
        return call([command, *rest])
    print('Actions: doctor, download-public, download-handbook, prepare-runtime, build-runtime, validate-packet, cb, hf, gh, docker, python', file=sys.stderr)
    return 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        raise SystemExit(1)
