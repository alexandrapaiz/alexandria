# Engineer run note, 2026-10-18 (third run, message): measure the buyer's path

Board card `c688ef2e-f0e8-4d14-ab99-60d0f6ff8317`, "Build a way to measure
the buyer's path", handed to this seat by the PM after pull request 339
cleared the install line. The card's own words: "Nothing in the site tracks
visits, installs or payments today, because no analytics of any kind has
been wired in. Without it nobody can tell which skill actually sells."

The PM left the method to this seat, because how a buyer's path is tracked
is an engineering decision. The pull request description is the standup
report; this file is the reasoning, written as the run worked.

## The constraint that decided the design, found before any code

`site/app/privacy/page.jsx` is live and it said, in the owner's own voice:

> There is no analytics, no tracking pixel, no advertising network, and no
> third-party script watching you read.

That sentence is a promise to a reader and it is the first thing any
measurement in this product has to survive. It ruled out three designs that
would otherwise be obvious, and it did so before cost or effort got a say.

- **A third-party analytics service** is out twice over. It breaks the
  sentence, and it needs a new account, which the charter makes a ledger
  proposal rather than an action.
- **A cookie or a `localStorage` id** is out. It is the "watching you read"
  the sentence denies, and in the European Union it needs a consent banner,
  so the cheapest design is also the one that costs the site a dialog.
- **A salted hash of an address and a user agent**, the design most
  cookieless analytics ship, is out too. Plausible publishes its own
  formula, `hash(daily_salt + website_domain + ip_address + user_agent)`,
  with "the salt is rotated and deleted every 24 hours". It is irreversible
  and it is still a pseudonymous identifier for one person, so the sentence
  would have to be softened to accommodate it, and softening it is a cost
  nobody asked this card to pay.

What survived is the strictest version, and it turned out to be the one that
answers the card. **Count events, identify nobody.** A row is a step, a path
and a timestamp, with no address, no user agent, no cookie, no referrer and
no identifier of any kind. The question the card actually asks is which
skill sells, and a count per skill answers that.

A count cannot answer what fraction of one person's visits became a payment,
so this measurement refuses to report a conversion rate rather than
computing one from two different sets of people. That refusal is the
discipline `tools/delivery_health.py` already practises in its own words: a
surface this environment cannot answer reads `unknown`, never green and
never red.

The privacy page changed anyway, because a page view counted is a page view
collected however little it holds. The sentence kept its promise and gained
the precision to stay true, and the date moved with it.

## The five steps, and the one that cannot be measured from here

| Step | Evidence | State |
| --- | --- | --- |
| a visit | the request, recorded in `site/middleware.js` | measurable today |
| the catalogue | the request to `/skills` | measurable today |
| one skill read | which skill was opened | measurable today |
| an install | GitHub's clone traffic | **unmeasured**, one permission away |
| checkout started | the `/api/checkout/[plan]` hop, which already existed | measurable today |
| a payment | `users.subscription_status`, written by the Polar webhook | measurable today, dormant until the owner creates the Polar account |

The install is the interesting one. `/plugin marketplace add
alexandrapaiz/alexandria` is a git clone from the buyer's terminal straight
to GitHub, so it never touches this site and no instrumentation here can
see it. The only observer is GitHub's own traffic API, and this seat's token
cannot read it:

```
gh api repos/alexandrapaiz/alexandria/traffic/clones
  -> 403 Resource not accessible by personal access token
```

So the step reports `unmeasured` with that reason attached, rather than a
guess or a zero. `tools/buyer_path.py` attempts the call on every run, so it
fills itself in the day the permission exists and no code changes for it.

## Shape

The same two-file seam the rest of this site uses, and the same split
`/api/delivery` established: the site publishes facts over a credential-free
surface, and the verdict lives in one Python copy, because no agent seat
holds `DATABASE_URL`.

- `db/schema.sql` gained `path_events` and `buyer_path_daily`.
- `site/lib/path-core.js` is every decision, pure and import-free.
- `site/lib/path.js` is the I/O, plus the `PATH_MEASUREMENT=off` switch.
- `site/middleware.js` records the step after the response, under `waitUntil`.
- `site/app/api/funnel/route.js` publishes counts, facts and never verdicts.
- `tools/buyer_path.py` is the reader, the judgement and the exit code.
- `docs/product/buyer-path.md` is the page a reader of the numbers needs.

## What the run found that it was not looking for

**A defect in its own code, caught by its own test.** `isCounted` read the
last path segment for a dot to recognise an asset, and a query string lives
in the last segment, so `/pricing?email=ada@example.com` was refused as an
asset. Middleware passes `nextUrl.pathname`, which carries no query, so the
defect was invisible from the only caller this change has and live for every
other. Normalising before the asset test is the fix and the comment says why.

**The charter's machinery-diff gate reads clean on a shallow clone.** Filed
as `INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone`, as a
repeat of the shallow-clone class that
`INC-2026-09-24-shallow-clone-merge-base-repeat` already holds. Worse than
that occurrence rather than the same, because a missing merge base fails
loudly and this fails in the direction of a pass. Unshallowing revealed two
runtime commits the gate could not see, one of them the removal of every
seat's `schedule:` block.

**The middleware grew.** 91.5 kB to 136 kB, because the Neon client is now
in the edge bundle. Well inside the platform's limit and the cheaper of the
two options: the alternative, posting from middleware to an internal route,
doubles the metered unit that HQ incident 5 is about.

## Status

Done. The pull request carries the evidence.
