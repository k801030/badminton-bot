import time

from http_client import CourtClient
from models.booking_result import BookingResult, BookingStatus
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
    Because the server might drop the bookings
    """
    print(f"[DEBUG] Starting reservation loop for cart: {current_cart}")

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
            print(f"[DEBUG] Item {item.id} is missing. Attempting to re-add.")
            ok = client.add(item.id)
            print(f"[DEBUG] Re-add item {item.id} result: {ok}")

    print(f"[DEBUG] Refreshing cart after re-adding missing items.")
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
    max_duration_seconds=15,
    interval_seconds=1,
) -> BookingResult:
    """
    Tries to add a court booking for the specified time range and keyword.
    Returns a BookingResult describing why the slot succeeded / failed.
    """
    slot_name = f"[ {start} - {end} ]"
    start_time = time.time()

    def result(status: BookingStatus, detail: str = "", available=None):
        r = BookingResult(start, end, status, detail, available or [])
        print(f"[RESULT] {r}")
        return r

    courts = None
    not_ready = False
    while True:
        print(
            f"[DEBUG] [{slot_name}] Fetching courts for {location}, {activity}, {date}"
        )
        data = client.get_courts_by_slot(location, activity, date, start, end)
        not_ready = bool(data.get("not_ready"))
        courts = Courts.from_json(data)
        print(f"[DEBUG] [{slot_name}] Found {len(courts.items)} courts available.")

        if courts.items:
            break

        elapsed = time.time() - start_time
        if elapsed > max_duration_seconds:
            print(f"The slot {slot_name} doesn't have available courts")
            if not_ready:
                return result(BookingStatus.NOT_OPEN, "日期尚未進入可預約期間")
            return result(BookingStatus.NO_COURTS, "API 回傳 0 個可預約場地")

        print(f"The slot {slot_name} doesn't have available courts yet, retrying...")
        time.sleep(interval_seconds)

    court_names = [court.name for court in courts.items]
    print(f"The slot {slot_name} has available courts: {court_names}")
    court_ids = select_court(courts, keyword)
    if not court_ids:
        print(f"[DEBUG] [{slot_name}] No courts matched the keywords: {keyword}")
        return result(
            BookingStatus.NO_MATCH,
            f"有 {len(court_names)} 個場地，但不符合「{keyword}」",
            court_names,
        )

    last_error = ""
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_duration_seconds:
            print(f"Reservation period of {max_duration_seconds} seconds has ended.")
            return result(
                BookingStatus.MISSED, last_error or "加入購物車逾時", court_names
            )

        for court_id in court_ids:
            add_result = client.add(court_id)
            if add_result:
                print(f"Succeeded to book the slot: {slot_name}")
                return result(BookingStatus.SUCCESS, available=court_names)
            last_error = describe_add_failure(add_result)


def describe_add_failure(add_result) -> str:
    """
    Converts a failed add-to-cart response into a human readable reason.
    """
    message = getattr(add_result, "message", None) or ""
    status = getattr(add_result, "status", None)
    if "already full" in message:
        return "場地已被別人搶走"
    if message:
        return f"{message} (status={status})" if status else message
    return "加入購物車失敗"
