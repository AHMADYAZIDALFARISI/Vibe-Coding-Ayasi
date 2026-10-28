---
name: implementation-craft
description: Write and change production code that fits the existing codebase. Use when implementing features, fixing bugs, or refactoring in frontend, backend, API, or database code. Covers validation, error handling, data access, naming, and the rules that keep generated code from becoming bloated or generic.
---

# Implementation Craft

## Defaults

- Match the repository's existing style, module system, and libraries.
- Make the smallest change that satisfies the acceptance criteria.
- Validate input at the trust boundary (route handler, form submit, message consumer). Return a specific status and message.
- Handle the failure path of every I/O call. The UI must show it; the server must log it without leaking internals.
- Keep side effects in named functions. No hidden writes in getters or render paths.
- Move focus in the same update that shows the target element (React: `useLayoutEffect` or `autoFocus`, not `useEffect`). Deferred focus drops the first keystrokes, and the wrong text gets saved.
- Name things after the domain, not the pattern (`renameItem`, not `handleUpdateHelper`).

## Do not

- Add a file, hook, utility, interface, or layer that has one caller and no complexity to hide.
- Add a dependency for something the platform or an existing dependency already does.
- Rewrite working code that the task does not touch.
- Silence type errors, lint rules, or failing tests to get green.
- Ship mock data, `TODO` handlers, or success messages that fire before the server confirms.
- Add speculative options, flags, or config "for later".

## Data and APIs

- Keep server and client limits identical. Put the number in one place per side and test both.
- Return 404 for missing resources, 400 for invalid input, and do not echo raw input back in error HTML.
- Use parameterized queries. Never build SQL with string concatenation.
- Schema changes need a migration path for existing data.

## Before handing off

Run the formatter or linter the project already uses. Read your own diff line by line. Delete anything you cannot justify in one sentence.
