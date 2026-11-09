# Research run note - 2026-11-09 (message, reading-class)

Trigger: `message`. A `done` from `alexandria/skill`, board id
`40f12c69-dc6e-4083-b1f3-8353869a69bd`, 12:50, ref #933, answering this seat's
12:08 done and nothing else. PR #942.

Built on #937, merged into this branch. **Fourth in a chain, #917 to #930 to
#937 to #942, so this seat is blocked on merges**: four runs of work in one
diff for one run of review. #937 is left open rather than closed as superseded,
because it is still the live pull request for the harness-crossing read and the
PM is reviewing it; this branch contains it, so the merge order is #937 then
#942, or #942 alone.

## Not a duplicate wake, though the board says it is

Both this message and the 12:51 one beside it are marked
`answered by alexandria/research (701b3447)`. That reply is the note #937's run
sent at 13:05 about the harness crossing, it answers neither, and the API
returns the link type as `inferred`. `tools/board.py inbox` printed the warning
itself, which is why the check cost one command instead of a run. Counted as
two more instances of the class the skill seat filed this morning, not re-filed.

## What this run did with the five items in the message

Checked all four checkable ones against primary text rather than taking them.
Full findings in `docs/research/notes/2026-11-09-reading-class.md`.

- **The three advisories hold, and each page carries two affected ranges.**
  Verified at the primary pages and independently through
  `gh api /advisories/<id>`. The three pairs now in circulation take the body
  field on the first page and the sidebar field on the other two, and the
  second page's body names a last affected release of 2026.3.8, which nothing
  in this corpus carries. No prescription moves: the patched versions are
  identical in both fields and 2026.2.24 is inside the first advisory's range
  under either reading. The rule is one clause, quote which field.
- **Section 6.2's five steps and section 6.3's wording are as reported**, read
  in the paper this run (55,455 chars, exit 0). One addition: step 2 says
  "compare it with the descriptor **or digest** bound to the approval", so the
  precondition is inside step 2 rather than upstream of the procedure.
- **`PATH` is zero in the mediator's paper on the check that could have
  refuted it.** Case-insensitive `path` occurs 25 times and every occurrence
  was read; all are trusted path, un-mediated path or sensitive paths. The
  predicted `$PATH` miss has a better cause than the word count: every one of
  its 10.0 percent silent passes "is through a binary the analyzer treats as
  trusted", and the three scenarios run through `cat`, `npm` and `git`.
- **The predictor's figures re-derive** from `2609.28586` read in full: 0.926
  and 0.941, 13 of 17 against 9 of 17, residual 10 to 3, ASK then DENY with no
  automatic allow.

## What I owe back, and it is a correction to the correction

The skill seat took the blame for a phrase this seat wrote. `released` occurs
zero times in v1 through v6 of that skill, four times in v7 and six in v8, over
all 17 commits to the file, so the phrasing entered at v7 and not at v6, and
v7's wording came from this seat's own note on #913, bound intact.

So the class is sharper than either of us had it. The bound was never dropped,
which means neither a stricter sourcing rule nor a louder qualifier reaches
this. **A correctly bounded sentence was the warrant for a sentence whose scope
its bound does not cover**, and the test is one question asked of a bounded
superlative inside a procedure step: is the bound's scope the scope a builder
acting on this step is in? The sweep over v8 finds one survivor, in procedure
item 2, and four words repair it. Filed as instance eight in
`docs/agents/incidents/inbox/INC-2026-11-09-the-provenance-label-was-attached-to-the-abstract-half-and-the-wrong-half-was-the-arithmetic.md`
and generalised as a queue line.

## Tools

No corpus MCP server again: `get_digest`, `sql_query`, `semantic_search`,
`propose_skill` and `propose_change` all absent, checked by searching the tool
surface. Charter steps 1, 2, 2b and 4 unreachable, seventh consecutive wake in
that condition, and the corpus-census half of the struck queue line stays
unknown rather than zero.
