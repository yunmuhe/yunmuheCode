# Repository Guidelines

This repository contains a Python/Flask backend for AI name generation and a separate uni-app frontend. Most contributor commands below run from `NameGenerationAgent/`.

## Project Structure & Module Organization
- `NameGenerationAgent/` backend root (run commands here).
- `NameGenerationAgent/src/api/` adapters + `unified_client.py` for AI routing.
- `NameGenerationAgent/src/core/` business logic (name generation, corpus enhancer).
- `NameGenerationAgent/src/web/` Flask app and routes.
- `NameGenerationAgent/config/` API config and prompts.
- `NameGenerationAgent/data/` SQLite corpus and cache files.
- `NameGenerationAgent/tests/` pytest tests.
- Frontend lives in a sibling uni-app directory; see `NameGenerationAgent/README.md` for the exact path.

## Build, Test, and Development Commands
```bash
cd NameGenerationAgent
../.venv1/Scripts/activate       # or: python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env            # set at least one API key
quick_start.bat                  # or: python main.py
python -m pytest tests/ -v
```
- Health check: `curl http://127.0.0.1:5000/health`.

## Coding Style & Naming Conventions
- Python 3.8+, 4-space indent, snake_case functions/vars, PascalCase classes.
- Prefer delayed imports to avoid circular dependencies (see `CLAUDE.md`).
- Use `src/utils/logger.py` for logging and `APIException` for adapter failures.
- New adapters: create `src/api/adapters/*_adapter.py`, implement `generate_names()`, register in `config/api_config.py` and `src/api/adapters/__init__.py`.

## Testing Guidelines
- Framework: pytest (`python -m pytest tests/ -v`).
- Tests live in `NameGenerationAgent/tests/` and follow `test_*.py`; classes typically `Test*`.
- Add coverage for core generation, adapters, and corpus integration (`test_corpus_integration.py`).
- No explicit coverage target is documented; include regression tests for fixes.

## Commit & Pull Request Guidelines
- Git history follows Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`) often with Chinese summaries.
- PRs should include a short summary, tests run, and any config/DB impacts. Add screenshots or a brief demo note for frontend changes.
- Do not commit large data files; `NameGenerationAgent/data/names_corpus.db` is gitignored. Rebuild via `cd data && python convert_csv_to_sqlite.py`.
