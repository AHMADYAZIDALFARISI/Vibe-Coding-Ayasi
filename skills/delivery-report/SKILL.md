---
name: delivery-report
description: Write the final report for engineering work and record lessons for next time. Use when handing off any implementation, fix, or audit to the user. Separates completed, failed, skipped, and unverified work, and logs recurring failure patterns without secrets.
---

# Delivery Report

## Report

```
SUMMARY: <one paragraph: what changed and why>
CHANGED FILES: <path: purpose>
VERIFIED: <check: command -> result>
NOT VERIFIED: <check: reason>
FIXED FINDINGS: <severity: title>
OPEN ISSUES: <severity: title, why not fixed>
LIMITATIONS: <known gaps>
```

Never write "all tests pass" unless the report shows the command and the count.

## Learning log

After a task that hit a real defect, append one line to `LEARNINGS.md` in the skill repo or project:

```
<date> | <pattern> | <which skill should have caught it> | <evidence>
```

Propose a skill edit only when the same pattern appears twice, or once with Critical severity. Edit skills through a reviewed change, never automatically.
