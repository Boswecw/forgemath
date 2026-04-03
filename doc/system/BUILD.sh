#!/bin/bash
set -euo pipefail

PARTS_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$PARTS_DIR/../.." && pwd)"
OUTPUT="$REPO_ROOT/SYSTEM.md"

echo "Assembling SYSTEM.md..."

cat "$PARTS_DIR/_index.md" > "$OUTPUT"

for part in "$PARTS_DIR"/[0-9][0-9]-*.md; do
  echo "" >> "$OUTPUT"
  echo "---" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  cat "$part" >> "$OUTPUT"
done

LINE_COUNT=$(wc -l < "$OUTPUT")
echo "SYSTEM.md assembled: $LINE_COUNT lines"

