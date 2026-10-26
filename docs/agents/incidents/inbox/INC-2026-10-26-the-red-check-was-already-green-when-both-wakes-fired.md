## INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired - four wake events about one red check, all four sent after it was fixed (2026-10-26, engineer seat)

**What happened.** This run was woken by four events at once. Two were
workflow-failure notices for `checks` on
`alexandria-engineer/2026-10-26-message-memory-eval`, runs 40274959065 and
40275869067. Two were messages from the PM seat, a handoff and then an ask,
both naming the same red check and both prescribing the same one-line repair
in `tools/skill_eval.py`. All four described a state that no longer existed.
The run history on that branch reads 3c76a50e failure, d9c39e6a failure,
313437c0 failure, 6c7e85c8 failure, then a38bf7e1 success at 05:54:07Z and
green on every commit after it, up to the head 6e2e4abf. Commit a38bf7e1 is
the repair, written by an earlier wake of this same seat eight minutes after
the last of the four failures it fixed. Verified rather than taken
on report: on the branch head `tests/test_skill_eval.py` is 137 passed and
`tests/test_corpus_drain.py -k paced` is 2 passed, and `gh pr checks 549`
returns the single defined check as pass.

**Why it is in this register.** The standing rule fires on the repeat, and
this is the class the charter already names,
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
which recorded three instances in ninety minutes on 2026-10-24. This is the
fourth, and it is the first with a new shape worth separating: the earlier
three were one event waking two runs of one seat, where the duplicate was
detectable by looking for the seat's own open pull request. Here a second
seat read the stale state and wrote two messages against it, so the duplicate
arrived as an instruction from the PM rather than as a repeated event, and
the PM's own run paid for a fix it then verified in a throwaway worktree.
Three of the four events were therefore generated after the work was done.

**What it cost.** One engineer wake spent entirely on verification and a
reply, and one PM wake spent deriving and worktree-verifying a repair that
was already pushed. No lines of product work were lost, because the
predecessor's commit is on the branch and green. The charter's duplicate-wake
clause did its job: the open pull request was found in the first three
commands and read rather than worked around.

**The fix, or why there is not one yet.** No code fix is owed. The shipped
repair differs from the PM's prescription in one way worth recording, because
the next reader will meet the difference: the PM asked for the `cap`
attribute read to be guarded by `hasattr`, on the evidence that
`tests/test_skill_eval.py` builds a fake cap double with no `last_tokens`
attribute. The commit that landed instead reads the attribute bare and gives
the double the attribute, because the real `llm.Cap` sets `last_tokens` in
`__init__`, so a double without it was modelling a cap that cannot exist. A
`hasattr` guard would also satisfy the corpus-drain grep, so both forms are
correct and the difference is taste rather than behaviour. What is owed is
upstream of all of it and already filed by the predecessor as
`INC-2026-10-26-the-pacing-rule-has-two-gates-and-they-do-not-agree`: two
enforcers of one pacing rule disagree about what counts as paced, one
accepting a `getattr` the other rejects, which is what made this check red in
the first place. The ledger proposal on that entry, folding the source
assertion into `budget.check_fallback_pacing()` so there is one gate, is the
durable fix and it belongs to a later run.

**For the relay.** The event stream has no suppression on a resolved
condition. A failure notice for a commit that is not the branch head, and a
message whose subject is a check that has since gone green, are both cheap to
filter at the sender and expensive to filter at the receiver, which is where
all four were filtered today.

**A second pair of gates found while filing this, and fixed.** Writing this
entry hit the same shape as the defect it describes. `tools/incidents.py new`
emitted its heading with an em dash separator, `tools/ban_list.py` entry 13
rejects U+2014 in anything the owner will read, and `tools/incidents.py check`
parses the id with a lookahead that accepts a plain space but not a comma or a
colon. So the generator produced a file that one gate failed and the obvious
repairs broke the other gate, which is two enforcers disagreeing about one
artifact for the second time in one run. The sibling file
`INC-2026-10-26-the-panel-build-note-named-one-blocker-and-there-were-four.md`
shows a previous seat already hand-fixed it to " - " and said nothing, so the
cost was paid silently at least once before. `SKELETON` now emits " - ", which
both gates accept. Verified by generating a throwaway entry, passing it
through both gates, and deleting it. `tests/test_incidents.py` is 31 passed.
