# Opening the till: the Polar checklist

The payments integration is built and merged. Nothing in it can take a
payment yet, because Polar is an account that does not exist, and creating
it is a decision with the owner's name on it rather than a seat's (ADR-30,
ADR-31). This file is what stands between the code and a live sale, in the
order it has to happen, and it is written for one person with a browser.

Nothing below is a code change. The site reads all four values out of its
environment, so the three products can be created, renamed or repriced in
Polar's dashboard and the pages follow with no commit and no pull request.
Vercel applies a changed environment variable on the next deployment, so
each step below ends with a redeploy of the same code rather than a new
version of it.

## Before you start

Two things Polar needs and no processor can assume, both already written:
`/privacy` and `/terms`, live on the site since 2026-09-19. Polar is the
Merchant of Record, so it registers and files the tax wherever the buyer
is, and the one tax that stays yours is Guatemalan income tax on what Polar
pays out.

Payout was verified on 2026-09-19 as reaching Guatemala through Stripe
Connect Express. The fee is roughly 4% plus 40 cents and it is contingent
on revenue, so this whole checklist costs $0 until somebody pays.

## 1. The account, and sandbox first

Create the organization at **sandbox.polar.sh**, not at polar.sh. The
sandbox is a separate instance with its own products, its own secrets and
test cards, and it exists so the first real sale is not also the first
test. Everything below is done twice, once in each, and the second time
takes five minutes because you have done it.

## 2. The three products

ADR-31's plan shape, and the names are the ones the pricing page already
prints:

| Product | Price | Recurring | Trial |
| --- | --- | --- | --- |
| Full access | $20 | monthly | 3 days |
| Full access, no trial | $20 | monthly | none |
| Lifetime | $200 | one time | none |

Two monthly products rather than one, because the trial is a property of
the product in Polar and the pricing page offers both doors. A reader who
wants the three free days takes the first. A reader who would rather just
pay takes the second.

The lifetime product must be **one time**, not recurring. That flag is
what the webhook reads to tell a $200 purchase from a monthly charge
(`product.is_recurring`), and a lifetime product created as a subscription
would be granted as a month.

## 3. A checkout link for each

Create a checkout link per product and copy the URL. Three links, three
environment variables, set in Vercel:

```
POLAR_CHECKOUT_TRIAL=https://buy.polar.sh/...
POLAR_CHECKOUT_MONTHLY=https://buy.polar.sh/...
POLAR_CHECKOUT_LIFETIME=https://buy.polar.sh/...
```

Until a variable is set, that offer appears on `/pricing` with its price
and the words "Opens shortly" instead of a button. So you can set them one
at a time and nothing on the page is ever a link to nowhere.

## 4. The webhook

Add an endpoint in the dashboard:

- **URL**: `https://libraryofalexandria.dev/api/polar-webhook`
- **Format**: raw
- **Events**: every `subscription.*` event, plus `order.paid` and
  `order.refunded`. Subscribing to more is harmless, since the endpoint
  acknowledges what it does not handle rather than failing it.

Copy the signing secret into the environment as:

```
POLAR_WEBHOOK_SECRET=...
```

That is the last variable. With it set, a payment becomes access with no
step in between.

One note for whoever reads the code next. Polar's secrets created on or
after 2026-09-08 follow the Standard Webhooks specification and older ones
use a scheme that predates it. The verifier implements the new one only,
which is safe because this account will be created after that date, and it
is in `site/lib/polar-core.js` beside the comment that says so.

## 5. The test, in the sandbox, before any of this is live

Buy your own product with Polar's test card, then check three things in
order:

1. Polar's dashboard shows the delivery to `/api/polar-webhook` with a
   `200`. A `401` means the secret does not match. A `503` means the
   endpoint is working and the `users` row has not arrived yet, which
   Polar retries on its own.
2. Your Clerk user carries `publicMetadata.hasSpine: true`, with
   `spineTier` and `spineUntil` beside it.
3. `select subscription_status, polar_customer_id from users where email =
   '...'` shows `active` and the Polar customer id.

Then cancel it and watch the same three go the other way.

## What is deliberately not automated

**A buyer with no account.** The checkout route asks for a Clerk account
before it sends anybody to Polar, so this only happens to someone who
found a Polar link somewhere other than this site. The webhook logs
`no Clerk account for this buyer` and acknowledges the event, because no
number of retries conjures an account. If you see that line, invite them
and the next event grants it.

**Two accounts on one address.** The email match refuses rather than
guessing, and logs `email is ambiguous`. Granting paid access to the wrong
one of two people is the one failure here that cannot be taken back
quietly.

**A status Polar adds later.** The verifier knows Polar's eight
subscription statuses as of 2026-10-13. A ninth closes the door and logs
`carried an unknown status`, which is the safe direction and is meant to be
noticed. Adding it is two lines in `site/lib/polar-core.js`.
