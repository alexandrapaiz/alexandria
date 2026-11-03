# PR/FAQ — Alexandria on WhatsApp

**Status: draft for alexandria's PM. Not a go.** Written by Alexandra Systems'
distribution seat (`prompts/distribution-agent.md`) under the company PM
standard §2c, which says nothing larger than a sprint item is planned until its
PR/FAQ exists, and that the owner's merge is the go decision. This document
exists so the decision can be made on the shelf's real economics, which
**changed on 1 October 2026** and are not what the distribution registry said
three weeks ago.

**The recommendation is in the Internal FAQ, and it is not "build it now."** It
is: start the one clock that is slow and non-delegable, decide the MCP host
first, and do not write the integration until both are settled. The press
release below is what we would be building toward when they are.

No quote in this document was collected from a person. §2c asks for the
press-release form, and the form includes quotes; these are written for the
document, and they are the voice it is aiming at rather than evidence that
anyone has said it.

---

## 1. Press release

*Dated as if it had already happened.*

### Alexandria now answers research questions on WhatsApp, with its sources attached

**Ask Alexandria a question about AI research in the same app you use to text
your family, and get an answer that names the papers and claims it stands on.**

**The problem, in the reader's words.** "I get the digest and I read maybe half
of it. When something in it matters to me I want to ask one follow-up question
— does this hold for smaller models, has anyone replicated it — and the honest
answer is I am not going to open a laptop, find the paper, and read section
four. So I skip it, and the thing I was curious about just goes away."

**The solution.** Alexandria's research corpus is already queryable: the same
`rag_answer` surface that serves the skills and the digest can take a question
in plain language and answer it with the claim IDs and source papers behind
each part of the answer. Putting that surface behind a WhatsApp number means
the follow-up question costs the reader one message in an app already open on
their phone. The answer comes back with its provenance — not a summary that
sounds confident, but a claim with the paper it came from and the date the
evidence was last revised.

**Why it matters, from the owner.** "The product's whole argument is that you
can see what an answer is standing on before you take its advice. That
argument is worth nothing if checking it requires more effort than believing
it. WhatsApp is where the people I know actually read and reply. Putting the
provenance in the place where the question gets asked is not a channel
decision, it is the argument."

**How a reader starts.** Send one message to Alexandria's number and reply
`YES` to the opt-in. From then on, any question about AI research gets an
answer with its sources. The weekly digest arrives in the same thread if they
want it there, and they can ask about any item in it by replying to it.

**What changed for one reader.** "I asked whether a context-compaction result
held up outside the paper's own benchmark. It came back with two claim IDs, one
of them revised in September, and said plainly that nobody had replicated the
second. That is the answer I wanted and it took eleven seconds."

**Call to action.** Message the number. There is nothing to install and no
account to create.

---

## 2. Customer FAQ

**What does it cost me?**
Nothing. Asking questions on WhatsApp is part of the free tier, the same as the
digest. The $20/month subscription is for the skills, the claim graph, and the
automations, and it is unchanged by this.

**Is this a bot that will message me every day?**
No. It answers when you ask. The only thing it sends unprompted is the weekly
digest, and only if you ask for it in WhatsApp rather than email. There is no
promotional messaging on this number.

**What does it not do?**
It does not search the live web, it does not read papers it has not ingested,
and it will not pretend to an answer it cannot source. When the corpus does not
cover a question it says so rather than generalising. It is not a general
assistant — ask it about AI research and it is useful, ask it to book a flight
and it will decline.

**How good are the answers, really?**
They are as good as the corpus, and the corpus is visible. Every answer names
the claims and papers it used, so you can disagree with it specifically rather
than in general. Where evidence has been revised, the answer says what changed
and when.

**What happens to my phone number?**
It is stored to deliver answers to you and for nothing else. It is not sold, it
is not used to advertise, and it is not matched against anything. WhatsApp
itself can see that you messaged a business, which is true of every business
number on WhatsApp and is Meta's relationship with you rather than ours.

**Will my questions be used to train a model?**
No.

**How do I leave?**
Send `STOP`. The number stops messaging you immediately and your phone number
is deleted. You can also block the number in WhatsApp, which Meta honours
without us being involved. Leaving WhatsApp does not affect your email
subscription, and leaving the email list does not affect this.

**Is this available in my country?**
WhatsApp is, and the number works from anywhere WhatsApp works. The service is
built for Guatemala first because that is where its readers are.

