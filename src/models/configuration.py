from dataclasses import dataclass
from typing import List

from datetime_utils import get_date


@dataclass
class Slot:
    start_time: str
    end_time: str

@dataclass
class Configuration:
    account_id: str
    location: str
    activity: str
    keyword: str
    date: str
    slots: List[Slot]

    @classmethod
    def from_json(cls, data: dict) -> 'Configuration':
        slots = [Slot(slot["start_time"], slot["end_time"]) for slot in data["slots"]]
        return cls(
            account_id=data["accountId"],
            location=data["location"],
            activity=data["activity"],
            keyword=data["keyword"],
            date=get_date(data["day_offset"]),
            slots=slots
        )
