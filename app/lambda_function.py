import logging

from app import handle_request
from models.court_booking_request import CourtBookingRequest

logger = logging.getLogger(__name__)


def handler(event, context):
    request = CourtBookingRequest.from_json(event)
    # only log a summary, the raw event is not needed for debugging
    logger.info(
        "Received event: account_id=%s, location=%s, date=%s, slots=%d",
        request.account_id,
        request.location,
        request.date,
        len(request.slots),
    )
    handle_request(request)
