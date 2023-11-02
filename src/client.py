import time
from configuration import Configuration, Slot
import requests
import yaml


class Client:
    host = ""
    default_header = ""

    def __init__(self):
        self.host = "https://better-admin.org.uk"
        self.default_header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://myaccount.better.org.uk",
        }

    def login(self, username, password):
        url = "{}/api/auth/customer/login".format(self.host)
        body = {"username": username, "password": password}

        r = requests.post(url, json=body, headers=self.default_header)
        data = r.json()
        if data["status"] != "success":
            raise Exception("invalid username/password")
        self.default_header["Authorization"] = "Bearer {}".format(data["token"])

    def get_courts_by_slot(self, location, activity, date, start_time, end_time):
        SLEEP_INTERVAL = 1
        url = "{}/api/activities/venue/{}/activity/{}/slots?date={}&start_time={}&end_time={}".format(
            self.host, location, activity, date, start_time, end_time
        )
        while True:
            r = requests.get(url, headers=self.default_header)
            if self._not_ready(r):
                time.sleep(SLEEP_INTERVAL)
                continue
            return r.json()

    def _not_ready(self, r):
        return (
            r.status_code == 422
            and "The date should be within the valid days" in r.json()["message"]
        )

    def add(self, id):
        url = "{}/api/activities/cart/add".format(self.host)
        body = {"items": [{"id": id, "type": "activity"}]}
        r = requests.post(url, json=body, headers=self.default_header)
        data = r.json()
        if r.status_code == 200:
            return True
        elif r.status_code == 409:
            print("status_code={}, message={}".format(r.status_code, data))
            return self.add(id)
        elif r.status_code == 422:
            print("status_code={}, message={}".format(r.status_code, data))
        else:
            print("status_code={}, message={}".format(r.status_code, data))
        return False

    def cart(self):
        url = "{}/api/activities/cart".format(self.host)
        r = requests.get(url, headers=self.default_header)
        return r.json()
