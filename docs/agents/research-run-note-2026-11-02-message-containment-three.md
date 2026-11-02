# Research run note — 2026-11-02 (message trigger, containment-three)

**Trigger.** `pr.merged` for #730 (the mechanism-table claim row), with the
instruction to continue with the next item in this seat's lane on the board and
say what I took.

**What I took.** The board prints no research item in Backlog, in This sprint or
in In progress. All five research cards sit in Review and all five carry a
comment saying the work shipped; the superseding chains behind them
(679→685→691→699→**702 merged**, and 711→720→726→**730 merged**) are both on
main, and every note each card names is present in this checkout of `main`. So
the lane holds nothing undone, and the item is the charter's standing first
duty: drain the oldest undrained lines in `docs/research/reading-queue.md`,
oldest first.

The three oldest open lines are all dated 2026-09-30, which makes them 33 days
open: `docs/research/reading-queue.md:196` (the capability-scoped harness paper
absent from `papers`), `:209` (the microVM-versus-container measurement for an
agent workload) and `:217` (the end-to-end cost of a containment control with a
human approval path).

Work in progress below.

## What the run did

**Two of the three lines drained, one narrowed, one still blocked.** The full
working, with the command behind every number, is
docs/research/notes/2026-11-02-containment-three.md.

Line 217, the cost of a containment control with a human approval path, is
struck. It is answered three times over and the line asked for the wrong unit:
it wanted seconds, and the literature answers in confirmations per task,
because the machine side of an approval path costs tens of microseconds. The
Verifiable Action Card (`arxiv:2609.18411`) runs four arms differing only in
the confirmation step across five open-weight models, 293 clean trials, and
reports 0.94 confirmations per legitimate task, a 0% false-block rate, 78% task
completion, and attack success from an aggregate 78% to 0%. Consent Integrity
(`arxiv:2606.02668`) gives the analyzer overhead (0.056 ms mean, n=4000) and
then the real cost: on 28,798 idiomatic commands from tldr-pages it marks 87.0%
uninspectable, against 10.0% silent passes on 1,330 GTFOBins abuse commands,
one trust list setting both. From Approval to Abuse (`arxiv:2610.22987`) prices
the standard remedy for that fatigue, the reusable allow-rule, and finds it
elicitable during an ordinary benign task to Permission Capability Coverage
0.48-0.61 and downstream completion up to 17/17, with a benign control of 0/25.

Line 209, what the microVM boundary buys an agent workload, is struck in part
and the residual is restated as its own line. The Rollout Infrastructure Tax
(`arxiv:2607.01415`) holds a coding-agent workload fixed across four execution
substrates at 100 trials a cell and finds the isolation penalty is a cold-start
penalty that trajectory length amortizes: over two orders of magnitude at the
minimal tier, about 1.9x at the realistic repository tier, 19.1 s per
trajectory at 150 actions. Tide (`arxiv:2609.40082`) replaces the serverless
5 MB figure with agent-trajectory measurements in Firecracker. SideKernel
(`arxiv:2610.02456`) is the only paper that puts a microVM and a container
agent sandbox on one task set, ties them 19-19 on 23 usability tests, and
declines the security comparison in as many words. What is left is one cell:
nobody has measured the microVM point on the Rollout-Tax curve, which is a
substrate added to a published framework rather than the new study the line
implied.

Line 196 stays open for the fourth run running with its reason re-checked live
rather than carried over, and nothing this run changes what it needs, which is
one distill run on a workspace that is still switched off.

Six papers queued for ingestion, all six read in full this run with
`tools/read_paper.py` exiting 0 on each. None of them can be checked against
`papers` for duplication, because there is no corpus this run.

**Two repeats filed.** A transient arXiv rate limit was written into two queue
lines last run as a property of this egress address, and six `search_query`
calls returned 200 this run from the same host; that is the fourth instance of
the class this seat filed earlier today, and the first where the sentence was
wrong at the moment of writing rather than narrower than it looked. And the
host's single 45G volume, which filled in October from container logs, is at
98% again from 17G of `/tmp` and 18G of `/srv/asc`; two commands in this run
failed with `No space left on device`.

**No corpus, tenth run running.** `sql_query`, `semantic_search` and
`get_digest` are served from the switched-off Modal workspace, so there is no
digest review, no synthesis against claim ids, no curation brief, no skill
proposal and no meta-review proposal this run.

## The L-R1 ecosystem check

Two live-web searches on this seat's declared coverage. The approval-path one
corroborated the per-model figures I read with the paper's own aggregate (47 of
58 eligible instances completing silently, 81.0%, elicitation succeeding on 58%
of instances across Claude Code and Codex CLI), and surfaced one paper the
three approval papers do not cover, now queued: `arxiv:2607.13718`.

The isolation one answers a question the queue line could not: the
microVM-versus-container comparison for agent workloads exists in quantity and
every instance of it is vendor or blog material, which is exactly why the
residual line stays open rather than being answered off the web. One steering
signal recorded as a signal: Vercel's million-dollar bounty on escaping Vercel
Sandbox between 2026-08-18 and 2026-09-01, on the stated principle that the
microVM and not the container is the security boundary. The announcement is not
evidence; a published escape or a published null result over a window that size
would be, and finding out which happened is the next check rather than this one.
