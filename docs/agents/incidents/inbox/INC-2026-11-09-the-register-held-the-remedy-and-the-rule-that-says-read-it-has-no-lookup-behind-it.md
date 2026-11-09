## INC-2026-11-09-the-register-held-the-remedy-and-the-rule-that-says-read-it-has-no-lookup-behind-it a seat obeyed check-the-register, shipped red, and the remedy was in an entry its own seat wrote twice (2026-11-09, engineer seat, message wake)

**What happened.** Every charter in this repository carries a step called "check
the register before you ship". This morning the skill seat followed it, shipped
a pull request red on the receipt gate anyway, and handed the merger a choice it
did not need. The remedy was already written down. It is in
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`,
filed by that same seat, which prescribes moving the superseded same-day bundle
to `skills/_validation/results/superseded/` because both consumers glob one
level and skip it. That seat had applied that remedy twice before. Its later run
found it, applied it a third time, and went from 1 failed to 29 passed on
`tests/test_skill_receipts.py`.

So the rule fired, the seat obeyed it, and the step still did not work. The
reason is not a missing rule and the seat that reported it said so in its own
words: "Missing lookup, not missing rule." Nothing in this repository answers
the question a seat actually holds, which is a failure rather than an id. Has
this failure been filed before, and did that entry prescribe a remedy?

**Why it is in this register.** The standing rule records a repeat at the moment
it repeats, and this is the second instance in one day. The first is
`INC-2026-11-09-a-sixth-day-of-one-defect-was-registered-to-this-seat-and-sat-thirteen-days-because-nothing-made-the-register-fire`,
written by this seat four hours earlier, whose own fix paragraph proposed a
reader of this register and then filed it as a ledger proposal rather than
building it, with the reason that the run's day was already spent. The register
also carries a 2026-09-30 precedent for the narrower shape,
`INC-2026-09-30-finance-ledger-never-checked-against-ban-list`, whose fix
paragraph says in its own words that the step "already exists and already covers
this seat, so this is not a missing rule, it is one run that had the rule and
skipped it". That reading was available for six weeks and this is what it cost
when the rule was obeyed rather than skipped.

**What it cost.** The skill seat's run shipped red on one test and said so
rather than routing around it, so the direct cost is one pull request that
needed a second pass and one merger decision that should not have existed. The
larger cost is not bounded by the reds anyone saw, and that is the same seat's
measurement rather than this one's inference: after its own edit it left two
bundles on one date and the published receipt read all ten current, because the
new name sorted before the old one on the letter `a`. Right by luck. So the
count of wrong published receipts is not bounded by the failures that announced
themselves.

Two structural numbers, measured here on `main` at `5c0b911a`, that say why
grepping the register is not the missing lookup either:

```
register entries in docs/agents/incidents.md     374
entries living only in docs/agents/incidents/inbox/   258
```

A seat that opens the register file and greps it reads 59% of the register. The
remedy missed this morning was in the inbox half, which is exactly what L-A18
asked for and exactly what the fold leaves unmoved, since `incidents.py check`
deliberately does not require an empty inbox.

**The fix, shipped in this pull request.** `tools/incidents.py prior` takes the
failure in whatever shape it arrived, a test name, an assertion, a path, a flag,
a sentence, or a whole pytest log through `--file`, and returns ranked entries
from both halves of the register with each one's fix paragraph printed and a
verdict on it: `REMEDY`, `OPEN` when the fix section says the fix is owed, and
`NONE` when the entry has no fix section. Terms are weighted by inverse document
frequency over the entries, so a path appearing in two entries outranks a word
appearing in four hundred and there is no stopword list to go stale. It reads
632 entries in 2.4 seconds with no network.

Its regression test is this incident. The query that reproduces this morning's
failure must keep returning the 2026-10-26 entry with a `REMEDY` verdict and the
word `timestamp` in the paragraph, or the instrument has stopped answering the
only question it was built for.

And one line of wiring, because an instrument nobody runs is the defect this
entry is about: `incidents.py new` now runs the lookup on the slug it has just
written. Filing is the one moment every seat passes through, and it is the
moment the seat holds the failure and has not yet read the register.

**What this does not fix, and it is the honest limit.** Nothing makes a seat run
it. The charter sentence still says "check the register" and a sentence is what
failed here. Wiring it into `new` catches the seat that files and misses the seat
that reads, decides there is no precedent, and ships. Making it a gate was
considered and rejected: a lookup that can fail a run is a lookup a seat stops
running, and an unrun lookup is the defect, so `prior` always exits 0. The
charter line that would name it belongs to the owner's merge, so it is proposed
in `docs/ideas.md` rather than written here.

**Two defects this run shipped into its own fix before catching them, recorded
because they are one mistake and it has instances elsewhere.** Both were default
arguments evaluated at import. `new_entry(inbox=INBOX)` meant a test that
redirected the inbox wrote a fixture into the real register's inbox, and it did,
once, before the line was changed. `report_prior(stream=sys.stdout)` meant the
report was written past `capsys` rather than to it, so a test asserting on the
output read an empty string and the first diagnosis was aimed at the ranking.
`tools/target_census.py` in the same family of tools already uses `stream=None`
with `or sys.stdout` in the body, so the convention existed and this code
diverged from it. Both are pinned by tests now. Blameless note: the second one
cost more than the first because its symptom pointed at the wrong component,
which is the ordinary shape of a defect in the test harness rather than in the
thing under test.
