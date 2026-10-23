# The archive's masthead line, for the frontend seat to set

**Writer seat, 2026-10-23. One candidate for one line, which is the job.
`site/` is the frontend seat's surface, so this file is the words and their
diff is the setting.**

## The line, and where it is

`site/content/issues/2026-W39.md`, line 3. It is the live public text of the
one week the archive publishes, because `site/lib/issues-core.js` says "the
record decides which weeks exist, the committed file decides the text of any
week that has one."

Now:

```
*The latest in AI research, read in full and distilled weekly: what's new,
what's gaining acceptance, and what newer evidence has overturned.*
```

Set to:

```
*What's new in AI research, what's gaining acceptance, and what newer evidence
has overturned.*
```

That is not a new candidate. It is `MASTHEAD` in `pipeline/weekly.py`,
verbatim, which is the string the owner's repair already put on every issue
the press writes from now on. This sets the one issue it could not reach.

## Why the change is a law and not a preference

Canon law 15 is her ruling of 2026-09-25, and it cites this exact string as
its own evidence.

> The masthead said "read in full and distilled weekly" on every issue ever
> sent, against 166 full reads out of 8,956 papers held.

Every paper in the corpus arrives as a title and an abstract. A much smaller
number have had their full text read. The masthead gives the arriving number
the reading number's verb, which is false about the product, and the law says
the repair is to drop the claim and never to soften it. Read, reviewed, read
at some depth, surveyed and processed are all the same false sentence in a
coat, which is ban list 50.

`docs/voice/taste.md` verdict 6 is the same ruling in her shortest form:
never "read" for ingested.

## Two things this is not

- **Not a rewrite.** Nothing in the issue's body changes. One line, replaced
  by a line that already exists in this repository and already prints on every
  future issue.
- **Not a correction to an issue's claims.** It is furniture. The masthead is
  not something the writing model chose, so no grade of 2026-W39's prose
  reaches it and none ever did, which is ban list 61.

## Checking it

```
$ python3 -I docs/voice/check_voice.py reading
```

Before this run that command read 61 surfaces and never opened the archive.
It now reads 63 and reports the line. After the line is set, the archive rows
go and the four open failures on `site/app/` remain, which are
`docs/voice/home-metric-line-2026-09-26.md` and the llms.txt repairs, both
drafted and both still waiting.

## The claims gate, per the charter's step 1b

This candidate makes no claim about our artifact. It removes one. So there is
no row in `docs/agents/quality-claims.md` to hold it against, and none is
needed: the sentence that needed a mechanism is the one coming out.
