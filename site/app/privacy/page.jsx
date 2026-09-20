export const metadata = { title: "Privacy — library of alexandr.ia" };

export default function Privacy() {
  return (
    <main className="page">
      <p className="page-kicker">Privacy</p>
      <h1 className="page-title">What we hold, and what we do not.</h1>
      <div className="prose">
        <p>
          <b>Last updated 19 September 2026.</b> This policy explains what
          personal data the library collects, why, and how you get it back or
          get rid of it. The library is run by Alexandra Paiz Delgado in
          Guatemala, who is the data controller for everything described here.
          Questions and requests go to{" "}
          <a href="mailto:hello@libraryofalexandria.dev">
            hello@libraryofalexandria.dev
          </a>
          .
        </p>

        <h2>The short version</h2>
        <p>
          There is no analytics, no tracking pixel, no advertising network,
          and no third-party script watching you read. Nothing is sold or
          rented to anyone, ever. The only personal data the library holds is
          what you typed in yourself, which is your email address and
          optionally your name.
        </p>

        <h2>What is collected</h2>
        <p>
          <b>If you join the digest</b>, the library stores your email
          address, your name when you give one, which list you are on, and
          whether you are still subscribed. It also stores which page you
          signed up from, so it is possible to tell which writing brings
          people in. That is all.
        </p>
        <p>
          <b>If you create an account</b>, authentication is handled by Clerk,
          which stores your email address, your name when you give one, and
          your login credentials. The library itself keeps only an account
          identifier, your email, your name, and your subscription status. The
          library never sees or stores your password.
        </p>
        <p>
          <b>If you subscribe to the paid tier</b>, payment is handled
          entirely by Polar, which acts as the merchant of record. Polar
          collects your payment and billing details under its own privacy
          policy. The library never receives your card number and never stores
          payment details.
        </p>
        <p>
          <b>Server logs.</b> Hosting produces ordinary request logs that may
          include IP addresses, kept briefly for security and debugging. These
          are not used to build a profile of you.
        </p>

        <h2>Why it is held</h2>
        <p>
          Your email exists so the digest can reach you, which is the thing
          you asked for. Account data exists so you can sign in and so the
          library knows what you have access to. Subscription status exists so
          paid features work. There is no other purpose, and your data is
          never used to train a model.
        </p>
        <p>
          The legal basis, for readers in Europe and the United Kingdom, is
          your consent for the digest and the performance of a contract for
          accounts and paid features. You may withdraw consent at any time,
          which is what the unsubscribe link does.
        </p>

        <h2>Who processes it</h2>
        <p>
          The library uses a small number of service providers, and each one
          only touches what it needs. Clerk handles authentication. Neon hosts
          the database. Vercel hosts the site. Polar processes payments and is
          the seller of record for them. During the current early phase the
          weekly digest is delivered through Gmail, which means your email
          address passes through that account when an issue is sent. Each of
          these providers processes data on the library&rsquo;s instructions
          and under its own security commitments.
        </p>
        <p>
          The research pipeline that reads papers and writes the digest runs on
          separate infrastructure and never receives subscriber data.
        </p>

        <h2>How long it is kept</h2>
        <p>
          Subscriber records are kept while you are subscribed. When you
          unsubscribe, the record is marked inactive and kept only so the
          library does not accidentally email you again, and you can ask for
          it to be deleted outright. Account data is kept while the account
          exists and is deleted when you delete the account. Payment records
          are kept by Polar for as long as tax law requires them.
        </p>

        <h2>Your rights</h2>
        <p>
          You can ask for a copy of everything held about you, ask for it to
          be corrected, ask for it to be deleted, ask for it in a portable
          format, or object to a particular use. Write to{" "}
          <a href="mailto:hello@libraryofalexandria.dev">
            hello@libraryofalexandria.dev
          </a>{" "}
          and it will be handled within thirty days, usually much sooner. You
          do not need an account to make a request, and you will not be asked
          why. Every digest also carries an unsubscribe link that works
          immediately without writing to anyone.
        </p>
        <p>
          Readers in Europe and the United Kingdom also have the right to
          complain to a local data protection authority.
        </p>

        <h2>Transfers, children, and changes</h2>
        <p>
          The library is operated from Guatemala and its providers operate
          servers in the United States and Europe, so your data is processed in
          those places. The library is not intended for children under 16 and
          does not knowingly collect their data.
        </p>
        <p>
          If this policy changes in a way that matters, the date above changes
          and subscribers are told in the digest before the change takes
          effect. Minor wording fixes will not be announced.
        </p>
      </div>
    </main>
  );
}
