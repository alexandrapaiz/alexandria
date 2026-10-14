# Reading enjoyability, the opening and the first section two ways

Commissioned by the owner through the chair's handoff of 2026-10-05:
reading enjoyability is urgent and the prose is not nailed down, because a
correct newsletter nobody enjoys does not keep a reader.

**What this page is, and what it is not.** The commission had three parts. The
third, the bar in `prompts/digest.md`, landed on 2026-10-05 and was extended
on 2026-10-06, so it is in the generator rather than on this page. The second
is below, and it is the part the owner asked to read and rule on. The first,
a study of how TLDR AI, Import AI, The Batch and Morning Brew actually write,
is **not here**, and saying so is better than a page that implies it is. The
nearest thing the company holds is the market seat's ranking of 2026-09-24
(`docs/market/briefs/2026-09-24-b.md`), which put Latent Space, Interconnects
and Ahead of AI above alexandria on enjoyability and alexandria first on
rigor, with the finding "this is a formatting and craft gap, not a substance
gap". `docs/market/newsletter-prose-guide.md` is the page that was supposed to
hold the study. It has read "Work in progress, populating from primary sources
now" since 2026-09-19, which is seventeen days, and it belongs to the market
seat rather than to this one.

**A warning that rides with every page like this one, and it is not optional.**
Canon law 14 carries two worked examples and a rule about them: no sentence
from one is ever copied into `prompts/digest.md`, into an issue, or onto the
site. The reason is on the record. A sentence from the first of those examples
reached subscribers through a person reading the file and setting a page, not
through the pipeline. The same holds for every line below. This page exists so
the owner can compare two versions of one morning's issue and say which one she
would forward. It is evidence, not supply.

## The subject

The opening and the first section of the issue sent on 2026-10-05, read from
the stored `digests` row, id 21, week 2026-W40, written by prompt sha
`c48d09624161`.

Measured on that artifact with `python3 docs/voice/check_voice.py measure`:
1,350 words, 26 blocks, longest block 140 words, 4 blocks over 100 words, zero
em dashes, eight semicolons, **two kinds of block on the whole page**, three
links. The two kinds are paragraphs and lines standing alone, and three of the
four lines standing alone are the masthead, the horizontal rule and the close,
which arrive on every issue whatever the model writes. No bulleted list and no
third-level heading anywhere in it, for the tenth issue running.

## As sent

> # Reward-free search and kernel-level kill switches redraw the agent stack
>
> You ship agents that improve themselves or you ship agents that stay safe,
> and until this week those two pipelines barely spoke. Today they are the same
> conversation. Three labs showed that an agent can edit its own harness for
> four dollars, that a POSIX signal can stop a rogue run in five microseconds,
> and that the memory you write into weights may be the memory you lose. The
> thread is control: who decides what an agent keeps, who can stop it, and what
> "better" means when the evaluator is the agent itself.
>
> ## What is gaining ground: recursive self-improvement with fewer guardrails
>
> The field has been treating self-improving agents as expensive,
> reward-hungry systems that need external scoring to know which version to
> keep. That picture is cracking. Two independent streams of evidence now show
> that agents can improve their own harnesses without a reward model at all,
> and that the harnesses they discover transfer to other models.
>
> A team led by Jungwoo Yang at Seoul National University reports that their
> SelfSearch system improves population-mean task success across six
> model-benchmark pairs, with individual agents gaining up to 11.2 percentage
> points on Terminal-Bench 2.1. The mechanism is spare: the agent gets
> read-only episode records from its own previous self-modification attempts,
> proposes edits to its implementation, and keeps the successor if it verifies.
> No external reward function scores the result. The search cost for a harness
> that hits 82.0% on Terminal-Bench 2.1 with DeepSeek V4 Flash was **$4.03**,
> matching the top-scoring Codex harness in a public comparison of nine. The
> authors' own experiments, not yet replicated outside the group.
>
> That finding is now tied to older work on recursive self-improvement through
> a direct update. The claim that RSIAgent yields measurable gains over a
> non-recursive baseline, which had accumulated six independent supports, is
> superseded this week by RRSI's regularized variant, which improves
> in-distribution performance by up to 14.1 points while using 30% fewer policy
> tokens. The field is not merely accepting recursive improvement; it is making
> it cheaper and more stable.
>
> The citation pattern on the earlier distillation work also shifted.
> Rethinking On-Policy Distillation II, which argued that one training example
> suffices, moved from 2 to 4 citations as a newer paper showed that 0.1% of
> tokens can match full-token performance. The claim itself is now refined, not
> merely cited.

