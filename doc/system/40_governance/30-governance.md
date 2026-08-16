# Governance

Governed payload truth is append-only and versioned. Supersession closes prior
truth while preserving history; only explicit lifecycle fields may change in
place. Missing or incompatible bindings, retired or non-deterministic runtime
profiles, and cross-lane relationships fail closed.

Computed canonical truth enters through the governed execution service.
Manual evaluation ingest is limited to non-computed historical or audit
records. Projections remain derived read models and never become source truth.

Formula, weight, threshold, rounding, quantization, and supported-lane changes
require explicit mathematical governance and updated golden evidence. Caller-
supplied expressions are prohibited.

## Research contract boundary

`contracts/research/` contains strict JSON Schema 2020-12 research artifacts
for `MathDecisionReceipt.v1`, `EquationPackageManifest.v1`, and
`SignedEquationPackageResearch.v1`. They model content-addressed decision
evidence, governed package contents, provenance, redaction posture, signature
claims, and verification policy. They are not imported by `app/`, exposed by
an API, persisted in canonical tables, or used to activate executable math.

The schemas fail closed to the five registered lanes, canonical decimal strings,
complete governed artifact roles, `executable=false`, and
`arbitrary_expression_allowed=false`. The signature fixture is explicitly
unverified. Runtime adoption requires separate governance for canonical JSON,
real cryptographic verification, key trust and rotation, revocation, threshold
enforcement, storage, lifecycle, approval, and migrations.

The research mapping uses W3C PROV entity/activity/agent concepts, separates
build definition from run details following SLSA provenance v1.2, and requires
per-artifact digests following signed-bundle verification practice. These are
interoperability influences, not conformance claims.
