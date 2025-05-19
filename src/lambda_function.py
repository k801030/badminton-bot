import helper
from app import handle_request
from models.court_booking_request import CourtBookingRequest


def add_court_val(client, location, activity, date, start, end, keyword):
    helper.book_court(client, location, activity, date, start, end, keyword)


def handler(event, context):
    print(f"receive event: {event}")
    request = CourtBookingRequest.from_json(event)
    handle_request(request)
