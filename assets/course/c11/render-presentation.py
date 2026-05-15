#!/usr/bin/env python3
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIG_RE = re.compile(r"^[ \t]*\[FIG\][ \t]+(.+?)[ \t]*$", re.MULTILINE)
SCENARIO_RE = re.compile(r"^[ \t]*\[SCENARIO\][ \t]+(.+?)[ \t]*$", re.MULTILINE)

def is_url(path: str) -> bool:
    return bool(re.match(r"^(https?://|data:)", path, re.IGNORECASE))

def normalize_inline_image_path(raw_path: str) -> str:
    p = raw_path.strip()

    if p.startswith("<") and p.endswith(">"):
        p = p[1:-1].strip()

    return p

def fig_repl(m: re.Match) -> str:
    path = normalize_inline_image_path(m.group(1))
    # blank lines around figure help pandoc keep blocks separated
    return f"\n![]({path})\n"

def scenario_repl(m: re.Match) -> str:
    path = m.group(1).strip()
    # leave as plain text or convert to a visible marker if needed
    # for now keep it as a paragraph so it doesn't break surrounding blocks
    return f"\n`[SCENARIO] {path}`\n"

def normalize_markdown(md: str) -> str:
    # Convert [FIG] lines to normal markdown images
    md = FIG_RE.sub(fig_repl, md)

    # Prevent custom scenario markers from confusing block parsing
    md = SCENARIO_RE.sub(scenario_repl, md)

    # Normalize line endings
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    # Ensure images are separated from surrounding blocks
    md = re.sub(r"\n(!\[[^\]]*\]\([^)]+\))\n?", r"\n\n\1\n\n", md)

    # Collapse excessive blank lines, but keep block separation
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip() + "\n"

def main() -> int:
    ap = argparse.ArgumentParser(description="Convert markdown to pptx via pandoc")
    ap.add_argument("input_md", help="Input markdown file")
    ap.add_argument("-t", "--template", help="Reference template PPTX", default="")
    ap.add_argument("-o", "--output", help="Output PPTX path", default="")
    args = ap.parse_args()

    input_md = Path(args.input_md).resolve()
    if not input_md.exists():
        print(f"Error: input file not found: {input_md}", file=sys.stderr)
        return 1

    base_dir = input_md.parent

    if args.template:
        template = Path(args.template).resolve()
        if not template.exists():
            print(f"Error: template not found: {template}", file=sys.stderr)
            return 1
    else:
        template = None

    output = Path(args.output).resolve() if args.output else input_md.with_suffix(".pptx")

    if shutil.which("pandoc") is None:
        print("Error: pandoc not found in PATH", file=sys.stderr)
        return 1

    original = input_md.read_text(encoding="utf-8")
    processed = normalize_markdown(original)

    with tempfile.TemporaryDirectory() as td:
        tmp_md = Path(td) / f"{input_md.stem}.pandoc.md"
        tmp_md.write_text(processed, encoding="utf-8")

        resource_paths = [
            str(base_dir),
            str(base_dir / "assets"),
            str(base_dir / "assets" / "images"),
        ]

        cmd = [
            "pandoc",
            str(tmp_md),
            "--from=markdown",
            "--to=pptx",
            "--output", str(output),
            "--resource-path=" + ":".join(resource_paths),
        ]

        if template is not None:
            cmd.append(f"--reference-doc={template}")

        try:
            subprocess.run(cmd, check=True, cwd=str(base_dir))
        except subprocess.CalledProcessError as e:
            print(f"Error: pandoc failed with exit code {e.returncode}", file=sys.stderr)
            return e.returncode

    print(f"Wrote: {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())