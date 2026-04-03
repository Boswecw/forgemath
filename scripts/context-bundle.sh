#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SYSTEM_DIR="$REPO_ROOT/doc/system"
OUTPUT="$REPO_ROOT/context-bundle.md"
ROADMAP="$REPO_ROOT/docs/forge_math_extended_roadmap.md"

WITH_ROADMAP=false
WITH_SPECS=false
DRY_RUN=false
LIST_ONLY=false
INCLUDE_ALL=false
PRESET=""
declare -a SECTIONS=()

show_list() {
  echo "Available sections:"
  for part in "$SYSTEM_DIR"/[0-9][0-9]-*.md; do
    basename "$part"
  done
  echo
  echo "Presets:"
  echo "  foundation -> 01 02 03 04 05 08 09 10 11 14 15"
  echo "  api        -> 05 08 09 11 13 14"
  echo "  schema     -> 02 05 09 11 13 15"
  echo "  docs       -> 01 02 04 10 12 15"
}

resolve_preset() {
  case "$1" in
    foundation) SECTIONS=(01 02 03 04 05 08 09 10 11 14 15) ;;
    api) SECTIONS=(05 08 09 11 13 14) ;;
    schema) SECTIONS=(02 05 09 11 13 15) ;;
    docs) SECTIONS=(01 02 04 10 12 15) ;;
    *)
      echo "Unknown preset: $1" >&2
      exit 1
      ;;
  esac
}

resolve_section_file() {
  local section="$1"
  local matches=("$SYSTEM_DIR"/"$section"-*.md)
  if [ ! -e "${matches[0]}" ]; then
    echo "Missing section file for $section" >&2
    exit 1
  fi
  printf '%s\n' "${matches[0]}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --list)
      LIST_ONLY=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --preset)
      PRESET="$2"
      shift 2
      ;;
    --all)
      INCLUDE_ALL=true
      shift
      ;;
    --with-roadmap)
      WITH_ROADMAP=true
      shift
      ;;
    --with-specs)
      WITH_SPECS=true
      shift
      ;;
    *)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        printf -v PADDED "%02d" "$1"
        SECTIONS+=("$PADDED")
        shift
      else
        echo "Unknown argument: $1" >&2
        exit 1
      fi
      ;;
  esac
done

if [ "$LIST_ONLY" = true ]; then
  show_list
  exit 0
fi

if [ -n "$PRESET" ]; then
  resolve_preset "$PRESET"
fi

if [ "$INCLUDE_ALL" = true ]; then
  SECTIONS=()
  for part in "$SYSTEM_DIR"/[0-9][0-9]-*.md; do
    SECTIONS+=("$(basename "$part" | cut -d- -f1)")
  done
fi

if [ ${#SECTIONS[@]} -eq 0 ]; then
  SECTIONS=(01 02 03 04 05 08 09 10 11 14 15)
fi

if [ "$DRY_RUN" = true ]; then
  echo "Would assemble:"
  for section in "${SECTIONS[@]}"; do
    file="$(resolve_section_file "$section")"
    echo "  $section -> $(basename "$file") ($(wc -l < "$file") lines)"
  done
  if [ "$WITH_ROADMAP" = true ]; then
    echo "  roadmap -> $(basename "$ROADMAP") ($(wc -l < "$ROADMAP") lines)"
  fi
  if [ "$WITH_SPECS" = true ]; then
    for spec in "$REPO_ROOT"/docs/*module_spec*.md; do
      [ -e "$spec" ] || continue
      echo "  spec -> $(basename "$spec") ($(wc -l < "$spec") lines)"
    done
  fi
  exit 0
fi

INDEX_FILE="$SYSTEM_DIR/_index.md"
cat "$INDEX_FILE" > "$OUTPUT"

for section in "${SECTIONS[@]}"; do
  file="$(resolve_section_file "$section")"
  echo "" >> "$OUTPUT"
  echo "---" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  cat "$file" >> "$OUTPUT"
done

if [ "$WITH_ROADMAP" = true ]; then
  echo "" >> "$OUTPUT"
  echo "---" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  cat "$ROADMAP" >> "$OUTPUT"
fi

if [ "$WITH_SPECS" = true ]; then
  for spec in "$REPO_ROOT"/docs/*module_spec*.md; do
    [ -e "$spec" ] || continue
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$spec" >> "$OUTPUT"
  done
fi

echo "context-bundle.md assembled: $(wc -l < "$OUTPUT") lines"
