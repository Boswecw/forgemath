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
