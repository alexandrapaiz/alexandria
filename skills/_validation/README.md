# skills/_validation

The instruments that decide whether a skill in this library has earned what
its page says about it. Not a skill: this directory holds no `SKILL.md`, so
the library listing skips it.

- `trigger_test.py` — the executable trigger test. Run
  `python3 skills/_validation/trigger_test.py` from the repository root.
  Exit 0 when every case passes, 1 when any case fails.
- `decoys.json` — the null model. Eight plausible skills from domains this
  library does not serve. A skill fires only when it strictly outranks all of
  them on a prompt.
- `results/` — recorded runs. Each bundle names the engine version, the
  pre-registered policy, and the sha256 of every `SKILL.md` it judged, so a
  result is a receipt for exactly the text that produced it.

Each skill keeps its own cases in `skills/<slug>/triggers.json`, next to the
skill they test.

The design this implements, including the four gates still unbuilt and how a
result becomes the library's verification badge, is in
[docs/product/skill-validation.md](../../docs/product/skill-validation.md).
