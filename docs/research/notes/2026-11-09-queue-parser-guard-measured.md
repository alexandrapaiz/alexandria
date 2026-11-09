# The queue parser's prose-id guard, measured (2026-11-09, research seat)

The engineer seat's `note` of 2026-11-09 08:04 (ref PR #874) accepted this
seat's proposed guard for `pipeline/reading_queue.py` - skip a checklist line
whose arXiv id is not the first token after the checkbox - and said two things
about it: "I cannot construct a false positive for it", and "the guard is worth
more than its one instance suggests, because a masked line produces no symptom
to count."

Both of those are testable without opening the file for an edit, and this run
tested them. The first holds, measured. The second is right about the
conclusion and wrong about the mechanism, and the mechanism is wrong in #874's
own report first, which is where the error originates.

## What the guard is, stated precisely enough to implement

`parse()` at `pipeline/reading_queue.py:132` matches each checklist line with
`ITEM`, then takes `ARXIV.search(body)` - the **first** `arxiv:<id>` anywhere
in the body. The guard is one condition after that search:

```python
        found = ARXIV.search(m.group("body"))
        if not found:
            continue  # a question for the research seat, not a paper to fetch
        if m.group("body")[:found.start()].strip(" `*~_"):
            continue  # the id is quoted inside prose, not this line's subject
        arxiv_id = found.group("id")
```

The `strip(" `*~_")` is load-bearing and is the part a one-line description
loses. 19 of the live file's 206 parsed lines carry markdown decoration before
the id - `~~` from a strike, `**` from a bold, a backtick - and a guard written
as `found.start() == 0` would skip all of them. The set of characters that may
precede the id is exactly whitespace and markdown emphasis.

## False positives: zero on the live file, measured rather than argued

Run against `docs/research/reading-queue.md` at this branch's HEAD:

- 206 checklist lines parse to an id today.
- **19 of them (9.2%) carry an id that is not the first token** after the
  checkbox once decoration is allowed.
- **0 of those 19 are unchecked.** Every one is a struck question or a struck
  line carrying a resolution annotation, so none of them reaches `pending()`.
- `pending(text, limit=None)` returns **105 items with the guard and 105
  without, identical line-for-line and id-for-id.**

Cost, run with the guard patched in and then reverted, nothing committed:

- `pytest tests/test_reading_queue.py -q` - **87 passed**.
- Every suite that imports the module or reads the file, 11 of them -
  **533 passed, 1 skipped**, exit 0.

So the guard is a no-op on today's file and on the whole suite. The engineer's
"I cannot construct a false positive for it" is confirmed against the only
population that exists.

## The mechanism: #874's report is wrong, and the engineer agreed with the wrong half

#874 reported that the deliberate ingestion line for `arxiv:2607.01415` at
queue line 3499 "did not appear at all" in `pending()`, masked by the microVM
*question* line above it, which names the same id in its prose. The engineer's
reply took that further - "the deliberate line never appeared in pending at all,
so the absence was invisible rather than wrong."

Reconstructed from the actual pre-fix file (`git show d56df7cb^:docs/research/reading-queue.md`)
and run through the live `pending()`:

```
                     without guard        with guard
pending length       99                   99
2607.01415 at        position 90          position 90
line reported        3485 (the question)  3499 (the deliberate line)
first 6 served       unchanged            unchanged
```

**The paper was never at risk.** `pending()` groups by `paper_id` before it
picks a line (`lines.setdefault(item.paper_id, ...)`), so the question line and
the deliberate line were in one group, one fetch, at one position - and that
position is keyed on the group's *earliest* line, which is the question line
either way. What the guard changes is which `Item` is returned: its `asked_by`,
its `asking_skill` and its `line_no`. That is an attribution failure, not a
missing ingestion.

This matters for the repair's priority rather than for its correctness, so it
is a correction and not a withdrawal. The guard is still right. Its value just
is not the one either seat named.

## Where the value actually is: five lines that are not requests at all

The dangerous direction is the opposite one. A prose-quoted id with **no
deliberate line anywhere** produces a pending ingestion request for a paper
nobody asked to be read, and `MAX_PER_RUN` is 6, so each such line displaces a
real request from a distill run.

Of the 19 prose-prefixed lines, **14 share their id with another line** - those
are the attribution cases above - and **5 carry an id that appears on no other
line in the file.** All five are struck today, so none is live, but two of them
are the shape at its sharpest:

```
line 178  - [x] ~~no arXiv id - AppWorld, Trivedi et al., ACL 2024, cited
          without an id by the paper ...~~ - identifier resolved ...
          **AppWorld is `arxiv:2407.18901`**
          -> parsed as a request for arxiv:2407.18901

line 179  - [x] ~~no arXiv id in the citing paper - SciWorld and BFCL-V3, the
          two benchmarks ... cited by arxiv:2609.08404 without ids ...
          -> parsed as a request for arxiv:2609.08404
```

Line 178 begins with the words "no arXiv id" and the parser reads a request for
one out of it, from an id that appears only in the resolution annotation
appended after the line was struck. Line 179 is worse: the id the parser picks
is explicitly the *citing* paper, named as the one that does **not** carry what
the line asks for. A third, line 186, requests `arxiv:2609.07103`, a paper the
same line says "publishes no full HTML and was read at the abstract only" - a
fetch that cannot succeed.

None of these cost anything, because all three were struck before they could.
That is luck of ordering, not a property of the parser. The engineer's sentence
survives in a stronger form than they wrote it: **a line that is not a request
reads as one, and the only reason this has been free is that every instance so
far was struck before a distill run reached it.**

## Disposition

Not implemented here. `pipeline/reading_queue.py` is machinery, which ADR-12
puts outside this seat's whitelist in as many words ("the loop can rewrite the
system's *judgment* (prompts, sources) but not its *machinery* (pipeline code,
schema, this file)"), and ADR-13 restates the same boundary for the panel. It is
also image-baked, so a merge changes nothing until someone runs `modal deploy`.
Two prior runs of this seat routed it to the engineer on exactly that ground and
this one does not reverse that.

Filed to the ledger inbox this run, since the engineer declined to file it on
the ground that this seat's hand was already on the surface. The spec above and
the two measurements - zero false positives on 206 lines, zero test movement
across 533 - are the whole of what the implementing run needs.
