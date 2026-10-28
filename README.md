# Plumbline

Agent Skills that keep AI-assisted coding honest: inspect before editing, build the smallest correct change, design interfaces on purpose, and prove every claim with a command you actually ran.

Plumbline is a set of eight `SKILL.md` skills plus three small scripts. It targets coding agents that load the Agent Skills format. Verified targets are listed under Compatibility.

## Skills

| Skill | Use it when |
|---|---|
| `plumbline-orchestrator` | Any build, fix, refactor, or audit task. Routes to the others and holds the quality gates. |
| `codebase-recon` | First contact with a repo or a bug. Produces a baseline and acceptance criteria. |
| `implementation-craft` | Writing or changing code. Validation, error paths, and anti-bloat rules. |
| `interface-design` | Any UI change. Visual direction, states, accessibility, anti-slop gate. |
| `security-review` | Changes that touch input, auth, data, secrets, or the network. |
| `verification` | Before claiming anything works. Tests plus browser checks at three widths. |
| `performance-review` | New dependencies, lists, media, queries, or reported slowness. |
| `delivery-report` | Handing work back. Separates verified from unverified, logs lessons. |

How the skills hand work to each other: [docs/orchestration.md](docs/orchestration.md).

## Scripts

| Script | What it does |
|---|---|
| `skills/interface-design/scripts/slop_scan.py` | Flags gradients, glass, glow, placeholder copy, invented metrics, timer-driven loading, zoom blocking. Advisory. |
| `skills/verification/scripts/ui_probe.py` | Opens a URL at 360/768/1280 px with Playwright. Reports console errors, failed requests, overflow, unlabeled inputs, unnamed or duplicate control names, broken ARIA references, missing focus styles, small targets, zoom blocking. Saves screenshots. It cannot see wrapped or misaligned layout; read the screenshots. |
| `scripts/validate_repo.py` | Checks skill frontmatter, links, required files, README coverage, and likely secrets. |

## Install

Requirements for the scripts: Python 3.10+, PyYAML. `ui_probe.py` also needs `playwright` and a Chromium build. The skills themselves are plain Markdown.

Claude Code, all projects:

```bash
git clone <your-fork-url> plumbline
mkdir -p ~/.claude/skills
cp -R plumbline/skills/* ~/.claude/skills/
```

Claude Code, one project: copy the folders into `<project>/.claude/skills/` instead.

Claude.ai: zip one skill folder at a time (the folder must contain exactly one `SKILL.md`) and upload it in the Skills settings.

Remove a skill by deleting its folder. Update by pulling and copying again.

## Validate

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

The browser test is skipped when Playwright is missing.

## Compatibility

| Runtime | Status |
|---|---|
| Agent Skills frontmatter rules (name, description, allowed keys) | Checked by `validate_repo.py` |
| Claude Code skill paths `~/.claude/skills/` and `.claude/skills/` | From the Claude Code docs; not tested in a Claude Code session by this repo |
| Claude.ai upload | Folder layout matches the upload rule; upload not tested |
| Codex, Gemini CLI, Cursor | Not verified |

## Case study

[examples/getting-started-app-rename/REPORT.md](examples/getting-started-app-rename/REPORT.md) applies the skills to a real open-source app. It lists the defects found in the new code, what the skills missed, the changes made in 0.2.0 because of it, and what is still open. Recurring patterns are tracked in [LEARNINGS.md](LEARNINGS.md).

## License

MIT. See [LICENSE](LICENSE).
