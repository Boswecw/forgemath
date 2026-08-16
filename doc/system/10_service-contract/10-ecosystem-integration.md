## 10. Ecosystem Integration

ForgeMath keeps its canonical math locally owned while exposing explicit,
bounded integration surfaces. Optional integration is not equivalent to no
integration: the Evaluation Spine file evaluation remains usable when lineage
is disabled or unavailable.

### 10.1 Current Integration State

| Service | Current relationship | Notes |
|--------|----------------------|-------|
| DataForge-Local | Optional ForgeLineage destination | When `FORGEMATH_LINEAGE_URL` is set, the Evaluation Spine flow emits ForgeMath-owned evaluation/output nodes and an optional consumed edge; default-off and non-blocking |
| Forge_Command | Health and artifact consumer | Invokes `python -m app.health_cli`; its gate walk may resolve the rich output contract artifact referenced by lineage |
| ForgeLineage | Pinned SDK contract | CI checks out a fixed SDK revision for lineage tests; the transport is never contacted by readiness |
| NeuroForge | None | No runtime AI inference path in this repository |

### 10.2 Evaluation Spine Boundary

`python -m app.evaluation_spine_cli` is a deterministic file-in/file-out
authority. It consumes an eval-calibration report and writes a ForgeMath lane
evaluation reference contract. This is distinct from the FastAPI bounded
execution service and does not add a fourth registered API execution lane.

The emitted `forgemath_output` node remains identity-only. The rich evaluation
result and `proposal_candidate_allowed` gate live in the referenced contract
artifact for Forge_Command to resolve.

### 10.3 Governance Inputs

The repo is grounded by external governing docs, but those documents are not
runtime dependencies. They are operator and design inputs.

