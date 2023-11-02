from datetime import datetime, timezone
import requests
import time


def cart(token):
    url = "https://better-admin.org.uk/api/activities/cart"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://myaccount.better.org.uk",
        "Authorization": token,
    }
    r = requests.get(url, headers=headers)
    return r.json()


def print_item(data):
    output = ""
    items = data["data"]["items"]
    for item in items:
        output += (
            item["cartable_resource"]["starts_at"]["format_24_hour"]
            + " - "
            + item["cartable_resource"]["ends_at"]["format_24_hour"]
            + " "
            + item["cartable_resource"]["location"]["name"]
            + "\n"
        )
    if len(items) == 0:
        output += "(empty)\n"
    print("[{}] {}".format(now(), output))

    if len(items) == 0:
        raise Exception("the cart is empty")


def now():
    return datetime.now().isoformat().split(".")[0]


token = "Bearer v4.local.ov8LkFD5rdBaZ8l9WGcFl0ogkBRcRRLlklrojwRXQOZ7EDHwqPied2t2nZfZYmQK0wJpF6hfjiQoNxEMzLcN7qwmEOAcaBvikf9qBvIVdxttTY72sogRkHJUbBNOu3X1mIQ-1G8PR-SFHL2S0oDX5lKlJlUKh-HQ1wMn25MPHzANE0s44A73tyskwEIO9j4u2JIHleumLWNfM1PFrA"

now1 = datetime.now().isoformat()
now2 = datetime.now(timezone.utc).astimezone().isoformat()
now3 = datetime.now(timezone.utc).isoformat()
print(now1)
print(now2)
print(now3)


while True:
    data = cart(token)
    print_item(data)
    time.sleep(30)
