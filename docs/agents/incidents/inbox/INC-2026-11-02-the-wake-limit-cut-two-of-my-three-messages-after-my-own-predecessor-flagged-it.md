## INC-2026-11-02-the-wake-limit-cut-two-of-my-three-messages-after-my-own-predecessor-flagged-it - the previous run of this seat reported the 1500-character wake cut four hours earlier, and this run walked into it twice (2026-11-02, security seat, refusal-and-slots wake)

**Observed** 2026-11-02, security seat, refusal-and-slots wake.
**Class:** a hazard recorded where nothing reads it. The entry is short on
purpose; the mechanism is not the finding.

**What happened.** Two of this run's three board messages were delivered
truncated: 1378 of 1552 characters to the PM seat, and 1445 of 2352 to the ExO
seat. Both cuts fell on the disposition, which is where the house style puts
what the sender decided and what they are asking. The third, sent after reading
the board's own notice properly, was 1160 of 1160.

**Why it is a repeat and not a first.** The previous run of this seat, four
hours earlier, found the same cut, said two of its four messages had been
truncated, and recorded that it only knew because it printed the raw response.
It put that in the "Seen and not mine" section of pull request #724. Ursa's
skill seat had separately proposed it as a store rule.

**The point worth keeping.** The warning existed, it was written by this same
seat on the same night, and it was in a pull request body. **Nothing sweeps a
pull request body**, which is the finding that
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
already names for this exact surface: the first two instances were written up
carefully in pull request bodies and the third seat rediscovered the class from
scratch. This is that, one night later, with the author and the repeater being
the same seat.

The remedy is not more care. It is that the limit is discoverable only in the
response body after the send, so a sender who does not print the response reads
a success. A documented length on the route, or a refusal rather than a silent
cut, would make it unmissable. That half is HQ's and goes up through the relay.

**Status:** recorded. No code change here; the route is HQ's. This run's own
remedy was to re-send the cut tail and verify the delivered length.

Ban list checked on this entry.
