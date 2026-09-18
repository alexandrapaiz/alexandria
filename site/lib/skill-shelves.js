// The shelves the skill library is organised on.
//
// The library holds two skills today and is built to hold fifty, so the page
// is organised by shelf rather than by a flat list that would be unreadable
// long before it got there. The shelves are not invented here: they are the
// gold layer named in docs/vision.md section 2 (context engineering, harness
// patterns, loop designs, serving and post-training) plus the owner's
// standing coverage areas of 2026-09-18 (multi-agent systems, agentic design,
// multi-modal systems), which are recorded in prompts/research-agent.md.
//
// A shelf with nothing on it still shows, with a line saying so. That is
// deliberate: the shape of the library is part of what the page tells a
// visitor, and an empty shelf is an honest statement about where the reading
// has and has not reached.
//
// skills/ belongs to the skill agent, so nothing here writes to it. The shelf
// of a skill is decided from its own frontmatter: by name first, and by the
// words in its description when the name is new. A skill that matches nothing
// still appears, on the last shelf, rather than disappearing off the page.

export const SHELVES = [
  {
    id: "harnesses",
    name: "Agent harnesses",
    blurb:
      "The scaffold around a model. Tools, prompts, loop structure, and the feedback the loop runs on.",
    names: ["harness-engineering"],
    keywords: ["harness", "scaffold", "tool use", "agent loop"],
  },
  {
    id: "context",
    name: "Context engineering",
    blurb:
      "What goes into the window, in what order, and what to do when it will not fit.",
    names: [],
    keywords: ["context", "retrieval", "memory", "prompt"],
  },
  {
    id: "multi-agent",
    name: "Multi-agent systems",
    blurb:
      "Several agents dividing work. How they are organised, how they hand off, and how they fail.",
    names: [],
    keywords: ["multi-agent", "multi agent", "orchestration", "delegation"],
  },
  {
    id: "training",
    name: "Training loops",
    blurb:
      "Post-training that updates the weights. Distillation, reward design, and self-improvement.",
    names: ["self-improving-post-training-loops"],
    keywords: [
      "post-training",
      "distill",
      "reward",
      "rubric",
      "fine-tune",
      "training loop",
    ],
  },
  {
    id: "serving",
    name: "Serving and inference",
    blurb:
      "Getting an answer out fast and cheap. Decoding, caching, and test-time compute.",
    names: [],
    keywords: ["serving", "inference", "latency", "throughput", "decoding"],
  },
  {
    id: "multimodal",
    name: "Multi-modal systems",
    blurb:
      "Models that read and act beyond text, across images, audio, and the world.",
    names: [],
    keywords: ["multi-modal", "multimodal", "vision", "audio", "robot"],
  },
];

// The last shelf only ever appears when something landed on it, so the page
// never shows an empty "other" bucket, and a new skill is never dropped.
export const CATCH_ALL = {
  id: "more",
  name: "More from the library",
  blurb: "Distilled and shelved, on a shelf of its own for now.",
};

function shelfFor(skill) {
  const name = (skill.name || "").toLowerCase();
  const byName = SHELVES.find((s) => s.names.includes(name));
  if (byName) return byName.id;
  const hay = `${name} ${skill.description || ""}`.toLowerCase();
  const byWord = SHELVES.find((s) => s.keywords.some((k) => hay.includes(k)));
  return byWord ? byWord.id : CATCH_ALL.id;
}

// A skill's `description` is written for an agent's router, so it opens with
// what the skill is and then runs a long list of "use when" triggers. The
// first part is the sentence a person wants; the whole thing is what an agent
// matches on. The page shows the first to people and keeps the second behind
// a disclosure that says whose text it is.
export function splitDescription(description = "") {
  const d = description.trim();
  const cut = d.search(/\.\s+Use when\b/i);
  if (cut > 0) return { summary: d.slice(0, cut + 1), routing: d };
  const stop = d.search(/\.\s+[A-Z]/);
  if (stop > 0 && stop < 260) return { summary: d.slice(0, stop + 1), routing: d };
  return { summary: d, routing: d };
}

export function shelveSkills(skills) {
  const shelved = skills.map((s) => ({ ...s, ...splitDescription(s.description) }));
  const shelves = SHELVES.map((s) => ({
    ...s,
    skills: shelved.filter((k) => shelfFor(k) === s.id),
  }));
  const rest = shelved.filter((k) => shelfFor(k) === CATCH_ALL.id);
  if (rest.length) shelves.push({ ...CATCH_ALL, skills: rest });
  return shelves;
}
