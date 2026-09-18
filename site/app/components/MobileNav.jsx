"use client";

import { useState } from "react";
import Link from "next/link";
import { Show, SignInButton } from "@clerk/nextjs";

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
          {/* the nav bar has no room for this on a phone, so the panel carries it */}
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button type="button" className="mobile-nav-signin">
                Sign in
              </button>
            </SignInButton>
          </Show>
        </div>
      )}
    </div>
  );
}
