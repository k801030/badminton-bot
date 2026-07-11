from concurrent.futures import ThreadPoolExecutor
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


# Book multiple court slots in parallel using ThreadPoolExecutor
def book_court_in_parallel(request: CourtBookingRequest):
    print(f"[DEBUG] book_court_in_parallel started with {len(request.slots)} slots.")
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
                request.keyword,
            )
            for slot in request.slots
        ]
        print(f"[DEBUG] Submitted all tasks to ThreadPoolExecutor.")
        for i, f in enumerate(futures):
            try:
                f.result()
                print(f"[DEBUG] Slot {i+1} booking task finished successfully.")
            except Exception as e:
                print(f"[ERROR] Slot {i+1} booking task failed: {e}")
                raise


# Main handler to process booking request
def handle_request(request: CourtBookingRequest):
    print(f"[DEBUG] Starting handle_request with account_id: {request.account_id}")

    # Retrieve account credentials from Secret Manager
    try:
        account = sm.get_account_by_id(request.account_id)
        print(f"[DEBUG] Retrieved credentials for account: {account.username}")
    except Exception as e:
        print(
            f"[ERROR] Failed to retrieve credentials for account_id {request.account_id}: {e}"
        )
        raise

    # Login to court booking system
    try:
        print(f"[DEBUG] Attempting login for user: {account.username}")
        court_client.login(account.username, account.password)
        print(f"[DEBUG] Login successful.")
    except Exception as e:
        print(f"[ERROR] Login failed for user {account.username}: {e}")
        raise

    # Book all requested slots in parallel
    try:
        print(f"[DEBUG] Starting parallel booking for slots.")
        book_court_in_parallel(request)
        print(f"[DEBUG] Parallel booking completed.")
    except Exception as e:
        print(f"[ERROR] Error during parallel booking: {e}")
        raise

    # Retrieve current shopping cart data after booking
    try:
        print(f"[DEBUG] Retrieving cart data.")
        data = court_client.cart()
        print(f"[DEBUG] Raw cart data received: {data}")
        cart = ShoppingCart.from_json(data)
        print(f"[DEBUG] Parsed cart with {len(cart.items)} items.")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve or parse cart: {e}")
        raise

    # Generate Line messaging notification content
    try:
        print(f"[DEBUG] Generating Line messages.")
        messages = line_flex_factory.generate_messages(
            items=cart.items, date=request.date, username=account.username
        )
        print(f"[DEBUG] Generated messages content: {messages}")
    except Exception as e:
        print(f"[ERROR] Failed to generate Line messages: {e}")
        raise

    # Send async notification to Line group
    try:
        print(f"[DEBUG] Sending notification to Line group {line_secret.group_id}")
        line_client.send_notification_async(
            messages=messages, group_id=line_secret.group_id
        )
        print(f"[DEBUG] Notification trigger sent.")
    except Exception as e:
        print(f"[ERROR] Failed to send Line notification: {e}")
        raise

    # If there are items in the cart, reserve them for a period
    if cart.items:
        print(f"[DEBUG] Cart has items, starting reservation.")
        try:
            helper.reserve_the_items_in_cart(court_client, cart)
            print(f"[DEBUG] Reservation completed.")
        except Exception as e:
            print(f"[ERROR] Error during item reservation: {e}")
            raise
    else:
        print(f"[DEBUG] No items in cart to reserve.")
