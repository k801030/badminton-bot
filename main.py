import datetime
from multiprocessing import Pool
import multiprocessing
import sys
import time
from configuration import Configuration, Slot
import requests
import yaml


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


def get_courts_by_slot(token, date, start_time, end_time):
    SLEEP_INTERVAL = 1
    while True:
        url = (
            "https://better-admin.org.uk/api/activities/venue/queensbridge-sports-community-centre/activity/badminton-40min/slots?date="
            + date
            + "&start_time="
            + start_time
            + "&end_time= "
            + end_time
        )
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://myaccount.better.org.uk",
            "Authorization": "Bearer " + token,
        }
        r = requests.get(url, headers=headers)
        data = r.json()

        if (
            r.status_code == 422
            and "The date should be within the valid days" in data["message"]
        ):
            time.sleep(SLEEP_INTERVAL)
            continue
        return data


def select(items, keyword):
    for item in items:
        if keyword in item["location"]["name"]:
            return item["id"]


def add(token, id):
    url = "https://better-admin.org.uk/api/activities/cart/add"
    body = {"items": [{"id": id, "type": "activity"}]}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://myaccount.better.org.uk",
        "Authorization": "Bearer " + token,
    }

    r = requests.post(url, json=body, headers=headers)
    data = r.json()
    if r.status_code != 200:
        return False
    else:
        return True


def add_court(token, date, start, end, keyword):
    title = "[ " + start + " - " + end + " ]"
    print("try to add court: " + title)

    courts = get_courts_by_slot(token, date, start, end)
    id = select(courts["data"], keyword)
    if id == None:
        print("the target slot is not found: " + title)
        return "FAILURE"
    ok = add(token, id)
    if ok == True:
        print("add to basket successfully: " + title)
        return "SCCUESS"
    else:
        print("fail to add item: " + title)
        return "FAILURE"


def multi_run_wrapper(args):
    return add_court(*args)


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


if __name__ == "__main__":
    print("started at " + now())
    manager = multiprocessing.Manager()

    config = read_from_yaml()
    token = ""

    try:
        user = login(config.username, config.password)
        token = user["token"]
    except:
        print("invalid username/password")
        sys.exit()

    numOfThreads = len(config.slots)
    args = []
    for slot in config.slots:
        args.append(
            (token, config.date, slot.start_time, slot.end_time, config.keyword)
        )

    with Pool(numOfThreads) as pool:
        results = pool.map(
            multi_run_wrapper,
            args,
        )
    print(results)
    print("finished at " + now())
