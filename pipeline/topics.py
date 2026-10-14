"""The claim taxonomy: one closed list, and the fold that gets a tag onto it.

`prompts/distill.md` has always called its topic list closed. Nothing enforced
that, so the model's tags went into `claims.topics` exactly as they came back,
and the research seat's census of 2026-09-26 found what that cost:

- 18 claims carry a **non-breaking hyphen** twin of a real topic: `post\u2011training`
  (11), `harness\u2011engineering` (4), `loop\u2011engineering` (2), `context\u2011engineering`
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
space-for-hyphen spellings are all typography, so `Post\u2011Training` and
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
    # Layer 4's four threads, added by the owner's directive of 2026-10-05 with
    # the definitions the research seat drafted in section 5 of
    # docs/research/notes/2026-09-30-protocols-containment-security-census.md.
    # The measured need: across 846 claims that census found `containment` 0
    # times and `protocols` 0 times, while 21 claims had already reached for
    # `safety`, `security` or a hyphen-variant the prompt does not sanction, so
    # a 0.0%-ASR result was filed under {evals, safety} and found by luck. The
    # precedent is `reasoning`, added the same way for Layer 3a.
    "protocols",
    "containment",
    "security",
    "self-improvement",
    "other",
)

# ---------------- the prose, which used to live in the prompts ----------------

# The boundary each tag states against its neighbours, keyed by tag, in the
# prompt's own words. These paragraphs were inside `prompts/distill.md` until
# 2026-10-09 and the list above was a second copy of the same fact, held
# together by a test that parsed the prose back out. That arrangement had two
# costs and the second one is the reason this moved.
#
# The first is the one `prompt_topics` was written for: two copies drift, and a
# tag the prompt offers that the insert rejects is dropped on every claim.
#
# The second is that `prompts/` is the owner's merge under the autonomy tiers
# (docs/standards/pm.md §10, Tier C), because that directory holds the agent
# charters. A taxonomy change is product code, but it had to edit a file in
# that directory to keep the two copies agreeing, so every tag the org added
# waited on the owner's hand. The four tags of 2026-10-05 waited four days
# inside a ten-run pull request chain that also carried the fix for a red test
# suite. Nothing about a topic name needs the owner's judgment, so nothing
# about a topic name should need the owner's merge.
#
# So the prompts carry a marker and this module carries the words. `render`
# substitutes one into the other at load time, which means the prompt the
# model is sent is assembled from this file and the sha written onto every
# claim covers the vocabulary. Before this, editing the list here changed what
# the insert accepted and left `claims.prompt_sha` untouched, so the audit
# trail said the vocabulary had not moved.
#
# A tag with no entry here is listed to the model without a boundary, which is
# a tag it guesses at. `tests/test_reasoning_rubric.py` requires one for every
# tag added since `reasoning`, and `pipeline/retag_threads.py` refuses to run
# without one for each thread it judges.
DEFINITIONS = {
    "reasoning": (
        "`reasoning` covers how a model's reasoning is TRAINED or SPENT, never "
        "the bare fact that a model reasoned. It holds reasoning-trace "
        "supervision and chain-of-thought training, process and outcome "
        "rewards, verifiable-reward RL (RLVR, GRPO and its variants), "
        "test-time compute and how the budget is allocated, distillation of "
        "reasoning into smaller models, and synthetic reasoning or preference "
        "data. Tag it beside `post-training` when the claim is about the "
        "recipe, and beside `serving` when it is about what the reasoning "
        "costs at inference. A paper that only measures reasoning ability is "
        "`evals`, not `reasoning`; this tag is for method, and it stops being "
        "useful the moment it is applied to every paper that uses the word."
        "\n\n"
        "For a reasoning claim, `procedure` is where the recipe goes: the "
        "reward, the data, the curriculum, the budget rule, with the "
        "thresholds the source states. A `reasoning` claim with a null "
        "`procedure` and no number in its evidence is usually an `evals` "
        "claim that took the wrong tag."
    ),
    "protocols": (
        "`protocols` covers the wire contract between agents, or between an "
        "agent and its tools: MCP, A2A, agent cards, task lifecycles, "
        "tool-calling schemas, agent identity as a principal (SPIFFE, "
        "per-agent OAuth, workload identity), and interoperability across "
        "independent implementations. Tag it when the claim is about the "
        "contract itself. A claim about what an agent *did* over a protocol "
        "is `tooling` or `multi-agent`, not this."
    ),
    "containment": (
        "`containment` covers the boundary an agent runs inside and what it "
        "costs: sandboxes, microVMs, wasm runtimes, containers and their "
        "pinned runtimes, capability and least-privilege schemes, measured "
        "escapes and their preconditions, and containment evaluation. Tag it "
        "when the claim is about the boundary. A claim about an agent's "
        "runtime performance inside a boundary is `systems`; a claim about "
        "the attack that crossed it is `security`, and claims about both take "
        "both tags."
    ),
    "security": (
        "`security` covers adversarial pressure on agents and the defenses "
        "measured against it: prompt injection and indirect injection, tool "
        "poisoning, jailbreaks, exfiltration, sabotage and collusion between "
        "agents, guardrails and monitors, and attack success rates. Tag it "
        "whenever a claim carries an ASR, a detection rate, or a sabotage "
        "frequency. `evals` is for how capability is measured; a security "
        "benchmark takes both."
    ),
    "self-improvement": (
        "`self-improvement` covers a system that changes itself and measures "
        "the gain: self-evolution, recursive self-improvement, self-play, "
        "self-refinement and self-rewarding loops, autonomous research "
        "harnesses, and the question of which of their own improvements such "
        "a system can be trusted to judge. Tag it when the claim is about the "
        "loop that closes back on the system. A single training run that "
        "produces a better model is `post-training`; a harness whose own "
        "scaffold is the thing being rewritten is this."
    ),
}

# Where a field report lands, which is a different question from what a tag
# means. `prompts/distill-practices.md` reads a practitioner's post rather than
# a paper, and this is the routing it was carrying. It moved for the same
# reason the definitions did: it names tags, so it changed whenever the list
# changed, which put a prompt file in the diff of every taxonomy change.
FIELD_REPORT_ROUTING = (
    "`systems` and `serving` carry most field reports: this is where "
    "production infrastructure, deployment, capacity and inference cost "
    "belong."
    "\n\n"
    "`containment` and `security` are where a field report most often lands "
    "in the four tags added on 2026-10-05, because a practitioner writing "
    "about agents in production is usually writing about the boundary they "
    "ran inside or the attack that crossed it. The boundary itself is "
    "`containment` and the adversary is `security`; a report that measures "
    "both takes both. Keep `systems` for what the agent cost to run inside "
    "the boundary. The full definitions are in prompts/distill.md and the "
    "two files share one list. `harness-engineering` and `loop-engineering` "
    "are for reports about running agents themselves. `reasoning` covers how "
    "a model's reasoning is TRAINED or SPENT, never the bare fact that a "
    "model reasoned, and a field report rarely earns it."
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
    "\u2010": "-",   # hyphen
    "\u2011": "-",   # non-breaking hyphen, the one that cost 18 claims
    "\u2012": "-",   # figure dash
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u2015": "-",   # horizontal bar
    "\u2212": "-",   # minus sign
    "_": "-",
}
SPACES = ("\u00a0", "\u2007", "\u202f", "\u3000")

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
    spelling, because "we dropped `post\u2011training`" is a report the owner can act
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
    """The topic names a RENDERED distill prompt actually offers the model.

    The prompt lists them as a comma-separated run inside a bullet that starts
    `- `topics``, after that bullet's colon, ending at the first blank line or
    the first full stop. Parsed rather than trusted, which used to be how TOPICS
    and a second copy of the list in the prompt were kept from drifting apart.
    There is no second copy as of 2026-10-09, so what this now checks is that
    `render` put the list where the prompt asked for it: a deleted or renamed
    marker leaves the model with no vocabulary, which is silent otherwise.

    Pass it rendered text. Both prompts introduce the run differently, the
    paper one with "tags from:" and the practices one with "tags from this
    closed list, and nothing else:", so the split is on the bullet's colon
    rather than on either wording. The practices copy went unchecked for nine
    days because this function only recognised the first of the two.
    """
    lines = prompt_text.splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith("- `topics`"):
            block = [line.split(":", 1)[-1] if ":" in line else ""]
            for follow in lines[i + 1:]:
                if not follow.strip():
                    break
                block.append(follow)
            run = " ".join(block)
            run = run.split(".")[0] if run.rstrip().endswith(".") else run
            return [t.strip(" `.") for t in run.replace("\n", " ").split(",")
                    if t.strip(" `.")]
    return []


# ---------------- rendering the vocabulary into a prompt ----------------

#: The markers a prompt uses to ask for the vocabulary. HTML comments, because
#: a prompt is markdown and a comment is the one construct that is invisible
#: to a reader of the rendered file and still obvious to a reader of the
#: source. A prompt that carries none of these is sent exactly as written.
LIST_MARKER = "<!-- topics:list -->"
DEFINITIONS_MARKER = "<!-- topics:definitions -->"
ROUTING_MARKER = "<!-- topics:field-report-routing -->"

#: The column the prompts wrap at. Measured from the files rather than chosen:
#: the longest line in the block this replaced was 79 characters, and
#: `tests/test_reasoning_rubric.py` asserts the rendered text is byte-identical
#: to what those files held before the vocabulary moved out of them.
WIDTH = 79


def _fill(body: str, prefix: str, indent: str) -> str:
    """One or more paragraphs, wrapped the way the prompts are wrapped.

    `break_on_hyphens` is off deliberately. Nine of the eighteen topic names
    carry a hyphen, and a line break inside `context-engineering` would hand
    the model a tag it cannot copy and `prompt_topics` a name it cannot parse.
    """
    import textwrap

    out = []
    for i, para in enumerate(body.split("\n\n")):
        out.append(textwrap.fill(
            para, width=WIDTH,
            initial_indent=(prefix if i == 0 else indent),
            subsequent_indent=indent,
            break_long_words=False, break_on_hyphens=False))
    return "\n\n".join(out)


def _substitute(line: str, marker: str, body: str) -> str:
    """`line` with `marker` replaced by `body`, keeping the line's own layout.

    The text before the marker becomes the first line's prefix, so a marker
    sitting at the end of a bullet produces a run that starts on the bullet's
    own line. Continuation lines take the line's leading whitespace, plus two
    more when the marker sits on a bullet, which is how markdown continues one.
    """
    prefix = line[:line.index(marker)]
    lead = prefix[:len(prefix) - len(prefix.lstrip())]
    indent = lead + ("  " if prefix.lstrip().startswith("- ") else "")
    return _fill(body, prefix, indent)


def topic_list() -> str:
    """The closed list as the prompts print it: a comma run ending in a stop."""
    return ", ".join(TOPICS) + "."


def definitions(topics=None) -> str:
    """The boundary paragraphs, in TOPICS order, for the tags that have one.

    Order comes from TOPICS rather than from DEFINITIONS so that the prose a
    model reads arrives in the same sequence as the list it was offered, and so
    that adding a tag in the middle of the list does not reorder the prose.
    """
    wanted = TOPICS if topics is None else tuple(topics)
    return "\n\n".join(DEFINITIONS[t] for t in wanted if t in DEFINITIONS)


def render(prompt_text: str) -> str:
    """A prompt with its vocabulary substituted in, ready to send to a model.

    Every reader of a distill prompt goes through this: `distill.load_prompt`
    before the call, `budget.prompt_text` before sizing the request,
    `retag_threads` before lifting the definitions back out. A reader that
    skipped it would size or judge against a prompt with two markers where the
    vocabulary should be, which is the failure this function is easiest to
    introduce.
    """
    out = []
    for line in prompt_text.splitlines():
        if LIST_MARKER in line:
            out.append(_substitute(line, LIST_MARKER, topic_list()))
        elif DEFINITIONS_MARKER in line:
            out.append(_substitute(line, DEFINITIONS_MARKER, definitions()))
        elif ROUTING_MARKER in line:
            out.append(_substitute(line, ROUTING_MARKER, FIELD_REPORT_ROUTING))
        else:
            out.append(line)
    rendered = "\n".join(out)
    return rendered + "\n" if prompt_text.endswith("\n") else rendered


def undefined(topics=None) -> list[str]:
    """Tags that would be offered to a model with no boundary stated.

    `reasoning` and everything added after it carries a definition. The thirteen
    that predate the rubric of 2026-09-26 are described by the prompt's
    surrounding prose instead, so this is not a list of defects: it is what
    `retag_threads` asks before it offers a model a tag to apply.
    """
    wanted = TOPICS if topics is None else tuple(topics)
    return [t for t in wanted if t not in DEFINITIONS]
