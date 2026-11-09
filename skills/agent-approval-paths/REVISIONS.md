# agent-approval-paths: the full revision record

One dated heading per entry in `provenance.revisions` in `SKILL.md`. The
frontmatter carries one line each, naming the date, the trigger and what
changed; the narrative lives here. The reason for that split is the measurement
recorded in `skills/harness-engineering/REVISIONS.md` and the rule is in
`prompts/skill-extract.md` section 2.

## 2026-11-09, seventh entry: the ceiling is an unshipped step, and the release the corpus held as fixed was itself affected

**Trigger.** ADR-37, a cited claim refined with confidence. The research seat's
`done` of 12:08Z (board id `15b98859`, ref #926) answered the two questions v7
queued, with all nine papers this skill cites read in full in that run. Its
companion `done` of 12:09Z (`06f8740c`) restored a word the first lost at the
character limit, and both are answered separately here for the same reason they
were sent separately.

**What this run verified for itself rather than taking from the note**, because
the correction changes a prescription and the charter's rule is that the source
wins:

| Claim | Checked here | Result |
|---|---|---|
| `2609.21081` section 6.2 is a five-step use-time procedure, the fix is step 2 and the ceiling is step 3 | `tools/read_paper.py 2609.21081`, exit 0, 55,455 chars | confirmed, verbatim, and section 6.3 names the OpenClaw release under "Bind and revalidate" |
| GHSA-q399-23r3-hfx4's range and patch | primary advisory page fetched this run | affected **<= 2026.2.26**, first patched **2026.3.1**, patch pins "path-token commands ... to canonical executable identity (`realpath`) across approval and execution", weaknesses CWE-367 and CWE-426 |
| GHSA-rw39-5899-8mxp | primary page fetched this run | all before **2026.3.11**, patched 2026.3.11, approvals "could display only an extracted shell payload such as `jq --version` while execution still ran a different outer wrapper argv" |
| GHSA-2j8v-hwgc-x698 | primary advisory page fetched this run | affected **<= 2026.5.16**, patched **2026.5.18** |
| `2609.28586`'s step-3 implementation | `tools/read_paper.py`, exit 0, 106,791 chars | **0.926** macro recall, 0.941 macro precision, 13/17 against 9/17, residual 10 to 3, and the `PreToolUse` proof-of-concept emits ASK and takes DENY |
| `2606.02668`'s step-3 implementation | `tools/read_paper.py`, exit 0, 45,895 chars | referenced-content inspection verbatim, "an interpreter call whose target is not observed is flagged rather than passed", and `PATH` occurs **0** times in the whole paper |
| `2609.38983` section IX on the drift shape | `tools/read_paper.py`, exit 0, 134,755 chars | "would not have caught any of our measured cases", and "We did not attempt or test this mechanism" |

### The claim this seat shipped twice, and what it should have said

v6 and v7 both said OpenClaw 2026.2.24 is **the only released vendor fix for
this class in any of the three namings**. Two things are wrong with that
sentence and only one of them is a fact about the world.

**First, the phrase is this library's and not the paper's.** `2609.21081`
section 6.3 says "OpenClaw supplies a released product fix", with its own
bounding sentence beside it. The "only" came from this seat reading across the
three papers' positives, which is a true statement about three papers and reads
as a statement about the product. That is the identical error shape as
`2609.38983` section IX's "we did not attempt or test this mechanism", which is
true of that paper and false as a statement about the field. **Two instances of
one reading error in one cluster, and both of them in this skill**: a
paper-bounded sentence carried as a field-wide one. The caveats now name the
class rather than the two instances.

**Second, the product has shipped at least three fixes in this family, and the
one the corpus held as fixed was inside another advisory's range.** 2026.2.24
closes the representation-completeness shape. GHSA-q399-23r3-hfx4's affected
range is at or below **2026.2.26**, so 2026.2.24 did not yet pin executable
identity. The display-versus-execution class itself reopened at
GHSA-rw39-5899-8mxp, patched 2026.3.11, and again at GHSA-2j8v-hwgc-x698,
patched 2026.5.18.

### The sentence that replaces it, and it is stronger than the null this seat expected

The queue line asked whether the released fix also closes the ceiling class, and
predicted a null. The answer is better than a null: **the ceiling is an
unshipped step rather than an unknown.** `2609.21081` section 6.2's five steps
are a published procedure, the shipped fix implements step 2, and the ceiling
class is step 3. A builder who knows which step is missing can build it; a
builder told the ceiling is unmeasured cannot.

### The `$PATH` dimension has a shipped fix of the one shape measured to catch nothing

GHSA-q399-23r3-hfx4 pins path-token commands to canonical executable identity by
`realpath` **across approval and execution**, and its own weakness classes are
TOCTOU and untrusted search path. So it detects a `$PATH` that changes between
the two. In every one of `2609.38983`'s measured cases the shadowed executable
is installed before the credential is ever issued, so `realpath` at approval
already resolves to the shadow and the comparison at execution agrees. Section
IX disposes of the whole shape in its own words. **A reader of v7 would have
concluded that this upgrade closes a `$PATH`-substitution finding**, which is
why `ap-t10` is written against exactly that decision and why the description
traded a word for the clause that reaches it.

### Step 3 is built twice, and the ceiling survives both with numbers

`2609.38983` leaves initial effect validation as its most concrete open problem
and says it did not build it. Two papers in this skill's own cluster did, one of
them cited four lines earlier in that same section:

- `2606.02668` reads the file an interpreter call targets and analyzes its body
  with the same fact extraction, flagging rather than passing a call whose target
  is not observed. Measured independently: 90.0 percent flagged and 10.0 percent
  silently passed over 1,330 GTFOBins abuse commands.
- `2609.28586` commits frozen, source-backed effect predictions before
  authorization: **0.926** macro recall, 0.941 macro precision, 13 of 17 exact
  effect sets against 9 of 17 for a command-only baseline, residual effect
  instances 10 to 3, carried through Claude Code's own `PreToolUse` hook.

**Neither removes the ceiling, and it is now a measured floor.** Every one of
the first's silent passes runs through a trust-listed binary, and the three
field-identical scenarios run through `npm`, `git` and `cat`. `PATH` occurs zero
times in that paper, so it does not model the dimension at all. The second's own
residual is 3 effect instances of 10 after binding. Nobody has run either
against the three scenarios, and that is the one experiment the queue now asks
for, narrower than the line it replaces.

### One scenario has no with-defense number for any defense

`2609.38983` section VII excludes the same-name `$PATH` pattern from its own
offline replay and says its predicted coverage "is derived, not empirically
tested". So of the three field-identical scenarios, the `$PATH` one has no
measured with-defense figure anywhere in this literature, including from the
paper that defines it. v8 does not claim one.

### The reading rule this entry adds to the caveats, and it is measured

A related-work summary is **admissible as evidence that a mechanism exists and
never as evidence of what the mechanism contains**. Across four enumerating
related-work summaries in this cluster, 10 of 10 components with no counterpart
in the summariser's own design were dropped. The control is the pair that makes
it more than an anecdote: `2609.38983` and `2609.18411` both summarise
`2606.02668` and keep **disjoint halves** of it, each half matching what the
summariser built. If the drops tracked importance in the summarised paper the
two would agree.

This skill is the instance. The corpus held `2609.21081` only through
`2609.38983` section VIII-A for weeks, the dropped field was the digest over the
rendered descriptor, and the ceiling v6 shipped had no precondition under it.
The skill's own case is two drops rather than the one v7 named: the issuer and
policy field is dropped too, and the summariser has no issuer field.

### What changed in the file

- `version` 7 to 8. `status` stays `draft` and `validated` stays empty.
- The papers entry for `2609.21081`, the delta 1 *Validation:* tag, three
  sentences in delta 1's body, checklist item 2 and delta 1 procedure item 2.
- The final caveat gains the reading rule and corrects **eight of eight read in
  full to nine of nine**, which v7 left stale when it added the ninth paper.
- `description`: one clause traded in, "when a vendor advisory or upgrade pins
  executable identity against a PATH-substitution finding", paid for by nine
  words cut elsewhere, because the budget was already at its 150-word ceiling.
- `evals.json`: `ap-t9`'s expected answer corrected, `ap-t10` added, twelve tasks.
- `triggers.json`: `ap-pos-6` added for the advisory decision.
- The fifth revision's frontmatter line is collapsed into the collapsed line to
  pay for the seventh's, the same trade the sixth made. The narrative for it is
  the fifth entry below and is untouched.

### Still unmeasured, in that word

No differential delta. No bare-arm screen. `NEON_RO_URL` is absent from this
run, so no claim row was read or written and the corpus-wide census of
summary-provenanced claims stays **unknown rather than zero**. The trigger
suite's 77 of 87 says this skill is findable and says nothing about whether it
helps.

## 2026-11-09, sixth entry: the ceiling has a precondition under it, and the only paper carrying the field is the one the corpus had never read

**Trigger.** ADR-37, a cited paper read in full for the first time. The research
seat's `done` of 10:55Z (board id `08830fa2`, ref #913) reported reading
`arxiv:2609.21081` (Loopjacking, A. A. Kumar, 17 Sep 2026) in full and routed
five items to this seat without applying any of them, because `skills/` is this
seat's surface under ADR-22. This entry is the application, and the paper was
read here independently first: `python3 tools/read_paper.py 2609.21081`, exit 0,
**55,190 chars**, the same count their note records.

### The finding, and it is a precondition rather than a caveat

v6 added a **ceiling** to the binding this file prescribes: the recorded fields
agree and the operation differs, because the divergence is below the mediation
point. v7 adds a **precondition**, and the two are invisible to the same check
for opposite reasons. The precondition is that the recorded fields agree
*because the record itself is lossy*, so the operation that differs was never in
the record to be compared against.

Checklist items 1 and 2 both ran in one direction, action to text. "Decoded from
the action that will execute" is satisfied by a lossy projection of that action,
and that is not a hypothetical: it is the shape of a measured positive at a
released version. A gateway-mediated shell path carried a positional argument
vector whose inline payload was `$0 "$1"`, with additional positional arguments
selecting the command and destination that created the marker. The paper's own
sentence is that **the full vector was prepared before approval** while the
product's approval event **represented only the inline payload**. So the
rendering was genuinely derived from the real command and was still a projection
of it. An allow-once decision then released the complete vector: **3 of 3**,
with direct unapproved execution denied 3 of 3 and unchanged approved commands
still succeeding.

The consequence for a builder is the one that justifies changing the decision
rule rather than appending a warning. A team that captures its descriptor from
the approval view, hashes it, and re-checks the hash at dispatch has built
something where the comparison **passes** and a different operation executes,
and the team's own proof of safety ("display and enforcement can never
disagree") is the hole. Eval task `ap-t9` is written against exactly that team.

### The field the corpus did not have, verified here rather than taken

Until this read, the corpus knew this paper only through `2609.38983`'s section
VIII-A, which reads it at length as concurrent work. That section reports
Loopjacking's section 6.1 canonical approval record as five items. **Section 6.1
has six bullets**, and the sixth, read here in the paper's own text, is:

> a digest over the same complete descriptor shown to the human.

followed immediately by the operative sentence:

> The display must be generated from this descriptor, not from a lossy
> convenience string while execution uses a richer object.

Three checks were run here rather than inherited:

| check | result |
|---|---|
| `digest` in `2609.38983` (132,653 chars, re-fetched this run) | **0 occurrences** |
| `digest` in `2609.28586` (105,779 chars) | 3, all source-content or prediction digests, none over what the human saw |
| `Loopjacking`/`Agno`/`OpenClaw` in `2609.28586` | **0**, so the two are independent |

**And one observation this seat adds to the research seat's note.** The citing
paper does not drop the field at random. Its own words are that Loopjacking's
record is "a field set with substantial overlap with our own seven-field
credential", so it summarises the record by mapping it onto its own mechanism,
and the single field it drops is the one with no counterpart there. That same
credential is the one its own measurement puts at a ceiling, scope 1.000 to
1.000 and arguments 0.450 to 0.400. So the omission and the ceiling are one fact
seen twice: the dropped field addresses a failure the dropping paper's mechanism
cannot see. Of the three independent namings of this class, this is the only one
carrying the field, and the only one with a **released vendor fix**, the next
version of the affected product, which reconstructs and checks the complete
argument vector and rejects the mismatch 3 of 3 while still executing the
approved command.

### The second timing-shaped repair is now ruled out, by two papers that do not cite each other

v6 already refused one: re-approving when an environment snapshot differs
between grant and dispatch catches **none** of the ceiling cases, because the
hook or shadowed executable is installed before the credential is issued. This
paper's negative control rules out the other, which is the repair a reviewer
reaches for when told approvals can be substituted after the click. Refusing to
persist approvals, or shortening the window, is not the fix: every approved
action was serialized, restored and resumed and executed **3 of 3 and 3 of 3**,
while a same-call-ID raw mutation was rejected. The paper's conclusion is that
resumability "is a carrier for post-approval substitution but neither a
necessary condition for the umbrella nor a sufficient cause of failure". What
the control preserves is a canonical invocation fingerprint across
serialization, which is a completeness property and not a timing one.

So both halves of delta 1's new material point the same way, and neither points
at duration.

### What changed in the file

1. **Checklist item 1** separates completeness from provenance, says in the file
   that a faithful render can still be lossy, and names the six measured fields
   for a shell surface: inline payloads, positional arguments, environment
   changes, working directory, interpreter flags, redirections. It carries the
   paper's collapsed-view rule, that a collapsed view may stay useful but
   approval must expose any material hidden field or refuse to authorize it.
2. **Checklist item 2** binds the complete resolved operation rather than the
   view, and requires the enforcement point to **reconstruct** that operation at
   dispatch and compare, rather than re-verify the fields it stored. It also
   names the three insufficiencies the paper states one per studied product:
   binding a call identifier, binding a run-level approved flag, and checking
   only at presentation time.
3. **Delta 1's procedure** items 1 and 2 carry the same two changes with the
   source's own five-step use-time decision in order, which is the first
   numbered procedure in this file taken verbatim from a paper rather than
   composed from its findings.
4. **Caveats** gain a seventh surface with this paper's bounds, and one
   prohibition in bold.
5. **Evals** gain `ap-t9`, paired with `ap-t8` as precondition to ceiling, five
   rubric criteria and a zero-scoring exploit.

### The prohibition, because it is the thing most likely to be misused

**This paper may never be cited for approval fatigue, dialog quality, deception
rates or interface comprehension.** Its approval decision was scripted, and only
after the test had asserted and recorded the exact product view, so it measures
binding behaviour and nothing about a human. It disclaims that reading twice in
its own text, in section 3.3 and in section 7.1. It is also the paper here whose
method most resembles a human-factors study, which is exactly why the disclaimer
needs to travel with it inside this file rather than only in a note.

### Rule 4, and the number this run owes the owner rather than the one it passes

`wc -l` is **119**, under rule 4's cap, down from v6's 120. v6 was the only file
in the library not under the cap, every other skill sitting at 119 or below, and
that is corrected here.

**That sentence is true and it is not the honest number, so both go in the pull
request.** `skills/_validation/skill_length.py` measures the same rule in
rendered lines at 100 columns, which is the unit rule 4 meant, and against that:

| version | `wc -l` | frontmatter | body | rendered |
|---|---|---|---|---|
| v5 | 118 | 99 | 347 | 446 |
| v6 | 120 | 118 | 402 | 520 |
| **v7** | **119** | **109** | **459** | **568** |

So the governing metric improved by one line while the file got 48 rendered
lines longer to read. This revision paid for its new material by collapsing four
superseded revision narratives in the frontmatter into one pointer line, which
is the right direction (the frontmatter is a record REVISIONS.md already holds in
full) and is why the frontmatter fell 118 to 109. It does not change the fact
that the body grew and the gate did not see it.

The instrument's own docstring predicted this seat's behaviour: it records that
three `harness-engineering` revision entries state, in their own words, cutting
reader-facing advice to make room for a revision entry. v6 did exactly that,
merging two cross-paper caveats to pay for a frontmatter line. v7 did the
inverse, and it still grew.

**The conclusion is the one v6's pull request already reached and this run now
has the number for: the approval-laundering and Loopjacking material is a
different surface from all three current deltas and belongs in a second skill.**
The longest single line in this file is 4,444 characters, about 45 rendered lines
in one paragraph, and it now carries a ceiling and a precondition from two papers
that neither of the three deltas was built around. That split is the next
maintenance item for this skill and is recorded as such, not done here, because
the charter allows one skill per run and this run's item was the revision.

### Still unmeasured

No route to either eval arm, so no delta. `status` stays `draft` and the word
**unmeasured** is in the pull request. The trigger suite moved 75 of 85 to 76 of
86 with **zero verdicts moved** and one case added, and a green trigger case says
this skill is findable and says nothing about whether it helps.

## 2026-11-09, fifth entry: the prescription had a ceiling and the file did not say so

**Trigger.** ADR-37, a cited prescription narrowed by papers read in full. The
research seat's `done` of 09:48Z (board id `e6764735`, ref #903) reported both
approval-laundering papers read in full, corrected two premises in this skill's
own queue lines, and asked this seat to say which paper each delta rests on. The
reading below is this seat's own, not the note's.

**What this seat did before writing anything.** Fetched both full texts with
`python3 tools/read_paper.py`, exit 0 both, 132,653 and 105,779 characters,
matching the research seat's counts exactly. Then read, in the texts rather
than in the note, section IX of `2609.38983` for the class-level claim and the
ruled-out repair, Table I for what each grant's own text excludes, the benign
example in section I for the argument mechanism, and sections III-C and the
Table III note of `2609.28586` for the four responses and the no-added-effect
ASK definition and count. Every figure quoted below was read in the paper.

### The finding: the half this file told a builder to ship is measured at zero on two of six classes

Checklist item 2 and delta 1's procedure item 2 said, in substance, bind the
approval to the one concrete action and re-verify it at dispatch, and said
nothing about what that does not reach. Three independent lines reach the
construction, which is why v4 called it a pattern, and none of the three
measured its ceiling. `2609.38983` does.

Its Bound-Gap Rate is the fraction of valid runs in which a per-scenario canary
effect outside the credential's own text occurs. Table III, Claude Code
2.1.197, Wilson 95 percent:

| class | N | BGR | 95% CI |
|---|---|---|---|
| Scope | 20 | 1.000 | [0.839, 1.000] |
| Temporal | 20 | 1.000 | [0.839, 1.000] |
| Tool, cross-tool identity | 19 | 0.000 | [0.000, 0.168] |
| Tool, same-name `$PATH` | 20 | 1.000 | [0.839, 1.000] |
| Argument | 20 | 0.450 | [0.258, 0.658] |
| Delegation | 19 | 0.947 | [0.754, 0.991] |
| Semantic (proxy) | 20 | 0.100 | [0.028, 0.301] |

Its defense is an HMAC credential over principal, agent id, session id, tool,
argument hash, scope and expiry, minted by a mediator and held server-side,
which is a strictly stronger version of what checklist item 2 asks for. Table V
replays it paired over the 118 runs of the six replayed scenarios, McNemar
exact:

| class | baseline | with defense | discordant | p |
|---|---|---|---|---|
| Delegation | 0.947 | 0.000 | 18/0 | 7.6e-6 |
| Temporal | 1.000 | 0.000 | 20/0 | 1.9e-6 |
| Argument | 0.450 | 0.400 | 1/0 | 1 |
| Scope | 1.000 | 1.000 | 0/0 | 1 |
| Semantic | 0.100 | 0.100 | 0/0 | 1 |
| Tool (cross-tool) | 0.000 | 0.000 | 0/0 | 1 |

**So the binding eliminates the two classes where a field diverges and moves
nothing where no field diverges.** The paper's own section IX sentence is that
`"Tool Laundering is blocked" is false as a class-level statement`, and the
mechanism it gives is structural rather than contingent: `$PATH` resolution
happens inside the dispatched process, below the `PreToolUse` mediation point,
and no field the hook receives can be made to reveal it. The three mechanisms,
from Table I:

- **Scope.** A grant of `Bash(npm run test *)` never names the canary read that
  a `package.json` script's child process performs.
- **Argument.** A grant of the literal `git commit -m "wip"` never names the
  unstaged edit a repository `pre-commit` hook running `git add -A` sweeps in.
  Eight of the nine successes issue the approved literal unmodified, so this is
  not the model widening its own arguments, and the ten failures attempt a
  *narrower* command which the allowlist correctly denies.
- **Tool, same-name `$PATH`.** The approved rule `Bash(cat *)`, the literal
  command text and the recorded tool identity all match what was granted, and
  only which executable `$PATH` resolves `cat` to differs.

### Why the obvious repair is in the file as a refusal rather than as an option

This is the part that makes the revision a decision-rule change rather than a
caveat. An engineer told that the binding has a ceiling reaches next for
re-approval on environment change, which the literature calls drift detection.
The paper measured it and says it `would not have caught any of our measured
cases`, because in every scenario the hook or shadowed executable is installed
before the credential is ever issued, so the snapshot is identical at approval
and at dispatch. Finer matching on the argument or scope field cannot help
either, and the paper's reason is the one to carry: there is no delta to match
against, since the field never changes.

What it names instead is *initial effect validation*, inspecting at approval
time what the already-present environment would make the credential produce and
refusing a grant whose own text excludes an effect the environment is already
configured to produce. **It did not build or test that**, and says so, calling
it the paper's most concrete open problem. Delta 1's procedure item 2 now
prescribes it and the file says it is unbuilt in the source, because
prescribing an untested mechanism as though it were a measured one is the
overstatement this library's provenance reviewer exists to catch.

### The second paper's half, and it lands in delta 2 rather than delta 1

`2609.28586` derives an information limit: if two validly bound executions
project to the same policy-visible record and need different effect-specific
decisions, no record-only rule can decide both. v5 of this file had no sentence
resting on that paper, and the queue line that asked for it claimed the limit
was `the strongest available argument for why delta 1 must read the resolved
object`. Read against Lemma 1 that is wrong twice, and the research seat caught
both: it is an information requirement rather than a hardness result, and it
licenses four responses rather than one. The paper's own words are that the
decision path `must conservatively represent the union, re-mediate, reject, or
contain the unresolved effects`, and its recommendation is the union, meaning
bind a source-backed prediction of the transitive effect boundary into the
approval object before authorizing. Reading the resolved object is one of the
four and is the one that needs the separating information to exist.

So the sentence lands in delta 2's procedure item 6, which is the item about
consulting effects, and it arrives with its price. **The cost figure the
abstract omits is the one a builder needs**, and it is in the note under Table
III: of the 17 reached cases in the frozen confirmatory holdout, **9 are
no-added-effect ASK**, which the paper defines as a reached case routed to ASK
whose realized trace exercises no effect class the command-only record had not
already disclosed. Positive stratum 4 of 9, controls 5 of 8. Against that, the
frozen predictions raise macro recall 0.770 to 0.926 at 0.941 precision, case
coverage 0.755 to 0.922, and cut residual effect instances 10 to 3, with all
seven newly disclosed effects in the positive stratum and control disclosure
unchanged. Over half the extra prompts bought nothing, and that ratio belongs
beside the coverage gain rather than under it.

### Which paper each new sentence rests on, because the research seat asked

The two are not interchangeable and the file now says which carries which.

**Delta 1's ceiling rests on `2609.38983` alone.** Single author. A working
draft dated 2026-09-22, target venue IEEE TDSC, stated in its own manuscript
line as not yet submitted. One harness, one pinned model version. A Codex CLI
replication was attempted and blocked because `codex exec` exposes no
observable per-call approval checkpoint. And the paper disqualifies its own
point estimates as harness-intrinsic: the runner forks the full parent
environment and all 138 valid traces load extra plugin instructions and a
previous-session summary on top of the published prompt, so in its own words the
repetitions `are not independent draws from a minimal, hermetic harness
configuration`. The kappa of 1.0 is an unblinded author cross-check re-measured
on the same 15 runs used to find the analyzer bug it is reported after, and
Scope's BGR is 0.80 before that fix and 1.00 after. **So take the direction and
the two zeros, not the rates**, which is what the validation tag now says.

**Delta 2's four responses and the 9-of-17 price rest on `2609.28586` alone**,
and its warrant is a different kind rather than a weaker one. It reports no
population dispersion anywhere, and the one interval it draws is labelled in its
own caption as a fixed-cohort case-resampling stability interval. What stands in
its place is freeze discipline: a parser frozen before a disjoint, prespecified
holdout of 18 workflows from 18 previously unseen fixed-SHA repositories, an
independent re-implementation that hash-checks 109 artifacts, six three-run
repeats at mean pairwise Jaccard 1.000, and a four-profile denominator
sensitivity. One predeclared target loses its margin under one of those
profiles, executed-control precision 0.875 primary and 0.778 when
`NOT_EXECUTED` is treated as empty, against a predeclared bar of 0.80. The
primary profile is the pre-registered one, so that is a boundary rather than a
miss, and it is the thinnest margin in the paper.

### What this run did not do, and why

**The queue lines were not corrected here.** Both carried premises this seat
wrote from abstracts, and both are wrong: the papers posted a week apart rather
than three weeks, `2609.28586` is the earlier of the two rather than the second,
there is a third independent naming thirteen days wide that neither of them
cites, and the information-limit sentence overstates Lemma 1. The research seat
corrected all four in place on #903, so correcting them again here would be the
same two lines written twice at one anchor. That file already conflicts between
the two branches, proved with `git merge-tree --write-tree`, and the resolution
is to keep both tail sections. Named in the pull request with the merge order
rather than resolved on this branch.

**Loopjacking is not cited.** `arxiv:2609.21081` is the first of the three
namings by posting date and this seat has not read it, so it appears nowhere in
`SKILL.md`. The research seat queued it on #903.

**Nothing moved on status.** `status: draft` stands, `validated` stays empty,
and no delta was measured, because neither eval arm has a route from this seat.
ap-t8 is written and unqualified like the other nine.

## 2026-11-09, fourth entry: the right number was on the wrong baseline, and the paper prints it twice

**Trigger.** ADR-37, a cited result refined again. The research seat read
`2610.40753` a third time, verified v4 cell by cell, upheld both of the
refinements v4 added, corrected one of its own sentences, and returned one
finding against v4's own reversal. Board note `5da14666`, 09:16Z, ref #897. It
arrived six minutes after the previous run's pull request opened, so it is new
work rather than a duplicate wake, which was checked on the bus before any of
this was written.

**What this seat did before writing anything.** Fetched the full text again
with `tools/read_paper.py`, exit 0, 69,442 characters, this seat's third full
read. Re-derived the Table 11 pooling from the per-level counts rather than
taking the note's arithmetic, and read the dagger footnote under Table 3 and
Table 9's SABER decision counts directly. Everything below reproduces.

### The finding: 61.8 is printed twice, so it is not prediction's price

Table 11 gives the twin false-block rate for six approver conditions across
four concealment levels. The levels are not equal in size, which is what makes
the pooling non-obvious: script, Makefile chain and binary hold 26 twins each
and command holds 24, for the 102 twins Table 12 names. Pooling each row:

| approver sees | per level | pooled |
|---|---|---|
| command | 100.0, 11.5, 0.0, 100.0 | 26 + 3 + 0 + 24 = **53 of 102, 52.0** |
| request + command | 88.5, 34.6, 46.2, 54.2 | 23 + 9 + 12 + 13 = 57 of 102, 55.9 |
| dialogue | 65.4, 50.0, 50.0, 83.3 | 17 + 13 + 13 + 20 = **63 of 102, 61.8** |
| dialogue + predicted | 46.2, 57.7, 46.2, 100.0 | 12 + 15 + 12 + 24 = **63 of 102, 61.8** |
| dialogue + observed | 0.0, 0.0, 0.0, 4.2 | 0 + 0 + 0 + 1 = **1 of 102, 1.0** |

**The pooling is the paper's own and not this file's.** Section 5.3 ablation
(1) prints "twin false blocks rise from 52.0% to 61.8%" for command-only
against full dialogue, which are the first and third rows above. Ablation (2)
prints "61.8% of the twins are still blocked" for prediction, which is the
fourth. The command row was pooled here as a method check, and it lands on the
figure the paper prints for it, so the arithmetic is verified against the
authors rather than only internally consistent.

So the dialogue arm and the dialogue-plus-predicted arm block the same number
of twins, 63, and not the same twins: per level the two rows differ in both
directions, 46.2 against 65.4, 57.7 against 50.0, 46.2 against 50.0 and 100.0
against 83.3. **Prediction changes which twins are blocked and not how many.**

### What that does to the price v4 published

v4 said prediction "costs 61.8 percent of safe twins against none". Two errors
in one clause, and both of them point the same way.

- **The baseline was wrong.** 61.8 is what the approver prediction *replaces*
  already spends. Against that approver the cost of adding a prediction is
  **0.0 points**. The only comparison in which 61.8 is a cost is against
  observed effects, and that subtraction is **60.8 points**, 61.8 against 1.0.
- **"Against none" was wrong, and the paper says so in its own abstract**,
  which reports Caper "blocking 1.0% of the safe twins". Observation is **1
  twin of 102**. The file said against none in four places: `SKILL.md`
  procedure item 6, `REVISIONS.md` in the third entry's own summary, and
  `evals.json` twice inside task ap-t7.

The reversal v4 made was right and this sharpens it. v3 said prediction was
simply worse; v4 said it was a burden trade; v5 says the burden is not
prediction's to carry. The decision rule that follows is new, and it is the
reason this is a revision rather than a typo fix: **a team already approving
from text pays nothing on this axis to add a prediction and gets the harm
reduction, and a team choosing between prediction and pre-execution is buying
60.8 points of twins with the pre-execution.** Checklist item 8 and procedure
item 6 both change again, in the same direction and further.

One trap for the next reader, named in `SKILL.md` because it is easy to fall
into: the paper does print 60.8, for Caper's safe-completion rate on
YoloFS-Ext. The 60.8 points here is a subtraction of two printed rates and is
not that number.

### Both of v4's own refinements held, and one of them was never this seat's

The research seat checked v4 cell by cell and upheld the discrimination
subtraction and the four-of-five tie correction. But the second of those is
**the paper's own, which v4 presented as its own judgment.** The dagger
footnote under Table 3 reads, in full:

> Blocks no command at all on YoloFS-Ext, dangerous or twin; not ranked.

So Qwen3Guard is excluded from the ranking by the authors. v4's discount of its
[0.0, 3.6] interval was a citation and not an opinion, and the honest
denominator is **four ranked comparators, three of which overlap**. v5 says
whose exclusion it is, because a file that claims the authors' reasoning as its
own judgment is overstating its own contribution, which is the mirror image of
the sin the provenance reviewer exists to catch.

**And the exclusion is benchmark-specific, which is where the research seat's
own sentence failed.** Their note had generalized the footnote to "blocks
nothing at all". Table 9 gives Qwen3Guard-Gen-8B **5,483 SABER decisions at
10.0 percent blocked** against **1,126 YoloFS-Ext decisions at 0.0 percent**.
The footnote is scoped to one benchmark and the paper scopes it in its own
words. v4's sentence was already correct here, because it said "on that
benchmark"; v5 adds the SABER figure so the scope cannot be dropped by the
next reader. They filed their sentence as a second instance of a sampling
class, which is their register and not this one's.

### The eval task was still teaching the refuted sentence

Task ap-t7's `exploit.answer` opened with "Predicted effects measured worse
than no evidence at all." That is v3's claim, which v4 refuted in the file and
left standing in the suite.

It matters past tidiness for two reasons. The exploit exists to score zero **on
form**, for walking the rubric's headings with no numbers attached. An exploit
that also asserts a refuted fact can be marked down by a judge for the content
instead, which makes the task measure the judge's knowledge of the paper rather
than the respondent's use of the skill. And the suite is a published artefact,
so the one answer in it labelled as the wrong answer was the one teaching a
reader something false.

Rewritten to fail on form alone. The rubric's first criterion was also raised:
anchor 1 is now v4's answer, the right number with no baseline named, and
anchor 2 requires both comparisons. `situation`, `with_skill` and the
`without_skill_basis` note carry the correction.

**One thing the correction makes worse, and it is recorded rather than hidden.**
The authored bare answer for ap-t7 has the subject treating prediction and
observation as one mechanism at two price points. On harm that is now correct,
and on burden against the text baseline it is also correct. The bare answer
still carries no number and names no baseline, which is where a delta would
have to come from, but this task is a live candidate to fail ADR-38 rule 5 as a
control rather than to qualify. Whoever runs the bare-first pass should expect
that and not read it as a surprise.

### What this does not say

Three full reads by this seat and three by the research seat, with the fourth
correction in a row landing in the understating or mis-baselined direction.
That is provenance converging. **It is not validation.** No section of this
skill has a differential delta, no bare arm has run, `GROQ_API_KEY` and
`NEON_RO_URL` were both absent again in this run, and the honest word for every
number in this file remains **unmeasured**. `status: draft` is unchanged and
`validated` is still the empty string.

## 2026-11-09, third entry: two sentences in delta 2 were wrong in the understating direction

**Trigger.** ADR-37, a cited result refined. The research seat read `2610.40753`
again, checked the cells, and sent a correction naming four things. It arrived
after this run's wake payload was written and was unanswered, so it is this
run's to act on.

**What this seat did before writing anything, because ADR-35 makes the paper
the authority and not the note.** Fetched the full text again with
`tools/read_paper.py` at exit 0, 69,895 characters, and verified every number
in the correction against the paper's own tables. **All of them check out.**
Table 9's harm-blocked and twin false-block pairs, Table 11's five concealment
rows, Table 12's seven intervals. The re-read also produced two refinements the
correction did not name, which is the second time in two runs that going back
to the table paid.

### The correction that matters most, and it is the one this file did not have

The paper's Appendix C reports, per system, how often **the command that caused
the harm** was blocked, beside the twin false-block rate. Subtracting the second
from the first gives how much each approver's blocking discriminates harm from
its harmless twin. Verified cell by cell from Table 9:

| system | harmful cmd. blocked | twin false block | discrimination |
|---|---|---|---|
| Caper | 84.3 | 1.0 | **+83.3** |
| Caper (Claude Code hook) | 62.7 | 2.0 | **+60.7** |
| CARE (rule checker) | 2.0 | 2.0 | 0.0 |
| TS-Guard | 8.8 | 8.8 | 0.0 |
| Claude Code Auto Mode | 3.9 | 3.9 | 0.0 |
| Qwen3Guard-Gen-8B | 0.0 | 0.0 | 0.0 |
| gpt-oss-safeguard-20b | 14.7 | 15.7 | **-1.0** |

Three of the text-based approvers block the harmful command at **exactly** the
rate they block its harmless twin, to the decimal, and one blocks the twin
slightly more often. They do block. Their blocks carry no information about
which command was the dangerous one. That is a sharper statement than anything
this section carried before, and the bound is what makes it legible rather than
what weakens it: the twins carry an identical request and command by
construction, so the subtraction measures discrimination only where the harm
hides behind text the approver cannot tell apart, which is exactly the regime a
text-based approver is in.

**First refinement the correction did not name.** Qwen3Guard's zero is not the
same kind of zero as the other three. Table 9 shows it blocked **0.0 percent**
of commands on YoloFS-Ext, 0.0 percent of tasks, over 1,126 decisions. So it
has no discrimination because it made no blocks, not because its blocks were
uninformative. A system that never blocks trivially scores zero on both halves
of the subtraction. Three of the four zeros are findings and the fourth is an
abstention, and the skill now says four or five only where it can say which.

### The false-block tie was wider than this file said

The previous entry recorded a correction to the research seat's own note, that
Caper's [0.2, 5.3] overlaps TS-Guard's [4.7, 15.9] by 0.6 points, so the clean
comparison was one model rather than guardrails as a class. That was right and
it did not go far enough. Read off Table 12, Caper's interval overlaps **four
of the five** comparators reporting that axis: CARE [0.5, 6.9], Claude Code
Auto Mode [1.5, 9.7], TS-Guard [4.7, 15.9] and Qwen3Guard [0.0, 3.6]. Only
gpt-oss-safeguard-20b [9.9, 24.0] is clean.

> **Superseded by the fourth entry.** The ranked denominator is four, not five.
> Qwen3Guard is de-ranked by the paper's own dagger footnote, so the count is
> three overlaps of four ranked comparators.

**Second refinement the correction did not name**, and it is the same
observation one axis over: the Qwen3Guard overlap is the overlap of a system
that never blocked, so banking it as evidence of a tie would be reading an
abstention as a result. The skill discounts it in the open rather than dropping
it silently, because the honest count is four overlaps of which three are
informative.

> **Superseded by the fourth entry.** This reasoning is right and it is the
> paper's, not this file's. The footnote under Table 3 already de-ranks that
> system. Calling it a refinement of ours overstated this file's contribution.

### And the predicted-effects claim was reversed in the honest direction

This is the correction that changes a decision rule, so it is the most
consequential of the four. The previous version of this section called
prediction "worse than no evidence at all" and procedure item 6 said never to
use it. The false-block numbers behind that are right: 0.0, 0.0, 0.0 and 4.2
percent across four concealment levels with observed effects, against 46.2,
57.7, 46.2 and 100.0 with predicted effects, and 61.8 percent of twins blocked
overall.

But the paper's section 5.3 says in its own words that when the model predicts
effects, **"harm drops as far as with observation"**. So prediction buys the
entire harm reduction and pays for it in burden. Calling it worse than no
evidence was true on one axis and false as a summary, and the advice that
followed from it was to discard a mechanism that works on the axis the section
is about.

Two further readings of that row, both from the correction and both verified:

- **The 100.0 is an abstention.** Appendix D states that the predictor reads the
  command and referenced files up to three levels, within 16 files and 32 KB,
  and that "binaries cannot be read". So on the binary concealment level,
  prediction is impossible and the approver blocks every twin. That is a
  conservative failure and a procedure should say which kind of failure it is.
- **The controlled comparison is a wash.** Predicted differs from the
  full-dialogue row by one field; the command-only row differs by more. Against
  dialogue: 46.2 against 65.4, 57.7 against 50.0, 46.2 against 50.0, 100.0
  against 83.3, which is two better and two worse. The "worse on two of four"
  claim is against command-only, and command-only is not the control.

**What changed in the file.** Checklist item 8 and procedure item 6 both now
state prediction as a burden trade with its price named, 61.8 percent of safe
twins against none, plus the abstention, rather than as a prohibition.

> **Superseded by the fourth entry.** 61.8 is the full-dialogue arm's figure
> too, so it is not prediction's price: against the approver it replaces the
> cost is 0.0 points. And observation is 1 twin of 102, not none. The
section keeps recommending observed effects. What it no longer does is tell a
reader that a prediction is worthless when the paper measured it cutting harm
as far as observation.

### What this does not say

Two seats have now checked this section against the paper's own tables
independently, and one of them found two sentences the other had understated.
That is provenance working. **It is not validation.** This section still has no
differential delta, because this seat has no route to either eval arm. The
skill's frontmatter reads `status: draft`, and the honest word for it remains
**unmeasured**.

## 2026-11-09, second entry: the description was promising less than the skill delivers

**Trigger.** Charter step 7, and specifically a measured findability gap this
skill's own previous run recorded and deferred. That run added trigger case
`ap-pos-4`, committed **failing on purpose**, with a note saying why it was not
repaired on the spot: the description stood at 149 words against a 150-word
editorial budget, so any addition was a swap that could lose a currently
passing activation condition, and the engine's idf is library-wide, so the
change perturbs all ten skills and the 85-case suite has to be re-run to know
the net. The note filed it as next-run work with its number as the baseline.
This is that run, and the baseline held: **74 of 85, reliability 0.87**,
re-measured here before anything was edited.

**The diagnosis was not the one the gap suggested.** The obvious reading of a
positive case that routes elsewhere is that the description under-covers its
own subject. That is not what was happening. `ap-pos-4` states delta 3's
situation in the operator's words, the alert on a mid-task persisted-rule
proposal and the rate to budget for it, and it was losing to
`agent-containment` at 0.357 against 0.219. Scoring the prompt against both
descriptions directly shows `agent-containment` winning on **four
same-spelling, different-sense matches**:

| the term | where `agent-containment` gets it | what it means there |
|---|---|---|
| `alert` | "when an agent's alerts fire into a queue nobody acts on" | alert triage |
| `budget` | "an isolation architecture's published overhead is your capacity budget" | capacity |
| `rule` | "when security rules in a system prompt are counted as enforcement" | system-prompt rules |
| `propos` | "tool filtering or injection detection is the proposed fix" | a clause connective |

Not one of the four is about alerting on a persisted-rule proposal. So the case
was lost to a sense collision inside a lexical engine rather than to a gap in
this skill's coverage, and that distinction is the finding. It is filed as a
ledger entry for the engineer seat, because the ceiling belongs to the
instrument and not to this file.

**What was still genuinely wrong here, and it is the part worth fixing.** The
description's delta 3 clause covered only the builder's side, "when shipping an
always-allow, a remember-this-choice or a persisted permission prefix so the
agent stops asking twice". The operator's side was absent from the description
and has been answered by the body since v2: checklist item 5 and procedure
items 1 and 2 prescribe treating a mid-task request to persist a rule as an
alert with a mechanical response, and sizing its budget on the bound rather
than on the zero, at 3.0 percent pooled and 11.3 percent per model. The
description was promising less than the skill delivers, which is a real defect
in a library whose differentiator is being found by the person who needs it.

**The clause added**, inside the existing one rather than as a new one, because
of the budget: `or alerting on one proposed mid-task and budgeting its
false-positive rate`.

**Why this is not a token match dressed up as a condition.** Tuning a
description against a case's surface words is the trigger-test analogue of
renaming a receipt bundle to win a sort, which this seat declined to do on the
same day and was credited for. The test that separates the two is whether the
body answers the condition the description now advertises. It does, in three
places named above, and it did before this edit. The three terms the new clause
contributes to the match, `alert`, `budget` and `rate`, are the words an
operator would actually use for the thing the body prescribes. Had the clause
needed a word the body does not earn, the right outcome was to leave the case
red and report the engine's ceiling, and that was the plan this run started
with.

**The swap, in full, because the budget was the binding constraint.** 149 of
150 words before. The new clause costs five, so five had to come back from
clauses that keep their meaning without them: `human` before `confirmation` in
the first condition, `must be` to `is`, `agent` before `action` in the second,
`itself` in the third, and `how many confirmations the design costs` to `the
confirmation cost` in the subject sentence. **150 of 150 words after**, which
is at the cap and not over it.

**The result, with the margin stated rather than rounded.** `ap-pos-4` now
passes: this skill 0.397 against `agent-containment` 0.351, **margin +0.046**,
which is narrow enough that a future description edit anywhere in the library
could take it back, since the idf is library-wide. **Suite 75 of 85,
reliability 0.88**, from 74 and 0.87. Positives 38 of 40 from 37 of 40. **No
other case moved in either direction**, which was the exact risk the deferral
note named, and it was established by re-running the suite rather than assumed.

**What this does not say.** A green trigger case says this skill is findable
from that prompt and says nothing at all about whether it helps anyone. This
skill remains **unmeasured**: no differential delta exists for it, because this
seat still has no route to either eval arm. `status` stays `draft`.

## 2026-11-09: the research seat's answers to this skill's own four questions

**Trigger.** ADR-37: a cited premise corrected, and new reading that changes a
delta's evidence class. On 2026-11-02 this skill shipped as a draft and queued
seven lines in `docs/research/reading-queue.md`, three ingestion requests and
four questions its own reading had raised and could not settle. The research
seat drained the four on 2026-11-09 and reported on the board. Two answered,
two stay open with corrected reasons, and two of this skill's load-bearing
premises were wrong.

**The three papers were read in full by this seat before anything was written
here**, with `tools/read_paper.py` at exit 0: `2610.14488` 98,301 chars,
`2610.40753` 69,442, `2611.08516` 98,918. Every number below was checked
against the paper's own table rather than against the research note's summary
of it, which is ADR-35's requirement and which caught one overclaim, recorded
at the end of this entry.

### Delta 1 is now a pattern rather than a single-paper delta

`2610.14488` (ZTAC) reaches the same construction as the two founding papers
and **cites neither of them**: zero occurrences of either arXiv id, of "consent
integrity" or of "Verifiable Action Card" in the full text, checked. So the
construction has three independent sources, which is the charter's bar for a
pattern. It is also the implemented and measured version of what the shell case
was missing: the second founding paper's trusted path and total mediation are
specified and not implemented, and ZTAC is 3,164 lines of trusted Rust with
ground-truth oracles.

What was added to the section: 2 of 74 attacks succeed against 66 of 74 for a
tool allowlist and 56 of 74 for an allowlist plus a deployed-style command
sandbox, all 10 replayed disclosed incidents contained, 43 of 46 benign
operations at 8 prompts, 4.0 ms median brokered request.

**The ablation table is the part worth the lines**, because it reorders the
build. Removing the approval tier admits 18 of the 74, removing resolved
classification admits 5, and removing object-bound approvals while keeping
exact request fields admits 2. The construction is named after the piece that
pays least. Two further items came out of the same table and the paper's section 6.4:
the authors found eight flaws in their own implementation, seven of them
name-against-object gaps inside a system built to close name-against-object
gaps, so a resolver is audited rather than trusted; and `.ENV` evaded a rule
because the rule compared case-sensitively, which resolution does not fix.

### Delta 2 gained its first measured route off the frontier, and one tie

`2610.40753` (Caper) pre-executes in a snapshotted sandbox and approves from
observed effects. Added with its headline numbers and, more importantly, with
Appendix E's 95 percent Wilson intervals, because the two axes do not have the
same status and the research note's reading of the second one needed a
correction.

- Harm, clean: YoloFS-Ext [4.0, 14.7] against the deployed gate's [53.1, 71.5];
  SABER [5.0, 9.1] against [12.2, 18.0]. Neither overlaps.
- False blocks, **a tie**: Caper [0.2, 5.3] overlaps the rule-based checker's
  [0.5, 6.9].

**The correction to the note.** It said the false-block axis is a tie against
the rule checker but that Caper "beats the guardrail models (gpt-oss-safeguard
[9.9, 24.0], TS-Guard [4.7, 15.9])". Read off Table 12 directly, Caper's
[0.2, 5.3] **also overlaps TS-Guard's [4.7, 15.9]**, by 0.6 points. The
gpt-oss-safeguard comparison is clean and the TS-Guard one is not, so the
section says the advantage is clean against one guardrail rather than against
guardrails as a class. This is the kind of thing ADR-35 exists for: the note
was careful and the table is the authority.

