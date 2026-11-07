# claude-skills

Personal Claude skills.

| Skill | Trigger | What it does |
|---|---|---|
| [`chart-audit`](skills/chart-audit/SKILL.md) | `/chart-audit` | Skeptically audits a chart (PNG/screenshot, optionally with CSV/Excel/code) for data validity, provenance, transformation errors, misleading design, unsupported claims, and rebuild-readiness (title, subtitle, axes, legend, sources, footnotes). |
| [`confidence-check`](skills/confidence-check/SKILL.md) | `/confidence` | Runs an iterative clarifying-question loop (multiple-choice, max 3 per round) until Claude is 95% confident it understands the request, then summarizes and proceeds. |

## Install

**Claude (web/desktop):** zip a skill folder (e.g. `skills/chart-audit`, with `SKILL.md` at the folder root) and upload it under Settings → Capabilities → Skills.

**Claude Code:** copy a skill folder into `~/.claude/skills/` (user-level) or `.claude/skills/` (project-level):

```bash
git clone https://github.com/AndrewAFerrante/claude-skills.git
cp -r claude-skills/skills/chart-audit claude-skills/skills/confidence-check ~/.claude/skills/
```

## Layout

```
skills/
├── chart-audit/        SKILL.md, references/, scripts/
└── confidence-check/   SKILL.md
```

## License

MIT
