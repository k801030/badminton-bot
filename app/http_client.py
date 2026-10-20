import json
import time

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(maxsize=10, cert_reqs="CERT_NONE", assert_hostname=False)


def not_ready_for_reservation(r):
    data = json.loads(r.data.decode("utf-8"))
    return (
        r.status == 422
        and "The date should be within the valid days" in data["message"]
    )


class CourtClient:
    host = ""
    default_header = ""

    def __init__(self):

        self.host = "https://better-admin.org.uk"
        self.default_header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://myaccount.better.org.uk",
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        }

    def login(self, username, password):
        url = "{}/api/auth/customer/login".format(self.host)
        body = {"username": username, "password": password}

        r = http.request(
            "POST", url, body=json.dumps(body), headers=self.default_header
        )
        data = json.loads(r.data.decode("utf-8"))
        if data["status"] != "success":
            raise Exception("invalid username/password")
        self.default_header["Authorization"] = "Bearer {}".format(data["token"])

    def get_courts_by_slot(
        self, location, activity, date, start_time, end_time, max_duration_seconds=15
    ):
        SLEEP_INTERVAL = 1
        url = "{}/api/activities/venue/{}/activity/{}/v2/slots?date={}&start_time={}&end_time={}".format(
            self.host, location, activity, date, start_time, end_time
        )
        started_at = time.time()
        while True:
            r = http.request("GET", url, headers=self.default_header)
            if not_ready_for_reservation(r):
                print(f"[DEBUG] Response from {url}: {r.data.decode('utf-8')}")
                if time.time() - started_at > max_duration_seconds:
                    print(
                        f"Reservation period of {max_duration_seconds} seconds has ended."
                    )
                    return {"data": []}
                time.sleep(SLEEP_INTERVAL)
                continue

            return json.loads(r.data.decode("utf-8"))

    def add(self, id) -> bool:
        url = "{}/api/activities/cart/add".format(self.host)
        body = {"items": [{"id": id, "type": "purchasableOccurrence"}]}
        r = http.request(
            "POST", url, body=json.dumps(body), headers=self.default_header
        )
        if r.status == 200:
            return True
        print(
            f"[DEBUG] Failed to add item {id} to cart: status={r.status}, response={r.data.decode('utf-8')}",
            flush=True,
        )
        return False

    def cart(self):
        url = "{}/api/activities/cart".format(self.host)
        r = http.request("GET", url, headers=self.default_header)
        data = json.loads(r.data.decode("utf-8"))
        if r.status == 200:
            return data
        elif r.status == 409:
            print("status_code={}, message={}".format(r.status, data))
            time.sleep(2)
            return self.cart()
        else:
            print("status_code={}, message={}".format(r.status, data))
            return data
