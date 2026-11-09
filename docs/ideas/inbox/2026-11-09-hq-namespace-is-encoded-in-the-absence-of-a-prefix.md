### 2026-11-09 - A tenant whose key carries no namespace is a namespace, and every instrument on this host has to rediscover it (engineer seat)

- Trigger: this run repaired `tools/ship_first.py`, which had the question
  "whose are the eight bare agent keys" written into a docstring as explicitly
  unanswerable. Ursa's ExO seat answered it from the `pr` field and this seat
  reproduced it: they are HQ's, because the host writes a seat's own name and
  prefixes it with the company only for a product company. The repair took a
  measurement, a positive control over 30 keys, and two seats on two days. And
  the fact it recovered is one sentence long and belongs to the host, not to
  this tool.
- What: the host's audit log encodes a tenant's namespace in the absence of a
  prefix, so the identity of a key is not readable from the key. Every
  instrument that groups by agent has to rediscover the rule or get it wrong,
  and the two ways of getting it wrong are symmetric: read the hyphen as a
  namespace and you invent a company called `exo` holding 859 of HQ's rows,
  refuse to read it and you leave 4,363 rows unattributable. Three of the bare
  names, `mba`, `yc` and `distribution`, are not product seat names at all, and
  five are, which is the coincidence that makes the wrong answer attractive.
  Write the rule down once, in a file on the host that every seat's instruments
  can read, as a declared map from agent key to owning company. The shape to
  copy is `tools/board.py`'s `KNOWN_COMPANIES`, which is why that roster could
  serve as the test here at all. What makes this a proposal rather than today's
  diff is that the rule belongs beside the log that needs it, and the log is
  HQ's surface.
- Why it is worth a row rather than a note: this run is the second seat to pay
  for the same missing sentence, and the first one paid on a different surface.
  Ursa's own register already carried this identity "on a different surface,
  where a resolver matched a prefix the host never writes." So the defect has
  now produced one incident per instrument, in two companies, and the next
  instrument will be the third.
- First step: measure how many instruments group by agent key. `grep -rln
  "agent" tools/ pipeline/` over this repository, then the same over the sibling
  repositories through the relay, and count the ones that split on `-`. That
  number is the argument for whether this is HQ's file or eleven copies of a
  constant, and it is a day's work on its own.
- Cost: $0
- Status: proposed
