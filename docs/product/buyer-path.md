# Measuring the buyer's path

What this product knows about how a buyer reaches it, how to read that, and
the two things it cannot see. Board card `c688ef2e`.

Read the numbers with one command:

```
python3 tools/buyer_path.py
python3 tools/buyer_path.py --json --days 30
python3 tools/buyer_path.py --surface install
```

It needs no credential, because the counts arrive from
`https://libraryofalexandria.dev/api/funnel`, which the site publishes from
its own environment. That is the same arrangement `/api/delivery` and
`tools/delivery_health.py` already use, and it exists for the same reason: no
agent seat holds `DATABASE_URL`, so a measurement only the owner's laptop can
read is a measurement no seat can report.

## What is recorded, and what is refused

One row per page a visitor opens. The row holds which step of the path it
was, which route, one bounded detail on the two steps that need it, and when.

That is the whole row. There is no address in it, no user agent, no cookie,
no session, no referrer and no identifier of any kind.

The refusal is the design and not an economy. `site/app/privacy/page.jsx`
promises a reader that there is no third-party script watching them read, and
that sentence is a promise to a person rather than a preference about
tooling. Three designs were ruled out by it before cost was considered: a
third-party service, a cookie, and the salted irreversible hash of an address
and a user agent that most cookieless analytics ship. The third is the one
worth naming, because it is the industry default and it is still a
pseudonymous identifier for one person.

What the refusal costs is a conversion rate. Two steps counted here are two
counts of events and not two counts of the same people, so a ratio of them
would read like a rate and mean nothing. `tools/buyer_path.py` reports the
counts and the biggest drop between two of them, and refuses the ratio in the
field a script reads rather than leaving a reader to work out why there isn't
one.

What the refusal buys is worth more than the rate at this stage. The counts
answer the question the card was written for, which is which skill anybody
actually opens. No consent dialog is needed, because there is nothing to
consent to. And the privacy page stays true, which is the asset this audience
is hardest to sell twice.

## The seven steps

| Step | What it means | Where it comes from |
| --- | --- | --- |
| `visit` | arrived anywhere on the site | `path_events` |
| `catalog` | opened the skill catalogue | `path_events` |
| `skill` | opened one skill, and which one | `path_events` |
| `install` | cloned the repository, which is what installing is | GitHub, and **unreadable today** |
| `pricing` | opened the pricing page | `path_events` |
| `checkout` | started a checkout, and which plan | `path_events` |
| `payment` | has an account that is paying | `users.subscription_status` |

The payment is not a row in `path_events` on purpose. The Polar webhook
already writes it onto the billing record (`site/lib/polar.js`), and a second
copy of that number could only ever agree with the first by luck.

## The install, which cannot be measured from here

`/plugin marketplace add alexandrapaiz/alexandria` is a git clone from the
buyer's terminal straight to GitHub. It never touches this site, so no
instrumentation here can see it, and that is a fact about the distribution
choice rather than a gap in the build.

GitHub's own traffic API is the only observer, and no token this org holds
can read it:

```
gh api repos/alexandrapaiz/alexandria/traffic/clones
  -> 403 Resource not accessible by personal access token
```

**What would clear it, in one line.** The traffic endpoints need
`administration: read` on a fine-grained token, or the `repo` scope on a
classic one. `tools/buyer_path.py` attempts the call on every run, so the
step fills itself in the day a token with that permission is in the
environment as `GH_TOKEN` or `GITHUB_TOKEN`, and nothing in this repository
has to change for it.

Two things to know before granting it. The window is GitHub's own fourteen
days and is not configurable, so the install count never lines up exactly
with the steps around it, and the report labels it with its own window rather
than pretending it matches. And a clone is an upper bound on installs rather
than a count of them, because a developer reading the repository clones it
too. It is still the only observation available, and an upper bound that
moves is worth more than a blank.

## The four states, and the two that are not failures

`ok`, `failing`, `unknown`, `idle`, and the exit code separates them so a
caller does not have to read prose:

```
0   every surface is ok or idle
1   at least one surface is failing
2   nothing is failing, and at least one surface could not be answered
```

`idle` is this file's own addition to the ladder
`tools/delivery_health.py` set, and it is the state that keeps the report
readable before launch. It means the instrument was proved to be working and
had nothing to measure. An empty table alone does not earn it: when the
recorder cannot be proved to work, the answer is `unknown`, because a quiet
week and a dead recorder are the same zeros and very different facts.

That distinction is the whole value of the tool. A quiet week reported as a
failure teaches the reader to stop reading. A dead recorder reported as a
quiet week is a month of zeros nobody questions, and the day the owner finally
asks which skill sells the answer is that nothing was ever recorded.

## Turning it off

One variable in the site's environment, no deploy and no revert:

```
PATH_MEASUREMENT=off
```

It exists because the judgement under this design is the owner's rather than
an engineer's. The reading built on is that a row holding a page and a time,
with no identifier, is not personal data, so the privacy page can describe it
honestly and nobody's consent is needed. That reading may be wrong, or she may
simply want the count off while she decides.

`/api/funnel` publishes the switch, so a reader with no access to that
environment sees a stopped recorder rather than a quiet week.

## What the owner has to do, and in what order

1. **Apply the schema.** `path_events` ships in `db/schema.sql` and nothing
   records until the table exists: `modal run pipeline/db_setup.py::apply_schema`.
   Until then `/api/funnel` answers 503 with that reason in it and
   `tools/buyer_path.py` reads `failing`, which is correct and is the one
   state a deploy can leave behind.
2. **Nothing else, for the counts.** `DATABASE_URL` is already in the site's
   environment. There is no new secret, no new service and no new account.
3. **Optionally, grant the traffic permission** described above, which is the
   only thing between this report and an install count.
4. **Optionally, mention it in an issue.** The privacy page's own last section
   says a change that matters is told to subscribers before it takes effect.
   This change collects nothing personal, so nothing here is owed under that
   clause, and saying it anyway is cheap and is the kind of thing this
   audience notices.

## What this does not measure, said once rather than discovered later

- **Where a visitor came from.** No referrer is stored, because a referrer
  carries a query string and a query string is where an address ends up by
  accident. Which writing brings people in is therefore still answerable only
  for signups, which `subscribers.source` already records.
- **One person's journey.** By construction. See the refusal above.
- **The digest.** No open or click is recorded anywhere, and a pixel in an
  email is the one thing the privacy page's "no tracking pixel" names
  outright.
- **The skill files themselves.** A skill installed is a markdown file on
  somebody's disk. Nothing phones home from it and nothing should.
