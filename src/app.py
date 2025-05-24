import multiprocessing

import helper
import line_client
import line_flex_factory
from client import Client
from models.court_booking_request import CourtBookingRequest, Slot
from models.shopping_cart import ShoppingCart


client = Client()


def book_court(request: CourtBookingRequest, slot: Slot):
    print("run")
    return helper.book_court(client=client,
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
                client,
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
    account = helper.get_account_by_id(request.account_id)
    client.login(account.username, account.password)

    book_court_in_parallel(request)

    data = client.cart()
    cart = ShoppingCart.from_json(data)

    messages = line_flex_factory.generate_messages(items=cart.items, date=request.date)
    line_client.send_flex_messages(messages)

    if cart.items:
        helper.reserve_the_items_in_cart(client, cart)
