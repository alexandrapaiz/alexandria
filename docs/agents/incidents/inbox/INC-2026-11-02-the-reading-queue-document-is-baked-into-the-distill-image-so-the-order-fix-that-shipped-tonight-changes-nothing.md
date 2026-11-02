## INC-2026-11-02-the-reading-queue-document-is-baked-into-the-distill-image-so-the-order-fix-that-shipped-tonight-changes-nothing - a fix merged into a document that the pipeline reads from an image, which is the merge-not-deployed class with a new kind of member (2026-11-02, research seat)

**What happened.** The skill seat corrected a conclusion this seat shipped
earlier tonight: that the three queued containment papers were blocked on the
compute workspace alone and not on a queue write. The correction is right and
was reproduced here rather than accepted. `pipeline/reading_queue.py`'s
`pending` deduplicates by paper id keeping the first line in file order, and
only then classifies the survivor into the blocked-skill group, so the
signature that decides a paper's group is whichever of its duplicate lines a
merge happened to put on top. Measured on the skill seat's own branch head,
94 pending lines after dedup either way:

| section order | priority-group members | the three papers drain at |
|---|---|---|
| skill sections above research's (as shipped) | 3 | 1, 2, 3 |
| research sections above skill's | 0 | 88, 89, 90 |
| either order, with dedup preferring the blocked signature | 3 | 1, 2, 3 |

`MAX_PER_RUN` is 6, so positions 88 to 90 are not "later", they are never.

**Why it is in this register, and it is not the ordering defect.** The
ordering defect is one seat's find and one engineer's repair. The repeat is
what happens to both repairs after they merge. `pipeline/distill.py:326`
installs `docs/research/reading-queue.md` into the Modal image with
`add_local_file`, and line 315 installs `pipeline/reading_queue.py` beside it.
So the skill seat's fix is a change to a baked document and the parser fix
routed to the engineer is a change to a baked module, and **neither reaches
the running drain until the chair runs `modal deploy` by hand.**

That is the class of `INC-2026-09-26-interpret-stale-third-sighting`,
`INC-2026-09-28-merge-not-deployed-repeat` and
`INC-2026-09-28-repair-written-never-deployed`, and this seat's own charter
already carries the rule as law: check whether the running image is current
before spending a proposal on an image-baked file, because a second fix
stacked behind an undeployed first one reads as progress and changes nothing.

**What is new, and it is the only part worth the entry.** Every prior instance
of this class was a prompt or a pipeline module, and the charter's list of
image-baked files names exactly those: six prompts and `sources.yaml`. A
document under `docs/` is on nobody's list. `docs/research/reading-queue.md` is
hand-edited by three seats every night, is the one file this seat's reading-
queue duty is defined over, and is as frozen as `prompts/distill.md`. The
deploy ladder was not evaded here; it was never consulted, because the file
does not look like the kind of thing the ladder governs.

**What this seat is doing about it.** Nothing in `pipeline/` or in the charter's
image-baked list, both of which are other seats' surfaces, and the charter's own
rule says not to spend a proposal into a file whose route is frozen. Routed to
the engineer with the measurement, and named here so the next seat that fixes
the queue's order learns the freeze from this file rather than from a drain that
keeps using the old order.

Ban list checked on this entry.
