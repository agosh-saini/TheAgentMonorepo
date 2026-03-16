# CLAUDE.md

You are a coding agent working inside a monorepo. The owner gives you a brief and you build it. Read this file before doing anything.

---

## What this repo is

A workspace for rapidly building independent projects using AI. Each project lives in isolation. The owner describes what to build; you build it.

---

## Where things go

| What | Where |
|---|---|
| Python-only project | `apps/python/<project-name>/` |
| Next.js-only project | `apps/nextjs/<project-name>/` |
| Python backend + Next.js frontend | `apps/fullstack/<project-name>/` |
| Shared code used by multiple projects | `packages/<package-name>/` |
| SQLite databases | `data/sqlite/<project-name>.db` |
| Project briefs and context | `agents/<project-name>/` |

---

## Stack defaults

**Python**
- Python 3.11+
- `uv` for dependency management (`uv init`, `uv add`, `uv run`)
- `ruff` for linting
- `pytest` for tests
- `python-dotenv` for env vars

**Next.js**
- Next.js latest stable (App Router)
- TypeScript strict mode
- Tailwind CSS
- ESLint + Prettier

**Database**
- SQLite only, stored in `data/sqlite/`
- Use `sqlite3` (Python) or `better-sqlite3` (Node)
- Never commit `.db` files

---

## Rules

1. Every project gets its own `README.md` with a one-line description and a run command
2. Every project gets a `.env.example` listing all required environment variables
3. Never share `node_modules` or `.venv` between projects
4. Use environment variables for all secrets — never hardcode
5. Write at least one test for non-trivial logic
6. Keep project folders flat and obvious — no deep nesting
7. If the brief is unclear, make a reasonable assumption and note it in the README
8. Do not add CI, Docker, or cloud infra unless explicitly asked
9. Prefer `uv run` over activating a venv manually
10. For fullstack projects: backend in `backend/`, frontend in `frontend/` inside the project folder

---

## Starting a new project

1. Read `agents/<project-name>/brief.md` if it exists
2. Create the project folder in the right `apps/` location
3. Initialize dependencies
4. Build the thing
5. Add `README.md` and `.env.example`
6. Confirm it runs

---

## Python project structure

```
apps/python/<name>/
├── README.md
├── .env.example
├── pyproject.toml
├── src/<name>/
│   └── main.py
└── tests/
    └── test_main.py
```

## Next.js project structure

```
apps/nextjs/<name>/
├── README.md
├── .env.example
├── package.json
├── src/app/
│   ├── layout.tsx
│   └── page.tsx
└── tests/
```

## Fullstack project structure

```
apps/fullstack/<name>/
├── README.md
├── backend/          ← Python
│   ├── pyproject.toml
│   └── src/
└── frontend/         ← Next.js
    ├── package.json
    └── src/app/
```
