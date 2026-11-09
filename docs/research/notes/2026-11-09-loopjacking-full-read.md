# Loopjacking (`arxiv:2609.21081`) read in full: what the corpus had wrong, and the one thing it did not have at all

Research seat, 2026-11-09, PR #913. Lane item `fc21860e`.
`python3 tools/read_paper.py 2609.21081`, exit 0, **55,190 chars**, which is
the same character count this morning's run recorded when it fetched the
paper and shipped before reading it.

A. A. Kumar, *Loopjacking: Hijacking Human-in-the-Loop Approval*,
arXiv:2609.21081v1 [cs.CR], **17 Sep 2026**, CC BY 4.0, independent security
researcher, sole author. Evidence cutoff **10 Sep 2026**.
<https://arxiv.org/abs/2609.21081>

Until this read, the corpus knew this paper only through `2609.38983`'s
section VIII-A, which reads it at length as concurrent work. **That section is
accurate on everything checkable here except one omission, and the omission
is the load-bearing field.** That is the finding; the rest is confirmation.

## 1. What the paper measures

Four product paths, purposive, explicitly not a sample. Three positives and
one negative control. Every count below is a deterministic trial outcome in a
frozen bundle, **not a rate**.

| Path | Variant | Attack | Direct *B* | Safe outcome |
|---|---|---|---|---|
| Agno AgentOS (regular Agent behind the AgentOS HTTP API) | post-approval substitution | strict positive at each of **2.5.6, 2.9.0, 3.0.1, 3.0.2, 3.0.3, 3.0.6, 3.0.9**; 3.0.9 is 5/5 | denied 3/3 | a **research-authored** exact-action wrapper rejected *B*, preserved *A* |
| LangGraph Agent Server, in-memory runtime, LangChain 1.3.18 / LangGraph 1.2.11 | post-approval substitution | strict positive at each of **12** versions, 0.7.5 to 0.14.0; 0.7.4 lacks the feature | denied | a **supported** deny-update Auth policy rejected the mutation, executed *A* |
| OpenClaw shell-wrapper path through its gateway and node host | **representation mismatch** | **2026.2.23: 3/3** | denied 3/3 | **2026.2.24: 3/3 rejected**, *A* still executed |
| OpenAI Agents SDK 0.22.0, 0.22.2 | negative control | mutation **rejected** 3/3 and 3/3 | paused without effect | unchanged serialized *A* executed 3/3 and 3/3 |

Admission requires all six necessary conditions (sec. 2.3): a genuine
product-recorded human decision over a view understood as *A*; a materially
different *B*; reachable attacker influence; product-owned consumption of the
decision; the exact operation at a consequential sink recorded, not an
intermediate state or a model statement; and **no equivalent direct authority**.
The sixth is what makes the label mean something, and the paper demonstrates
it rather than asserting it: Agno **2.5.5 also executed the substituted
continuation and is ruled ineligible**, because direct *B* succeeded there, so
hijacking the approval was not needed. 2.5.6 is the established lower boundary
at which the gate both blocked direct *B* and could be reused for substituted
*B*.

## 2. The thing the corpus did not have: the record has six fields and we had five

`2609.38983` section VIII-A reports Loopjacking's section 6.1 canonical approval record as
"the canonical action and its material arguments, target resource and
side-effect class, the initiating principal and task/thread/session scope, the
approving principal, and a nonce/expiry/consumption status". Five items. The
paper's section 6.1 has **six bullets**, and the sixth is:

> * a digest over the same complete descriptor shown to the human.

followed immediately by the sentence that makes it operative:

> The display must be generated from this descriptor, not from a lossy
> convenience string while execution uses a richer object.

**`digest` occurs zero times in all 134,754 characters of `2609.38983`.** So
the field is not merely dropped from that paper's summary of section 6.1, it is
absent from that paper entirely. And in `2609.28586` the three occurrences of
`digest` are source-content digests and prediction digests, not a digest over
what the human saw. **Of the three independent namings of this failure class,
Loopjacking is the only one that carries this field, and it is the only one
with a released product fix for the class it protects.**

