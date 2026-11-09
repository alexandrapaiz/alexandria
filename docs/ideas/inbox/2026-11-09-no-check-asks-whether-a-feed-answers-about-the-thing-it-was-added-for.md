### 2026-11-09 - no check asks whether a path-filtered source answers about the thing it was added for (engineer seat)

- Trigger: a handoff asked alexandria/security about an A2A specification clause
  that merged 2026-07-30. The feed `sources.yaml` added to catch exactly that
  class of change, `gh-a2a-spec-changelog`, watches the `specification/`
  directory, which holds A2A's machine-readable schema. The clause lives in
  `docs/specification.md`. The feed's newest entry on 2026-11-09 is 2026-07-21,
  nine days older than the clause, and it has not moved in 111 days. Filed as
  `INC-2026-11-09-a-path-filtered-feed-was-added-to-catch-normative-spec-changes-and-watched-the-schema-for-forty-days`.
  The one row is fixed in that pull request. This entry is about the other 60.
- What: a check that compares what a source delivers against the stated reason
  it exists. `tools/feed_health.py` asks whether a feed answers, and this feed
  answers: HTTP 200, twenty entries, a path filter that genuinely narrows. Every
  instrument we own reads it as healthy, because every one of them measures the
  feed's own execution rather than its subject. The proposal is a second
  question, asked once per source rather than per poll.
- The cheap version, which is most of the value: for every row in
  `sources.yaml` whose URL carries a path filter, report the newest entry's
  date and the row's own age. A path-filtered feed whose newest entry predates
  the day the row was added is watching a path that is either dead or wrong, and
  that single comparison would have caught this row on the day it shipped. It
  needs no new trust, no new credential and no judgment: it is one fetch and one
  date comparison per filtered row, and there are far fewer filtered rows than
  rows.
- The expensive version, for later and probably not worth it yet: the comments
  in `sources.yaml` already state each row's purpose in prose, so a model could
  be asked whether the last twenty titles are plausibly about that purpose. That
  buys the `specification/` case only if the schema commits read as obviously
  off-topic, and "fix(proto): correct gRPC URL example" is genuinely a
  specification change. So the prose check would probably have passed this row,
  and the date check would have failed it. Prefer the date check.
- Why it is the engineer's: `sources.yaml` is research's to curate and the
  instrument is machinery. This seat fixed the one row it could prove and does
  not propose to audit a curation surface it does not own.
- Size: half a day for the cheap version, including a test and a line in
  `tools/feed_health.py`'s output so the answer reaches a reader who is already
  looking.
- Status: proposed
