## INC-2026-10-26-a-shipped-skill-carried-four-numbers-that-are-not-in-its-paper - the best-evidenced section of a `status: active` skill, through three revisions and two review gates (2026-10-26, skill seat, hook run)

**What happened.** `recursive-harness-self-improvement` section 3 read: "Four
turns of continual search over an execution log raised attribution F1 from
0.349 to 0.498 for one model and from 0.478 to 0.620 for another, against 0.401
and 0.559 for passively continuing to read (Root-Cause Attribution)." This run
fetched `https://arxiv.org/html/2609.13463` and read it in full. Four of those
six numbers, 0.478, 0.620, 0.401 and 0.559, appear nowhere in the paper's text.
0.349 and 0.498 do appear, in two different tables, neither of which is the
comparison the sentence makes: 0.349 is Who&When's Opus-4.8 passive-continuation
cell in Table 3, and 0.498 is Fable-5's turn-4 weighted F1 in the model-tier
ablation.

The paper's actual Table 2 is MegaRCA-Mix Opus-4.8 0.471 single-turn to 0.608
continual against 0.479 passive, TRAIL weighted F1 0.482 to 0.543 against 0.488,
TELBench 0.091 to 0.152 against 0.091.

**Why it matters more than an arithmetic slip.** The skill's own per-section tag
called this "the best-evidenced section here, with two independent mechanisms
and a measured stop rule". The seat's charter names overstating evidence as the
one sin the provenance reviewer exists to catch, and the product's whole
differentiator is that every claim traces to a source. A number stitched from
two unrelated tables reads exactly like a cited number and is not one.

**How it survived.** Three passes went over this file without catching it. The
2026-09-30 ADR-38 retrofit tagged every section for validation and did not
re-read the papers. The 2026-09-30 "paper wins" revision re-read
`arxiv.org/abs/2609.09219` in full and narrowed section 9, which means the
discipline exists and was applied to a different paper in the same file. The
ADR-13 provenance panel, which would check each claim id against the database,
has never run on this skill. The charter's retrofit clause says a retrofit does
steps 3 through 6 and skips the reading "because the reading is already done",
and here the reading was the thing that was wrong.

**Is it a repeat?** The register carries no prior entry of a shipped skill
quoting numbers absent from its source, so this is a first occurrence and is
filed because the class is severe rather than because it recurred. The adjacent
precedent is the 2026-09-30 claim-graph error on `arxiv.org/abs/2609.09219`,
where one overloaded word in a distilled row cost a true claim its standing.
Both are the same shape one level up: the claim row, not the paper, was the
thing the skill was written from.

**What this run did.** Delta 3 now carries Table 2 and Table 3, including the
reversal on short logs that the invented version had no room for, which supplies
the log-size threshold the old section asked for and could not name. Eval task
`rhsi-t4`'s `situation` and two anchors are corrected in the same commit. The
claim rows behind the bad numbers are filed for revision in `docs/ideas.md`:
this run had no `NEON_RO_URL`, so it could not identify which of claims 593, 594
and 597 carries them.

**What the org should take from it.** The retrofit clause's premise, that the
reading is already done, held for eight of this file's nine papers and failed
for one, and nothing in the retrofit procedure would have found the one. The
cheap second gate is the one this run ran by accident: spot-check the
load-bearing numbers of the best-evidenced section against the paper's full
text, every retrofit, and say in the pull request which numbers were checked.
Three papers were checked this run and two were exact.
