import json
import time

from botocore.exceptions import ClientError

from aws_session import session
from client import Client
from models.account import Account
from models.shopping_cart import ShoppingCart


def get_account_by_id(account_id) -> Account:
    region_name = "eu-west-2"
    secret_id = f"account/{account_id}"

    # Create a Secrets Manager client
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_id
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    json_str = json.loads(secret)
    return Account(json_str["username"], json_str["password"])


def reserve_the_items_in_cart(client: Client, current_cart: ShoppingCart,
                              reserve_duration_seconds: int = 600,
                              check_period_seconds: int = 3):
    """
    Continuously checks the cart for missing items and re-adds them if needed.
    """
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > reserve_duration_seconds:
            print(f"Reservation period of {reserve_duration_seconds} seconds has ended.")
            return

        data = client.cart()
        updated_cart = ShoppingCart.from_json(data)

        # items are missing
        if len(current_cart.items) != len(updated_cart.items):
            warn = f"[WARN] cart items are missing, original={len(current_cart.items)}, current={len(updated_cart.items)}"
            print(warn)
            if not add_missing_items_to_cart(client, current_cart, updated_cart):
                return

        time.sleep(check_period_seconds)


def add_missing_items_to_cart(client: Client, cart: ShoppingCart, updated_cart: ShoppingCart) -> bool:
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


def select_court(items, keyword) -> list[str]:
    """
    Selects court item IDs that match given keyword(s) in their location name.
    """
    keywords = [k.strip() for k in keyword.split(",")]
    ids = []
    for k in keywords:
        for item in items:
            if k in item["location"]["name"]:
                ids.append(item["id"])
    return ids


def book_court(client: Client, location, activity, date, start, end, keyword):
    """
    Tries to add a court booking for the specified time range and keyword.
    """
    slot_name = f"[ {start} - {end} ]"

    courts = client.get_courts_by_slot(location, activity, date, start, end)

    court_names = [court["location"]["name"] for court in courts["data"]]
    print(f"The slot {slot_name} has available courts: {court_names}")
    ids = select_court(courts["data"], keyword)
    while True:
        for id in ids:
            ok = client.add(id)
            if ok:
                print(f"Succeeded to book the slot: {slot_name}")
                return
        time.sleep(1)
