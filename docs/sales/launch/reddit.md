# Reddit — subreddit drafts (launch day, 2026-10-13)

Rewritten 2026-09-30. The 2026-09-18 version said one skill was live, and it
used em dashes and a middle-dot separator inside the post bodies, which are
banned characters in reader-facing copy. Numbers verified against
`../claim-ledger.md`.

## Venue read, and the one thing this file cannot do for her

Self-promotion tolerance is specific to each subreddit and changes without
notice, and this seat cannot verify a current rule or a required flair. **Read
each subreddit's current self-promotion rule and flair requirement immediately
before posting.** Do not take it from this file.

Post a day apart rather than all at once, so that one removal does not cost the
whole set. Three subreddits, chosen for audience fit rather than size.

A Reddit post that reads as a press release gets removed by a human moderator
who has seen a thousand of them. Every draft below is written as a builder
describing what they measured, because that is the only register this venue
does not reject on sight, and it also happens to be the truth.

## r/ClaudeAI

Fit: this audience already writes and loads skill files, so the trigger
reliability number is a problem they have personally had.

```
Title: I measured whether my six Claude skills actually get picked, and
published the three that failed

An audit of 216 public Claude Code skills reported last month that 69 percent
of them would not reliably trigger, and that matched my own experience of
writing skills and then watching the model ignore them.

So I built a trigger test for my own library. Six skills, 43 cases, eight decoy
skills to catch false positives, and the scoring rule written down before the
run rather than after it. Positives are cases where a skill should fire,
negatives are cases where every skill should stay quiet, and confusion cases are
where two skills are plausible and only one is right.

Result was 40 of 43, reliability 0.93 with a 95 percent interval from 0.81 to
0.99. The three failures are in the output with their prompts and their scores,
which is the part I actually want feedback on. Two were negatives where a skill
fired on a question about serving and GPU memory that no skill should have
touched, and one was a confusion case where the wrong one of two related skills
won.

The test and the results are in the repo under skills/_validation/. I am not
claiming my number beats the 69 percent audit, because the two were not
measured with the same instrument and pretending otherwise would be the kind of
thing this whole exercise is against.

github.com/alexandrapaiz/alexandria
```

## r/AI_Agents

Fit: people who evaluate orchestration claims for a living and are the audience
for the record of what stopped being true.

```
Title: A record of which agent-research claims later got contradicted, rather
than another list of new papers

The thing that has cost me the most time building agents is not missing a new
technique. It is continuing to rely on one that quietly stopped being the right
answer several months ago, because the post that recommended it is still the
top result and nothing ever goes back to correct it.

So the project I have been running keeps the correction instead of the summary.
Findings from papers get recorded as individual claims, and when later work
supports or contradicts one, that becomes an edge rather than a new post. What
it is for is answering how solid a finding is before you build on it.

Six skill files come out of it so far, one per subject area, and each one lists
the papers behind it with links to the full text. A trigger test on 2026-09-29
scored 40 of 43 on whether the right file gets picked and the wrong ones stay
quiet, with the failures published.

Happy to be told the record is too thin to be useful yet. It reads a lot of
research and has read a much smaller amount of it in full, and I would rather
hear that objection than have it politely not raised.

github.com/alexandrapaiz/alexandria
```

## r/SideProject

Fit: builders who will find the agent-run organisation interesting on its own
terms, and who are the most forgiving audience for a thin product honestly
described.

```
Title: My side project is run by about a dozen AI agents with written job
descriptions, and every one of their failures is public

Alexandria reads AI research and turns the findings that hold up into skill
files an agent can load. That is the product. The part people usually ask about
is how it is built.

There are around a dozen agents, each with a written charter in the repository
that says what it owns and what it is not allowed to do. Each one opens pull
requests and I merge them or I do not. On one morning last week there were
sixteen open at the same time.

The part I did not expect to be the most interesting is the failure register.
When one of them breaks something, the fix includes writing down what happened,
numbered and dated, and that file is now the longest document in the project. It
is public. This post was drafted by the agent whose charter says it prepares and
I send, and it has never posted anything anywhere.

Where it actually is: six skills live, one issue in the archive, and
subscriptions opening today. The digest is free and the library is $20 a month.

github.com/alexandrapaiz/alexandria
```

## Never in any of these

No subscriber count and nothing that implies one. No claim that our trigger
number beats the published audit's number. No paper count with the verb "read"
attached unless it is the full-read count beside the arriving count. No cropped
screenshot of a result with the failures cut out of it. Plain ASCII throughout,
including the separator between two links, which is a comma or a new line and
never a middle dot.

## If the checkout has not landed by 2026-10-12 (Shape B)

Checked against `../launch-gate.md` §1. "Subscriptions opening today" is the
line that fails, and on these subs a dead-end click is also a rule problem,
because several of them forbid promotion of a thing that is not available.

The repair, in the where-it-actually-is paragraph:

```
Where it actually is: six skills live, one issue in the archive, and no
checkout yet. The digest is free and arrives in full. The library is $20 a
month and is not open, so there is nothing to buy today.
```

A post that says there is nothing to buy is the most self-promotion-rule-safe
version of this post that exists, which is an accident worth taking.
