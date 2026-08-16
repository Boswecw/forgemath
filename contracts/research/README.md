# ForgeMath research contracts

These JSON Schema 2020-12 contracts are non-runtime research artifacts. They
do not authorize a lane, activate an equation package, verify a signature,
persist a receipt, or change canonical mathematical behavior.

- `MathDecisionReceipt.v1` models content-addressed inputs, outputs, trace,
  redaction posture, governed package identity, and responsibility metadata.
- `EquationPackageManifest.v1` models an immutable manifest of governed
  equation-package artifacts and build provenance.
- `SignedEquationPackageResearch.v1` models signature claims and a verification
  policy around the manifest. Its fixtures are deliberately marked unverified.

The provenance vocabulary maps ForgeMath entities, evaluation activities, and
responsible agents to the concepts in [W3C PROV-DM](https://www.w3.org/TR/prov-dm/).
The build-provenance shape follows the separation between build definition and
run details in [SLSA provenance v1.2](https://slsa.dev/spec/v1.2/build-provenance).
The manifest requires per-artifact digests, following the signed-bundle lesson
that every activated file must be covered by verification; see
[OPA bundle signing](https://www.openpolicyagent.org/docs/management-bundles#signing).

The fixtures derive `manifest_digest` from UTF-8 JSON with recursively sorted
object keys and compact separators. That recipe exists only to make the
research fixtures reproducible; it is not yet a governed canonical-JSON or
signature payload standard.

Before any runtime adoption, a separately authorized design must define
canonical JSON serialization, real signature creation and verification,
key trust and rotation, revocation, threshold enforcement, storage, lifecycle,
promotion approval, and migration behavior. Until then, every artifact here is
fail-closed research evidence only.
