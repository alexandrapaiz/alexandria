## INC-2026-10-27-a-cost-figure-with-its-unit-and-its-backbone-still-inverted-the-cost-ordering -- the morning's own remedy was applied in full and the repaired sentence still told a builder to pick the expensive defence (2026-10-27, research seat, message wake, PR #637)

**Fourth instance in two days of a number in shipped skill text that its own
primary source cannot support as stated, and the first to occur *inside the
repair for the third*.** The standing rule records a repeat at the moment it
repeats, so it is written here rather than reasoned about.

The three before it:
`INC-2026-10-26-a-shipped-skill-carried-four-numbers-that-are-not-in-its-paper`
(skill seat, four of six figures absent from the paper),
`INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`
(research seat, three of thirteen queue lines naming a paper that does not
contain the quantity), and
`INC-2026-10-27-a-bare-multiple-costs-two-runs-to-check-and-the-second-found-the-units-did-not-match`
(skill seat, four multiples with no unit and no backbone, two runs of two seats
to resolve).

**What happened.** The remedy the third instance shipped, at 01:10Z this
morning, is a convention: *a figure written into a skill carries its unit and
its backbone, or it is not written.* It was applied in the same run, and the
repaired `skills/agent-containment` delta 1 is materially better for it. The
same run's new caveat ends:

> Read with the same care that a tool filter, which looks like the cheap
> defence, costs 7.06x input tokens at the median under attack, more than CaMeL
> does.

That sentence satisfies the morning's convention completely. The unit is
written in (input tokens). The statistic is written in (median). The condition
is written in (under attack). The backbone is written in two sentences above
(Claude 3.5 Sonnet). Both figures check out against CaMeL's Table 13 — the tool
filter's input median is 7.06x and CaMeL's is 2.02x.

**And it is the only cost comparison in the skill, so a builder reads it as the
cost ordering, which runs the other way.** Cost is paid on two token streams at
different prices. CaMeL's output stream is 6.08x the undefended mean under
attack; the tool filter's is 1.03x. With output priced at five times input —
Claude 3.5 Sonnet's published ratio on the day CaMeL was measured — the blended
multiples over the undefended task from the paper's own absolute Tables 11 and
12 are CaMeL **4.30x**, full tool filter **3.43x**, prompt sandwiching 1.48x,
efficient tool filter 1.43x, spotlighting 1.02x. CaMeL is the most expensive of
the five and stays the most expensive at every output-to-input price ratio above
2.03, which is every frontier model's pricing for the last two years. Not under
attack the gap is wider: 5.61x against 3.90x, break-even at 0.64.

**Why this is an incident and not a correction.** A correction would be the
replacement sentence, which is routed in `docs/research/reading-queue.md` under
today's drain record. The incident is that the surface survived its own remedy
*on the same day*, applied correctly, by the seat that wrote the remedy. Each
instance of this class has produced a remedy aimed at the attribute the last
instance was missing, and each remedy has been satisfied by the next instance:

| instance | what was missing | the remedy it produced |
| --- | --- | --- |
| four numbers not in the paper | the paper | name the paper the fact was read out of |
| the capability benchmark | the quantity in the paper | grep the fetched text for the named quantity |
| the bare multiple | the unit and the backbone | a figure carries its unit and its backbone |
| this one | the second token stream | — |

So the extension this one earns is **a cost figure names its statistic, its
condition and both token streams, or it is not a cost figure** — and the general
form behind all four, which is the part worth carrying: *a figure is checkable
when it names its provenance, and usable when it answers the question the
sentence around it asks.* Every remedy so far has bought checkability. None has
bought usability, and the sentence above is checkable and wrong.

**What it cost.** Nothing yet, because no buyer has read it. The sentence was
live for roughly ninety minutes. Finding it cost one paper fetch, which this
seat owed anyway, because a routed resolution is itself a second-hand claim and
re-reading CaMeL was the point of the run.

**Two more facts the same reading produced, filed here so they are not
rediscovered.** First, the three-value discrepancy the third instance recorded
inside CaMeL is understated: there are four values, not three, because the
headline 2.82x is a *mean of per-task ratios* reported as a median, and the
ratio of the means (3.58x input under attack) and the ratio of the medians
(1.82x) are two more defensible answers to the same question. Second, the
corpus ruling that follows is in the drain record: the absolute token counts
enter and no ratio is privileged, because every ratio is then derivable and
none of the four can be converted into the others.
