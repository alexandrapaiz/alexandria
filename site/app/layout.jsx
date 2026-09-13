import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "library of alexandr.ia",
  description:
    "A library live with the latest AI research: what the field knows right now, and the best known methods, ready for your agents to load.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
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
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
        </nav>
        {children}
        <footer className="footer">
          <span>library of alexandr.ia</span>
          <span>© 2026</span>
        </footer>
      </body>
    </html>
  );
}
