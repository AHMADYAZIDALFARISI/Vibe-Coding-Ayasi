---
name: verification
description: Prove that a change works. Use after implementing or fixing anything, before claiming tests pass, and whenever a UI must be checked in a real browser. Covers test selection, running the suite, browser checks across viewports, accessibility basics, and the rule that unexecuted checks are reported as unverified.
---

# Verification

## Rules

- Run it, then report it. Paste the command and the summary line of the output.
- A check you did not run is "not run". A check that could not run is "blocked" with the reason.
- Tests must fail before the fix when you are fixing a bug. Show the red run. For a fix found during your own work, revert it once and confirm a test goes red.
- Run browser interaction suites at least three times. One green run does not rule out a race.
- Isolate test state. Reset the data, clear request interception, and use test data no other step creates. A leaked route or a stray record turns one failure into many.

## What to test

Write tests from acceptance criteria, not from implementation details.

1. Happy path for each criterion.
2. Invalid input at the boundary: empty, too long, wrong type, missing field.
3. Missing resource and server failure.
4. The UI states: pending, error, success, empty.

Prefer a few tests that exercise real behaviour over many that assert on mocks.

## Browser checks

When a browser automation tool is available, run `scripts/ui_probe.py <url> --out <dir>`. It loads the page at 360, 768, and 1280 px, saves screenshots, and reports:

- console errors and failed requests (pass `--ignore-host` for hosts the sandbox blocks; they are listed, not counted)
- horizontal overflow
- inputs without labels, buttons without accessible names, images without alt
- duplicate control names and ARIA references to missing ids
- controls with no visible focus change when reached by Tab (checked at the widest viewport, after transitions settle)
- viewport meta that blocks zoom

The probe does not see wrapped rows, misaligned controls, or text that changes size between states. Only the screenshots show those.

Then exercise the feature with a scripted interaction (click, type, keyboard). Look at the screenshots. A screenshot you did not open is not visual verification.

If no browser is available, say so and list what a human must check.
