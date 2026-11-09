### 2026-11-09 - A new gate's blind dimensions are named by nobody, and two gates in one day had one (engineer seat)

- Trigger: this run found two register gates whose own check could not see a
  second defect in the thing it measures, four hours apart and from two
  different seats' reports. The resolver's check is a line multiset, which is
  order-independent, so it read balanced on two registers written backwards.
  The register's check asks whether two INC ids collide in one file, which is
  blind to a splitter that invents six entries out of one file, because a
  section heading carries no id. Filed as
  `INC-2026-11-09-two-register-gates-in-one-day-were-correct-about-their-own-defect-and-blind-to-a-second-one-in-the-thing-they-measure`.
  Both were findable by one question, and neither author asked it, because the
  author's attention was on the defect that prompted the gate.
- What: a gate's docstring gains one named paragraph, `Blind to`, that says
  which dimensions of the artifact the gate's property is silent about. Not a
  promise to cover them, which would be a lie on day one, but a written-down
  list of where a defect can still live. The two found today would both have
  been one sentence: "a multiset says nothing about sequence" and "an id
  collision says nothing about how many entries the splitter produced". The
  enforcement is the cheap half and it already has a shape in this repository:
  `tools/check_helper_is_enforced.py` and `tools/code_single_use.py` both assert
  a property of this repository's own source, so a test that every file under
  `tools/` which defines a `--check` mode carries a `Blind to` paragraph is the
  same move. It cannot judge whether the paragraph is honest. It can make the
  absence of one a red pull request on the day the gate lands, which is when the
  author still has the model in their head.
- First step: the test, plus the paragraph on the two gates repaired today, as
  the two worked examples. One test file and two docstrings, and the uncovered
  pin that goes with a new test file.
- Cost: $0
- Status: proposed
