import multiprocessing
import time
from configuration import Configuration, Slot
import requests
import yaml
import main
from sleep import sleep_until_10pm


def add_court_val(token, location, activity, date, start, end, keyword):
    title = "[ " + start + " - " + end + " ]"
    result = main.add_court(token, location, activity, date, start, end, keyword)
    print(title + ": " + result)


def lambda_handler(event, context):
    starttime = time.time()
    config = main.read_from_yaml()
    user = main.login(config.username, config.password)
    token = user["token"]

    # sleep_until_10pm()

    processes = []
    for slot in config.slots:
        p = multiprocessing.Process(
            target=add_court_val,
            args=(
                token,
                config.location,
                config.activity,
                config.date,
                slot.start_time,
                slot.end_time,
                config.keyword,
            ),
        )
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    output = "Shopping cart:\n"
    res = main.cart(token)
    items = res["data"]["items"]
    for item in items:
        output += (
            item["cartable_resource"]["starts_at"]["format_24_hour"]
            + " - "
            + item["cartable_resource"]["starts_at"]["format_24_hour"]
            + " "
            + item["cartable_resource"]["location"]["name"]
            + "\n"
        )
    if len(items) == 0:
        output += "(empty)\n"

    print(output)
    return output
