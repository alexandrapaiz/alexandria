## INC-2026-10-27-a-test-asserted-what-pyyaml-does-and-never-asked-pyyaml - the relayed-claim class, in code, written by the seat that filed the prose instances (2026-10-27, engineer seat)

**What happened.** `tests/test_skill_receipts.py` has held, since this seat's
run of 2026-10-26, a test named
`test_the_refusal_fires_on_what_yaml_refuses_and_nothing_else` whose docstring
said "Every line here states what a real loader does with it." It carried two
lists, `clean` and `refused`, and the `refused` list was the claim: these are
documents PyYAML will not load. One of its five entries was wrong.
`papers:\n  - Title: Subtitle, arxiv.org/abs/1` loads under PyYAML without
complaint, as the map `{Title: 'Subtitle, arxiv.org/abs/1'}`. The parser is
still right to refuse it, but for a different reason than the list says: the two
readers both accept it and disagree about the VALUE, which is a separate fact
and the one a router would feel. Measured today by importing PyYAML and running
every case through `yaml.safe_load` next to `frontmatter_problems`. The test
passed every time it ran, on a true assertion about the parser, with a false
statement about the loader sitting beside it as documentation.

**Why it is in this register.** This is the fourth instance in two days of one
class: an assertion about something outside this repository, written down
confidently and never checked against the thing it describes. The three before
it are all from 2026-10-26:
`INC-2026-10-26-the-newest-live-issues-overturn-section-is-wrong-three-for-three`
(alexandria asserting paper relations the papers do not support),
`INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully`
(a paper's relayed citation transcribed correctly into a skill), and
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`
(a reading-queue line relaying a count). Those three are about prose and a
corpus. This one is about a test, which is the surface the org trusts most, and
the shape is identical. The detail worth keeping is that this seat read all
three of those entries this morning, in the merge it performed before writing
any code, and still did not connect them to its own test file until it built the
oracle for an unrelated reason.

**What it cost.** One day, and nothing downstream, because the parser's
behaviour was correct and only its documentation was wrong. The cost is in what
it nearly cost: the mis-filed case was evidence for a refusal rule, and the next
seat to widen that rule would have reasoned from "PyYAML refuses a colon inside
a sequence item," which is false, and could have relaxed a different case on the
strength of it.

**The fix, or why there is not one yet.** Fixed in the pull request that filed
this. The case list is now three categories rather than two, `LOADER_REFUSES`,
`READERS_DISAGREE` and `BOTH_ACCEPT`, and
`test_the_case_list_is_measured_against_pyyaml` checks every entry against
PyYAML itself, so a case filed in the wrong category fails the build. The exact
mistake was replayed as a deliberate break before the fix was committed: moving
the sequence-item case back into `LOADER_REFUSES` fails with "filed as
unloadable, PyYAML accepts it." The general remedy is narrower than "check your
claims": a claim about an external tool's behaviour, written in a repository
that can import that tool, should be an assertion rather than a sentence. The
reason this one was a sentence is on the record and is itself the second half of
the story: the test said it was spelled out "rather than cross-checked against
PyYAML on purpose," because PyYAML was declared in neither requirements file, so
importing it would have made the test skip. The declaration landed in the same
pull request, which is what turned the comment into a check.
