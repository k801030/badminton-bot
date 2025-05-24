from dataclasses import dataclass
from typing import List


@dataclass
class Reservable:
    id: str
    start_at: str
    end_at: str
    name: str

    def __str__(self):
        return f"{self.start_at} - {self.end_at} {self.name}"

    @classmethod
    def from_json(cls, data: dict) -> "Reservable":
        return cls(
            id=data["id"],
            start_at=data["starts_at"]["format_24_hour"],
            end_at=data["ends_at"]["format_24_hour"],
            name=data["location"]["name"],
        )


@dataclass
class Courts:
    items: List[Reservable]

    def __str__(self):
        return "".join(f"{item}\n" for item in self.items) if self.items else "(empty)"

    @classmethod
    def from_json(cls, data: dict) -> "Courts":
        items_data = data["data"]
        items = [Reservable.from_json(item) for item in items_data]
        return cls(items=items)
