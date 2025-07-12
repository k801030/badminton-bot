import time

from http_client import CourtClient
from models.courts import Courts
from models.shopping_cart import ShoppingCart


def reserve_the_items_in_cart(
    client: CourtClient,
    current_cart: ShoppingCart,
    max_duration_seconds: int = 600,
    interval_seconds: int = 5,
):
    """
    Continuously checks the cart for missing items and re-adds them if needed.
    """
    print(current_cart)

    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_duration_seconds:
            print(f"Reservation period of {max_duration_seconds} seconds has ended.")
            return

        data = client.cart()
        updated_cart = ShoppingCart.from_json(data)

        # items are missing
        if len(current_cart.items) != len(updated_cart.items):
            warn = f"[WARN] cart items are missing, original={len(current_cart.items)}, current={len(updated_cart.items)}"
            print(warn)
            if not add_missing_items_to_cart(client, current_cart, updated_cart):
                return

        time.sleep(interval_seconds)


def add_missing_items_to_cart(
    client: CourtClient, cart: ShoppingCart, updated_cart: ShoppingCart
) -> bool:
    """
    Identifies and re-adds missing items to the cart.
    """

    updated_ids = {item.id for item in updated_cart.items}
    for item in cart.items:
        if item.id not in updated_ids:
            client.add(item.id)

    data = client.cart()
    updated_cart = ShoppingCart.from_json(data)
    if not updated_cart.items:
        print("unable to add items to cart")
        return False
    return True


def select_court(courts: Courts, keyword) -> list[str]:
    """
    Selects court item IDs that match given keyword(s) in their location name.
    """
    keywords = [k.strip() for k in keyword.split(",")]
    ids = []
    for k in keywords:
        for item in courts.items:
            if k in item.name:
                ids.append(item.id)
    return ids


def book_court(
    client: CourtClient,
    location,
    activity,
    date,
    start,
    end,
    keyword,
    max_duration_seconds=120,
    interval_seconds=1,
):
    """
    Tries to add a court booking for the specified time range and keyword.
    """
    slot_name = f"[ {start} - {end} ]"
    data = client.get_courts_by_slot(location, activity, date, start, end)
    courts = Courts.from_json(data)

    court_names = [court.name for court in courts.items]
    if not court_names:
        print(f"The slot {slot_name} doesn't have available courts")
        return

    print(f"The slot {slot_name} has available courts: {court_names}")
    court_ids = select_court(courts, keyword)

    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_duration_seconds:
            print(f"Reservation period of {max_duration_seconds} seconds has ended.")
            return

        for court_id in court_ids:
            ok = client.add(court_id)
            if ok:
                print(f"Succeeded to book the slot: {slot_name}")
                return
        time.sleep(interval_seconds)
