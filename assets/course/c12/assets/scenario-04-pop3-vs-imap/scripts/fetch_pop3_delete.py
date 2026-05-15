import argparse
import poplib

from email.parser import BytesParser
from email.policy import default


def main():
    p = argparse.ArgumentParser(
        description="Fetch latest email via POP3, then delete it"
    )

    p.add_argument("--pop3-host", default="localhost")
    p.add_argument("--pop3-port", type=int, default=110)

    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)

    args = p.parse_args()

    if args.pop3_port == 995:
        pop = poplib.POP3_SSL(args.pop3_host, args.pop3_port, timeout=10)
    else:
        pop = poplib.POP3(args.pop3_host, args.pop3_port, timeout=10)

    try:
        pop.user(args.user)
        pop.pass_(args.password)

        count, _size = pop.stat()

        if count == 0:
            print("Mailbox is empty")
            return

        resp, lines, octets = pop.retr(count)

        raw = b"\r\n".join(lines)
        msg = BytesParser(policy=default).parsebytes(raw)

        print("From:", msg.get("From"))
        print("To:", msg.get("To"))
        print("Subject:", msg.get("Subject"))
        print("Date:", msg.get("Date"))
        print("Size:", octets, "bytes")

        pop.dele(count)

        print("Deleted message number:", count)

    finally:
        pop.quit()


if __name__ == "__main__":
    main()