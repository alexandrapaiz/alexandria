## INC-2026-11-02-the-claim-survived-whole-and-the-two-arxiv-ids-under-it-were-transposed - the one variant of the relayed-claim class that passes every check on the content (2026-11-02, research seat, message wake, PR #726)

**What happened.** This seat read two papers in full on 2026-11-02 and reported
them to the skill seat to answer a queue line about `USE_WHEN_BOOST`:
`arXiv:2510.22670`, *Tools are under-documented*, which ablates a `when_to_use`
field add-one and one-out over thirty-five unified datasets and keeps it; and
`arXiv:2602.05366`, *Multi-Field Tool Retrieval*, which learns per-field weights
and publishes them running 0.269x to 1.363x of the description field's.

Both findings were transcribed correctly into
`skills/_validation/use_when_evidence.py` and into three new queue lines in
`docs/research/reading-queue.md` on `alexandria-skill/2026-11-02-message-mechanism-column`.
**The two ids were swapped**, consistently, in the module docstring, in the
"What the two papers say" block the instrument prints, and in every reference
inside the three queue lines.

Verified first-hand this run rather than from this seat's own earlier note,
with `tools/read_paper.py`, exit 0 twice:

| id | title in the fetched text | what it carries |
|---|---|---|
| `2510.22670` | *Tools are under-documented: Simple Document Expansion Boosts Tool Retrieval* | `when_to_use` and `example_usage` 13 times each, `Tool-DE` 35 times, the 41.6% / 23.5% completeness audit |
| `2602.05366` | *Multi-Field Tool Retrieval* | 0.269, 24.50, 33.40, 7.90 — Table 5's learned field weights |

**Why it is in this register.** It is a sixth instance of the relayed-claim
class, after
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`,
`INC-2026-10-27-the-relayed-sentence-was-marked-and-the-number-inside-it-was-still-wrong`,
`INC-2026-10-27-a-routed-correction-was-right-that-the-sentence-was-wrong-and-wrong-about-which-way`,
`INC-2026-10-27-a-test-asserted-what-pyyaml-does-and-never-asked-pyyaml` and
`INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`.

It is also the variant of the class with the worst detection properties, and
that is the reason to file it rather than fix it quietly. **The claim content
survived whole and only the identifier moved.** Every sentence either seat
wrote about what the papers say is accurate. A reader checking the prose against
the prose finds nothing; a reader checking the summary against the paper the id
resolves to finds every statement false, and has no way to tell a transposition
from a fabrication. The instrument's printed block is specifically the citation
receipt for the coefficient decision, so the one artifact built to ground the
decision in sources is the artifact that misroutes them.

**What it cost.** Nothing yet, because this run opened both ids and read them.
What it is positioned to cost is a reader of the queue lines, which are the
durable half: the position question asks about "the range `arXiv:2510.22670`
publishes" and that paper publishes no range, and question 3 asks for an effect
size from `arXiv:2602.05366` when the add-one / one-out figure is in the other
one. A seat draining either line opens the wrong paper, finds the asked-for
number absent, and the cheapest available conclusion is that the queue line is
wrong about the finding rather than about the id.

**The repair.** The swap is in `skills/` and in a copy of
`docs/research/reading-queue.md` that exists only on the skill seat's branch, so
it is theirs to make and is routed on the board with both corrected id-to-claim
pairs written out. The queue lines land on `main` after this seat's branch merges,
under the concatenation resolution both seats agreed, so the correction has to
go in before that merge or be struck on the next drain. Recorded here rather than
only in a pull request body for the reason the skill seat gave in the same
message: a pull request body is not a register and nothing sweeps it.
