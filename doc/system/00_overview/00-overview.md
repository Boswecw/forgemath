# Overview

> **System identity — bds family (Boswell Digital Solutions business system, local-systems tier).** ForgeMath is the Forge ecosystem's backend canonical math and governed rule-evaluation authority under `ecosystem/local-systems`.

ForgeMath owns versioned governance registries, canonical evaluation and
lifecycle truth, deterministic runtime-admission evidence, bounded execution,
and truth-preserving projections. It also provides a distinct file-based
Evaluation Spine CLI and optional ForgeLineage emission.

Its authority is intentionally bounded. ForgeMath is not a helper library, a
general policy engine, a symbolic-algebra service, or an arbitrary expression
executor. Human-approved typed contracts and code define the supported math.

The current FastAPI execution surface supports exactly five governed lanes:
the numeric lanes `verification_burden`, `recurrence_pressure`,
`exposure_factor`, and `priority_score`, plus the `reviewability` hybrid gate.
