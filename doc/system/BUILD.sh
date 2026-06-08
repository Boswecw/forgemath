#!/usr/bin/env bash
set -euo pipefail

PARTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$PARTS_DIR/../.." && pwd)"
OUTPUT="${OUTPUT:-doc/MATSYSTEM.md}"
VALIDATOR="$PARTS_DIR/validate_snapshots.sh"

mkdir -p "$(dirname "$ROOT_DIR/$OUTPUT")"

TMP_OUTPUT="$(mktemp)"
trap 'rm -f "$TMP_OUTPUT"' EXIT

if [ -f "$PARTS_DIR/_index.md" ]; then
  cat "$PARTS_DIR/_index.md" > "$TMP_OUTPUT"
fi

# Assemble an explicitly-enumerated chapter set so the build is deterministic.
# Two numbering schemes currently live in this directory: the granular content
# chapters below, and the Forge Documentation Protocol v1 skeleton stubs
# (00-overview, 01-architecture, 10-scope, 20-structure, 30-governance,
# 40-change-control, 90-appendices). A bare [0-9][0-9]-*.md glob would
# concatenate BOTH and duplicate the artifact, so the content chapters are
# listed here. Consolidating onto a single scheme is a tracked follow-up
# (see 15-handover-migration-notes.md, Deferred Work).
PARTS=(
  "01-overview-philosophy.md"
  "02-architecture.md"
  "03-tech-stack.md"
  "04-project-structure.md"
  "05-configuration.md"
  "06-design-system.md"
  "07-frontend.md"
  "08-api-layer.md"
  "09-backend.md"
  "10-ecosystem-integration.md"
  "11-database-schema.md"
  "12-ai-integration.md"
  "13-error-handling.md"
  "14-testing-infrastructure.md"
  "15-handover-migration-notes.md"
)
for part in "${PARTS[@]}"; do
  part_path="$PARTS_DIR/$part"
  if [ ! -f "$part_path" ]; then
    echo "assembly failed: missing chapter $part" >&2
    exit 1
  fi
  echo "" >> "$TMP_OUTPUT"
  echo "---" >> "$TMP_OUTPUT"
  echo "" >> "$TMP_OUTPUT"
  cat "$part_path" >> "$TMP_OUTPUT"
done

if [ -x "$VALIDATOR" ]; then
  bash "$VALIDATOR" "$TMP_OUTPUT"
fi

cp "$TMP_OUTPUT" "$ROOT_DIR/$OUTPUT"
chmod 664 "$ROOT_DIR/$OUTPUT"

LINE_COUNT=$(wc -l < "$ROOT_DIR/$OUTPUT")
echo "$OUTPUT assembled: $LINE_COUNT lines"
