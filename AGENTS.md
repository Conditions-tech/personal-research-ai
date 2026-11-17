# Repository Instructions

These instructions apply to the entire Personal Research AI workspace.

## Project boundaries

- The active application is `app.py`. The files `app_backup_v01.py` and `app_before_search_fix.py` are historical copies; do not edit, rename, or delete them unless the user explicitly requests it.
- `data/research.db` contains the user's local research records. Preserve it. Never use it in tests, migrations, fixtures, or exploratory writes.
- Do not change the production database schema or records without explicit approval. Any approved schema change must include a documented backup and migration/rollback plan.
- Do not initialize Git, commit, push, add paid services, or implement product features without explicit user approval.
- Do not install or upgrade packages unless explicitly approved. Do not reveal credentials, secrets, private research text, or database record contents in logs or reports.

## Safe development

- Read the relevant source and current workspace state before editing. Keep changes focused and reviewable.
- Run tests only against temporary or isolated data. Tests must not import the Streamlit script in a way that initializes or writes to the real database.
- The Streamlit script executes its UI at module scope. Use isolated helper tests or Streamlit-aware tests with an explicitly temporary database path.
- Treat `README.md` and `docs/` as the maintained project handover. Separate verified behavior from assumptions, proposals, and untested compatibility claims.
- Keep `requirements.txt` limited to third-party packages imported by the active application. Use the standard library for tests unless a test dependency is deliberately approved and documented.
- Before completing work, run focused non-destructive checks, inspect the diff, and report commands, outcomes, and any remaining verification gaps.