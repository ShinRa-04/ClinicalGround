# Shared research tools

October 17, 2026: user authorized a general reusable Crawl4AI install. Main agent installed **Crawl4AI 0.9.5**, isolated from BigData/Runner and other project environments.

- Tool home: `C:/Users/prath/.local/share/codex-tools/crawl4ai/`.
- Python: `.venv/Scripts/python.exe`, CPython 3.11.9; 96 installed packages, pinned version snapshot in `requirements.lock.txt`.
- Shared launcher: `C:/Users/prath/.local/bin/crawl4ai.ps1`.
- Local README, `crawl.py`, dependency snapshot and smoke-check receipts live in that tool home. Those machine-local files are outside this repository.
- Playwright 1.64.0 Chromium 1248, headless shell and support binaries installed in the standard user browser cache `C:/Users/prath/AppData/Local/ms-playwright/`.
- Installed from binary wheels using uv; no host compiler, Docker, WSL migration or system-Python package mutation. No model extras or model downloads were requested; dependencies do include LLM client libraries, but no model/provider calls were made.
- Launcher explicitly uses `headless=True`, isolated browser context, certificate checks, no stealth, no user browser profile, single URL and robots check. It refuses output overwrite and records HTTP/extraction status, URL, timestamp and Markdown hash separately from extracted text.
- PATH and automatic updates were not changed. Use the absolute launcher from any project; outputs belong in that project's appropriate research cache. A successful extraction is not factual verification or guaranteed access to other sites.

```powershell
& "$env:USERPROFILE\.local\bin\crawl4ai.ps1" 'https://example.com' --output '.\research\example.md'
```

Executed checks: import/version **0.9.5** passed; headless extraction of example.com **HTTP 200**, 953 Markdown characters; public Medicaid transportation page **HTTP 200**, 39,655 Markdown characters. Receipts are under tool-home `checks/`. Both browser sessions were closed automatically. No visible browser was requested. These checks verify installation and those two extractions, not every site or all Crawl4AI features. The existing evidence audit used its independently captured source corpus; installation does not retroactively upgrade its claims.

Official installation documentation: https://docs.crawl4ai.com/core/installation/ . The installed wrapper and dependency snapshot, rather than that documentation alone, define the tested local configuration.