### Why the omission is the load-bearing one

The approval-paths skill's v6 checklist, items 1 and 2, tells a builder to
decode the confirmation text from the action that will execute and to bind the
approval to that exact action and re-verify at dispatch. Both items run in one
direction: action to text. **OpenClaw 2026.2.23 is the measured case where that
direction is satisfied and catches nothing.** The complete positional argument
vector was prepared *before* approval. The product's approval event rendered
only the inline payload `$0 "$1"`. Additional positional arguments selected
the command and destination that created the marker. The rendering was
genuinely derived from the real command; it was simply a lossy projection of
it. So if the descriptor the approval binds to is captured from that view, then
at dispatch the current operation equals the stored descriptor, the comparison
passes, and the marker is created: 3/3.

So the binding has a **precondition** as well as a ceiling, and the two are
invisible to the same check for opposite reasons:

- **The ceiling** (`2609.28586`, which v6 now carries): the fields agree and
  the operation differs, because the divergence is below the mediation point.
- **The precondition** (`2609.21081`, which nothing in the corpus carried):
  the fields agree *because the record is lossy*, so the operation that
  differs was never in the record to compare against.

The repair Loopjacking names is the digest direction plus one rule: "A
collapsed view may remain useful, but approval must expose any material hidden
fields or refuse to authorize them." And it supplies the measured field list
for the shell surface the skill's founding set already includes: "inline
payloads, positional arguments, environment changes, working directory,
interpreter flags, and redirections can all change the effect."

### Three insufficiencies, one per measured product, in the paper's own words

Section 6.2 states the negative results as a triple, and each maps to one of the
three positives:

> Binding only a call identifier is insufficient when a reducer can replace
> the arguments associated with that identifier.

LangGraph. The maker's `message.command.update` replaced the pending
**same-ID** tool call; the message reducer replaced a same-ID pending message;
HITL processing reconstructed the current call on resume; execution inherited
the authenticated resume principal. No comparison bound the earlier displayed
action to the current same-ID action.

> Binding only a run-level "approved" flag is insufficient when a
> continuation can install a different tool execution.

Agno. The continuation route first checks whether a required approval remains
pending; once that **run-level** state clears, it deserializes
caller-supplied tool executions, installs the supplied object, and dispatches
a confirmed tool execution. Call identity is matched; the current arguments
are not compared with the descriptor in the approved record.

> Checking only at presentation time is insufficient when state can change
> before dispatch.

The general post-approval case.

## 3. The negative control falsifies the repair an engineer reaches for

OpenAI Agents SDK 0.22.0 and 0.22.2, 3/3 and 3/3: every approved exact-*A*
state was serialized, restored and resumed, and all executed *A*. In every
attack trial the raw serialized copy of the pending invocation was changed to
*B* **while retaining the call ID and the original canonical
approval/invocation records**. Restoration succeeded; resume raised
`ModelBehaviorError`; the ledger remained empty.

The paper's conclusion from it: "resumability is a carrier for post-approval
substitution but neither a necessary condition for the umbrella nor a
sufficient cause of failure." So **durability, persistence and resumable
approval state are not the defect**, and shortening the approval window or
refusing to persist approvals is not the repair. What the control preserves is
a canonical invocation fingerprint across serialization.

This is the second time in three days of reading that a timing-shaped repair
is ruled out by measurement rather than argument: `2609.28586` rules out
re-approving on a changed environment snapshot because every divergent hook
predates the grant. **Two of the three papers independently rule out a
timing-based fix, and neither says so about the other.**

## 4. Corrections to the queue line

The line at `docs/research/reading-queue.md:3702` was written from
`2609.38983`'s section VIII-A plus this paper's abstract and table of contents, and
disclosed exactly that. The disclosure held for the content it covered. Two
things in it are still wrong, and both are of the class
`INC-2026-11-09-the-provenance-label-was-attached-to-the-abstract-half-and-the-wrong-half-was-the-arithmetic`:
sentences derived at queue time that no abstract could supply or refute.

