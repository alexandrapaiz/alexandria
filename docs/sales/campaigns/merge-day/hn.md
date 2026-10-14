# Hacker News — Merge Day (Show HN, 2026-10-13)

Drafted 2026-10-05 under Shape B of `../../launch-gate.md` §6. Every number
has a command beside it in that file or in `../../claim-ledger.md`. Not
posted, not scheduled.

## Venue read

Hacker News will not reward a launch with nothing to buy, and it will reward
a document it can open and argue with. The submission therefore does not
lead on the product. It leads on the register, which is the one artifact
here that nobody else in this category has and that cannot be assembled
retroactively.

The thread's first hostile comment is predictable and it is the same one the
skill-marketplace Show HN took on 2026-09-17: why would I pay for this. The
post answers it by saying the thing is not for sale yet, which removes the
objection entirely and is the one advantage Shape B has over Shape A.

The second hostile comment is "another agent-swarm post". The defence is not
rhetoric. It is that this post's central number is an embarrassing one, and
that readers can run the command themselves in the time it takes to write
the comment.

## Title

Pick one. The first is the stronger submission and the second is the safer
one. Both are plain ASCII and neither has a colon.

```
Show HN: Our AI-run company's failure register cannot count its own failures
```

```
Show HN: Twelve agents, one human who merges, and the whole record in public
```

## The post

```
I run a one-person company where most of the work is done by twelve agents,
each with a written charter in the repo, each opening its own pull requests.
I merge. Nothing gets sent, posted or paid without me, and the charters say
so in the files you can read.

The product is a weekly digest of AI research that carries the evidence under
each finding, and a library of skill files those findings become. The digest
is free and arrives in full. The library costs $20 a month and is not open
yet, which is why this is not a sales post.

What I am submitting is the record. Three paths, in the order I would read
them.

prompts/ is the twelve charters. The sales agent's charter is the one to open
first, because it forbids that agent from contacting anyone, and it drafted
the post you are reading.

docs/agents/incidents.md is eighty entries of things that went wrong, written
by the agents that caused them. The best one is about the register itself.
Twenty-six of the entries are numbered, and those twenty-six numbers resolve
to fourteen distinct ones, because a counter in a file is not an allocator
when every agent writes on its own branch and none of them can see each
other. Incidents 24, 25 and 26 each exist three times.

  grep -cE '^## Incident [0-9]+' docs/agents/incidents.md
  grep -oE '^## Incident [0-9]+' docs/agents/incidents.md | sort -u | wc -l

The collision has its own entry, written by the seat that caused it, and the
fix it prescribes is the date-and-subject identifier the newer fifty-four
entries use.

docs/decisions.md is forty-three dated decisions with the reversed ones left
in, including the week the pricing changed and the week a launch-blocking
payment choice had to be remade because Stripe does not operate in the
country I live in.

Three things I would rather you hear from me than find. The archive holds one
issue, because the pilot before it was pulled for not being good enough to be
the first thing a stranger reads. Six skills are live and one of them carries
a recorded trial showing that loading it changed what the model recommended,
so that result is an anecdote and not yet a practice. And the register cannot
tell you which of its own incidents are open, because most entries carry no
status line, which is written down in the company standards file as a lesson
rather than fixed.

If you find something wrong in any of it, I will register it with your handle
on the entry.

github.com/alexandrapaiz/alexandria
[SITE_URL]
```

## The comments that are coming, and the answers

**"So an AI runs your company."**

```
Agents draft and I decide. Nothing is published, nothing is sent and no money
moves without me. What is automated is the checkable part, which is the
reading, the drafting and the proposing.
```

**"Why is there nothing to buy?"**

```
Because the checkout is not built. The digest is free and that part works. I
would rather launch the record on the day I said I would than open a cart I
have to apologise for a week later.
```

**"Eighty incidents in three weeks is a lot."**

```
It is, and most of them are small. The alternative was eighty incidents and
no register, which is the same three weeks with less learned from it.
```

**"Sixty-four open pull requests means nothing ships."**

```
It means twelve agents produce faster than one person reviews, which is a
real problem and the one I am working on. The queue is public, so you can
watch whether that number goes down.
```

**"A record that grades itself is not independent."**

```
Correct, and it is the fair objection. Every finding cites papers you can
open, so the grading is checkable even though the grader is not
disinterested. Outside verification is a thing this does not have yet.
```

## Rules for this post specifically

- Post the title and the paths. Do not post a feature list.
- The register's numbering defect stays in the body and does not get softened
  on the morning of the send. It is the reason the post works.
- No queue number unless the sentence also explains it.
- Plain ASCII throughout, including in replies written in the thread.
- No reply argues with a critic who is correct. Concede and link.
