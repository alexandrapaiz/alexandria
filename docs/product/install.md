# Install the library

The skills are distributed as a Claude Code plugin, served from a marketplace
manifest in this repository. Two lines get a reader from nothing to nine
skills loaded, and both of them are facts about files on `main` rather than
copy, which is what `tools/check_plugin_manifest.py` exists to keep true.

<!-- install-line:start -->

## The two lines

In a Claude Code session:

```
/plugin marketplace add alexandrapaiz/alexandria
/plugin install alexandria-skills@alexandria
```

Or in a terminal, which does the same thing and prints more:

```
claude plugin marketplace add alexandrapaiz/alexandria
claude plugin install alexandria-skills@alexandria
```

That installs nine skills. None of them loads until a session needs it, so
the standing cost is the nine descriptions and nothing else, about 1,900
tokens measured with `claude plugin details alexandria-skills` on
2026-10-18. A skill's body is read only when the work in front of the agent
matches what the skill says it is for, and those bodies run from 1,500 to
6,700 tokens each.

<!-- install-line:end -->

## What arrives

Nine skills, each one written from papers read in full rather than from
abstracts, and each one carrying the claim ids and papers it stands on in its
own front matter. Read the `status` field before you lean on one.

| Skill | Status | The decision it is for |
| --- | --- | --- |
| `agent-containment` | provisional | Where to enforce the boundary an agent runs inside, and what each choice measures |
| `agent-memory-selection` | provisional | The write-versus-read split in what an assistant remembers across a long horizon |
| `agent-security-measurement` | draft | Judging and siting the defences around an agent that faces an adversary |
| `context-window-engineering` | active | Spending a finite token budget, including which eviction rule a fixed KV cache forces |
| `evaluation-integrity` | active | Whether an evaluation can be trusted when the instrument is itself generated |
| `harness-engineering` | active | Rebuilding the harness around a model rather than fine-tuning the model |
| `recursive-harness-self-improvement` | active | Loops where an agent rewrites its own scaffold unattended and keeps or reverts on evidence |
| `self-improving-post-training-loops` | active | Closed-loop post-training where a model grades or teaches its own next step |
| `skill-library-engineering` | active | What a SKILL.md has to contain to beat loading nothing, and how it gets picked |

ADR-36 defines two of those three grades. A skill with no eval behind it is
`draft` and never `active`, and a skill whose eval shows no gain is retired
with the numbers rather than quietly kept. The third grade, `provisional`, is
carried by two skills today and no decision record defines it, which is a gap
in this project's own register rather than a subtlety a reader should have to
infer. It is filed in `docs/ideas.md` as of 2026-10-18.

What every one of the nine shares is that no reviewer panel has passed it yet.
ADR-13 created that panel and the `provenance.validated` field of each skill is
still empty, which each file says in its own front matter rather than leaving a
reader to assume.

## The monorepo note

This repository is 40 MB on disk and the skills are 2.2 MB of it, because the
pipeline, the site and the project's own written record live here too. A
reader who wants only the skills can say so:

```
claude plugin marketplace add alexandrapaiz/alexandria --sparse .claude-plugin skills
```

That is a git sparse checkout, so it fetches the manifest and the library and
leaves the other 95 percent alone. The plain line above stays the one to
publish, because a second flag on the first command a stranger runs is a
second thing that can go wrong.

## What it cannot do

Installing from a marketplace is a clone and a read, so a plugin is trusted
because its source is trusted. Anthropic's documentation says this plainly:
`claude plugin validate` checks structure, and there is no code signing or
attestation behind a marketplace entry. What this library adds on top of that
is not a stronger transport promise. It is that every skill names the evidence
it came from and gets revised when that evidence moves, which `claude plugin
validate` has no opinion about and no catalogue can check for you.

The plugin ships nine files and nothing else. No hooks, no agents, no MCP
server, and no command that runs on install, which `claude plugin details`
prints as four zeros next to the skill count. Check it yourself before you
trust the sentence.

## Keeping it honest

`tools/check_plugin_manifest.py` reads the two manifests, the skill
directories and the marked block above, and fails when the sentence and the
repository disagree. It checks the marketplace name, the install id, the
repository slug and every count of skills inside the block, because the
catalogue page on the site spent weeks telling visitors the library held two
skills while nine sat on `main`. A number in a sentence needs a gate behind it
or it is a number from the day somebody last looked.

```
python3 tools/check_plugin_manifest.py
claude plugin validate . --strict
```

The first command owns the prose and the second owns the JSON. Run both.
