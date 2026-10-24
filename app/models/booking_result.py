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


SUCCESS_LABEL = "成功"
FAILURE_LABEL = "失敗"
NOT_OPEN_LABEL = "未開放"

# the detailed status is kept for logs; LINE only shows 3 states
STATUS_LABELS = {
    BookingStatus.SUCCESS: SUCCESS_LABEL,
    BookingStatus.NOT_OPEN: NOT_OPEN_LABEL,
    BookingStatus.NO_COURTS: NOT_OPEN_LABEL,
    BookingStatus.NO_MATCH: FAILURE_LABEL,
    BookingStatus.MISSED: FAILURE_LABEL,
    BookingStatus.ERROR: FAILURE_LABEL,
}

LABEL_COLORS = {
    SUCCESS_LABEL: "#6B9E78",  # muted green
    FAILURE_LABEL: "#C0716B",  # muted red
    NOT_OPEN_LABEL: "#AAAAAA",  # grey
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

    @property
    def color(self) -> str:
        return LABEL_COLORS[self.label]

    def __str__(self):
        text = f"[{self.slot_name}] {self.status.value}"
        return f"{text}: {self.detail}" if self.detail else text
