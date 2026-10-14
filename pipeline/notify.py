"""The owner's alarm, for any job that can fail while nobody is watching.

`pipeline/weekly.py` has had `notify_owner` since incident 24, whose real cost
was not the 404 but the three days it took the owner to notice her inbox was
empty. That function is press-shaped: its body names the press, the issue and
the subscriber list. This is the same channel with the press taken out of it, so
a second unattended job does not have to choose between copying thirty lines and
alarming nobody.

Same Gmail secret, same SMTP path, so it needs no new secret and no new service.
`weekly.py` keeps its own copy for now rather than importing this one: the press
is the one job in the pipeline that must not be touched by a change made for
something else, and consolidating the two is a separate commit on a day when the
press is not the subject.

Never raises. A failure to deliver the alarm must not replace the original error
with a different one, so this returns a status string and the caller prints it.
"""

from __future__ import annotations


def notify_owner(subject: str, detail: str, what_to_check: list[str],
                 sender: str = "alexandria") -> str:
    """Mail the owner. Returns what happened, including when nothing did."""
    import os
    import smtplib
    from email.mime.text import MIMEText

    addr = (os.environ.get("GMAIL_ADDRESS") or "").strip()
    pw = (os.environ.get("GMAIL_APP_PASSWORD") or "").strip()
    to = (os.environ.get("PRESS_ALERT_TO") or "").strip() or addr
    if not addr or not pw:
        return ("NOT NOTIFIED: no gmail secret in this environment, so the "
                "owner was not told. This is the incident 24 failure mode and "
                "it is still open here.")

    steps = "\n".join(f"  {n}. {line}"
                      for n, line in enumerate(what_to_check, start=1))
    body = f"{detail}\n\n-- \nWhat to check, in order:\n{steps}\n"
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = f"{sender} <{addr}>"
        msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(addr, pw)
            smtp.sendmail(addr, [to], msg.as_string())
    except Exception as exc:
        return f"NOT NOTIFIED: the alarm email itself failed ({exc})"
    return f"owner notified at {to}: {subject}"
