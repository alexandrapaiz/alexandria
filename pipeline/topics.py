"""The claim taxonomy: one closed list, and the fold that gets a tag onto it.

`prompts/distill.md` has always called its topic list closed. Nothing enforced
that, so the model's tags went into `claims.topics` exactly as they came back,
and the research seat's census of 2026-09-26 found what that cost:

- 18 claims carry a **non-breaking hyphen** twin of a real topic: `post‑training`
  (11), `harness‑engineering` (4), `loop‑engineering` (2), `context‑engineering`
  (1). Every one of them is invisible to `topics @> '{post-training}'`, which is
  how the digest, the graph page and the skill agent all read the column.
- 22 more tags were invented outright: `training` (8), `analysis` (5), `safety`
  (3), `reward-design` (2) and a tail of singletons.
- 3.9% of all tag applications were off the list.

A topic nobody can reliably query is a topic that does not exist, and that
matters more from today, because `reasoning` has just been added to the list by
the owner's directive of 2026-09-26. A brand new tag whose adoption cannot be
counted is a tag that cannot be shown to be working.

So this module is the single place that decides what a topic is. `pipeline/
distill.py` folds every tag through `normalize` before the insert and prints
what it dropped, which turns a silent 3.9% into a number in the run log.

## What the fold does, and what it refuses to do

It fixes spelling, never meaning. Case, Unicode dashes, non-breaking spaces and
space-for-hyphen spellings are all typography, so `Post‑Training` and
`post training` both land on `post-training`. Three aliases go further and they
are all licensed by the prompt's own words: the rubric names chain-of-thought
and test-time compute as `reasoning` in the text the model is given, so a model
that answers with the phrase instead of the tag made a formatting mistake and
not a judgment.

Anything else unknown is dropped rather than guessed. `training` is not silently
promoted to `post-training` and `safety` is not mapped to anything, because a
fold that invents meaning would write tags the distiller never chose and the
column would stop being evidence of anything. Dropped tags are returned to the
caller so they can be printed, counted, and turned into a proposal for
`prompts/distill.md` by the seat that owns that file.

    python3 -m pytest tests/test_reasoning_rubric.py -q
"""

# The closed list, in the order `prompts/distill.md` prints it. These two must
# agree exactly: the prompt is what the model is told, this is what the database
# accepts, and a tag the prompt offers that this list rejects would be dropped
# on every single claim. tests/test_reasoning_rubric.py parses the prompt and
# fails if they drift apart.
TOPICS = (
    "skills",
    "context-engineering",
    "harness-engineering",
    "loop-engineering",
    "memory",
    "retrieval",
    "multi-agent",
    "evals",
    "post-training",
    "reasoning",
    "serving",
    "systems",
    "tooling",
    "other",
)

# The tag a claim gets when every tag it came with was dropped. `other` is on
# the list for exactly this: an untagged claim is unfindable, and a claim tagged
# `other` is at least countable.
FALLBACK = "other"

# Aliases, licensed by the prompt's own sentences rather than by this file's
# judgment. `prompts/distill.md` defines `reasoning` as covering
# chain-of-thought training and test-time compute, so a model that answers with
# the phrase from the definition instead of the name of the tag has made a
# formatting error. Nothing here maps a tag whose meaning the prompt does not
# already settle.
ALIASES = {
    "chain-of-thought": "reasoning",
    "cot": "reasoning",
    "test-time-compute": "reasoning",
}

# Typography, not meaning. U+2011 is the non-breaking hyphen that produced 18
# invisible claims; the rest of this table is every other dash and space a
# model's tokenizer might hand back in its place. The writer's ban-list entry 13
# polices these same characters in the weekly issue, and they were entering the
# database unchecked the whole time.
DASHES = {
    "‐": "-",   # hyphen
    "‑": "-",   # non-breaking hyphen, the one that cost 18 claims
    "‒": "-",   # figure dash
    "–": "-",   # en dash
    "—": "-",   # em dash
    "―": "-",   # horizontal bar
    "−": "-",   # minus sign
    "_": "-",
}
SPACES = (" ", " ", " ", "　")

# How many tags one claim may carry. The prompt asks for a handful; a model that
# returns twenty has stopped classifying and started listing, and the digest
# payload truncates the column at 180 characters anyway (pipeline/budget.py).
MAX_PER_CLAIM = 5


def fold(tag: str) -> str:
    """One tag, reduced to the spelling the list uses. Typography only."""
    text = (tag or "").strip().lower()
    for bad in SPACES:
        text = text.replace(bad, " ")
    for bad, good in DASHES.items():
        text = text.replace(bad, good)
    # Space-for-hyphen spellings ("multi agent", "context engineering") are the
    # same tag with a different separator, so collapse whitespace runs into the
    # separator the list uses.
    text = "-".join(text.split())
    # "post--training" from a doubled separator, and any leading or trailing one.
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-")


def normalize(tags) -> tuple[list[str], list[str]]:
    """(kept, dropped) for one claim's tags.

    Kept tags are on TOPICS, deduplicated, in the order the model gave them, and
    capped at MAX_PER_CLAIM. Dropped tags are returned in their ORIGINAL
    spelling, because "we dropped `post‑training`" is a report the owner can act
    on and "we dropped `post-training`" reads like a bug in this function.

    An empty result is FALLBACK rather than nothing, so no claim is written
    untagged. That case is worth watching: it means the model answered entirely
    off-list for that claim.
    """
    if isinstance(tags, str):
        tags = [tags]
    kept: list[str] = []
    dropped: list[str] = []
    for raw in tags or []:
        if not isinstance(raw, str):
            dropped.append(str(raw))
            continue
        folded = ALIASES.get(fold(raw), fold(raw))
        if folded in TOPICS:
            if folded not in kept and len(kept) < MAX_PER_CLAIM:
                kept.append(folded)
        elif folded or raw.strip():
            dropped.append(raw.strip())
    return (kept or [FALLBACK]), dropped


def prompt_topics(prompt_text: str) -> list[str]:
    """The topic names `prompts/distill.md` actually offers the model.

    The prompt lists them as a comma-separated run inside a bullet that starts
    `- `topics` — tags from:` and ends at the first blank line. Parsed rather
    than trusted so that TOPICS and the prompt cannot drift apart unnoticed;
    the test that calls this is the only caller.
    """
    lines = prompt_text.splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith("- `topics`"):
            block = [line.split("tags from:", 1)[-1]]
            for follow in lines[i + 1:]:
                if not follow.strip():
                    break
                block.append(follow)
            run = " ".join(block)
            run = run.split(".")[0] if run.rstrip().endswith(".") else run
            return [t.strip(" `.") for t in run.replace("\n", " ").split(",")
                    if t.strip(" `.")]
    return []
