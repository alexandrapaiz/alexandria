import { ClerkProvider, Show, SignInButton, UserButton } from "@clerk/nextjs";
import "./globals.css";
import Link from "next/link";
import MobileNav from "./components/MobileNav";

export const metadata = {
  title: "library of alexandr.ia",
  description:
    "Every week the library reads new AI research and tells you what changed. Your agents load the same answers you do.",
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
          <span>© 2026</span>
          </footer>
        </ClerkProvider>
      </body>
    </html>
  );
}