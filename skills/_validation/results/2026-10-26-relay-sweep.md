# Relayed-citation sweep of the nine shipped skills, 2026-10-26

**Why this exists.** The engineer seat landed a fifth value on a claim's
evidence grade, `relayed`, for a claim whose subject is another work's result,
an `attributed_to` column naming that work, and an `evidence-relayed` finding
in the panel's adversary that lists a skill's second-hand cited claims. The
handoff that announced it carried the limit with it: the grade is written at
distill, so it reaches the next claim and none of the roughly two thousand rows
already in the corpus. Every claim these nine skills cite was written before it.

So the reviewer's new finding reports nothing on this library today, and a
reader who sees nothing cannot tell a clean library from an unlabelled one. The
read-only corpus audit that will size it needs the Modal workspace, which has
been down since 2026-10-23. This sweep is the number the library can have
without either: it looks for the shape in the skills' own prose, which is this
seat's surface, and it is a hand count rather than an instrument.

**Method, and it is reproducible without a credential.** For each of the nine
`SKILL.md` files, every sentence containing an attribution or a reporting verb
was extracted and read:

```bash
python3 - <<'PY'
import glob, re
pat = re.compile(r"\b(reported|reports|claimed|claims|states|argues|notes|"
                 r"concludes|explains away|dismisses|disputes|published|others|"
                 r"prior work|previous work|according to|attributed to|et al)\b", re.I)
for f in sorted(glob.glob("skills/*/SKILL.md")):
    body = open(f, encoding="utf-8").read().split("\n---\n", 1)[-1]
    for sent in re.split(r"(?<=[.!?])\s+", body.replace("\n", " ")):
        if pat.search(sent):
            print(f, sent.strip())
PY
```

79 sentences matched, across all nine skills. Each was read against the paper
named in its own clause, asking one question: is the subject of this sentence a
result the cited paper ran, or a result the cited paper reports about somebody
else? A sentence like "the published forwarding rate is 36 of 36" is first-hand
however relational it sounds, which is the same hard case the engineer's guard
was shaped around.

**Result: three instances in nine skills, and all three were already visible
to a reader.** None of the three was found by a grade, because no grade exists
on any of these rows.

| skill | the second-hand sentence | load-bearing? | state after this run |
|---|---|---|---|
| `context-window-engineering` | Random Attention's section 5.1 explaining away "the large gaps others report" in two cited works | **yes**, it was delta 1's framing | repaired. Both cited works were read in full by the research seat on 2026-10-26, the framing is withdrawn on the page, and the Caveats bullet names the class with both arXiv ids |
| `agent-memory-selection` | the reconciliation of SmartSearch against Fidelity Before Structure as two groups measuring at two keep ratios | no, the threshold is the paper's own k=3 to k=20 comparison | marked in place, both works named with their arXiv ids, both queued, and delta 2's heading narrowed to the within-study decision rule it can support |
| `agent-containment` | Hard Stop's incident facts, which trace to a vendor timeline and a METR investigation | no, the caveat exists to discount the paper | already marked in the file and already carried as `asserted` on claims 884 and 885. Queued as a question, because `attributed_to` wants the two works' names and the skill does not have them |

**What the number is worth, and what it is not.** Three of 79 relational
sentences, two of them non-load-bearing, is a better result than this seat
expected, and it is not a clean bill. It covers what the skills *say*, not what
the claim rows behind them say: a skill cites claim ids, a claim carries
evidence text, and a relayed sentence inside evidence text that no skill quotes
is invisible to this method. That half is the corpus audit's, and it stays open.

The one load-bearing instance was found by a seat reading two papers, not by
any guard, and it was in the skill this library has revised most. That is the
argument for the grade rather than against it.

**Reproduced on:** this branch, `alexandria-skill/2026-10-26-message-relayed-caveat`.
`python3 -m pytest tests/test_panel_provenance.py -q` 55 passed,
`python3 tools/skill_eval.py --check` exit 0 with 9 of 9 conformant,
`python3 skills/_validation/trigger_test.py` 58/67 unchanged from the base commit.