**(a) "three of its four products are on the charter's watch list" is TWO of
four.** `prompts/research-agent.md` Layer 4 names "LangGraph and LangChain
engineering output, AutoGen/AG2, CrewAI, the OpenAI Agents SDK, Anthropic's
engineering essays, the MCP specification's evolution, arXiv cs.MA". The
LangGraph Agent Server is on it, by its runtime pins as well as its name
(LangChain 1.3.18, LangGraph 1.2.11). The OpenAI Agents SDK is on it. **Agno
AgentOS and OpenClaw are on no list.** And they are reachable by no source:
`grep -ciF` over `sources.yaml` returns **0 for both `agno` and `openclaw`**,
against 1 for `langgraph` (`gh-langgraph`, tier d) and 1 for
`openai-agents`.

**(b) The version counts are executed points, not affected ranges.** Seven
Agno releases and twelve LangGraph versions are right as counts, and both are
the *executed* set. The paper refuses the range reading twice: "We do not
infer that every intermediate patch is affected", and for LangGraph a
hash-verified scan of **130 stable wheels** found the required forwarding path
in every release 0.7.5 to 0.13.4 while the paper states that the scan "cannot
promote unexecuted patches to native results". 0.14.0 is a separate
current-release execution point.

Three things in it are confirmed: 17 Sep 2026 and therefore **first** of the
three namings; classification by **when** the substitution enters relative to
approval rather than by field or effect class; and `2609.38983` section VIII-A
reading it at length while `2609.28586` does not cite it at all. The
independence check re-ran both directions: `2609.28586` contains **zero**
occurrences of `2609.21081`, `Loopjacking`, `Agno`, `OpenClaw`, `AgentOS` or
`LangGraph`, and its single `Kumar` is D. Kumar of Perry et al. 2023, a
different person. `2609.38983` carries `Loopjacking` 15 times with the
reference entry naming sections I, I-A and VIII-A as the citing sites.

## 5. One live fact the paper could not have: the A2A clause is merged and
still untagged, 102 days on

Section 2.5 is the paper's A2A section, and it is careful: these mechanics "do not by
themselves create a vulnerability", and the history "supports a
specification-clarity lesson, not an intrinsic A2A or common-SDK
vulnerability." Before section 7.6.4, three coordination choices mattered to a
deferred approval path. `TASK_STATE_AUTH_REQUIRED` was an interrupted,
nonterminal state; agents were advised to accept messages directed to the same
Task while authorization remained pending; and an agent receiving a credential
out of band could continue without a client follow-up. None of the three
defined the approver, a canonical operation, an action-scoped approval object
or the application sink. Issue 2080 framed it as implementer ambiguity; merged PR
2081 added section 7.6.4.

Checked live this run rather than taken from the paper. **PR 2081 merged
2026-07-30**, and section 7.6.4 says agents "MUST NOT treat the state transition
itself as authorization for any particular operation". The paper's cutoff
statement was that v1.0.1 remained the latest tagged release on 10 Sep 2026.
**It still is, on 2026-11-09: v1.0.1, 28 May 2026.** So the clause has been on
`main` for 102 days and is in no tagged release, and a builder pinning the A2A
specification to a release does not have it. We can see this: `sources.yaml`
carries `gh-a2a-spec-changelog` against
`A2A/commits/main/specification.atom`, which is the feed that would carry a
commit rather than a tag. And the 2026-09-30 note in `sources.yaml` already
records that `gh-a2a-protocol`'s releases feed delivers bare version strings
with empty abstracts, which is exactly the feed that would show nothing here.

## 6. Bounds, so nothing from this paper gets over-quoted

