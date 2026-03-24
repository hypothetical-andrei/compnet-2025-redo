#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input-folder> <output-folder>"
  exit 1
fi

INPUT_DIR="$(realpath "$1")"
OUTPUT_DIR="$(realpath "$2")"

if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: input folder does not exist: $INPUT_DIR"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "Error: pdflatex is not installed"
  exit 1
fi

if ! command -v convert >/dev/null 2>&1; then
  echo "Error: ImageMagick 'convert' is not installed"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

find "$INPUT_DIR" -type f -name '*.tex' | while IFS= read -r TEX_FILE; do
  REL_PATH="${TEX_FILE#$INPUT_DIR/}"
  REL_DIR="$(dirname "$REL_PATH")"
  BASE_NAME="$(basename "$TEX_FILE" .tex)"

  mkdir -p "$OUTPUT_DIR/$REL_DIR"

  WORK_DIR="$TMP_DIR/${BASE_NAME}_$$"
  mkdir -p "$WORK_DIR"
  cp "$TEX_FILE" "$WORK_DIR/"

  echo "Rendering $REL_PATH..."

  (
    cd "$WORK_DIR"
    pdflatex -interaction=nonstopmode -halt-on-error "$BASE_NAME.tex" >/dev/null
    convert -density 300 "$BASE_NAME.pdf" -quality 100 "$OUTPUT_DIR/$REL_DIR/$BASE_NAME.png"
  )

  echo " -> $OUTPUT_DIR/$REL_DIR/$BASE_NAME.png"
done