import json
import time
import socket
import paramiko


def run_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err


def connect_with_retry(host, port, username, password, retries=20, delay=1):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            print(f"connecting to {host}:{port}, attempt {attempt}/{retries}", flush=True)

            # Debug Docker DNS visibility.
            print(f"{host} resolves to {socket.gethostbyname(host)}", flush=True)

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10,
                banner_timeout=10,
                auth_timeout=10,
            )
            return ssh

        except (OSError, paramiko.SSHException) as err:
            last_error = err
            print(f"SSH not ready yet: {err}", flush=True)
            time.sleep(delay)

    raise RuntimeError(f"Could not connect to {host}:{port}") from last_error


def main():
    with open("plan.json", "r", encoding="utf-8") as f:
        plan = json.load(f)

    for h in plan["hosts"]:
        ssh = connect_with_retry(
            host=h["host"],
            port=h.get("port", 22),
            username=h["user"],
            password=h.get("password"),
        )

        print("connected to", h["host"], flush=True)

        for cmd in h.get("commands", []):
            print("run", cmd, flush=True)
            out, err = run_cmd(ssh, cmd)
            if out.strip():
                print("[out]", out.strip(), flush=True)
            if err.strip():
                print("[err]", err.strip(), flush=True)

        sftp = ssh.open_sftp()
        for fobj in h.get("files", []):
            print("upload", fobj["src"], "->", fobj["dst"], flush=True)
            sftp.put(fobj["src"], fobj["dst"])
        sftp.close()

        out, _ = run_cmd(ssh, "ls -la ~/site && cat ~/site/status.txt")
        print(out, flush=True)

        ssh.close()


if __name__ == "__main__":
    main()