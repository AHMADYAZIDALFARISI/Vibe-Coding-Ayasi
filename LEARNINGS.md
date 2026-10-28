# Learnings

Format: date | pattern | skill that should have caught it | evidence. A pattern becomes a skill edit after two occurrences, or one at Critical severity (see `skills/delivery-report`).

2026-10-28 | Focus set in useEffect dropped the first keystrokes after opening an inline editor; wrong text was saved | implementation-craft | getting-started-app case study, defect 1. Critical. Skill edited in 0.2.0
2026-10-28 | One green e2e run hid that race; repeat runs failed 6 of 13 checks | verification | case study, mutation runs. Tied to the Critical defect. Skill edited in 0.2.0
2026-10-28 | Test state leaked between checks (held route; a record created by a manual curl) | verification | case study, two occurrences. Skill edited in 0.2.0
2026-10-28 | Hung request left the form locked with Cancel disabled; no client timeout | implementation-craft | case study, defect 2. High, first occurrence. Logged only
2026-10-28 | Server validation was tightened without updating the client that posts to the endpoint; error body would have been added as a list item | implementation-craft | case study, defect 3. High, first occurrence. Logged only
2026-10-28 | Malformed JSON returned an HTML stack trace with absolute server paths (Express default handler) | security-review | case study, curl. High, first occurrence. Logged only
2026-10-28 | Computed focus styles read during a CSS transition looked like "no focus indicator" | verification | case study. Fixed in ui_probe (settle delay), not a skill rule
2026-10-28 | `pkill -f "node src/index.js"` killed the agent's own shell because the pattern matched its command line | verification | session log. Low. Logged only; use a PID file
2026-10-28 | Edit field used a smaller font than the row text, so text jumped when entering edit mode | interface-design | screenshot review. Low. Logged only
