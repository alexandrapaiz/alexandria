"use client";

import { useState } from "react";
import Link from "next/link";

const LINKS = [
  ["/library", "Library"],
  ["/skills", "Skills"],
  ["/graph", "Graph"],
  ["/mission", "Mission"],
];

export default function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <div className="mobile-nav">
      <button
        type="button"
        className="mobile-nav-toggle"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span className={open ? "open" : ""} />
        <span className={open ? "open" : ""} />
      </button>
      {open && (
        <div className="mobile-nav-panel" role="menu">
          {LINKS.map(([href, label]) => (
            <Link key={href} href={href} onClick={() => setOpen(false)}>
              {label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
