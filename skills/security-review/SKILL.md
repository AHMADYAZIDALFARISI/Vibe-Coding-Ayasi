---
name: security-review
description: Review code changes for security risk before delivery. Use when a change touches authentication, authorization, user input, file handling, database queries, secrets, third-party calls, or anything exposed over the network. Maps findings to OWASP Top 10 categories and requires each finding to point at a file and line.
---

# Security Review

Review the diff and the code paths it reaches. Not the whole repo, unless asked.

## Steps

1. Draw the trust boundary: which inputs come from users, other services, or files.
2. For each input, check: type, length, allowed values, and where it ends up (SQL, HTML, shell, filesystem, logs, another service).
3. Check authorization on every new route or action. Ask: can user A act on user B's resource?
4. Check secrets: none in code, logs, client bundles, or error responses. `.env` files are ignored by git.
5. Check output encoding: the framework escapes by default; look for bypasses (`dangerouslySetInnerHTML`, `innerHTML`, template `|safe`, `v-html`).
6. Check dependencies added in this change: maintained, needed, no known critical advisories (`npm audit`, `pip-audit`, or the ecosystem equivalent).
7. Check abuse paths proportional to exposure: rate limits on auth and write endpoints, body size limits.

## Finding format

```
[SEVERITY] <title>
WHERE: <file:line>
OWASP: <A01..A10 category, 2021 list>
IMPACT: <what an attacker gets>
FIX: <specific change>
VERIFIED BY: <test or request that proves the fix>
```

Do not report a finding you have not traced to code. Do not mark a finding fixed without a test or a reproduced request.
