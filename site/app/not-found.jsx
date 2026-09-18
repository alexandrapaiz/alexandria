import Link from "next/link";

export const metadata = { title: "Not found — library of alexandr.ia" };

export default function NotFound() {
  return (
    <main className="page">
      <p className="page-kicker">404</p>
      <h1 className="page-title">That page does not exist.</h1>
      <p className="page-intro">
        The link may be out of date, or the address may have a typo in it.
        Everything the library has published is one page away.
      </p>
      <div className="page-cta">
        <Link href="/" className="pill ghost">
          Home
        </Link>
        <Link href="/library" className="pill">
          All issues
        </Link>
      </div>
    </main>
  );
}
