from concurrent.futures import ThreadPoolExecutor
import logging
import os
import threading

from log_config import setup_logging

setup_logging()

from datetime_utils import wait_until_next_hour
import helper
import line_flex_factory
from http_client import CourtClient
from line_client import LineClient
from models.booking_result import BookingResult, BookingStatus
from models.court_booking_request import CourtBookingRequest
from models.shopping_cart import ShoppingCart
from secret_manager import SecretManager

logger = logging.getLogger(__name__)

region = os.environ.get("AWS_REGION")
is_dev = os.environ.get("ENV", "").lower() == "dev"

# Initialize SecretManager to fetch secrets based on environment
sm = SecretManager(region=region, is_dev=is_dev)
# Retrieve Line messaging API secrets
line_secret = sm.get_line_secret()

# Initialize HTTP clients for court booking and Line messaging
court_client = CourtClient()
line_client = LineClient(access_token=line_secret.access_token)


# Book multiple court slots in parallel using ThreadPoolExecutor
def book_court_in_parallel(request: CourtBookingRequest) -> list[BookingResult]:
    logger.info("Booking %d slots in parallel", len(request.slots))
    results: list[BookingResult] = []
    # the `with` block waits (shutdown(wait=True)) for every slot thread to finish
    with ThreadPoolExecutor(max_workers=len(request.slots)) as executor:
        futures = [
            executor.submit(
                helper.book_court,
                court_client,
                request.location,
                request.activity,
                request.date,
                slot.start_time,
                slot.end_time,
                request.keywords,
            )
            for slot in request.slots
        ]
        for slot, f in zip(request.slots, futures):
            try:
                results.append(f.result())
            except Exception as e:
                # keep going so the other slots are still reported to LINE
                logger.exception(
                    "Booking task for slot %s-%s failed", slot.start_time, slot.end_time
                )
                results.append(
                    BookingResult(
                        slot.start_time, slot.end_time, BookingStatus.ERROR, str(e)
                    )
                )
    for r in results:
        logger.info("Slot result: %s", r)
    return results


# Wait for the LINE notification thread so Lambda doesn't freeze before it's sent
def wait_for_notification(thread: threading.Thread | None, timeout: float = 10):
    if thread is None:
        return
    thread.join(timeout=timeout)
    if thread.is_alive():
        logger.warning("LINE notification still running after %ss", timeout)


# Send an error notification to LINE when the flow crashes before the result is sent
def notify_failure(request: CourtBookingRequest, error: Exception):
    try:
        message = line_flex_factory.generate_error_message(
            date=request.date, account_id=request.account_id, error=error
        )
        line_client.send_notification(messages=message, group_id=line_secret.group_id)
    except Exception:
        logger.exception("Failed to send failure notification")


# Main handler to process booking request
def handle_request(request: CourtBookingRequest):
    try:
        cart, messages = book_and_build_messages(request)
    except Exception as e:
        logger.exception("Booking failed for account_id=%s", request.account_id)
        # nothing has been sent to LINE yet, so let the group know it failed
        notify_failure(request, e)
        raise

    notify_and_reserve(cart, messages)


# Login, book every slot and build the LINE result message
def book_and_build_messages(request: CourtBookingRequest):
    logger.info(
        "Handling request: account_id=%s, date=%s", request.account_id, request.date
    )

    account = sm.get_account_by_id(request.account_id)
    court_client.login(account.username, account.password)
    logger.info("Login successful for account_id=%s", request.account_id)

    # Wait until the top of the hour (:00:00) if triggered at minute 59
    wait_until_next_hour()

    results = book_court_in_parallel(request)

    cart = ShoppingCart.from_json(court_client.cart())
    logger.info("Cart has %d items", len(cart.items))

    messages = line_flex_factory.generate_messages(
        items=cart.items,
        date=request.date,
        username=account.username,
        results=results,
    )
    return cart, messages


# Send the result to LINE, then keep the cart items reserved
def notify_and_reserve(cart: ShoppingCart, messages: dict):
    notify_thread = line_client.send_notification_async(
        messages=messages, group_id=line_secret.group_id
    )
    try:
        # If there are items in the cart, reserve them for a period
        if cart.items:
            helper.reserve_the_items_in_cart(court_client, cart)
        else:
            logger.info("No items in cart to reserve")
    finally:
        # Always wait for the notification before the handler returns
        wait_for_notification(notify_thread)
