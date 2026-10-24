// One definition of "a browser context pointed at our own server", because on
// 2026-10-24 there were six and only one of them was right.
//
// The two things every script in this directory needs, and the reason each is
// here rather than copied:
//
// GUARD 1, nothing leaves localhost. It was copied into six context sites
// across four scripts, identically, which is fine until something has to
// change beside it. Something did.
//
// THE CLERK COOKIE. `clerkMiddleware` answers a browser navigation with a 307
// to the dev-browser handshake whenever `__clerk_db_jwt` is absent, and says
// so in `x-clerk-auth-reason: dev-browser-missing`. Guard 1 then aborts the
// redirect, so the navigation fails with `ERR_SSL_VERSION_OR_CIPHER_MISMATCH`
// and the script dies before it photographs anything. The cure was found on
// 2026-10-24 and written into `shoot.mjs`, which was the script that run
// needed, and into the README as advice for "a new script". The five context
// sites that already existed were not a new script, so they kept the bug: on
// the next run `zoom.mjs` could not load a single page.
// (`INC-2026-10-24-the-clerk-cure-landed-in-one-of-the-four-scripts-that-needed-it`)
//
// This is not a credential and it is not a sign-in. The value is never
// validated, because the redirect is decided on the cookie's presence alone.
// Every page the harness photographs is a signed-out page, which is what the
// harness wants.
export async function ourContext(browser, opts = {}) {
  const ctx = await browser.newContext({ deviceScaleFactor: 1, ...opts });
  await ctx.addCookies(
    ["127.0.0.1", "localhost"].map((domain) => ({
      name: "__clerk_db_jwt",
      value: "dvb_visual_harness",
      domain,
      path: "/",
    }))
  );
  await ctx.route("**/*", (route) => {
    const u = new URL(route.request().url());
    if (u.hostname === "127.0.0.1" || u.hostname === "localhost") return route.continue();
    return route.abort();
  });
  return ctx;
}