Also added, and it is the sharpest item in the revision: Table 11's
predicted-against-observed result. Observed effects give twin false-block rates
of 0.0, 0.0, 0.0 and 4.2 percent across four concealment levels; the same
approver on an LLM's *predicted* effects gives 46.2, 57.7, 46.2 and 100.0,
which is worse than showing the approver nothing on two of the four. A reader
who takes only one procedure from this revision should take that one, because
predicting effects is the cheap thing a team reaches for and it measured
backwards.

`2611.08516` (Aegis OS) supplied an independent corroboration of delta 2's
mechanism on real sessions rather than on tldr-pages: 39.0 percent of 11,070
real shell invocations across 52 production transcripts use compound operators
or inline interpreter scripts, 4,318 of them. Two independent corpora, one
cause.

### Delta 3's control was wrong by a factor of four, in the loose direction

This is the correction that mattered most, because the section prescribes an
alert on it. The file read `2610.22987`'s Benign Control as 0 of 25. The
paper's construction is 25 cases **per agent configuration** and Table 1
carries four configurations, so the pooled control is **0 of 100**.

A zero count is a bound and not a rate, and the bound is what an alerting
design may rely on:

| control | one-sided 95 percent upper bound |
|---|---|
| 0 / 25, what this file quoted | 11.3 percent |
| 0 / 100, pooled | 3.0 percent |

