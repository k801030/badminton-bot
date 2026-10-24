import helper
from models.courts import Courts, Reservable

courts = Courts(
    [
        Reservable(id="1", name="London Court", start_at="16:00", end_at="17:00"),
        Reservable(id="2", name="Manchester Court", start_at="16:00", end_at="17:00"),
        Reservable(id="3", name="Bristol Court", start_at="16:00", end_at="17:00"),
        Reservable(id="4", name="Edinburgh Court", start_at="16:00", end_at="17:00"),
    ]
)


def test_select_court_single_keyword():

    result = helper.select_court(courts, "London")
    assert result == ["1"]


def test_select_court_multiple_keywords():
    result = helper.select_court(courts, "London, Manchester")
    assert result == ["1", "2"]


def test_select_court_no_match():
    result = helper.select_court(courts, "Paris")
    assert result == []


def test_select_court_keyword_with_spaces():
    result = helper.select_court(courts, " London , Manchester")
    assert result == ["1", "2"]


def test_book_court_retries_when_initially_empty():
    class FakeClient:
        def __init__(self):
            self.fetch_calls = 0
            self.added_ids = []

        def get_courts_by_slot(self, location, activity, date, start, end):
            self.fetch_calls += 1
            if self.fetch_calls < 3:
                return {"data": []}
            return {
                "data": [
                    {
                        "id": "court-1-id",
                        "starts_at": {"format_24_hour": start},
                        "ends_at": {"format_24_hour": end},
                        "location": {"name": "Court 1"},
                    }
                ]
            }

        def add(self, court_id):
            self.added_ids.append(court_id)
            return True

    client = FakeClient()
    helper.book_court(
        client=client,
        location="queensbridge-sports-community-centre",
        activity="badminton-40min",
        date="2026-10-23",
        start="19:20",
        end="20:00",
        keyword="Court 1",
        max_duration_seconds=5,
        interval_seconds=0.01,
    )

    assert client.fetch_calls == 3
    assert client.added_ids == ["court-1-id"]


def test_book_court_times_out_when_always_empty():
    class FakeClient:
        def __init__(self):
            self.fetch_calls = 0

        def get_courts_by_slot(self, location, activity, date, start, end):
            self.fetch_calls += 1
            return {"data": []}

        def add(self, court_id):
            return False

    client = FakeClient()
    helper.book_court(
        client=client,
        location="queensbridge-sports-community-centre",
        activity="badminton-40min",
        date="2026-10-23",
        start="19:20",
        end="20:00",
        keyword="Court 1",
        max_duration_seconds=0.05,
        interval_seconds=0.02,
    )

    assert client.fetch_calls >= 2


# ---------- BookingResult reasons ----------
from models.booking_result import AddResult, BookingStatus


def _court(court_id, name, start="18:00", end="18:40"):
    return {
        "id": court_id,
        "starts_at": {"format_24_hour": start},
        "ends_at": {"format_24_hour": end},
        "location": {"name": name},
    }


def _book(client, keyword="Court 1,Court 3"):
    return helper.book_court(
        client=client,
        location="loc",
        activity="badminton-40min",
        date="2026-10-30",
        start="18:00",
        end="18:40",
        keyword=keyword,
        max_duration_seconds=0.05,
        interval_seconds=0.01,
    )


class _Client:
    def __init__(self, courts_response, add_result=None):
        self.courts_response = courts_response
        self.add_result = add_result

    def get_courts_by_slot(self, *args):
        return self.courts_response

    def add(self, court_id):
        return self.add_result


def test_book_court_result_success():
    client = _Client({"data": [_court("c1", "Court 1")]}, AddResult(ok=True))
    result = _book(client)
    assert result.status == BookingStatus.SUCCESS


def test_book_court_result_missed_when_session_already_full():
    # [ 18:00 - 18:40 ] Found 2 courts, add -> 422 "already full"
    client = _Client(
        {"data": [_court("c1", "Court 1"), _court("c3", "Court 3")]},
        AddResult(
            ok=False, status=422, message="The session being booked is already full"
        ),
    )
    result = _book(client)
    assert result.status == BookingStatus.MISSED
    assert result.detail == "場地已被別人搶走"
    assert result.available_courts == ["Court 1", "Court 3"]


def test_book_court_result_no_courts():
    # [ 20:00 - 20:40 ] Found 0 courts available
    result = _book(_Client({"data": []}))
    assert result.status == BookingStatus.NO_COURTS


def test_book_court_result_not_open():
    result = _book(_Client({"data": [], "not_ready": True}))
    assert result.status == BookingStatus.NOT_OPEN


def test_book_court_result_no_match():
    client = _Client({"data": [_court("c2", "Court 2")]})
    result = _book(client)
    assert result.status == BookingStatus.NO_MATCH
    assert result.available_courts == ["Court 2"]


def test_generate_messages_includes_slot_reasons():
    import line_flex_factory
    from models.booking_result import BookingResult

    results = [
        BookingResult("18:00", "18:40", BookingStatus.MISSED, "場地已被別人搶走"),
        BookingResult(
            "20:00", "20:40", BookingStatus.NO_COURTS, "API 回傳 0 個可預約場地"
        ),
    ]
    msg = line_flex_factory.generate_messages([], "2026-10-30", "user", results)
    text = str(msg)
    assert "沒搶到" in text
    assert "場地已被別人搶走" not in text
    assert "未開放" in text
