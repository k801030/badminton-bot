from app import handle_request
from models.court_booking_request import CourtBookingRequest


def handler(event, context):
    print(f"receive event: {event}")
    request = CourtBookingRequest.from_json(event)
    handle_request(request)
