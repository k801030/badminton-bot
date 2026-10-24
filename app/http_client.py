import json
import logging
import time

import urllib3

from models.booking_result import AddResult

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(maxsize=10, cert_reqs="CERT_NONE", assert_hostname=False)

logger = logging.getLogger(__name__)


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
                logger.debug(
                    "Not ready for reservation yet: %s", r.data.decode("utf-8")
                )
                if time.time() - started_at > max_duration_seconds:
                    logger.info(
                        "Date still not bookable after %ss", max_duration_seconds
                    )
                    # mark the response so callers can tell "not open yet" from "0 courts"
                    return {"data": [], "not_ready": True}
                time.sleep(SLEEP_INTERVAL)
                continue

            return json.loads(r.data.decode("utf-8"))

    def add(self, id) -> AddResult:
        url = "{}/api/activities/cart/add".format(self.host)
        body = {"items": [{"id": id, "type": "purchasableOccurrence"}]}
        r = http.request(
            "POST", url, body=json.dumps(body), headers=self.default_header
        )
        if r.status == 200:
            return AddResult(ok=True, status=r.status)
        raw = r.data.decode("utf-8")
        logger.debug(
            "Failed to add item %s to cart: status=%s, response=%s", id, r.status, raw
        )
        try:
            message = json.loads(raw).get("message", raw)
        except (ValueError, AttributeError):
            message = raw
        return AddResult(ok=False, status=r.status, message=message)

    def cart(self):
        url = "{}/api/activities/cart".format(self.host)
        r = http.request("GET", url, headers=self.default_header)
        data = json.loads(r.data.decode("utf-8"))
        if r.status == 200:
            return data
        elif r.status == 409:
            logger.warning("Cart request conflicted (409), retrying")
            time.sleep(2)
            return self.cart()
        else:
            logger.error("Cart request failed: status=%s", r.status)
            return data
