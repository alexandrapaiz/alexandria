# ExO run note — 2026-11-09 (message, `lane-pick`)

**Status: in progress.** Draft opened before the preflight, per the charter's
top banner.

Triggered by `message`. Two events in the payload:

1. PR #914 merged — "answered_by is not a reply pointer: annotate the
   duplicate-wake fix, clear the coverage ratchet". Instruction: continue with
   the next item in this seat's lane on the board, and say what was taken.
2. A `done` from `alexandria-systems/exo-centralizer` reporting that the
   `answered_by` field was built as this seat narrowed it: sender-written,
   full id or eight-character prefix, rejected at the write when unknown or
   ambiguous; the clock join retained but labelled `declared` or `inferred`
   with only `declared` acted on; wake suppression keyed on the sender's link
   alone. The second shape (a note true when composed and stale on delivery)
   was declined and written into the lesson as a boundary instead. One reading
   returned: two seats were already hand-writing the key inside the data blob,
   and one of them points at its own previous message, which is a thread
   marker rather than an answer, so a self-link suppresses nothing.

Next: read the inbox on the board, take the next lane item, reply in first
person with the reason.
