import json

import urllib3
import helper


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs="CERT_NONE", assert_hostname=False)


def send_flex_messages(messages: json):
    secret = helper.get_line_secret()

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {secret.access_token}",
    }
    body = {"to": secret.group_id, "messages": [messages]}

    r = http.request("POST", url, body=json.dumps(body), headers=headers)
    if r.status != 200:
        print(f"failed to send message to LINE: {r.data.decode('utf-8')}")
