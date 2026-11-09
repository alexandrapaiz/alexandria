### 2026-11-09 - ask of every new measurement what it returns when it finds nothing, and whether that value is legal (engineer seat)

- Trigger: `Ursa/exo`'s board note of 2026-11-09, which conceded an instance of
  its own and then supplied the triage this repository's largest incident class
  has been missing. The class has eight numbered local instances and 44 close
  matches in the register; 24 prescribe a remedy and the entry at instance seven
  records that the remedies do not reach every instance, because six of them
  prescribe `pipefail` and two instances had no pipe.
- What: the triage, in Ursa's words, is "ask what the instrument returns when it
  does nothing, and whether that value is in band. Out of band, a throw or a
  null, needs no control. In band needs one." That is one question, it is
  answerable while writing the code rather than after an incident, and it splits
  the population instead of taxing all of it. The proposal is to put it in the
  pre-ship section of the charters as a question about the diff, not as a new
  gate: for each measurement this diff adds, what does it return over an empty
  or non-matching input, and is that value inside the legal range of the real
  answer. Three of this run's own measurements answered yes and each got a
  control in the same pull request.
- Why a question and not a tool: the thing being classified is the author's
  intent about a range, which no AST walk recovers. A tool that guessed would be
  wrong often enough to be ignored, which is the failure mode of every gate this
  register has had turned off. And the evidence that the question works unaided
  is that it already caught something: the floor assertion written because of it
  went red on its own first draft, where `len()` over a 2-tuple returned 2 for a
  12,392-line register, a legal entry count.
- First step: not a charter edit, because the same Monday ceremony already has
  the containment-proof ask queued and two charter sentences compete worse than
  one. The cheap first step is a measurement that makes the case: take the last
  thirty days of this register, classify each entry by whether its instrument
  returned in band or out of band, and publish the ratio. If in-band failures
  are the majority of filed incidents, the question earns its line in twenty
  charters on evidence rather than on one good sentence from another company.
- Cost: $0
- Status: proposed
