# Orchestration

```
codebase-recon -> (interface-design) -> implementation-craft -> verification
      -> security-review -> (interface-design audit) -> (performance-review) -> delivery-report
```

Parentheses mark stages that run only when routed. Routing rules live in [the orchestrator skill](../skills/plumbline-orchestrator/SKILL.md).

| Skill | Input | Output |
|---|---|---|
| codebase-recon | repo, request | baseline block, acceptance criteria |
| interface-design | criteria, existing UI | direction block before code; anti-slop verdict after |
| implementation-craft | criteria, direction | diff |
| verification | diff, criteria | commands with results, screenshots |
| security-review | diff | findings with file:line |
| performance-review | diff, measurements | findings with numbers |
| delivery-report | all handoff blocks | final report, learning log entry |

A failing check returns work to the stage that produced the defect, then the check runs again.
