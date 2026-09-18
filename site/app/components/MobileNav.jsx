"use client";

import { useState } from "react";
import Link from "next/link";

const LINKS = [
  ["/library", "Library"],
  ["/skills", "Skills"],
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
          {/* The bar has no room for sign-in on a phone, so the panel carries
              it. This is the /sign-in route rather than the bar's modal
              button, because that button is Clerk's and renders nothing until
              Clerk's script has loaded, which would leave a phone with no way
              in at all on a slow connection. */}
          <Link href="/sign-in" className="mobile-nav-signin" onClick={() => setOpen(false)}>
            Sign in
          </Link>
        </div>
      )}
    </div>
  );
}
