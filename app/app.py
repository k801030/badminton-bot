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
sm = SecretManager(region=region, is_dev=is_dev)
line_secret = sm.get_line_secret()

court_client = CourtClient()
line_client = LineClient(access_token=line_secret.access_token)


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


def handle_request(request: CourtBookingRequest):
    account = sm.get_account_by_id(request.account_id)
    court_client.login(account.username, account.password)

    book_court_in_parallel(request)

    data = court_client.cart()
    cart = ShoppingCart.from_json(data)

    messages = line_flex_factory.generate_messages(items=cart.items, date=request.date)
    line_client.send_notification_async(
        messages=messages, group_id=line_secret.group_id
    )

    if cart.items:
        helper.reserve_the_items_in_cart(court_client, cart)
