import datetime
import time
import multiprocessing
from configuration import Configuration, Slot
import requests
import yaml
import main


def multiprocessing_func(region):
    print("endpoint for {} is {}".format(region, endpoint))
    time.sleep(1)
    print("endpoint for {} is {}".format(region, endpoint))


def login(username, password):
    url = "https://better-admin.org.uk/api/auth/customer/login"
    body = {"username": username, "password": password}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://myaccount.better.org.uk",
    }

    r = requests.post(url, json=body, headers=headers)
    data = r.json()
    if data["status"] != "success":
        raise Exception("invalid username/password")
    return data


def read_from_yaml():
    with open("config.yaml", "r") as yamlfile:
        data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    slots = []
    for slot in data["slots"]:
        slots.append(Slot(slot["start_time"], slot["end_time"]))

    config = Configuration(
        data["username"],
        data["password"],
        data["url"],
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


def lambda_handler(event, context):
    starttime = time.time()
    config = read_from_yaml()
    user = login(config.username, config.password)
    token = user["token"]

    processes = []
    for slot in config.slots:
        p = multiprocessing.Process(
            target=main.add_court,
            args=(token, config.date, slot.start_time, slot.end_time, config.keyword),
        )
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    output = "That took {} seconds".format(time.time() - starttime)
    print(output)
    return output
