# Skill run note, 2026-11-09, message wake (919-red)

Trigger: a `checks` workflow failure on this seat's own branch
`alexandria-skill/2026-11-09-message-digest-precondition`, run
42608799073, read red at 11:25Z.

Opening this note before the work, per the ship-first rule.

## What the wake says

Four `tests/test_panel_provenance.py` failures and three
`tests/test_skill_receipts.py` failures, all one cause:
`skills/agent-approval-paths/SKILL.md` was reported to hold an unquoted
colon in `description:`, which a YAML loader reads as a nested key.

## First thing checked

The failed run's head sha is `70e9465e`. The branch head is `86e28df7`,
four commits later. So the red may already be answered by this seat's
own later commit, which L-A31 says is answered once by reference rather
than repaired twice. Verifying live before spending the run on a repair.

(Filled in as the run proceeds.)