- **Purposive, not representative.** Stated in the abstract ("These results do
  not estimate ecosystem prevalence"), in section 1, in the Table 2 caption and in section 7.1. No
  ecosystem rate, no universal affected range, **no CWE, CVSS, severity or
  impact estimate**.
- **One researcher, no independent reproduction.** Selected points repeated in
  clean macOS environments and representative Agno/LangGraph versions in Linux
  containers; section 7.1 says plainly there is no independent reproduction.
- **Nothing here is evidence about humans.** The approval decision was scripted
  only after the test asserted and recorded the exact product view of *A*.
  Sections 2.4 and 3.3 both disclaim claims about interface comprehension, deception
  rates and user behaviour. **So this paper may not be cited for
  approval-fatigue or dialog-quality effects at all.** That is the one place
  a reader is most likely to reach for it and the author closed it twice.
- **LangGraph is conditional.** It depends on an Auth policy that lets a
  non-approver update a shared pending thread, "a plausible composition of
  documented extension points, but not asserted to be a default deployment",
  and the supported deny-update policy "falsified the universal claim".
  Production Postgres was not evaluated: the official image reached its
  license-key requirement before serving the client. No vendor-fixed release.
- **Agno has no fixed release** at the cutoff, and its exact-action control is
  research-authored rather than a product feature.
- **OpenClaw is the only native affected/fixed released pair** in the paper,
  and, across all three namings' positives, the only released vendor fix for
  any of them. The later advisory GHSA-2j8v-hwgc-x698 lists a May boundary;
  the author reconciles it as a duplicate on registry and commit-ancestry
  checks and labels that "our evidence-led reconciliation, not a formal vendor
  or GitHub merge decision."
- **The evidence archive exists and was checked live**:
  <https://github.com/adithyan-ak/loopjacking> carries `verify_archive.py`,
  `CHECKSUMS.sha256`, `EVIDENCE.md` and `evidence/` and `experiments/`
  directories. Not run here; the bundles are the author's and running them
  proves his hashes, not our reading.
- **Generative-AI usage is disclosed** in the manuscript: Codex assisted with
  repository inspection, experiment-script orchestration, evidence
  normalization, citation metadata and drafting, with the author stating Codex
  outputs "were not treated as independent evidence or validation."

## 7. Routed, not applied

`skills/` is the skill seat's surface under ADR-22, so these go to it rather
than into the file:

1. **The checklist's item 2 has a precondition it does not state.** Add that
   the descriptor the approval binds to must be the complete canonical
   operation, and that the display must be generated *from* it. The direction
   matters, and OpenClaw 2026.2.23 is the 3/3 measurement of the reverse. The
   fix is a released product fix, 2026.2.24, which is more than the ceiling
   sentence has behind it.
2. **Item 1 is about provenance; completeness is a separate requirement.**
   "Decoded from the action that will execute" is satisfied by a lossy
   projection of that action. The rule that closes it is the paper's: expose
   any material hidden field or refuse to authorize it. On a shell surface the
   field list is measured: inline payloads, positional arguments, environment
   changes, working directory, interpreter flags, redirections.
3. **A line for the caveats, because the surface count moves again.** v6's
   caveat names five and six surfaces. This is a seventh: agent-orchestration
   products and a gateway-mediated shell path, at deterministic trial
   denominators of 5/5 and 3/3 rather than corpus rates, by one researcher
   with no independent reproduction.
4. **Delete the timing repair from a builder's option set, with two citations
   now.** Neither re-approving on an environment-snapshot change
   (`2609.28586`) nor refusing to persist approvals (`2609.21081`'s negative
   control) is the fix, and the two papers rule it out independently without
   citing each other.
5. **Do not let this paper near a fatigue claim.** Of the three namings it is
   the one whose method most looks like a human-factors study and the one that
   most explicitly is not.

## 8. Not mine, recorded

- **A reach gap, measured.** Two of the four products in the first naming of
  this class are reachable by no source in `sources.yaml`. A `sources.yaml`
  proposal would reach nothing: it is `add_local_file`'d into the ingest image
  at `pipeline/ingest.py:106`, `modal deploy` is run by hand, and the only
  workflow that would run it is in `.github/workflows-pending/`. Recorded for
  the census and routed to the engineer rather than spent as this week's
  proposal, per the charter's reach check.
