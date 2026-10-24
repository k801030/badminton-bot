from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class BookingStatus(Enum):
    # Court added to cart successfully
    SUCCESS = "success"
    # API said the date is not within the valid booking window (not released yet)
    NOT_OPEN = "not_open"
    # API returned 0 courts for the slot (not released / fully booked / no session)
    NO_COURTS = "no_courts"
    # Courts were available, but none matched the keywords
    NO_MATCH = "no_match"
    # Courts were available, but adding to cart failed (e.g. someone else got it)
    MISSED = "missed"
    # Unexpected exception
    ERROR = "error"


STATUS_LABELS = {
    BookingStatus.SUCCESS: "搶到了",
    BookingStatus.NOT_OPEN: "未開放",
    BookingStatus.NO_COURTS: "未開放",
    BookingStatus.NO_MATCH: "沒搶到",
    BookingStatus.MISSED: "沒搶到",
    BookingStatus.ERROR: "系統錯誤",
}


@dataclass
class AddResult:
    """Result of adding an item to the cart."""

    ok: bool
    status: Optional[int] = None
    message: Optional[str] = None

    def __bool__(self):
        return self.ok


@dataclass
class BookingResult:
    start: str
    end: str
    status: BookingStatus
    detail: str = ""
    available_courts: List[str] = field(default_factory=list)

    @property
    def slot_name(self) -> str:
        return f"{self.start} - {self.end}"

    @property
    def label(self) -> str:
        return STATUS_LABELS[self.status]

    def __str__(self):
        text = f"[{self.slot_name}] {self.status.value}"
        return f"{text}: {self.detail}" if self.detail else text

