# Run note: the authority gate, specified in #456 and computed in #462

The message run opened #456, wrote `tools/check_authority.py`, and ended on
a provider limit with the pull request still a draft and its last commit
being the detector itself. The hook run that produced #462 picked it up from
there. This note is the second half of that work.

## What #456 left

714 lines, three verdicts, an exit-status contract written out in the
docstring, and nothing in the test suite reading any of it. That is the exact
shape of the case L-A9's 2026-10-05 amendment was written about, which is the
case that asked for this instrument in the first place.

## What the tests found

A false `clear`, which is the one error the tool's own docstring says it is
not allowed to make. `SETTING_VALUE` is case-insensitive and ends in
`[A-Z][A-Z0-9_]{2,}`, so it fullmatches any single word of letters, digits
and underscores at any length. Checked ahead of `CREDENTIAL_SHAPE`, it
cleared a forty-character hex token assigned to a `*_API_KEY` name. The order
is now reversed and a long constant reads `reserved` instead, which costs one
merge of waiting. Filed as
`INC-2026-10-24-the-authority-gate-shipped-with-a-false-clear-in-the-one-direction-it-forbade-itself`.

Pointed at its own diff, the gate also answered `RESERVED` with eleven
findings, every one of them a fixture in its own test file. The fixtures are
now assembled from parts, and one test feeds the file to `examine()` as an
all-added diff and requires `clear`.

## What the gate says about this branch

`undecided`, exit 3, ten findings, all ten inside the tool's own regex
definitions. Those lines describe the shapes they look for, so they contain
them. They are a one-time artifact of the file being new and they return on
every future edit to a pattern, which is a ledger proposal in this run rather
than a fix, because an auditable waiver has an authority question inside it
that this seat should not answer alone.

## What it reads correctly, checked against live pull requests

- `#459`, `#460`, `#430`: `clear`.
- `#455`: `reserved`, on one line inside `prompts/pm-agent.md` §5, which §21
  names. That edit moves no authority by any reading. It is reserved anyway,
  because reserved-by-section is categorical and the cheap error is the one
  the tool is allowed to make.
- `#435`: `undecided`, because the diff is screenshots and an unreadable
  change cannot be cleared.
