import { ClerkProvider, Show, SignInButton, UserButton } from "@clerk/nextjs";
import "./globals.css";
import Link from "next/link";
import MobileNav from "./components/MobileNav";

export const metadata = {
  title: "library of alexandr.ia",
  description:
    "A library live with the latest AI research: what the field knows right now, and the best known methods, ready for your agents to load.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ClerkProvider>
          <nav className="nav">
          <Link href="/" className="nav-logo">
          <span className="dot" />
          library of alexandr.ia
          </Link>
          <div className="nav-links">
          <Link href="/library">Library</Link>
          <Link href="/skills">Skills</Link>
          <Link href="/graph">Graph</Link>
          <Link href="/mission">Mission</Link>
          </div>
          <div className="nav-right">
          <MobileNav />
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="pill ghost" style={{ cursor: "pointer", marginRight: 10 }}>Sign in</button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <span style={{ marginRight: 10, display: "inline-flex", verticalAlign: "middle" }}><UserButton /></span>
          </Show>
          <Link href="/pricing" className="pill">
          Subscribe
          </Link>
          </div>
          </nav>
          {children}
          <footer className="footer">
          <span>library of alexandr.ia</span>
          <span>© 2026</span>
          </footer>
        </ClerkProvider>
      </body>
    </html>
  );
}