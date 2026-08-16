# Architecture Surfaces

ForgeMath exposes two distinct authority surfaces:

1. The FastAPI service routes governed registry writes and reads, manual
   non-computed ingest, canonical bounded lane execution, lifecycle and
   admission inspection, and projections through SQLAlchemy persistence.
2. The Evaluation Spine CLI reads a calibration-report contract and writes a
   deterministic ForgeMath contract artifact. It does not call the FastAPI
   lane-execution route and does not expand the three registered API lanes.

The lightweight health CLI is a third operational interface, not a math lane.
Its default mode checks only the Evaluation Spine CLI import surface for
Forge_Command. Explicit `--readiness` mode inspects local service readiness
without creating or migrating a database or contacting lineage transport.
