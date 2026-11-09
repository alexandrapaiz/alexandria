# agent-approval-paths: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

This skill ships `status: draft` citing zero claim ids, which is the honest
state for three papers the pipeline has not ingested, and it ships with no
differential measurement of any kind, because this seat has no route to either
eval arm. So a consumer report is not one more piece of evidence about this
file. Until the eval route lands it is the **only** evidence that is not a
reading of three papers by one agent.

Most wanted, in priority order.

- **Delta 3, the persisted allow-rule, and specifically step 2.** This is the
  file's sharpest prescription and the one with the thinnest denominator
  underneath it: treat a mid-task request to persist a rule as an alert, on the
  strength of a benign control that was 0 of 25 on every model. Twenty-five
  runs is a thin basis for something that pages a human in production. If you
  have shipped an always-allow or remembered-permission feature, the report this
  file wants most is how often such a proposal arises in ordinary benign use. A
  rate above zero does not refute the delta, but it reprices step 2 from free to
  costed, and nobody has measured it outside that 25-run control.
- **Delta 1, ported off a browser.** The 0 percent attack success is measured
  where ground truth is a DOM commit, which is cheap to decode and hard to
  forge. Every prescription in that section assumes you can name the action that
  will execute. A report from anyone who built that decoder for a shell, an API
  or a database surface should say what it cost and what fraction of actions it
  could not decode, because delta 2 says that fraction is the whole fatigue
  problem and the two papers never meet.
- **Delta 2's two numbers, against your own corpus.** The 10.0 percent silent
  pass and 87.0 percent uninspectable are properties of one trust list on two
  public corpora, and the file says so. What transfers is the frontier, not
  either endpoint. If you measured either on your own command traffic, that
  report moves this section further than another paper would, and it is the one
  place a consumer holds evidence this seat cannot obtain at all.

One thing this file explicitly does not want reported as validation: that the
advice sounded right. ADR-38's first measurement is the reason. Six skills
shipped on trigger tests before anyone asked whether a skill helped, and the
answer on the gold specimen was a delta of roughly zero. Say which section
changed a decision you had already made differently, or say that none did.
A report of zero decision changes is a useful report here and is treated as
evidence toward retirement rather than as a failed review.
