### 2026-11-09 - A drift card keyed on the running sha is orphaned the moment the running sha changes

- Trigger: `tools/drift_watch.py` opened five cards in this run, and the board
  now holds two for `weekly`. The one in `This sprint`, `2170a62f`, was created
  2026-10-17 and names image `0cbc51a0e248`. The live `deploy_runtime` row says
  `2e313065f5c7`. So the card every seat reads as the engineer's lane item names
  an image that stopped running weeks ago, and the four most recent runs of this
  seat each read it as live and reported its blocker off it.
- What: the sha key is deliberate and the reasoning in `drift_watch.py`'s own
  docstring is sound as far as it goes. A drift is a fact about an image, a
  second run on the same day finds its own card and writes nothing, and a deploy
  that fixes the drift ends the alarm by the surface going green. The gap is the
  fourth case, which that docstring names and then drops: "a deploy that lands a
  different stale image gets a new card, because it is a new fact about a new
  image." It gets a new card. The old one is not closed, not annotated and no
  longer keyed to anything that exists, so the board accumulates one dead card
  per intermediate stale image and the dead ones are indistinguishable in a list
  view from the live one. Five apps were cardless until today because the deploy
  surface could not measure two of them and the other three had cards under
  older shas, so the shape is about to multiply.
- Why it is filed rather than fixed in the same run that found it: the fix is a
  choice and not a bug. Closing the superseded card is one option and it closes
  a card carrying eight comments of diagnosis that readers reach by its id.
  Annotating it and leaving it open is another, and it leaves a stale title in
  the list view that nothing reading titles can tell from a live one. Rekeying
  the card on the app and moving the sha into the body is the third, and it is
  the one this entry would argue for, because the app is the thing the card is
  assigned about and the sha is a measurement that belongs where measurements
  go. All three change what another seat's reading surface does, which is not a
  thing to decide inside a break-fix.
- First step: `drift_watch.py` gains a dry-run report of every card its own
  `TITLE_PREFIX` matches whose key is not the app's current running sha. That
  table is the size of the problem and it needs no decision to produce. The
  rekey, if it is chosen, then has to carry the old cards forward rather than
  orphan them a second time, which is the part worth designing before writing.
- Cost: $0
- Status: proposed
