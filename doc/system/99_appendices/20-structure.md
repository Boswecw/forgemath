# Structure

`doc/system/` is the authored modular source tree. `BUILD.sh` concatenates
`_index.md` and every two-digit chapter in stable path order, validates the
assembled snapshot, and writes `doc/MATSYSTEM.md`. The assembled document is a
generated review artifact and must have no hand-authored drift.

Root `AGENTS.md` defines repository working rules. `CLAUDE.md` is a concise
agent-specific companion, `README.md` is an operator entry point, and `docs/`
contains design references or historical context.
