## INC-2026-11-02-the-backfill-entry-point-built-for-this-exact-gap-has-never-run-and-two-more-papers-the-window-cannot-reach-turned-up - the window gap is now a repeat with a built, unexercised remedy (2026-11-02, research seat)

**What happened.** The skill seat asked for a reader on one queue line: nothing
in this repository's corpus justifies `USE_WHEN_BOOST`, the 1.25x activation
multiplier that has been in the trigger instrument since lexical/2, and they
could not name a candidate arXiv id to queue against it. Two searches found two.
`arxiv:2602.05366` (Multi-Field Tool Retrieval, Tsinghua DCST, cs.IR, 5 Feb
2026) publishes the learned weights on the one field that corresponds to an
activation clause, and they span 0.269x to 1.363x of the description field's
weight across six dataset and retriever cells, below 1.0 in five of the six.
`arxiv:2510.22670` (Tools are under-documented, Oct 2025) ablates a `when_to_use`
field add-one and one-out on a dense and a sparse retriever over 35 unified
datasets. Both read in full this run, `tools/read_paper.py`, exit 0 twice,
74,580 and 71,958 characters. Neither id appears anywhere in `docs/`, `skills/`
or `sources.yaml`. **The categories are not the gap.** `cs.IR` is in
`sources.yaml` at tier `a` on line 13 and has been. The gap is the ingest
window: after the 2026-10-26 repair `pipeline/ingest.py` runs a forward date
cursor with `ARXIV_MAX_LOOKBACK_DAYS = 14` and its own comment says that past
fourteen days "a backlog is a backfill job, run deliberately". These papers are
nine and thirteen months old, so no run of the daily job on any day will ever
see them.

**Why it is in this register.** Third instance of the class and the first with
the remedy already built. The first was the monthly source census of 2026-10-26,
whose finding produced the window repair. The second is
`INC-2026-10-27-a-queue-lines-stated-reason-was-carried-through-an-amendment-and-had-been-false-since-the-day-it-was-written`,
where a queue line named six papers by id and the window could reach zero of
six. The third is this one, and what is new is that `ingest_ids` exists
specifically for it: `modal run pipeline/ingest.py --ids <ids>`, tier `b`, whose
docstring calls itself "the entry point the reading queue needs when a line
names a paper the window cannot reach". It has never been run for any paper this
seat has named, because running it needs the `NEON_RO_URL` and Modal credentials
absent from this sandbox for eleven consecutive runs. A remedy that is built,
correct, documented and unexercised is a different failure from a missing one,
and it is the one the register has not recorded before.

**And it is the relevance law failing as a mechanism rather than as an
attitude.** `prompts/research-agent.md` makes it charter that relevant does not
mean recent, that impact is revealed by traction rather than release date, and
that "a ranking that reads as a release-date feed violates it". The ingest can
see fourteen days. A 2023 paper compounding through the field this month, which
is the charter's own example of what should outrank yesterday's upload, is
unreachable by construction. The owner had to state that rule repeatedly before
it became charter; the pipeline has never been able to obey it.

**What it cost.** Nothing yet in this instance, because the finding is the
paper rather than the ingestion, and the two queue lines are written out in
`docs/research/notes/2026-11-02-use-when-boost.md` in the form they should take.
What it has cost cumulatively is three named papers this seat read in full and
could not file: `arxiv:2607.17598` four runs ago, and these two. Each took one
search to find and none is in the corpus.

**Two other repeats this run, counted here rather than filed again.** The wake
delivered 1,446 of 3,606 characters and cut before the sender's disposition,
which is the fifth truncated wake of 2026-11-02 and the third for this seat. The
class is already recorded twice, in
`INC-2026-11-02-the-truncated-wake-fired-a-third-time-while-the-entry-naming-it-sat-on-a-branch`
and
`INC-2026-11-02-the-second-wake-fired-after-its-own-answer-was-already-on-the-board`,
and both of those entries are on this seat's own unmerged branches, so `main`
holds neither. A third entry on a third branch makes the register worse rather
than better, which this file's own 2026-09-24 duplicate-removal note says in its
own words. **So the sighting is counted and the finding is that three entries
for one class now sit on three unmerged branches, which is the condition the
first of them was named for.**

**The fix, or why there is not one yet.** Two ids need one backfill run:
`modal run pipeline/ingest.py --ids 2602.05366,2510.22670`. Routed to the
engineer seat on the board, because `pipeline/` is outside the whitelist ADR-12
gives this seat and the credential is outside this sandbox. No meta-review
proposal is spent on it: the only whitelisted file the finding touches is
`sources.yaml`, which is image-baked, and the charter's precondition for
proposing into an image-baked file is a deployed-sha comparison against
`claim_links.method`, `triage_log.prompt_sha` or `digests.prompt_sha`, all three
behind the absent credential. The standing question this entry leaves open for
the ExO seat is whether a seat that names a paper the window cannot reach should
be able to queue the backfill without the credential, because today the only
route from "this seat read the paper" to "the corpus holds it" runs through a
job no seat on this host can start.

Ban list checked on this entry.
