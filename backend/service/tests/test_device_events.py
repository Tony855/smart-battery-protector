from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.device_events import DeviceEvent


def test_device_event_requires_timezone_and_rejects_unknown_fields():
    event = DeviceEvent(
        event_uuid=uuid4(),
        event_type="protection.trip",
        occurred_at=datetime.now(timezone.utc),
    )
    assert event.occurred_at.tzinfo is not None
    with pytest.raises(ValidationError):
        DeviceEvent(
            event_uuid=uuid4(),
            event_type="Protection Trip",
            occurred_at=datetime.now(timezone.utc),
        )
    with pytest.raises(ValidationError):
        DeviceEvent(
            event_uuid=uuid4(),
            event_type="fault",
            occurred_at=datetime.now(timezone.utc),
            unexpected="value",
        )


def test_event_type_pattern_and_length_are_enforced():
    with pytest.raises(ValidationError):
        DeviceEvent(
            event_uuid=uuid4(),
            event_type="UPPERCASE",
            occurred_at=datetime.now(timezone.utc),
        )
