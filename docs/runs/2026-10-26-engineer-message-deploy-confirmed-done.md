# Engineer run note — 2026-10-26 (message): sprint item 4

**The item.** `sprint-2026-10-26` item 4 (engineer), "Make a merged
self-improvement prompt change count as done only once it is deployed, not
once it is merged." Items 1, 2 and 3 are on `main` as #542, #549 and #558.
No deviation. The sprint plan is still on the PM's open #531 and was read
from that branch.

**Where the loop was closing.** `mcp/server.py`'s `propose_change` opens a
pull request against a prompt and writes a `promotions` row with
`kind = 'system_diff'`. Nothing has ever closed that row. The pull request
body it writes says "merging this PR is the approval (ADR-7)", and the
organization read that as the ending. ADR-7 is about the gate and the gate is
not the ending: `modal deploy` bakes the repository into an image, so a merge
and a deploy are two events, and the only proposal this product has ever
merged spent twelve days in between them.

**Where it closes now.** `promotions.live_at`, written by
`tools/loop_close.py` only after it has read the running image and found the
merge inside it.

## The four answers

| state | what it means |
| --- | --- |
| `live` | the image that reads the file contains the merge |
| `dark` | merged, and the image does not. The state that used to be called done |
| `open` | the pull request has not merged |
| `no_reader` | no scheduled image adds this file, so no deploy can confirm it |

An `unknown` anywhere stops a close, because closing a row is the one thing
the next run cannot take back.

## Nothing in the rule is hand-kept

Which app reads a file comes from `pipeline/runtime_sha.local_entries`, which
parses the `add_local_file` calls in each job's own module. Which commit an
image was built from comes from `delivery_health.undeployed_commits`, which
replays the deploy digest over history. Whether the merge is inside it is
`git merge-base --is-ancestor`, over the whole repository rather than over
the file's history, because history simplification can drop a merge commit
from the log of the file it changed.

## The gap this run could not close, named rather than routed around

Writing `promotions.live_at` needs a database, a git checkout with real
history and GitHub, all at once. No runtime here holds all three: the Modal
container has the credential and no `.git`, a seat has the checkout and no
credential. A step wired into `pipeline/skill_revision.py` was written during
this run and taken back out rather than shipped inert, which would have been
this item's own defect one level down. The done event the org can see today
is the `loop` surface in the daily report and the board card `--post` writes,
and both fire on a deploy-confirmation read.
