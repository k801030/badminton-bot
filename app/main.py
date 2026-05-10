import os

os.environ.setdefault("ENV", "dev")

from app import handle_request
from datetime_utils import now
from models.court_booking_request import CourtBookingRequest

sample_request = {
    "accountId": "1",
    "location": "queensbridge-sports-community-centre",
    "activity": "badminton-40min",
    "keyword": "Court 1,Court 3",
    "day_offset": 7,
    "slots": [
        {"start_time": "19:20", "end_time": "20:00"},
        {"start_time": "20:00", "end_time": "20:40"},
        {"start_time": "20:40", "end_time": "21:20"},
        {"start_time": "21:20", "end_time": "22:00"},
    ],
}

if __name__ == "__main__":
    print(f"started at {now()}")
    request = CourtBookingRequest.from_json(sample_request)
    handle_request(request)