---

## 3. Internal FAQ

### What has to be true for this to work

Four things, and **two of them are false today.** Each is measured, with the
command, so the next reader re-measures rather than inherits.

1. **`rag_answer` has to be serving. It is not.**
   `https://ap4509--alexandria-mcp-serve.modal.run/mcp` returns **404** with
   the body `modal-http: workspace ac-5DsaR3hWSUxqyNoGYiowja is disabled`,
   measured 2026-10-26 and unchanged across four weekly readings. The entire
   press release above is one HTTP call to a host that is switched off. **This
   initiative is downstream of the owner's decision to restore that workspace
   or retire the server**, which is item 1 of Alexandria's distribution map
   and already blocks six other shelves. Nothing here should start before it.

2. **We have to be able to reach a reader on WhatsApp. We cannot.**
   Alexandria's only capture surface is the waitlist, and it takes an email
   and nothing else: `site/app/api/waitlist/route.js` calls
   `subscribe(body?.email, body?.source)`, read on `main` 2026-10-26, and the
   file contains no phone, tel or WhatsApp field. So there is no WhatsApp
   identity for anyone on the list, and there is no opt-in record either —
   which WhatsApp requires, not as etiquette but as policy. A phone capture
   with an explicit, logged opt-in is a prerequisite build item, and it is
   small.

3. **A payment method has to be on file before the first reply is delivered.**
   New as of three weeks ago and it is a gate rather than a preference; see
   the cost section.

4. **Meta Business verification has to be done.** Non-delegable, owner-only,
   and the slow one. Without it the account is capped at 250 unique recipients
   per 24 hours — *that figure is a secondary source, aggregated from provider
   documentation rather than read from Meta's own verification page, and it is
   the one number in this document that is not first-party.*

Subscribers today: **0** (portfolio model, 2026-09-20). A channel built for a
list of zero is a channel built on a forecast, and that is the strongest
argument in this document against doing it now.

### What it costs — and the shelf's economics inverted on 1 October 2026

