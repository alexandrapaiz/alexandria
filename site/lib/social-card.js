import { SITE_ORIGIN } from "./public-routes.js";

// What a link to this site looks like when somebody shares it.
//
// Until this file existed, every link to libraryofalexandria.dev rendered as a
// bare URL. The site served a `<title>`, a `<meta name="description">` and
// nothing else, so Slack, WhatsApp, Discord, X, LinkedIn and every preview
// crawler had no card to build and fell back to the hostname. That is not a
// cosmetic gap. The product is shared as a link — the weekly issue is a link,
// the skills catalogue is a link, and the owner's home market runs on a chat
// app whose unfurl is the only thing a reader sees before deciding to tap.
//
// The reading that found it, 2026-11-02: an anonymous fetch of `/` on both
// public hosts returned `title`, `description` and one `rel=alternate` to
// llms.txt. No `og:` tag of any kind, no `twitter:` tag, no `rel=canonical`.
// A search of this repository's pull requests for `openGraph`, `og:image` and
// `social preview` returned nothing, open or closed: the surface had never
// been worked rather than having been tried and dropped.
//
// **The words are not declared here.** `app/layout.jsx` owns the site's title
// and description, and this file is a function of them, so a card can never
// drift from the page it describes. The alternative was a second copy of both
// strings next to the first, which is the defect that cost this company five
// files of disagreeing About panels.
//
// **`og:url` is deliberately absent.** Next resolves it per route against
// `metadataBase`, which `app/layout.jsx` sets to the canonical origin, so
// every page gets its own absolute URL on libraryofalexandria.dev — including
// the pages served from the `alexandria-lilac.vercel.app` alias, which is the
// one duplicate-host signal this file can carry on its own. Writing `url`
// here would instead stamp the front page's address onto all eleven routes.

// The card image, and why it is null rather than a path.
//
// There is no `site/public/` directory in this repository and no image asset
// anywhere under `site/`, so there is nothing to point at. A path to a file
// that does not exist is worse than no tag: the crawler fetches it, gets the
// 404 page, and caches a broken card against the URL.
//
// Choosing and producing the image is a design act, not this seat's. When one
// lands, set it here and the Twitter card type below follows on its own,
// because the two decisions are one decision and a reviewer should not have to
// remember the second half. Facebook's and X's documented minimum for a large
// card is 1200 by 630.
export const OG_IMAGE = null;

export function socialCard({ title, description }) {
  if (!title || !description) {
    throw new Error(
      "socialCard needs the page's own title and description; it does not keep a copy of them",
    );
  }
  const openGraph = {
    type: "website",
    siteName: title,
    locale: "en_US",
    title,
    description,
  };
  if (OG_IMAGE) {
    openGraph.images = [new URL(OG_IMAGE, SITE_ORIGIN).toString()];
  }
  return {
    openGraph,
    twitter: {
      // A summary card with no image renders as text, which is a card. A
      // large-image card with no image renders as nothing at all.
      card: OG_IMAGE ? "summary_large_image" : "summary",
      title,
      description,
    },
  };
}
