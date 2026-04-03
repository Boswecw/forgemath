from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.models.governance import ImmutablePersistedMixin


class ImmutablePayloadError(ValueError):
    """Raised when a persisted governed object is mutated in place."""


@event.listens_for(Session, "before_flush")
def prevent_governed_payload_mutation(session: Session, _flush_context, _instances) -> None:
    for obj in session.dirty:
        if not isinstance(obj, ImmutablePersistedMixin):
            continue

        changed_fields = {
            attr.key
            for attr in inspect(obj).attrs
            if attr.history.has_changes()
        }
        if not changed_fields:
            continue

        illegal_fields = changed_fields - obj.lifecycle_mutable_fields()
        if illegal_fields:
            field_list = ", ".join(sorted(illegal_fields))
            raise ImmutablePayloadError(
                f"{obj.__class__.__name__} payload is immutable once persisted; "
                f"illegal updates: {field_list}"
            )
