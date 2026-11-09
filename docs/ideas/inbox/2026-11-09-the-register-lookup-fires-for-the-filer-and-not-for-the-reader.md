### 2026-11-09 - The register lookup fires for the filer and not for the reader (engineer seat)

- Trigger: this run built `tools/incidents.py prior` because the skill seat
  obeyed "check the register before you ship", shipped red anyway, and the
  remedy was in an entry its own seat had applied twice. The lookup now runs
  automatically at one moment, which is `incidents.py new`. That catches the
  seat that files. It misses the seat that reads the charter line, decides there
  is no precedent, and ships, which is precisely the seat that failed this
  morning. Filed as
  `INC-2026-11-09-the-register-held-the-remedy-and-the-rule-that-says-read-it-has-no-lookup-behind-it`,
  whose own "what this does not fix" paragraph says this in one sentence.
- What: the check-the-register step in every charter gains one command beside
  its prose, the way the machinery-diff step already carries
  `git log --since="36 hours ago"` and the guard step carries
  `gh run list --workflow=checks.yml`. Both of those work, and they work for the
  same reason: a step that names a command gets run and a step that names a
  duty gets skipped. The sentence would read "before you call `gh pr ready`, run
  `python3 tools/incidents.py prior "<the failure you are shipping against>"`
  and say in the PR what it returned". The "say in the PR" half is the part that
  makes it checkable by a reviewer, which is the same move L-E10 made for the
  pull-request survey when it required the numbers in the description rather
  than in the seat's reasoning.
- First step: the sentence itself, in `prompts/engineer-agent.md` under "Check
  the register before you ship", since this seat's charter is the one place a
  change can be rehearsed on a single seat before the ExO relays it to the
  others. It is one paragraph and it is not this seat's to write: charters are
  edited only by the owner's merge, and §22 of the company PM standard makes it
  an `ask` the PM posts with its own recommendation that proceeds after
  forty-eight hours of silence. So the first step is the ask, not the diff.
- Cost: $0
- Status: proposed
