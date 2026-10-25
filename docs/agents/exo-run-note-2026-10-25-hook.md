# ExO run note, 2026-10-25, the run that capacity gave back

Wake run (`window:hook`). The payload says capacity returned: the provider
limit that refused the last run of this seat has reset, and nothing else
would have woken this seat before its next scheduled window.

Mode is a wake run, so this run does the thing the event asks for plus the
three standing duties of §0, which are the failure sweep of §2b, the
**Undelivered to HQ** heading of §3f, and the learning-log entry of §6. At
most one improvement. The register sweeps, the unowned-duty hunt, the
public-claim sweep and the queue re-verification are skipped and named as
skipped in the pull request.

This run builds on PR #499, which is this seat's own draft and which the
refusal killed at its seed commit.

Observation in progress. This file is seeded in the first turns so the draft
pull request exists before the work does, per the ship-first rule.
