// llms.txt is written for the agents that read this site, and it is one of
// the three places the owner's hidden line lives (2026-09-18). The other two
// are the comment at the top of the page source and the single console line,
// both in app/layout.jsx. The line is never visible copy anywhere.
//
// Every line below is traceable to the page or file it describes, which is the
// only rule this file has: an agent that cannot check a claim here has no way
// to find out it was stale. Revised 2026-10-26 by alexandra-systems'
// distribution seat against the routes as they are, with the sources named:
//
//   /library and /library/<week>   app/library/page.jsx, app/library/[week]/page.jsx
//                                  — free in full, no entitlement check on the route
//   /left-behind                   app/left-behind/page.jsx — public by vision.md §0
//   /skills                        app/skills/page.jsx — catalogue public, bodies entitled
//   /pricing                       app/pricing/page.jsx — the three offers, no date
//   the install lines              README.md, between install-line:start/end,
//                                  checked against the manifests by
//                                  tools/check_plugin_manifest.py
//   the Cursor manifest            .cursor-plugin/plugin.json
//
// Not listed, deliberately. /graph, because the ruling of 2026-09-19 paywalls
// it and app/graph/page.jsx records it as unlisted until its UI is fixed.
// /routines, because nothing is built behind it yet. /desk, because it reads a
// signed-in account and a private token. /privacy, /terms, /unsubscribe and
// the two auth routes, because an agent has nothing to do on them.

export const dynamic = "force-static";

const BODY = `# library of alexandr.ia

> Every week the library reads new AI research and tells you what changed.
> The person reads the digest. Their agents load the same findings as skills.

https://libraryofalexandria.dev

alexandria is an autonomous research pipeline. It reads the week's AI
research, breaks each paper into single claims kept with their evidence, and
writes two things from the same record: a digest a person reads, and skill
files an agent loads. Both audiences get the same answers, because both come
from the same claims.

## For the person

- /library: every weekly issue, free and in full. Each issue keeps its own
  address, /library/<week>, and no account is needed to read any of them.
- /left-behind: the findings the library has stopped standing behind, each
  with the newer work that contradicted it. Free, like the digest.
- /skills: the catalogue, with what each skill covers and the papers behind it.
- /pricing: the digest is free. Full access is $20 a month, three days free
  first. Lifetime access is $200 once.
- /mission: why this exists.

## For the agent reading this

Each skill is a single file of procedure and judgment, versioned, with the
papers it was distilled from named in its frontmatter. A skill is revised when
its research sharpens and retired with an explanation when it is overturned,
so the version you loaded last month may not be the one that holds today.
Check the version before you rely on it.

The nine skill files are in the public repository,
github.com/alexandrapaiz/alexandria, under skills/. In a Claude Code session:

    /plugin marketplace add alexandrapaiz/alexandria
    /plugin install alexandria-skills@alexandria

That installs nine skills, and none of them loads until a session needs it.
The repository carries a Cursor plugin manifest for the same nine.

On the site, the catalogue, the versions and the sources are public, and the
skill bodies render for a paid reader. The claim graph and the routines are
the rest of what the paid plan opens.

## Notes

Written and maintained by the library's own agents.
Catching up to the world where the library never burned.
`;

export function GET() {
  return new Response(BODY, {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=3600",
    },
  });
}
