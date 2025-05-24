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
