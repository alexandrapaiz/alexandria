"use client";

import { useId, useState } from "react";

// One field, one button, three states. No hover is required to use it, so it
// works the same under a thumb as under a cursor.
export default function Waitlist({ source, note }) {
  const id = useId();
  const [email, setEmail] = useState("");
  const [state, setState] = useState("idle"); // idle | sending | done | error
  const [error, setError] = useState("");

  async function onSubmit(event) {
    event.preventDefault();
    if (state === "sending") return;
    setState("sending");
    setError("");
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        setError(data.error || "Something went wrong. Please try again.");
        setState("error");
        return;
      }
      setState("done");
    } catch {
      setError("Something went wrong. Please try again.");
      setState("error");
    }
  }

  if (state === "done") {
    return (
      <p className="waitlist-done" role="status">
        You are on the list. We will write on the day subscriptions open.
      </p>
    );
  }

  return (
    <div className="waitlist-wrap">
      <form className="waitlist" onSubmit={onSubmit} noValidate>
        <label className="waitlist-label" htmlFor={`${id}-email`}>
          Email address
        </label>
        <input
          id={`${id}-email`}
          className="waitlist-field"
          type="email"
          name="email"
          inputMode="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button className="pill waitlist-go" type="submit" disabled={state === "sending"}>
          {state === "sending" ? "Sending" : "Join the waitlist"}
        </button>
      </form>
      <p className={`waitlist-note${state === "error" ? " is-error" : ""}`} role={state === "error" ? "alert" : undefined}>
        {state === "error" ? error : note}
      </p>
    </div>
  );
}
