## INC-2026-10-26-the-panel-build-note-named-one-blocker-and-there-were-four - a document asserted the state of machinery nobody had run, in the same file that did it three weeks ago (2026-10-26, engineer seat)

**What happened.** `docs/product/reviewer-panel.md` has said since 2026-10-03
that ADR-13's third slice is "blocked on the owner minting a PR-merge-scoped
token", in bold, and that "**this is now the only thing between ADR-13 and a
working loop**". This run built the merge executor and found four blockers, of
which the token is the last. One: nothing had ever filed a verdict about a pull
request, because all three reviewers read skills from `main`, so
`panel_consensus` could only be unanimous about text that no longer needed
merging. Two: ADR-12's whitelist refuses every proposal the panel will ever
see, and the number is 16 of the 546 pull requests this repository has ever
held that change a `skills/<slug>/SKILL.md`, with every one of the 16 carrying
at least one path outside it and none clean. Three: the whitelist admits `prompts/*.md`,
which held one prompt when ADR-12 was written and holds twelve seat charters
now, so a literal reading authorises the panel to merge a charter that HQ
standard section 21 reserves to the owner. Four: the token. Each of the first three is
checkable from the repository alone, and none of them needed a credential to
find.

**Why it is in this register.** The standing rule records any issue that occurs
more than once at the moment it repeats, and this is the same file and the same
class as `INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had`, where
this document said a reviewer's file half "runs on every pull request" from the
day it was written and no workflow had ever named it. That entry recorded the
general shape as "the second time in two days that this seat described a CI
step in prose and shipped no step". This is the third instance of that shape in
the same document, and the distinguishing feature of this one is that the
sentence was not about a step at all. It was a claim about what remained, which
is the hardest kind to check and the easiest kind to inherit: the sprint that
groomed this item, the register row in `docs/agents/registers.md`, and
`README.md` all carry the same one-blocker reading.

**What it cost.** Nothing was lost, and that is luck rather than process. The
cost is the twenty-three days from 2026-10-03 to today during which the
repository held a true-looking sentence saying one owner action would close
ADR-13, while three of the four conditions were nobody's dependency on the
owner at all. The second one, the 16-of-16 whitelist, is still an owner
decision and has therefore not been asked for in those twenty-three days
because nothing knew to ask.

**The fix, or why there is not one yet.** `docs/product/reviewer-panel.md` gains
a slice 4 section in this run's pull request, and it ends with the four
remaining steps numbered and attributed, which is the form the sprint item
asked for. The generalisable half is filed in `docs/ideas.md` as today's first
idea: a build note that says what remains is a claim about unrun machinery, and
the only thing that makes such a claim checkable is a command that prints the
blockers. `tools/panel_merge.py` is that command for this one, and the ledger
entry proposes the pattern rather than assuming it.
