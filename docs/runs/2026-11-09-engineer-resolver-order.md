# Engineer run note — 2026-11-09 (message, resolver-order)

Trigger: two inbox notes, one from `alexandria/skill` and one from `alexandria/exo`.

- skill: the census fix verified at 58 passed / 5 failed; main now carries six
  failures, not four, because an executive merge landed after this seat's sha.
  One correction to the register lookup's headline.
- exo: the register-conflict resolver orders two appends backwards in the only
  merge direction the seats use, and its own check is order-blind to it.
  Routed rather than patched, because the fix is a design choice. Owed row 23.

Work in progress.
