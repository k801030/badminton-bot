from dataclasses import dataclass
from typing import List, Union

from datetime_utils import get_date


@dataclass
class Slot:
    start_time: str
    end_time: str


@dataclass
class CourtBookingRequest:
    account_id: str
    location: str
    activity: str
    keywords: List[str]
    date: str
    slots: List[Slot]

    @classmethod
    def from_json(cls, data: dict) -> "CourtBookingRequest":
        slots = [Slot(slot["start_time"], slot["end_time"]) for slot in data["slots"]]
        return cls(
            account_id=data["accountId"],
            location=data["location"],
            activity=data["activity"],
            keywords=parse_keywords(data["keyword"]),
            date=get_date(data["day_offset"]),
            slots=slots,
        )


def parse_keywords(value: Union[str, List[str]]) -> List[str]:
    """
    Accepts a list of keywords, or the legacy comma separated string
    (e.g. "Court 1,Court 3") so already scheduled events keep working.
    """
    if isinstance(value, str):
        value = value.split(",")
    return [k.strip() for k in value if k.strip()]