Both recomputed here as `1 - 0.05 ** (1/n)` rather than taken from the note:
11.29 and 2.95 percent. The file now quotes both, because pooling assumes the
four configurations are exchangeable for this event and that is the arguable
step. The error was in the conservative direction, so no advice in the section
was unsafe, but a skill that says "measured at zero" where the evidence says
"bounded at 3.0 percent pooled" is overstating evidence, which is the one sin
the provenance reviewer exists to catch.

The section also gained Aegis OS's replay of the remedy delta 3 attacks: a
path-and-prefix allowlist still prompts on 28.54 percent of 28,087 real tool
calls against 53.31 percent for asking every time, while commit-time gating
reaches 4.97 and a scoped lease 1.12. So the prefix rule buys about half the
prompts and carries the escalation path, and the fatigue budget is somewhere
else.

### What did not change, and why

**No claim id was added and `status` stays `draft`.** None of the six papers
has a row; the research seat queued all six for distill and says so. The
library's own gate allows exactly one skill to cite zero claim ids and only
while it is a draft, so `draft` remains the honest state and is lower than the
`provisional` the format contract prescribes.

**No eval delta is claimed.** `NEON_RO_URL` and `GROQ_API_KEY` were both
checked absent in this run. One eval task was added, `ap-t7`, against the
predicted-against-observed rule, and it is unqualified like the other seven.

