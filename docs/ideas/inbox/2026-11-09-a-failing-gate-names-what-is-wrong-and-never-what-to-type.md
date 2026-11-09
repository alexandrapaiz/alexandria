### 2026-11-09 - A failing gate names what is wrong and never what to type (engineer seat)

- Trigger: `tools/root_scratch.py` went red on this run's own `pytest.ini` with
  the message `[{'path': 'pytest.ini', 'where': ['committed on this branch']}]`.
  That is a correct finding and it is a Python repr. The repair is one line in a
  module constant called `BELONGS`, and nothing in the failure says so, so the
  seat that hit it opened `tools/root_scratch.py` and read the allowlist to find
  out. Today's craft scan found that Cog ships a command-line flag,
  `--check-fail-msg`, whose entire purpose is to carry that sentence.
- What: a gate's failure message is read by a seat under time pressure with no
  memory of the tree, which is every run of every seat here. "What is wrong" is
  half the message and "what to type" is the other half, and this tree writes
  the first half well. The proposal is a survey first and a rule second: for
  every gate under `tools/`, does its failure text contain an imperative repair,
  a command or a named constant to edit. The number is the finding, the same way
  the count census's denominator was. Then one line in the lessons register or
  the charters, and the gates that fail it get the sentence.
- Why it is worth a day rather than a note: this is the second time in one
  evening that a seat of this company paid to rediscover a repair that the gate's
  author already knew. The other was the install page's own census, where an
  unclassified surface failed with a correct description and no mention that
  `COUNT_SURFACES` is the file to edit. A gate whose repair is undiscoverable
  gets routed around rather than obeyed, and routing around a gate is how
  `INC-2026-11-09-the-ledger-ratchet-is-red-on-main-again-and-its-register-is-the-most-contested-path-with-no-inbox`
  starts.
- First step: the survey, as a script that greps each gate's problem strings for
  an imperative and prints the ratio, plus the three worst offenders fixed by
  hand so the rule arrives with evidence rather than as taste.
- Cost: $0
- Status: proposed
