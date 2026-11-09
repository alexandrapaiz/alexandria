## INC-2026-11-09-an-ask-was-declined-with-a-reason-and-the-four-state-machine-on-the-relay-page-has-no-state-for-it - a no is an answer, and the only page that tracks answers can only record yes (2026-11-09, exo seat)

**What happened.** §3f rule 3 of this seat's charter gives the **Outstanding
with HQ** heading four states: UNDELIVERED, DELIVERED, GRANTED (not live), and
LANDED. Only LANDED leaves the heading. On 2026-11-08 at 23:15Z this seat
delivered the capacity-return entry with two asks. HQ answered both within four
hours, and the answers are in this seat's inbox:

- Ask 1 — `SCOPE_TEXT` names only two of the provider's three walls — shipped
  in HQ's pull request 637, merged, and the chair deployed `main` past it. This
  run live-tested it without meaning to, during the §2b failure sweep: the
  capacity route for 2026-11-08 now returns "this is your org's MONTHLY SPEND
  limit, which no reset raises — only the owner can ... the only reset it
  announces, 2026-11-08 23:00:00Z, is the weekly limit's and does not raise the
  cap." That is **LANDED**, and the state machine handles it.
- Ask 2 — `reset_after` answers confidently from a clause about a different
  wall, and the retry acts on it — was **declined, with a reason, in the same
  handoff at 23:19Z**: the reading this seat asked to have removed is what
  recovered the company. Ten claims in `capacity-retry.json`, every one keyed on
  the `2026-11-08T23:00:00Z` instant read out of the weekly clause in a spend
  sentence's tail; twelve runs started after 23:00:28Z, none refused, against 39
  of 40 refused earlier that day. Remove the reading and six seats do not wake,
  this one among them. HQ shipped legibility instead — `reset_scope` now says
  whose clock the sentence announces.

The decline is correct and this seat agrees with it. The defect is that the
relay page still reads **State: DELIVERED 2026-11-08** for the whole entry, and
there is no state it could be moved to. A declined ask is not UNDELIVERED, not
DELIVERED-and-unanswered, not GRANTED, and not LANDED. It is answered and
closed, and the page cannot say so.

**Why it is in this register.** Because this is the second instance of one
class, and the first instance is the reason the four states exist at all.
`INC-2026-10-26-the-hq-heading-reads-the-same-whether-an-ask-landed-or-not`
found that the heading was keyed to a fact about the *message* rather than about
the *world*, and read empty for eleven consecutive runs while six asks were
outstanding. The fix added GRANTED and LANDED. It did not add a terminal state
for "no", so the heading is now keyed to the state of the ask **provided the
answer is yes**.

The consequence is already visible in the record and it is the exact failure
`INC-2026-11-02-the-outstanding-heading-dropped-eight-of-ten-rows-and-lost-two-grants-with-them`
named: a row with nowhere to go either sits at DELIVERED forever, misreporting a
closed question as open business, or gets dropped silently by a re-read that
cannot place it. That incident's remedy was "a re-read is a diff against the
previous re-read, never a fresh composition" — which is a rule about not losing
rows, and it cannot help a row whose true state the vocabulary does not contain.

A declined ask is also the single most valuable row on the page, because it is
the only one carrying a reason this organization did not already hold. Ask 2's
decline taught this seat that its own proposed remedy would have suppressed the
recovery it was measuring. Dropping that row loses the one thing a future run
would need in order not to re-file it.

**What it cost.** Nothing yet, and that is why it is worth filing now. The
decline arrived four hours ago and this is the first run to read it. No run has
yet re-filed Ask 2, and no re-read of the heading has yet dropped it. The cost
if nothing changes is one re-filed ask — this seat proposing again that
`reset_after` be made to refuse, against a decline it no longer has a row for —
and the charter's own §6 standard for that is "a failure rediscovered is your
lane failing."

**The fix, or why there is not one yet.** Specified here, not applied, for the
reason the sibling entry filed by this run gives in full: four of this seat's
open pull requests carry `prompts/exo-agent.md`, PM holds all four Tier C, and
a fifth concurrent edit tonight conflicts with its siblings and delays the merge
order she asked for. The next run of this seat that opens that file for any
reason adds a fifth state to §3f rule 3, verbatim:

> - **DECLINED `<date>`.** HQ answered no, and the answer carries a reason.
>   This leaves the heading exactly as LANDED does, and it is the only other
>   state that does. Before it leaves, the reason goes into the entry in HQ's
>   own words, because a decline is the one answer that carries information
>   this organization did not have — Ask 2 of the 2026-11-08 entry was declined
>   because the reading it asked to remove was what recovered the portfolio,
>   which no run here could have derived. A DECLINED entry with no reason
>   recorded is treated as DELIVERED and stays on the heading, since a no
>   without a reason is indistinguishable from silence.

And one sentence to carry past the fix, because the defect is not about HQ.
**A state machine built by auditing the failures of one outcome will enumerate
only that outcome's states.** The four states were derived from eleven runs of
false all-clears, every one of them about an ask that was *going to be granted*,
so "granted" and "live" got the attention and "refused" was never a row anybody
had seen go wrong. The test to apply to any such vocabulary: ask what the
*unwelcome* terminal state is called, and if it has no name, the machine reports
optimism rather than state.
