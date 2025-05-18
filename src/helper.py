import datetime
import json
import time

from botocore.exceptions import ClientError

from client import Client
from models.configuration import Configuration, Slot

from models.account import Account
from aws_session import session


def multi_run_wrapper(args):
    """
    Wrapper function for multiprocessing.
    """
    return add_court(*args)


def get_account(account_id) -> Account:
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


def read_json_event(data):
    """
    Reads the json event and constructs a Configuration object.
    """
    slots = []
    for slot in data["slots"]:
        slots.append(Slot(slot["start_time"], slot["end_time"]))

    config = Configuration(
        data["accountId"],
        data["location"],
        data["activity"],
        data["keyword"],
        get_date(data["day_offset"]),
        slots,
    )
    return config


def get_date(day):
    """
    Gets the future date offset by a given number of days.
    """
    today = datetime.date.today()
    return str(today + datetime.timedelta(days=day))


def now():
    return datetime.datetime.now().isoformat().split(".")[0]


def get_ids_from_cart(client: Client, data):
    """
    Extracts item IDs and descriptions from cart data.
    """
    dict = {}
    items = data["data"]["items"]
    for item in items:
        id = item["cartable_id"]
        value = "{} - {} {}".format(
            item["cartable_resource"]["starts_at"]["format_24_hour"],
            item["cartable_resource"]["ends_at"]["format_24_hour"],
            item["cartable_resource"]["location"]["name"],
        )
        dict[id] = value
    return dict


def reserve_the_items_in_cart(client: Client, ids: dict,
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
        items = data["data"]["items"]
        # items are missing
        if len(ids) != len(items):
            warn = "[WARN] items are missing, original={}, current={}".format(
                len(ids), len(items)
            )
            print(warn)
            add_missing_items(client, ids, items)
            data = client.cart()
            if len(data["data"]["items"]) == 0:
                print("cannot add any items, exit")
                return

        time.sleep(check_period_seconds)


def add_missing_items(client: Client, ids: dict, items):
    """
    Identifies and re-adds missing items to the cart.
    """
    item_ids = set()
    for item in items:
        item_ids.add(item["cartable_id"])

    for id in ids:
        if id not in item_ids:
            print("item is missing: {}".format(ids[id]))
            client.add(id)


def print_cart(data):
    """
    Prints the shopping cart contents in a readable format.
    """
    output = "[Shopping Cart]\n"
    items = data["data"]["items"]
    for item in items:
        output += "{} - {} {}\n".format(
            item["cartable_resource"]["starts_at"]["format_24_hour"],
            item["cartable_resource"]["ends_at"]["format_24_hour"],
            item["cartable_resource"]["location"]["name"],
        )
    if len(items) == 0:
        output += "(empty)\n"

    print("----------------")
    print(output)
    print("----------------")


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


def add_court(client: Client, location, activity, date, start, end, keyword):
    """
    Tries to add a court booking for the specified time range and keyword.
    """
    title = "[ " + start + " - " + end + " ]"

    print(f"{title} get_courts_by_slot...")
    courts = client.get_courts_by_slot(location, activity, date, start, end)
    print(f"{title} get_courts_by_slot result: {courts}")
    ids = select_court(courts["data"], keyword)
    while True:
        for id in ids:
            ok = client.add(id)
            if ok == True:
                print(f"add item successfully: {title}")
                return "SCCUESS"
        time.sleep(1)
