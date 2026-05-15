import argparse
import mimetypes
import smtplib

from pathlib import Path

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

from email.utils import make_msgid, formatdate


def main():
    p = argparse.ArgumentParser(
        description="Send an email attachment via SMTP"
    )

    p.add_argument("--smtp-host", default="localhost")
    p.add_argument("--smtp-port", type=int, default=587)

    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)

    p.add_argument("--to", dest="to_addr", required=True)

    p.add_argument("--subject", default="Attachment demo")
    p.add_argument(
        "--body",
        default="This message contains an attachment."
    )

    p.add_argument("--file", required=True)

    # local demo stack does not advertise STARTTLS
    p.add_argument("--starttls", action="store_true", default=False)
    p.add_argument("--no-starttls", dest="starttls", action="store_false")

    args = p.parse_args()

    attachment_path = Path(args.file)

    if not attachment_path.exists():
        print("Attachment file does not exist")
        return

    domain = args.user.split("@", 1)[1]

    msg = MIMEMultipart()

    msg["From"] = args.user
    msg["To"] = args.to_addr
    msg["Subject"] = args.subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=domain)

    # text body
    msg.attach(
        MIMEText(args.body, "plain", "utf-8")
    )

    # detect mime type
    mime_type, _ = mimetypes.guess_type(attachment_path.name)

    if mime_type is None:
        mime_type = "application/octet-stream"

    maintype, subtype = mime_type.split("/", 1)

    # attachment part
    with open(attachment_path, "rb") as f:
        part = MIMEBase(maintype, subtype)
        part.set_payload(f.read())

    # base64 encode binary content
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{attachment_path.name}"'
    )

    msg.attach(part)

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
            [args.to_addr],
            msg.as_string()
        )

        print("OK: attachment email sent")


if __name__ == "__main__":
    main()