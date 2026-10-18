# Engineer run note, 2026-10-18 (fourth run): the sale that could not happen

## What I took

A handoff from the PM, delivered on the board's message bus at 01:54 UTC. Its
half-sentence of scope: one more surface on the delivery health tool that
fetches the public pricing page, asserts at least one checkout link is present
and that it answers when followed, and fails otherwise. Sized as a morning
rather than a project. Built, and it is stricter than the ask in one named way.

The handoff came out of an outside advisor reading our own pricing page the way
a stranger would. Both paid tiers rendered the words "Opens shortly" with no
link behind either one, five days past the date the company committed to being
able to take a payment, and nothing inside either repository had said so.

## What I verified myself before writing anything

Against the deployed site, by unauthenticated request, on 2026-10-18:

- `/pricing` answers HTTP 200.
- It carries no `/api/checkout/` href anywhere in its markup.
- Two `pill ghost` spans with no `href` are what the paid tiers render instead.
- `/api/checkout/monthly` answers 303 to
  `/sign-up?redirect_url=%2Fapi%2Fcheckout%2Fmonthly`.
- `/api/checkout/nonsense` answers 303 to `/pricing`.

The fourth of those is the fact that decided the design, and it is the one a
reader is most likely to get wrong.

## The design, in one paragraph

Two assertions in a fixed order. The page has to render at least one checkout
link, and then every link it renders has to open when followed. The order is
load-bearing rather than stylistic, because the checkout route asks a stranger
for an account **before** it looks up the checkout link, so an anonymous probe
of the route gets the same 303 to the sign-up page whether the offer is
configured or not. A probe built on the route alone is green on the exact
morning both tiers were unbuyable. The rendered href is the only evidence from
outside that the variable behind it is set. So the page is the artifact and the
route is the follow-up, never the other way round, and that argument is a test
rather than a comment.

## Where I went past the ask, and why

The handoff asked for at least one link present and answering. The surface
fails instead whenever any offer in `OFFERS` has no link on the page, which is
the same rule applied per offer rather than once. `OFFERS` is also what renders
the tiers, so an offer the owner stops selling leaves that list and stops being
expected here, while an offer that stays on the page and cannot be bought is
exactly the thing being watched. One tier opening while the other two stay shut
would otherwise read green.

## What it cannot do, stated rather than discovered later

It cannot tell whether a configured URL is a live product at the seller. That
needs a session, so the anonymous probe stops at the sign-up page and never
learns where it would have gone. The next rung is in the ledger today: the site
holds the three variables, so the site is the only party that can ask the
seller, and the delivery receipt is where it would publish the answer.

## What I did not do

I did not create the payment account and I did not set any variable. The check
fails honestly today and will keep failing until the owner acts, which is the
point of it existing. A check that went green when nothing was fixed would be
worse than no check.

## Two repeats filed

Both in `docs/agents/incidents.md` in this pull request, because the standing
rule at the top of that file is that a repeat is recorded at the moment it
repeats.

The till having no outside observer is incident 24's shape on the one surface
that takes money. The general finding there is the part worth keeping: every
row on that register was added after its surface failed, so the cheap
predictive question nobody has asked of it is to list what a stranger can do
with this product and check that each one has a surface.

The second is that this run was told to read its inbox on the board and the
board client in this repository has no command that can see a message. I found
the bus by probing the API until a path answered. That is the no-reader
incident of 2026-09-28 with a different noun.
