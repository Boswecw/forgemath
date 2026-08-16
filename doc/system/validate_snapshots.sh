#!/usr/bin/env bash
set -euo pipefail

PARTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$PARTS_DIR/../.." && pwd)"
ASSEMBLED_OUTPUT="${1:-$ROOT_DIR/doc/MATSYSTEM.md}"

require_contains() {
  local file="$1"; local needle="$2"; local label="$3"
  if ! grep -Fq -- "$needle" "$file"; then echo "snapshot validation failed: $label missing in $file" >&2; echo "expected: $needle" >&2; exit 1; fi
}
require_absent() {
  local file="$1"; local needle="$2"; local label="$3"
  if grep -Fq -- "$needle" "$file"; then echo "snapshot validation failed: $label still present in $file" >&2; echo "unexpected: $needle" >&2; exit 1; fi
}

require_contains "$PARTS_DIR/_index.md" "**Designation:** MAT" "index designation"
require_contains "$PARTS_DIR/_index.md" "BDS Documentation Protocol v2.0" "index protocol"
require_contains "$PARTS_DIR/_index.md" 'Primary output: `doc/MATSYSTEM.md`' "index primary output"
require_contains "$PARTS_DIR/BUILD.sh" 'DESIGNATION="MAT"' "build designation"
require_absent "$PARTS_DIR/_index.md" 'Primary output: `doc/SYSTEM.md`' "index legacy primary output"
test -f "$ASSEMBLED_OUTPUT"
require_contains "$ASSEMBLED_OUTPUT" "Document version" "assembled document version header"
require_contains "$ASSEMBLED_OUTPUT" "**Designation:** MAT" "assembled designation"
require_contains "$ASSEMBLED_OUTPUT" 'Primary output: `doc/MATSYSTEM.md`' "assembled primary output"
require_contains "$ASSEMBLED_OUTPUT" "BDS Documentation Protocol v2.0" "assembled protocol"
require_contains "$ASSEMBLED_OUTPUT" "truth classes" "assembled truth classes"
require_contains "$ASSEMBLED_OUTPUT" '`verification_burden`' "verification burden lane"
require_contains "$ASSEMBLED_OUTPUT" '`recurrence_pressure`' "recurrence pressure lane"
require_contains "$ASSEMBLED_OUTPUT" '`exposure_factor`' "exposure factor lane"
require_contains "$ASSEMBLED_OUTPUT" "Evaluation Spine CLI" "Evaluation Spine surface"
require_contains "$ASSEMBLED_OUTPUT" "Forge_Command" "Forge Command relationship"
require_contains "$ASSEMBLED_OUTPUT" "FORGEMATH_LINEAGE_URL" "optional lineage configuration"
require_absent "$ASSEMBLED_OUTPUT" "registry-generated bootstrap scaffold" "bootstrap placeholder"
require_absent "$ASSEMBLED_OUTPUT" "| DataForge | None at runtime |" "stale DataForge relationship"
echo "snapshot validation passed: $ASSEMBLED_OUTPUT"
