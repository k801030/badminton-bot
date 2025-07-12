import multiprocessing
import os

import helper
import line_flex_factory
from http_client import CourtClient
from line_client import LineClient
from models.court_booking_request import CourtBookingRequest, Slot
from models.shopping_cart import ShoppingCart
from secret_manager import SecretManager


region = os.environ.get("AWS_REGION")
is_dev = os.environ.get("ENV", "").lower() == "dev"

# Initialize SecretManager to fetch secrets based on environment
sm = SecretManager(region=region, is_dev=is_dev)
# Retrieve Line messaging API secrets
line_secret = sm.get_line_secret()

# Initialize HTTP clients for court booking and Line messaging
court_client = CourtClient()
line_client = LineClient(access_token=line_secret.access_token)


# Book a single court slot using helper function
def book_court(request: CourtBookingRequest, slot: Slot):
    return helper.book_court(
        client=court_client,
        location=request.location,
        activity=request.activity,
        date=request.date,
        start=slot.start_time,
        end=slot.end_time,
        keyword=request.keyword,
    )


# Book multiple court slots in parallel using multiprocessing
def book_court_in_parallel(request: CourtBookingRequest):
    processes = []
    for slot in request.slots:
        p = multiprocessing.Process(
            target=helper.book_court,
            args=(
                court_client,
                request.location,
                request.activity,
                request.date,
                slot.start_time,
                slot.end_time,
                request.keyword,
            ),
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


# Main handler to process booking request
def handle_request(request: CourtBookingRequest):
    # Retrieve account credentials from Secret Manager
    account = sm.get_account_by_id(request.account_id)

    # Login to court booking system
    court_client.login(account.username, account.password)

    # Book all requested slots in parallel
    book_court_in_parallel(request)

    # Retrieve current shopping cart data after booking
    data = court_client.cart()
    cart = ShoppingCart.from_json(data)

    # Generate Line messaging notification content
    messages = line_flex_factory.generate_messages(
        items=cart.items, date=request.date, username=account.username
    )

    # Send async notification to Line group
    line_client.send_notification_async(
        messages=messages, group_id=line_secret.group_id
    )

    # If there are items in the cart, reserve them for a period
    if cart.items:
        helper.reserve_the_items_in_cart(court_client, cart)
