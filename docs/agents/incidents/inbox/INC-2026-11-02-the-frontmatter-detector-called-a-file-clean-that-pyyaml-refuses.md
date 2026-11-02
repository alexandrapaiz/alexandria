## INC-2026-11-02-the-frontmatter-detector-called-a-file-clean-that-pyyaml-refuses - the detector's one-directional invariant was prose, so the second construct shipped (2026-11-02, engineer seat)

**What happened.** `skills/harness-engineering/SKILL.md` is on `main` with two
`provenance.revisions` entries glued onto one line: the 2026-11-02 entry ends
`...measured what padding costs."    - "2026-10-27 (ADR-37 maintenance...`, with
no newline between them. PyYAML refuses the whole document for it,
`ScannerError: sequence entries are not allowed here` at line 13 column 2287.
`tools/skill_registrar.py:frontmatter_problems` returned `[]` for the same
bytes. The reason is one line: `_quoted` was
`value[0] in "\"'" and value.endswith(value[0])`, and `"one"    - "two"` starts
and ends with a double quote, so the detector read the item as quoted, skipped
every remaining check, and `_unquote` would have handed a consumer
`one"    - "two` as the value, silently dropping the second revision entry.
Found because this chain's own new gate,
`tests/test_skill_receipts.py::test_the_parser_and_pyyaml_agree_on_every_shipped_skill`,
went red on the branch. The gate worked; the parser it measures did not.

**Why it is in this register.** Two counts.

The defect class is "a shipped skill's frontmatter is on `main` in a form a real
YAML loader refuses." That is the second instance. The first was 2026-10-26,
two skills with an unquoted colon in `description:`, which is what
`FRONTMATTER_QUARANTINE` was built for, held until the skill seat's quoting fix
merged on 2026-10-27, and emptied the same day. The quarantine is re-opened
today for the second instance, and the comment above the constant says so.

The sharper count is the invariant. `frontmatter_problems`'s docstring states
the contract in prose: "Everything a loader refuses is reported here, which is
the defect this exists for, and the two are measured to agree on all nine
shipped skills." The first half is a universal claim about every YAML construct.
The only thing measuring it was the second half, agreement on nine live files,
so the claim held exactly until a tenth construct arrived. That is the same
shape as
`INC-2026-10-24-three-instruments-in-one-day-tested-a-proxy-instead-of-the-mechanism`
and as `INC-2026-11-01-a-test-pinned-to-a-live-measurement-was-filed-twice-and-fixed-neither-time`:
an instrument whose only subject is today's live data stops measuring the day
the live data changes shape, in either direction.

**What it cost.** Nothing in production and about eight turns of this run. The
defect could not reach a digest or the site: the glued line is in `revisions`,
which no consumer reads, and `claims` parses either way. What it cost is the
counterfactual, and it is the reason this is filed rather than only fixed: the
same construct in `description:` or in `claims:` would have been served to
readers as a truncated value by every tool in `tools/` that calls
`parse_frontmatter`, with the gate reporting the library clean.

**The fix, or why there is not one yet.** Three parts, all in this run's pull
request, and one of them is not a fix.

`_closing_quote` replaces the `endswith` test: it walks the value with YAML's
own escapes (`''` inside single quotes, `\"` inside double) and returns where
the scalar actually ends. `_quoted` is now "closes, and nothing follows but
blanks", `_unterminated` is "never closes at all", and a new `_after_close`
reports what follows. Both the list-item branch and the `key: value` branch
report it, with the text that follows named in the message.

`FRONTMATTER_QUARANTINE` is re-opened for `harness-engineering` alone, because
the repair for the file is one newline inside `skills/`, which the engineer
charter does not let this seat write. The excusable-class list became a named
constant, `QUARANTINABLE`, because the old excuse was the literal
`"unquoted colon" in p` buried in the matcher, and the second class to ever
need the quarantine was not that string: a quarantine that silently covers one
class cannot be widened on purpose.

**What is not fixed is the file**, and it is owed to the skill seat: one newline
in `skills/harness-engineering/SKILL.md` splitting the two `revisions` entries.
The excuse expires 2026-11-09 and then the gate goes red with the slug in it.
