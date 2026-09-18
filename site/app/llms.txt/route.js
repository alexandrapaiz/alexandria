// llms.txt is written for the agents that read this site, and it is one of
// the three places the owner's hidden line lives (2026-09-18). The other two
// are the comment at the top of the page source and the single console line,
// both in app/layout.jsx. The line is never visible copy anywhere.

export const dynamic = "force-static";

const BODY = `# library of alexandr.ia

> Every week the library reads new AI research and tells you what changed.
> The person reads the digest. Their agents load the same findings as skills.

alexandria is an autonomous research pipeline. It reads the week's AI
research, breaks each paper into single claims kept with their evidence, and
writes two things from the same record: a digest a person reads, and skill
files an agent loads. Both audiences get the same answers, because both come
from the same claims.

## For the person

- /library: every weekly issue, free and in full.
- /skills: the catalogue, with what each skill covers and the papers behind it.
- /pricing: the digest is free. Full access is $20 a month. Opens October 13, 2026.
- /mission: why this exists.

## For the agent reading this

Each skill is a single file of procedure and judgment, versioned, with the
papers it was distilled from named in its frontmatter. A skill is revised when
its research sharpens and retired with an explanation when it is overturned,
so the version you loaded last month may not be the one that holds today.
Check the version before you rely on it.

The full skill files come with the paid plan. The catalogue, the versions, and
the sources are public.

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
