---
name: codebase-recon
description: Understand an existing codebase before changing it. Use at the start of any task in a repository you have not inspected in this session, before planning a feature, or when a bug report needs reproduction. Produces a baseline of stack, conventions, how to run and test, and current failures.
---

# Codebase Recon

Inspect before deciding. Answer these from the repository, not from assumptions.

## Steps

1. List the tree, excluding dependency and build folders.
2. Read the manifest (package.json, pyproject, go.mod, etc.). Note runtime versions, scripts, and dependencies that are declared but unused, or used but undeclared.
3. Find the entry point and trace one request or one user action end to end.
4. Read the existing tests. Note what they mock and what they leave untested.
5. Run the install, the test command, the linter, and the app. Record the exact command and result for each. A test suite that cannot run is a finding, not a skip.
6. Note conventions: module style, naming, error handling, state management, styling approach.
7. Note hazards: destructive defaults (paths, env vars, migrations), secrets in the tree, disabled checks.

## Output

```
STACK: <languages, frameworks, versions>
RUN: <command> -> <result>
TEST: <command> -> <result>
CONVENTIONS: <bullets>
HAZARDS: <bullets with file:line>
BASELINE FAILURES: <what already fails before you touch anything>
```

## Requirements

Convert the request into acceptance criteria. Each must be checkable by a test or a scripted browser action. When the request is ambiguous, state one assumption and proceed. Ask only when the choice is destructive or cannot be reversed.
