import datetime
from multiprocessing import Pool
import multiprocessing
import sys
import time
from configuration import Configuration, Slot
import requests
import yaml
from client import Client


def select_court(items, keyword):
    for item in items:
        if keyword in item["location"]["name"] and item["spaces"] != 0:
            return item["id"]


def add_court(client: Client, location, activity, date, start, end, keyword):
    title = "[ " + start + " - " + end + " ]"
    print("try to add court: " + title)

    courts = client.get_courts_by_slot(location, activity, date, start, end)
    id = select_court(courts["data"], keyword)
    if id == None:
        print("the target slot is not found or full: " + title)
        return "FAILURE"
    ok = client.add(id)
    if ok == True:
        print("add item successfully: " + title)
        return "SCCUESS"
    else:
        print("fail to add item: " + title)
        return "FAILURE"


def multi_run_wrapper(args):
    return add_court(*args)


def read_from_yaml(file):
    with open(file, "r") as yamlfile:
        data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    slots = []
    for slot in data["slots"]:
        slots.append(Slot(slot["start_time"], slot["end_time"]))

    config = Configuration(
        data["username"],
        data["password"],
        data["location"],
        data["activity"],
        data["keyword"],
        next_week(),
        slots,
    )
    return config


def next_week():
    today = datetime.date.today()
    return str(today + datetime.timedelta(days=7))


def now():
    return datetime.datetime.now().isoformat().split(".")[0]


def get_ids_from_cart(client: Client, data):
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


def check_cart_then_add(client: Client, ids: dict):
    while True:
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

        print("sleep for 5 secs")
        time.sleep(5)


def add_missing_items(client: Client, ids: dict, items):
    item_ids = set()
    for item in items:
        item_ids.add(item["cartable_id"])

    for id in ids:
        if id not in item_ids:
            print("item is missing: {}".format(ids[id]))
            client.add(id)


def print_cart(data):
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


if __name__ == "__main__":
    print("started at " + now())
    manager = multiprocessing.Manager()

    config = read_from_yaml("test.yaml")

    client = Client()

    try:
        client.login(config.username, config.password)
    except:
        print("invalid username/password")
        sys.exit()

    numOfThreads = len(config.slots)
    args = []
    for slot in config.slots:
        args.append(
            (
                client,
                config.location,
                config.activity,
                config.date,
                slot.start_time,
                slot.end_time,
                config.keyword,
            )
        )

    with Pool(numOfThreads) as pool:
        results = pool.map(
            multi_run_wrapper,
            args,
        )

    data = client.cart()
    print_cart(data)
    print("finished at " + now())

    ids = get_ids_from_cart(client, data)
    check_cart_then_add(client, ids)
