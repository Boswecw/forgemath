# ForgeMath Canonical Equation Stack — Top-Level Overview

**Date:** April 2, 2026  
**Time Zone:** America/New_York

---

## Purpose

This document freezes the top-level architectural position for the ForgeMath math stack.

It converts the prior discussion into one clear implementation posture:

- what ForgeMath is,
- what kinds of lanes exist,
- what outputs are canonical,
- what must be governed alongside equations,
- and what the next implementation documents are expected to lock.

---

## Top-Level Thesis

ForgeMath is not a helper library and not a dashboard math convenience layer.

ForgeMath is the ecosystem’s **canonical constitutional math and rule authority**.

That means canonical lane results are only authoritative when they are produced through:

- approved lane specifications,
- approved variable vocabulary,
- immutable parameter bindings,
- approved threshold and policy bundles,
- deterministic runtime execution,
- compatible execution bindings,
- frozen input bundles,
- replay-aware persistence,
- and governed trace output.

If those conditions are not satisfied, authority must be reduced, blocked, or moved to audit-only posture.

---

## Core Architectural Position

A canonical ForgeMath result is no longer just:

```text
f(inputs, parameters) = output
```

It is now effectively:

```text
ForgeMathResult = f(inputs, parameters, policies, compatibility, runtime_profile)
```

subject to:

- admissibility,
- compatibility resolution,
- deterministic execution enforcement,
- result-status classification,
- replay classification,
- stale-state doctrine,
- and trace-tier rules.

---

## Lane Classes

ForgeMath should treat lane families in three distinct classes.

### Class 1 — Canonical numeric lanes

These are proper numeric or bounded composite lanes:

- Verification Burden
- Recurrence Pressure
- Exposure Factor
- Control Effectiveness
- Governance Velocity
- Residual Governance Risk
- Priority Score
- Improvement Yield

### Class 2 — Hybrid gate lanes

These must not be reduced to pure scalar math:

- Reviewability

A hybrid lane may emit:

- numeric posture,
- classified posture,
- blocked posture,
- degraded posture,
- audit-only posture,
- or invalid posture.

### Class 3 — Governance support surfaces

These are not ordinary incident lanes, but they govern whether canonical outputs are valid at all:

- compatibility resolution state
- replay state
- stale state
- result status
- trace tier
- determinism certificate / runtime profile

---

## Canonical Result Doctrine

Every canonical lane result must bind to:

- lane spec version
- variable registry version
- parameter set version
- threshold registry version
- prior registry version where applicable
- decay registry version where applicable
- null policy version
- degraded mode policy version
- trace schema version
- projection schema version
- submodule build version
- deterministic runtime profile
- frozen input bundle id / hash

No single parameter set alone is enough to validate a result.

---

## Required Output Layers

Each canonical lane should emit outputs in layers.

### Layer 1 — Root evaluation record
One authoritative evaluation fact.

### Layer 2 — Output values
Raw, banded, classified, or gated values.

### Layer 3 — Factor values
Contributing raw, normalized, and weighted factors.

### Layer 4 — Trace bundle
Trace information at the required tier.

### Layer 5 — Projection record
Read-model output for ForgeCommand and related surfaces.

---

## Required Status Surfaces

Every canonical evaluation must explicitly emit:

### Result status
- `computed_strict`
- `computed_degraded`
- `blocked`
- `audit_only`
- `invalid`

### Replay state
- `replay_safe`
- `replay_safe_with_bounded_migration`
- `audit_readable_only`
- `not_replayable`

### Stale state
- `fresh`
- `stale_upstream_changed`
- `stale_policy_superseded`
- `stale_input_invalidated`
- `stale_semantics_changed`
- `stale_determinism_retired`

---

## Determinism Doctrine

A lane cannot claim canonical status unless runtime determinism is enforced, not assumed.

Every execution path should bind to a deterministic runtime profile that fixes:

- numeric precision mode
- rounding mode
- sort / accumulation order
- serialization policy
- timezone policy
- seed policy
- nondeterminism prohibition

For bit-exact lanes, repeated execution over the same frozen bundle and same compatibility tuple should produce byte-identical canonical outputs.

---

## Persistence Doctrine

ForgeMath should persist canonical truth using an append-only, replay-aware posture.

### Control and registry truth
Best held in Postgres:

- lane specs
- variable registry
- parameter sets
- threshold sets
- policy bundles
- determinism policies
- compatibility matrices
- override audit
- runtime profiles
- migration packages

### High-volume fact and trace truth
Best held in append-optimized fact storage:

- lane evaluations
- factor values
- output values
- trace bundles
- trace events
- replay diagnostics
- projection records

---

## Top-Level Lane Position

The current recommended first implementation lane wave remains:

- Verification Burden
- Recurrence Pressure
- Exposure Factor
- Priority Score
- Reviewability

But the full canonical equation stack should already be designed to accommodate the second wave:

- Control Effectiveness
- Governance Velocity
- Residual Governance Risk
- Improvement Yield

---

## Implementation Rule

Every lane spec should include seven sections at minimum:

1. equation or rule definition
2. admitted input variables
3. parameter and cap set
4. null / degraded policy dependencies
5. result-status behavior
6. replay / trace requirements
7. persistence outputs

---

## What Comes Next

This top-level document implies two deeper implementation documents:

1. **ForgeMath Canonical Equation Specification v1**
2. **ForgeMath Lane Governance, Persistence, Replay, and Runtime Contract v1**

Together, those documents are sufficient to move from planning posture into schema, DDL, DTO, and build sequencing work.

---

## Final Position

ForgeMath is now past “what should this be?”

It should be treated as:

- one canonical math authority,
- one governed equation stack,
- one replay-aware persistence surface,
- one deterministic runtime contract,
- and one ecosystem-wide mathematical control plane.

That is the top-level position to carry forward.