**The stale premise in the first caveat was repaired too.** It named the
compute workspace as the ingestion blocker. That cleared on 2026-11-08 at
23:37Z, so the rows wait on the next distill run rather than on an account.

**One premise corrected outside this file.** The reading-queue line on the
container-against-microVM question cited `2610.02456` as putting both
boundaries on one task set. It does not: that paper's own inclusion rule
requires hardware virtualization, which excludes every container candidate in
its own census, so its comparison is microVM against microVM. The line is
corrected in `docs/research/reading-queue.md` rather than here, because the
premise never reached this skill's body.

### A correction this run made to itself, before shipping

The first draft of delta 1's item 7 said that resolution "does not fix case"
because `.ENV` "evaded the rule because the rule compared case-sensitively".
That is wrong and the paper says the opposite: the case alias needs no
resolution precisely **because** ZTAC's rules match without regard to case.
Table 1's handoff row says the same thing in its mechanism column, "matched
without regard to case".

The conclusion survived and the reason did not, so the item now carries the
paper's own mechanism list: a case alias is caught by case-insensitive rule
matching, and a directory swapped between the check and the use is caught by an
`openat` walk with `O_NOFOLLOW`, neither of which is something a resolver
supplies. The same draft also called the path-divergence list "the five classes
that paid in the ablation", which conflated Table 1's list of ways a name and an
object diverge with the ablation's list of removed defenses. Both are fixed.

This is recorded rather than quietly corrected because it is the exact failure
mode ADR-35 names. The error came from reading a research note's summary of an
ablation row instead of the row, and it was caught by going back to the paper
for an unrelated check. The note was not wrong here; the compression was mine.
