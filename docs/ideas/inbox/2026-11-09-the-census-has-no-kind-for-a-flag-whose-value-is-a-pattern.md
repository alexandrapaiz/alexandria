### 2026-11-09 - the target census has six kinds and none of them fits a flag whose value is a regex (engineer seat)

- Trigger: vendoring HQ's register merger as `tools/merge_register.py` added
  five pattern flags and `tools/target_census.py --check` went red on all five,
  correctly. Classifying them found that the census's six kinds are `roster`,
  `path`, `date`, `text`, `opaque` and `number`, and a regex is none of them.
  They are declared `text` in that commit under protest, with the protest in
  the diff.
- What: the comment above `KINDS` says "the only one of these that can answer a
  confident zero about a subject it never found is `roster`". That is false for
  a pattern flag and the merger is the proof: `--heading` that matches nothing
  does not raise and does not refuse, it parses the whole register as a single
  entry and merges it at exit 0, which is a confident zero about the register's
  contents. `text` is the closest kind and its own justifying clause is
  "nothing to resolve", which is exactly wrong here. So the census is one kind
  short rather than these five flags being prose. The proposal is a seventh
  kind, `pattern`: a value compiled and then applied to a corpus, whose
  non-match is in band. Its probe is not a roster check. It is the question
  `Ursa/exo` named on 2026-11-09, what does this return when it matches
  nothing, and is that value legal.
- Why it is worth a kind rather than a comment: the kinds already carry probes,
  and this one has a real one. For every declared `pattern` flag the census can
  ask whether the repository holds a documented invocation of it and whether
  that invocation finds more than a floor of matches in the file it names.
  `tests/test_merge_register.py` already does this by hand for four patterns
  and the floors caught a defect in their own first draft. Moving it into the
  census makes it the gate's job for every pattern flag instead of one test
  file's job for one tool.
- First step: count the population before adding anything, the same way the
  prose-claim entry of this morning asks. Walk every `add_argument` in `tools/`
  and `pipeline/` whose help text or default looks like a pattern, and report
  how many there are and how many have a documented invocation anywhere in the
  tree. Five is the known floor and all five arrived today, so the honest
  possibility is that the population is five and the right answer is a comment
  rather than a kind. The measurement decides it.
- Cost: $0
- Status: proposed
