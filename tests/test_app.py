import sys
import types

import pytest

import line_flex_factory
from models.court_booking_request import CourtBookingRequest
from models.line_secret import LineSecret


@pytest.fixture
def app_module(monkeypatch):
    """Import `app` with a fake SecretManager so no AWS call is made."""

    class FakeSecretManager:
        def __init__(self, *args, **kwargs):
            pass

        def get_line_secret(self):
            return LineSecret("token", "group-1")

        def get_account_by_id(self, account_id):
            raise RuntimeError("parameter not found")

    fake = types.ModuleType("secret_manager")
    fake.SecretManager = FakeSecretManager
    monkeypatch.setitem(sys.modules, "secret_manager", fake)
    monkeypatch.delitem(sys.modules, "app", raising=False)
    import app

    yield app
    sys.modules.pop("app", None)


def _request():
    return CourtBookingRequest.from_json(
        {
            "accountId": "1",
            "location": "loc",
            "activity": "badminton-40min",
            "keyword": "Court 1",
            "day_offset": 7,
            "slots": [{"start_time": "18:00", "end_time": "18:40"}],
        }
    )


def test_handle_request_sends_failure_notification(app_module, monkeypatch):
    sent = []
    monkeypatch.setattr(
        app_module.line_client,
        "send_notification",
        lambda messages, group_id: sent.append((messages, group_id)),
    )

    with pytest.raises(RuntimeError):
        app_module.handle_request(_request())

    assert len(sent) == 1
    message, group_id = sent[0]
    assert group_id == "group-1"
    assert "parameter not found" in message["text"]


def test_generate_error_message_truncates_reason():
    msg = line_flex_factory.generate_error_message(
        "2026-10-30", "1", RuntimeError("x" * 1000)
    )
    assert msg["type"] == "text"
    assert line_flex_factory.ERROR_TITLE in msg["text"]
    assert len(msg["text"]) < 300
