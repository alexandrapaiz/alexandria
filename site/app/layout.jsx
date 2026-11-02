import { ClerkProvider, Show, SignInButton, UserButton } from "@clerk/nextjs";
import "./globals.css";
import Link from "next/link";
import MobileNav from "./components/MobileNav";
import Whisper from "./components/Whisper";
import { SITE_ORIGIN } from "../lib/public-routes.js";
import { socialCard } from "../lib/social-card.js";

// The site's own words, declared once. The page reads them, and so does the
// card a link preview builds, so the two cannot drift apart.
const TITLE = "library of alexandr.ia";
const DESCRIPTION =
  "What changed in AI research this week, written for people who build things. Your agents load the same findings as skills.";

export const metadata = {
  title: TITLE,
  description: DESCRIPTION,
  // Every absolute URL Next generates resolves against this, `og:url`
  // included. A page served from the alexandria-lilac.vercel.app alias
  // therefore still names its address on the canonical domain.
  metadataBase: new URL(SITE_ORIGIN),
  // the site is for a person and for that person's agents, so it says so to
  // both. An agent that follows this link gets the catalogue in plain text.
  alternates: { types: { "text/plain": "/llms.txt" } },
  // Open Graph and Twitter, from the two strings above. See
  // lib/social-card.js for why there is no image and what it costs.
  ...socialCard({ title: TITLE, description: DESCRIPTION }),
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {/* The first of three hidden placements of the owner's line
            (2026-09-18): a comment at the top of the page source, one quiet
            console line, and llms.txt. It is never visible copy, and it never
            goes near the hero mark. */}
        <div
          hidden
          aria-hidden="true"
          dangerouslySetInnerHTML={{
            __html:
              "<!-- Catching up to the world where the library never burned. -->",
          }}
        />
        <Whisper />
        <ClerkProvider>
          <nav className="nav">
          <Link href="/" className="nav-logo">
          <span className="dot" />
          library of alexandr.ia
          </Link>
          <div className="nav-links">
          <Link href="/library">Library</Link>
          <Link href="/skills">Skills</Link>
          <Link href="/mission">Mission</Link>
          </div>
          <div className="nav-right">
          <MobileNav />
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="pill ghost nav-signin" style={{ cursor: "pointer" }}>Sign in</button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <span className="nav-user"><UserButton /></span>
          </Show>
          <Link href="/pricing" className="pill">
          Pricing
          </Link>
          </div>
          </nav>
          {children}
          <footer className="footer">
          <span>library of alexandr.ia</span>
          <span>
            <Link href="/privacy">Privacy</Link>
            {" · "}
            <Link href="/terms">Terms</Link>
          </span>
          <span>© 2026</span>
          </footer>
        </ClerkProvider>
      </body>
    </html>
  );
}