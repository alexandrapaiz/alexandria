# Engineer run, 2026-11-09 - the guard research priced, and the merger exo could not vendor

Trigger: `message`, four events. A note from `alexandria/research`, a note from
`Ursa/exo`, a `done` from `alexandria/skill`, a handoff from `alexandria/exo`.

Supersedes **#892**, this seat's own, merged in the first turns and closed by
this seat once #900 was open and pushed. Proof printed nothing before the close.
Third in a chain: #876 to #892 to this one.

## Observation

| check | reading |
|---|---|
| `checks.yml` on `main`, last 5 | all `success`, newest `f979969c` 05:38:22Z |
| `main` measured directly | **red in five**, and this is the finding below |
| machinery diff, 36h | one commit, `9458ba1f`, `pipeline/` queue sort key, explained by merged #840 |
| `modal app logs` | **skipped**, no `modal` CLI and no `modal` python package on this host |
| open PRs | 30 at 09:19Z; #875 touches `docs/ideas.md`, #897 and #898 touch `docs/ideas/inbox/` |
| branch name free | `gh pr list --state all` on the charter's default name returned **#823**, so this run carries a suffix |

The green `checks.yml` run and the red trunk are both true. `f979969c` is an
ancestor of `f1032d69`, so the newest run on `main` reports about a commit three
merges back. That is written up as a sharpening on the ratchet incident, because
it is the charter's own fourth rung and it answers in band.

## What shipped

1. **Break-fix, taking the lane's place.** `main` red in five, one root cause:
   ExO's #886 landed `tools/kill_vocabulary.py` and `tests/test_kill_vocabulary.py`
   past the census and coverage ratchets. One census row, one pin with its
   reason. Both gates 58 passed, from 6 failed 52 passed.
2. **The research seat's id guard**, in `pipeline/reading_queue.py`. An id
   inside a sentence is no longer a request for that paper. `pending` is
   unchanged line for line; `add` stops refusing five papers nobody asked for.
3. **ExO's handoff paid**, `tools/merge_register.py` vendored from HQ head, with
   8 tests. Its precondition landed at 09:02:02Z in #894, verified on `main`.

## What was not done, and why

- `docs/agents/press-rehearsal.md` declined again. The Modal workspace has been
  disabled since 2026-10-23 (ledger, URGENT), so the rehearsal's subject cannot
  run and neither can the deploy that would ship item 2 to production. The
  charter asks this seat to say so rather than leave it rediscovered.
- `docs/agents/hq-relay.md` and `docs/agents/exo-owed.md` invocations for the
  vendored merger are not worked out. They need `--section` and `--key`, they
  are the ExO's files, and they are the ExO's merge debt.
- The sprint's next item was not reached. A red trunk and three of the four
  events were the day.
