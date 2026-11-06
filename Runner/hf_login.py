"""Authenticate the isolated runner using a token received privately on stdin."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys


HANDBOOK_REPO = 'actava/managed-care-operations-handbook'


def failure_summary(phase: str, error: Exception) -> dict:
    response = getattr(error, 'response', None)
    return {
        'phase': phase,
        'error_type': type(error).__name__,
        'http_status': getattr(response, 'status_code', None),
    }


def save_result(result: dict) -> None:
    folder = Path('/runner/logs')
    folder.mkdir(exist_ok=True)
    result['checked_at_utc'] = datetime.now(timezone.utc).isoformat()
    (folder / 'huggingface-login.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8'
    )


def main() -> int:
    token = sys.stdin.read().strip()
    if not re.fullmatch(r'hf_[A-Za-z0-9]+', token):
        print('Invalid token format. Paste the raw hf_ access token without terminal control characters.', file=sys.stderr)
        return 2

    # Debug HTTP logs can contain authentication headers. Keep this path quiet.
    os.environ.pop('HF_DEBUG', None)
    os.environ['HF_HUB_VERBOSITY'] = 'error'
    from huggingface_hub import HfApi, login

    try:
        login(token=token, add_to_git_credential=False)
    except Exception as error:
        details = failure_summary('login', error)
        print(f"Login failed: {details['error_type']} (HTTP {details['http_status']}).", file=sys.stderr)
        return 1

    print('Login successful. Credentials are saved in the isolated runner cache.')
    result = {'login_verified': True, 'handbook_repository': HANDBOOK_REPO}
    try:
        HfApi(token=token).auth_check(HANDBOOK_REPO, repo_type='dataset')
    except Exception as error:
        details = failure_summary('handbook_read_access', error)
        result.update(handbook_read_access_verified=False, **details)
        save_result(result)
        print(f"Login is saved, but handbook access failed: {details['error_type']} (HTTP {details['http_status']}).", file=sys.stderr)
        return 3

    result['handbook_read_access_verified'] = True
    save_result(result)
    print('Handbook read access verified. No benchmark run or submission was started.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
