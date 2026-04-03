from datetime import datetime, timezone

import pytest

from app.schemas.evaluation import InputBundleCreate
from app.services.evaluation_service import create_input_bundle
from app.services.immutability import ImmutablePayloadError


def test_input_bundle_payload_is_immutable_once_persisted(db):
    bundle = create_input_bundle(
        db,
        InputBundleCreate(
            input_bundle_id="bundle-immutability-001",
            provenance_class="operator_collected",
            collection_timestamp=datetime(2026, 4, 2, tzinfo=timezone.utc),
            admissibility_notes="frozen payload",
            normalization_scope="local_governance_surface",
            source_artifact_refs=[{"kind": "ticket", "ref": "INC-IMM-1"}],
            inline_values={"implementation_minutes": 9},
            frozen_flag=True,
            created_by="phase2-test",
        ),
    )

    bundle.inline_values = {"implementation_minutes": 10}
    with pytest.raises(ImmutablePayloadError):
        db.commit()
    db.rollback()