## Rewritten

Same morning, same papers, same numbers. Nothing invented and nothing dropped
except the two things named under it.

> # An agent rewrote its own instructions for four dollars
>
> If you run agents, the instructions wrapped around the model are yours to
> write and yours to keep rewriting. This week a team let the agent do it.
>
> That wrapper has a name, the harness, and it is the prompts, the retry rules
> and the checks a team puts around a model to keep it on task. Rewriting it is
> normally slow, and the usual way to know whether a rewrite helped is to score
> it with a second model.
>
> ## An agent that improves itself needs nothing scoring it
>
> Jungwoo Yang's group at Seoul National University gave an agent read-only
> records of its own earlier attempts to rewrite itself, let it propose the next
> edit, and kept the new version whenever it verified. Nothing scored it. There
> was no second model and no reward signal of any kind.
>
> **The best harness it found cost $4.03 to search for.**
>
> That harness reaches 82.0% on Terminal-Bench 2.1 running DeepSeek V4 Flash,
> which is level with the strongest hand-built Codex harness in a public
> comparison of nine. Individual agents gained up to 11.2 points, and mean task
> success rose across all six model-benchmark pairs the team ran. This is the
> group's own work and nobody outside it has repeated the result.
>
> What it changes for a builder is who does the tuning. A harness has been a
> thing a person maintains. For four dollars it is a thing you can let run.
>
> ### The same week, a cheaper way to keep the gains
>
> Agents that rewrite themselves tend to drift, getting better on the tasks in
> front of them and worse everywhere else. A regularized version called RRSI
> holds that drift down.
>
> - **It gains up to 14.1 points** on the tasks it was tuned for.
> - **It spends 30% fewer tokens** getting there.
>
> The older RSIAgent result that six separate papers had been building on is
> the one it replaces, which is the first time anything in this line has been
> superseded rather than extended.
>
> ### Training on a tenth of a percent of the data
>
> The standing advice for teaching a small model from a large one is to feed it
> everything the large model produced. A new paper trains on **0.1% of those
> tokens** and matches the full-token result.
>
> If that holds, the cost of distilling a model is not the cost of the data. It
> is the cost of picking which thousandth of it to use.

## What changed, and why each change is a rule rather than a preference

- **Two things were dropped and neither was a finding.** The sentence "The
  field is not merely accepting recursive improvement, it is making it cheaper
  and more stable" is the issue telling the reader what to conclude, and canon
  law 7 gives that job to the contents. And the citation count is gone from the
  text while the paper it pointed at stayed: "moved from 2 to 4 citations" is
  our own bookkeeping, and the finding was the clause hanging off it. That is
  ban list 97 and it is now in the generator.
- **The title names what happened to somebody.** "Reward-free search and
  kernel-level kill switches redraw the agent stack" has three terms of art in
  one line, in the one place a stranger decides whether the issue is for them.
- **The load-bearing noun gets its clause at first use.** "Harness" appears
  eight times in the issue as sent and is never defined once. Canon law 12a and
  the owner's ruling of 2026-09-19 both say the intro carries the strictest
  on-ramp duty there is.
- **Four kinds of block instead of one.** Paragraphs, a line standing by
  itself, a bulleted list where two results are genuinely parallel, and two
  third-level headings written from the day's own material. Canon law 14 names
  the shape count as the measurement that four other counts can pass while it
  fails, and it is the count that has not moved in ten issues.
- **The number that matters stands on its own line.** $4.03 is the fact a
  builder repeats to someone else, and in the version as sent it is the eighth
  thing in a 109-word block.
- **Every result is followed by a line with no number in it.** Who does the
  tuning now. What the cost of distillation actually is. Canon law 14's sixth
  rule asks for that line and the issue as sent spends the slot on its evidence
  grade instead, in seven items out of seven, measured on this same artifact by
  the review of 2026-10-05.
- **Zero semicolons.** The version as sent has eight across the issue, all of
  them two finished sentences in a balanced contrast, which canon law 1 names
  outright.

## The one thing the owner is asked to rule on

Which of the two would she forward to another builder. If the answer is the
second, the devices above stop being available and become the shape of every
issue, and the next grade scores an issue that has none of them as a failure
rather than as a note. If the answer is that neither is there yet, the useful
thing to say is which sentence in the second one is wrong, because this seat
has nine grades of evidence about what the generator does and almost none about
what she would actually send to a friend.
