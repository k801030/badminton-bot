from dataclasses import dataclass
from typing import List


@dataclass
class Cartable:
    id: str
    start_at: str
    end_at: str
    name: str

    def __str__(self):
        return f"{self.start_at} - {self.end_at} {self.name}"

    @classmethod
    def from_json(cls, data: dict) -> "Cartable":
        return cls(
            id=data["cartable_id"],
            start_at=data["cartable_resource"]["starts_at"]["format_24_hour"],
            end_at=data["cartable_resource"]["ends_at"]["format_24_hour"],
            name=data["cartable_resource"]["location"]["name"],
        )


@dataclass
class ShoppingCart:
    items: List[Cartable]

    def __str__(self):
        output = "----------------\n"
        output += "[Shopping Cart]\n"
        output += "".join(f"{item}\n" for item in self.items)
        if len(self.items) == 0:
            output += "(empty)\n"
        output += "----------------\n"
        return output

    @classmethod
    def from_json(cls, data: dict) -> "ShoppingCart":
        items_data = data["data"]["items"]
        items = [Cartable.from_json(item) for item in items_data]
        items = sorted(items, key=lambda x: x.start_at)
        return cls(items=items)
