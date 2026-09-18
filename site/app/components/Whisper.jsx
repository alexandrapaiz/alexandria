"use client";

import { useEffect } from "react";

// One quiet line in the console on load, and nothing else. This is the second
// of the three hidden placements of the owner's line (2026-09-18); the other
// two are the comment at the top of the page source, in app/layout.jsx, and
// llms.txt. The line is never visible copy on any page, and it never touches
// the hero mark.
export default function Whisper() {
  useEffect(() => {
    console.log("Catching up to the world where the library never burned.");
  }, []);
  return null;
}