Everything below was read from
[Meta's own pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)
on **2026-10-26**. It supersedes the 2026-09-20 reading that Alexandra Systems'
distribution registry carried, which was wrong in three ways by the time
anyone could have acted on it.

- **Service messages are charged, per message, since 2026-10-01.** Meta's
  words: "Effective October 1, 2026 — Meta will charge on a per-message basis
  for all service messages, consistent with how Meta charges for template
  messages. These messages have not been charged since November 1, 2024." A
  non-template reply is a service message, and it is the only way to answer a
  user — non-template messages can only be sent inside an open **24-hour
  customer service window**, which opens and resets with each user message.
- **No card on file means no delivery, not a bill.** "For businesses that does
  not have a payment method on file by September 30, 2026, Meta will stop
  delivering service messages as of when they become charged on October 1,
  2026."
- **The free tier is real and it is the number this proposal rests on:**
  "For each business phone number, Meta provides **1,000 free service messages
  per month**, which do not roll over but reset monthly. Thus, Meta only
  charges as of the 1,001st service message for each business phone number."
  Beyond it, service messages stay free only for eligible governments and
  non-profits through 2027-12-31, which we are not.
- **The free-entry-point window is up to 7 days** and covers marketing,
  utility, authentication and service messages while open — but Meta
  "continues to charge for Meta Business Agent messages," and that category is
  billed on "both token consumption (input and output tokens only) and message
  delivery." **If this integration is registered as a Meta Business Agent, the
  free tier and the free window do not apply to it.** That is a registration
  choice, it is ours to make, and making it carelessly is the most expensive
  mistake available here.
- **Guatemala's region is settled, its rate is not.** Meta has 47 markets on
  the rate card as of 2026-10-01 — 39 countries and 8 regions — and the
  published mapping lists "Rest of Latin America — 15 markets" containing
  "Guatemala (GT) - 502". The per-message rates are published as separate rate
  cards rather than on the page, so **this document states no Guatemala
  figure.** What would settle it: the Rest-of-Latin-America rate card.
- **Twilio**, if used instead of Meta direct: **$0.005 per message** inbound
  or outbound plus Meta's pass-through fees, and a $0.001 failed-message
  processing fee (Twilio's own pricing page, verified 2026-09-20). Twilio buys
  a sandbox and an SDK; it does not remove the Meta verification or the
  service-message charge, because it resells the same platform.

**The inversion, which is the reason this document exists.** The obvious
WhatsApp idea is the digest as a broadcast. That is the expensive shape: one
marketing-category template per subscriber per issue, forever, growing linearly
with the list, in the most expensive and most reportable category Meta sells.
Against Alexandria's stated economics — a ~$0 cost base and a $20/month price —
a recurring per-subscriber-per-week message fee is the first line item that
breaks the argument, and it breaks it on the free tier, where no revenue
offsets it.

The answering shape is the cheap one. A reader asking questions consumes
service messages, and **1,000 per month per number** covers something like a
hundred readers asking ten questions each — an order of magnitude beyond
Alexandria's plausible first-year list. **v1 fits entirely inside the free
tier.** The cost of the answering surface is engineering time, verification,
and a card on file that is never charged; the cost of the broadcast surface is
a per-message bill that scales with success.

Same shelf, opposite economics, and October's change widened the gap rather
than narrowing it. **So the recommendation is the answering surface, inbound
only, and explicitly not the digest broadcast** — and if the digest ever goes
to WhatsApp it should go as a reply inside a thread the reader opened, which
keeps it inside the window the reader's own message opened.

### Dependencies on owner-only actions

Per L-D2 and the company standard, agents prepare and the owner submits; no
seat creates an account, posts, or spends. Three here, and each is an ADR-004
register entry before it happens:

1. **Meta Business verification.** The slow one and the only one with a clock
   that runs independently of every other decision in this document.
2. **A payment method on the Messaging account.** A spend path, even though
   the expected spend inside the free tier is zero.
3. **The Modal workspace decision** — restore or retire. Not WhatsApp-specific,
   but this initiative is strictly downstream of it.

### Why now rather than later — answered honestly, and the answer is "mostly later"

**Later, for the build.** Two of the four preconditions are false, the list is
zero, and the surface the press release describes is a 404 today. Writing the
integration now would produce code whose first integration test cannot pass.

**Now, for exactly one thing: the verification clock.** Meta Business
verification is non-delegable, takes real time, and is a precondition for every
WhatsApp shape — broadcast or answering, Twilio or direct. It does not depend
on the Modal decision, the phone capture, or the subscriber count. **If the
owner wants WhatsApp at all this quarter, starting verification is the only
action that is both useful today and useless to defer.** Everything else in
this document should wait behind the MCP host decision.

**And one thing is now urgent that was not before.** The 2026-10-01 change
means any future WhatsApp reply path needs a card on file to deliver at all.
That is worth knowing before a sprint discovers it, which is the whole purpose
of writing this down.

### What breaks

- **The registration choice.** Register as a Meta Business Agent and the free
  tier and free window stop applying, and billing moves to tokens plus
  delivery. The cost case above does not survive that choice.
- **Answer quality in a chat is less forgiving than in a digest.** A digest
  item that is vague gets skimmed; a vague answer to a direct question gets
  the number blocked. Alexandria's provenance is the mitigation and it only
  works if the "I cannot source this" path is as well built as the answer path.
- **Reports and blocks are a platform-level risk.** Enough of them and Meta
  restricts the number, and the restriction applies to the number rather than
  to the campaign that earned it. This is the second reason to keep marketing
  templates off this number entirely.
- **The free tier is per phone number and resets monthly with no roll-over.**
  A single burst — one popular digest item, one link shared widely — can spend
  a month's tier in a day, and the overage is silent. Whatever gets built needs
  a counter against the 1,000 and a decision about what happens at 900.

### What would change this recommendation

One command and one decision. If
`curl -s https://ap4509--alexandria-mcp-serve.modal.run/mcp` stops returning
`workspace ... is disabled`, precondition 1 is met and this moves from "not
yet" to "the phone capture is the next sprint item." If the owner decides to
retire that server instead, this document should be closed rather than
deferred, because the press release has no product behind it.

---

## Attribution hook

Per the distribution standard, every shelf gets an attribution hook where one
exists. Alexandria's waitlist carries a `source` field, 32 characters maximum
(`site/app/api/waitlist/route.js`), and it is the hook here: a reader who
arrives from WhatsApp and later joins the list should carry `source=whatsapp`.
That is one string, it costs nothing, and without it this shelf reports the
same "no data" that every other shelf on Alexandria's map currently reports.
