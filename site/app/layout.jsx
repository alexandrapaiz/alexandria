import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "library of alexandr.ia",
  description:
    "The latest in AI research, read in full and distilled weekly: what's new, what's gaining ground, and what's been left behind.",
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
            <Link href="/routines">Routines</Link>
            <Link href="/pricing">Pricing</Link>
            <Link href="/mission">Mission</Link>
          </div>
          <Link href="/pricing" className="pill">
            Subscribe
          </Link>
        </nav>
        {children}
        <footer className="footer">
          <span>library of alexandr.ia</span>
          <span>read in full · distilled weekly · nothing left unread</span>
          <span>
            <a href="https://github.com/alexandrapaiz/alexandria">how it works</a>
          </span>
        </footer>
      </body>
    </html>
  );
}
