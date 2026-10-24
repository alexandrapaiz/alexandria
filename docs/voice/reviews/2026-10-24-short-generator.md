# The second generator, which no gate has ever read

**Writer seat, 2026-10-24, run 48. In progress.**

`prompts/digest-short.md` is a live generator prompt. `pipeline/weekly.py`
loads it at three call sites and `pipeline/budget.py` names it
`SHORT_ISSUE_PROMPT`, with a comment saying it is "the writer seat's surface
and not this one". `docs/voice/check_voice.py` names `prompts/digest.md` and
nothing else.

So the finding that closed run 47 has a remainder, and the remainder is a
whole file: every gate in this repository reads either finished output or the
full generator, and the prompt that writes the issue when the full edition
cannot be reached is read by none of them.
