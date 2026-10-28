# Contributing

1. Open an issue that shows the failure a change would prevent: the task, what the agent did, and what went wrong.
2. Keep skills short. Move long material to the skill's `references/` folder.
3. A new rule needs evidence that it changes agent output. A case study or a before/after diff is enough.
4. Run `python3 scripts/validate_repo.py` and `python3 -m unittest discover -s tests` before opening a pull request.
5. Add a line to `CHANGELOG.md` under Unreleased.

New skill checklist: folder name equals the `name` field, description says what and when, the skill is listed in the README table and in `docs/orchestration.md`.
