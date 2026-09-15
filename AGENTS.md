# BOMS — agent entry point

Everything an AI agent needs lives in **[`.agent/`](./.agent/)** — one folder, no duplicates.

```
.agent/
  AGENTS.md          ← read this first
  README.md          what the kit contains
  skills/            the four installed skills (single copy)
  docs/              conventions: wireframes, design tokens, skill usage
  guides/            how-to runbooks
  scripts/           the wireframe generator
  skills-lock.json   skill provenance + hashes
```

Other assistants read the same files through symlinks:

| Tool | Path | Points at |
|------|------|-----------|
| Claude Code | `.claude/skills` | `.agent/skills` |
| Cursor | `.cursor/skills` | `.agent/skills` |
| Anything else | `AGENTS.md`, `CLAUDE.md` | `.agent/AGENTS.md` |

**Read [`.agent/AGENTS.md`](./.agent/AGENTS.md) now.**
