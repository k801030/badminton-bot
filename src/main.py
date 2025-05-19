from app import handle_request
from datetime_utils import now
from models.court_booking_request import CourtBookingRequest


sample_request = {
    "accountId": "1",
    "location": "queensbridge-sports-community-centre",
    "activity": "badminton-40min",
    "keyword": "Court 1, Court 2",
    "day_offset": 2,
    "slots": [
        {
            "start_time": "16:00",
            "end_time": "16:40"
        },
        {
            "start_time": "18:40",
            "end_time": "19:20"
        }
    ]
}

if __name__ == "__main__":
    print(f"started at {now()}")
    request = CourtBookingRequest.from_json(sample_request)
    handle_request(request)
