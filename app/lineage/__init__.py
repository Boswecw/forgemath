"""ForgeLineage emission for ForgeMath (Phase 07).

Maps ForgeMath's internal lane evaluation, output, runtime admission, and
trace concepts into shared LineageNode/ImpactEdge contracts. Non-blocking:
emission failure does not interrupt evaluation.
"""

from app.lineage.emitter import (
    ForgeMathLineageEmitter,
    LineageEmissionStatus,
    NullLineageEmitter,
)

__all__ = ["ForgeMathLineageEmitter", "LineageEmissionStatus", "NullLineageEmitter"]
