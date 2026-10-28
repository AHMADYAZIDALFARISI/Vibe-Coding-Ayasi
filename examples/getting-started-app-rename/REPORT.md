# Case study: inline rename in docker/getting-started-app

Plumbline 0.1.0 was used on a real open-source app to build one feature end to end. The run was then reviewed adversarially: the goal was to find what the skills missed, not to show that they worked. This report records what was found, what changed, and what is still open.

- Target: [docker/getting-started-app](https://github.com/docker/getting-started-app) at commit `6b025fc` (Express 5, SQLite or MySQL, React 16 compiled in the browser by Babel).
- Feature: rename a todo item inline.
- Environment: Node 22, Python 3.12, Playwright 1.56 with Chromium, Linux sandbox without access to Google Fonts.

## Files here

| File | Purpose |
|---|---|
| `rename-feature.patch` | The full change to the app, minus `package-lock.json`. Apply with `git apply`, then `npm i -D jest@29.7.0`. |
| `run_app.sh` | Starts the app on a fresh database and seeds three items. Refuses to start if port 3000 is taken. |
| `rename_e2e.py` | 13 browser checks for the acceptance criteria. |

Reproduce:

```bash
git clone https://github.com/docker/getting-started-app && cd getting-started-app
git checkout 6b025fc
git apply ../plumbline/examples/getting-started-app-rename/rename-feature.patch
npm ci && npm i -D jest@29.7.0
SQLITE_DB_LOCATION=/tmp/todo-test/todo.db npm test
../plumbline/examples/getting-started-app-rename/run_app.sh .
python3 ../plumbline/examples/getting-started-app-rename/rename_e2e.py
```

Set `SQLITE_DB_LOCATION` for the tests. Without it, `spec/persistence/sqlite.spec.js` deletes `/etc/todos/todo.db`.

## Recon findings (before any change)

| Finding | Evidence |
|---|---|
| No `test` script, jest not declared, so the spec suite could not run | `npm test` reported a missing script |
| Persistence tests delete the default production database path | `spec/persistence/sqlite.spec.js:3` |
| Empty, numeric, and 5000-character names accepted | `curl` returned 200 for each |
| POST without a body returned 500; PUT on an unknown id returned 200 with an empty body | `curl` |
| Viewport blocks zoom (WCAG 1.4.4) | `index.html:6`, found by both scripts |
| At 360 px the delete button wrapped below its row | Screenshot only. `ui_probe` 0.1 reported zero issues |
| High npm audit advisories (body-parser, @isaacs/brace-expansion, http-cache-semantics) | `npm audit --omit=dev` |

## Acceptance criteria

1. Each item has an edit control whose accessible name includes the item name.
2. Activating it shows a labelled field, prefilled and focused.
3. Enter or Save sends PUT. The list updates only after the server confirms, with a pending state.
4. Escape or Cancel restores the name, sends nothing, and returns focus.
5. The server returns 400 with a JSON message for empty, non-string, or over-255-character names (both schemas use `varchar(255)`).
6. PUT on an unknown id returns 404, and the UI shows the message.
7. Network failure shows an error, never a success.
8. Layout holds at 360, 768, and 1280 px, and zoom is allowed.

## Defects found in the new code

| # | Severity | Defect | Found by | Fix | Proof |
|---|---|---|---|---|---|
| 1 | Critical | Focus set in `useEffect` dropped the first keystrokes after Rename. "Renew passport in Feb" became "port in Feb", which would have been saved | e2e | `useLayoutEffect` | With fix: 13/13 in each of 3 runs. Fix reverted: 7/13 in each of 3 runs, different checks failing each time |
| 2 | High | A hung request left the form on "Saving..." with Cancel disabled | e2e | 15 s timeout with `AbortController` | Check with `page.clock.run_for(16000)` passes |
| 3 | High | The new POST validation would have pushed `{error}` into the list as an item | diff review | Add form reads errors and shows them | "no phantom item" check passes |
| 4 | Medium | Add button stayed enabled while submitting (it only had a `disabled` class) | diff review | Real `disabled` attribute | e2e |
| 5 | High | Malformed JSON returned an HTML stack trace with absolute server paths | `curl` during security review | JSON error handler for 400, 413, 500 | `curl` returns `{"error":"Request body must be valid JSON."}` with 400 |
| 6 | Low | Edit field text was 14 px and row text 16 px, so text jumped on edit | screenshot | CSS on `.rename-row .form-control` | Computed font size 16 px in both states |
| 7 | n/a | Test harness: a held route leaked into later checks and cascaded failures | e2e | Clear routes before each check | 13/13 stable |

One run of the e2e script reported 4/13 after a server restart. The cause was not confirmed. After stopping every server and adding the port guard to `run_app.sh`, three runs passed 13/13.

## Before and after

| Check | Before | After |
|---|---|---|
| `npm test` | could not run | 5 suites, 22/22 pass |
| Browser e2e | n/a | 13/13, three consecutive runs |
| HTTP: whitespace, missing body, number, 256 chars, malformed JSON | 200, 500, 200, 200, HTML stack | 400 JSON for each |
| HTTP: PUT unknown id | 200 empty | 404 JSON |
| `ui_probe` 0.2 at 1280 px (fonts host ignored) | unlabeled input 1, duplicate names 2, broken ARIA ref 1, zoom blocked | all zero, exit 0 |

## What the skills missed, and what changed in 0.2.0

| Gap | Evidence | Change |
|---|---|---|
| `ui_probe` printed a traceback and exited 1 on an unreachable URL; its docs promised exit 2 | run against a stopped server | Clean message, exit 2, with a test |
| `ui_probe` missed the broken `aria-describedby="basic-addon1"` | baseline app | ARIA reference check |
| `ui_probe` missed three identical "Remove Item" names, which the interface-design skill forbids | baseline app | Duplicate name check |
| `ui_probe` had no focus check | manual inspection | Tab-through focus audit. App as shipped: 0 findings. `button:focus` rule removed: 9 findings |
| Sandbox-blocked fonts counted as failures | every run | `--ignore-host`, listed separately |
| The verification skill accepted a single green run | defect 1 passed one early run | Run interaction suites three times; revert each self-found fix once |
| No rule on test isolation | defect 7 and a polluted record | Isolation rule |
| No rule on focus timing | defect 1 | One line in implementation-craft |

Defects 2, 3, and 5 were logged in `LEARNINGS.md` and did not change skill text. The repository rule allows a skill edit after two occurrences or one Critical occurrence, and each of these happened once at High.

## Still open

| Severity | Issue |
|---|---|
| High | `sqlite.spec.js` still deletes `/etc/todos/todo.db` when the env var is unset |
| High | npm audit advisories (pre-existing). Fixing them changes the lockfile and needs the maintainer's call |
| Medium | Lost update: rename sends the client's copy of `completed`, which can overwrite a change made in another tab |
| Medium | Toggle and delete ignore errors. A failed initial load leaves "Loading..." on screen |
| Medium | The app has no authentication or authorization (by design for a tutorial app) |
| Low | Google Fonts loaded from a third party; Babel compiles JSX in the browser |

## Limits of this review

- One agent built and reviewed the change. No second reviewer was involved.
- Screen reader output was not tested. Accessible names and focus were checked through the DOM and computed styles.
- Only Chromium was used. Firefox and Safari were not tested.
- The MySQL path was not run.
- The skills were not loaded through Claude Code's skill loader. They were followed by reading them in a chat session.
