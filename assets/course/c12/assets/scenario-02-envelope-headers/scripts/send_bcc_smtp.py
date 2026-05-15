import argparse
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate


def main():
    p = argparse.ArgumentParser(
        description="Send an email with To and Bcc recipients via SMTP"
    )

    p.add_argument("--smtp-host", default="localhost")
    p.add_argument("--smtp-port", type=int, default=587)

    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)

    p.add_argument("--to", dest="to_addr", required=True)
    p.add_argument("--bcc", dest="bcc_addr", required=True)

    p.add_argument("--subject", default="Bcc demo")
    p.add_argument("--body", default="Testing Bcc behavior")

    # Local teaching stack does not advertise STARTTLS
    p.add_argument("--starttls", action="store_true", default=False)
    p.add_argument("--no-starttls", dest="starttls", action="store_false")

    args = p.parse_args()

    domain = args.user.split("@", 1)[1]

    msg = MIMEMultipart()

    msg["From"] = args.user

    # Visible recipient
    msg["To"] = args.to_addr

    # Intentionally NO Bcc header here
    # Bcc exists only in SMTP envelope recipients

    msg["Subject"] = args.subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=domain)

    msg.attach(MIMEText(args.body, "plain", "utf-8"))

    # SMTP envelope recipients
    recipients = [
        args.to_addr,
        args.bcc_addr
    ]

    with smtplib.SMTP(
        args.smtp_host,
        args.smtp_port,
        timeout=10
    ) as smtp:

        smtp.ehlo()

        if args.starttls:
            smtp.starttls()
            smtp.ehlo()

        smtp.login(args.user, args.password)

        smtp.sendmail(
            args.user,
            recipients,
            msg.as_string()
        )

        print("OK: email sent with Bcc recipient")


if __name__ == "__main__":
    main()