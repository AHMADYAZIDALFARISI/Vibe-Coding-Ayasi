# Changelog

## [0.2.0] - 2026-10-28

Changes driven by the getting-started-app case study. Each one maps to a row in `examples/getting-started-app-rename/REPORT.md`.

- ui_probe: exit 2 with a plain message when the page cannot load (was a traceback and exit 1).
- ui_probe: new checks for duplicate control names, ARIA references to missing ids, and controls with no visible focus change.
- ui_probe: `--ignore-host` lists requests the environment blocks without counting them as issues.
- verification skill: run interaction suites three times, revert self-found fixes once, isolate test state; documents what the probe cannot see.
- implementation-craft skill: move focus in the same update that shows the target element.
- Added LEARNINGS.md and the case study.

## [0.1.0] - 2026-10-28

- Eight skills: plumbline-orchestrator, codebase-recon, implementation-craft, interface-design, security-review, verification, performance-review, delivery-report.
- Scripts: slop_scan.py, ui_probe.py, validate_repo.py.
- Unit tests for the three scripts.
