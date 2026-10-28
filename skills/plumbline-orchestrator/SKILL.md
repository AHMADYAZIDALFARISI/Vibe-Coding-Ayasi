---
name: plumbline-orchestrator
description: Entry point for software engineering work on a real codebase. Use when the user asks to build, fix, refactor, audit, or ship a feature in an existing web or full-stack project, or says "vibe code", "implement", "add feature", "review this repo". Routes work to the other Plumbline skills, enforces stage order and quality gates, and defines the evidence format every stage must hand off.
---

# Plumbline Orchestrator

Route the task. Do not load every skill for every task.

## Routing

| Task signal | Load | Skip |
|---|---|---|
| Unknown or new repo | codebase-recon first, always | |
| Feature touching UI | interface-design, implementation-craft, verification | performance-review unless lists, media, or bundles change |
| Backend/API only | implementation-craft, security-review, verification | interface-design |
| Bug report | codebase-recon (reproduce first), implementation-craft, verification | interface-design unless the bug is visual |
| Audit only, no edits | the relevant review skills, delivery-report | implementation-craft |
| Auth, input handling, file upload, secrets, payments | security-review is mandatory | |
| Anything delivered to the user | delivery-report | |

## Stage order

1. Recon: read the code, run the existing checks, record the baseline.
2. Requirements: write acceptance criteria as testable statements.
3. Design: only when UI changes. State the visual direction before code.
4. Implement: smallest correct change that fits existing patterns.
5. Verify: run tests, then the running app.
6. Review: security, then UI audit, then performance if routed.
7. Deliver: report with evidence.

Any failed check sends work back to the stage that caused it. Re-run the failed check after the fix. Do not mark a gate as passed from memory.

## Handoff record

Every stage ends with this block in the working notes:

```
STAGE: <name>
DID: <what was done>
EVIDENCE: <command + exit code, file:line, screenshot path>
OPEN: <unresolved items with severity>
```

A claim without EVIDENCE is "unverified". Report it as such.

## Conflicts between skills

Resolve in this order: correctness and security, then accessibility, then the user's explicit request, then existing project conventions, then visual polish, then performance micro-gains. Record the trade-off in the handoff block.

## Parallel work

Safe in parallel: reading files, research, independent reviews of a frozen diff.
Sequential only: edits to the same file, migrations, anything that changes what a reviewer is reviewing.

## Quality gates before delivery

Check each. Mark pass, fail, or not-checked with a reason.

1. Acceptance criteria met, each tied to a test or manual check.
2. Fits existing architecture and conventions.
3. No new dependency without a written reason.
4. Loading, empty, error, and success states exist for every async UI path.
5. Keyboard and screen-reader basics pass (see verification).
6. Layout checked at 360, 768, and 1280 px widths.
7. Security review done when routed.
8. Tests executed in this session, with output.
9. No fake data, fake success, or placeholder handlers left in shipped paths.
10. Delivery report lists changed files and limitations.

Severity: Critical blocks delivery. High is fixed unless the user accepts the risk. Medium and Low go in the report.
