#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIG_RE = re.compile(r"^\[FIG\]\s+(.+?)\s*$", re.MULTILINE)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

def to_assets_images_path(raw_path: str) -> str:
    p = raw_path.strip().strip("<>").strip()

    # Do not touch URLs or data URIs
    if re.match(r"^(https?://|data:)", p, re.IGNORECASE):
        return p

    # Normalize slashes and strip leading ./ or /
    p = p.replace("\\", "/")
    p = re.sub(r"^(\./)+", "", p)
    p = p.lstrip("/")

    # Map any path to assets/images/<original path>
    return f"./assets/images/{p}"

def preprocess(markdown: str) -> str:
    # [FIG] something.png -> ![](./assets/images/something.png)
    def fig_repl(m: re.Match) -> str:
        path = m.group(1)
        return f"![]({to_assets_images_path(path)})"

    markdown = FIG_RE.sub(fig_repl, markdown)

    # Rewrite existing markdown images to ./assets/images/...
    def img_repl(m: re.Match) -> str:
        alt = m.group(1)
        path = m.group(2)
        new_path = to_assets_images_path(path)
        return f"![{alt}]({new_path})"

    markdown = IMG_RE.sub(img_repl, markdown)

    return markdown

def main() -> int:
    ap = argparse.ArgumentParser(description="Convert markdown to pptx via pandoc, mapping images into ./assets/images.")
    ap.add_argument("input_md", help="Input markdown file")
    ap.add_argument("-t", "--template", help="Reference template PPTX (optional)", default="")
    ap.add_argument("-o", "--output", help="Output PPTX path (optional). Default: input basename + .pptx", default="")
    args = ap.parse_args()

    input_md = Path(args.input_md)
    if not input_md.exists():
        print(f"Error: input file not found: {input_md}", file=sys.stderr)
        return 1

    asset_dir = Path("./assets/images")
    if not asset_dir.is_dir():
        print("Error: asset dir not found: ./assets/images", file=sys.stderr)
        return 1

    if args.template:
        template = Path(args.template)
        if not template.exists():
            print(f"Error: template not found: {template}", file=sys.stderr)
            return 1
    else:
        template = None

    if args.output:
        output = Path(args.output)
    else:
        output = input_md.with_suffix(".pptx")

    if shutil.which("pandoc") is None:
        print("Error: pandoc not found in PATH", file=sys.stderr)
        return 1

    original = input_md.read_text(encoding="utf-8")
    processed = preprocess(original)

    with tempfile.TemporaryDirectory() as td:
        tmp_md = Path(td) / (input_md.stem + ".pandoc.md")
        tmp_md.write_text(processed, encoding="utf-8")

        cmd = ["pandoc", str(tmp_md), "-t", "pptx", "-o", str(output)]
        if template is not None:
            cmd.append(f"--reference-doc={template}")

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: pandoc failed with exit code {e.returncode}", file=sys.stderr)
            return e.returncode

    print(f"Wrote: {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
