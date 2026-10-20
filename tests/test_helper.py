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
