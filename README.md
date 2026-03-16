# TheAgentMonorepo

A monorepo for building things fast with AI coding agents. Open a brief, describe what you want, let the agent build it.

---

## Workflow

1. **Have an idea** — write a brief in `agents/<project-name>/brief.md`
2. **Point your agent at it** — open Claude Code or Codex in this repo
3. **Say:** _"Read agents/<project-name>/brief.md and build it"_
4. **Done** — project lands in `apps/`

---

## Repo layout

```
TheAgentMonorepo/
├── apps/
│   ├── python/          # Python-only projects
│   ├── nextjs/          # Next.js-only projects
│   └── fullstack/       # Python backend + Next.js frontend
├── agents/              # Project briefs — describe what to build here
├── packages/            # Shared utilities (used across projects)
├── data/
│   └── sqlite/          # SQLite databases (gitignored)
├── scripts/             # Scaffold and automation scripts
├── configs/             # Shared config files
├── docs/                # Notes and documentation
└── CLAUDE.md            # Rules the AI agent follows
```

---

## Writing a brief

Create a file at `agents/<your-project-name>/brief.md`:

```markdown
# My Project Name

## What it does
A CLI tool that summarizes a webpage given a URL.

## Stack
Python only

## Key features
- Accept a URL as a CLI argument
- Fetch the page content
- Summarize using Claude API
- Print to stdout

## Notes
Store API key in .env as ANTHROPIC_API_KEY
```

Then tell your agent: _"Read agents/url-summarizer/brief.md and build it"_

---

## Examples

| Path | What it shows |
|---|---|
| `apps/python/example/` | Python-only project structure |
| `apps/nextjs/example/` | Next.js-only project structure |
| `apps/fullstack/example/` | Python backend + Next.js frontend structure |

---

## Scripts

```bash
bash scripts/create-python-app.sh <name>    # scaffold a Python project
bash scripts/create-nextjs-app.sh <name>    # scaffold a Next.js project
bash scripts/create-fullstack-app.sh <name> # scaffold a fullstack project
bash scripts/lint-all.sh                    # lint everything
bash scripts/test-all.sh                    # test everything
```

---

## Stack

The agent defaults to:
- **Python 3.11+** with `uv`, `ruff`, `pytest`
- **Next.js** (latest) with TypeScript, Tailwind, ESLint
- **SQLite** for any persistence
- **Anthropic Claude API** for LLM calls

Override defaults by specifying a different stack in your brief.

---

## Rules the agent follows

See [`CLAUDE.md`](CLAUDE.md).
