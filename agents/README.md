# agents/

This is where you write project briefs. One folder per project idea.

The AI agent reads your brief and builds the project in `apps/`.

## How to write a brief

Create `agents/<project-name>/brief.md` and describe:

- What it does (one paragraph)
- Stack preference (Python / Next.js / Fullstack)
- Key features (bullet list)
- Any specific requirements or constraints

Then open Claude Code and say:
> "Read agents/<project-name>/brief.md and build it"

## Example

```
agents/
└── url-summarizer/
    └── brief.md
```
