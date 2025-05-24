import json

import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs="CERT_NONE", assert_hostname=False)


class LineClient:
    def __init__(self, access_token):
        self.access_token = access_token

    def send_flex_messages(self, messages: json, group_id: str):

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        body = {"to": group_id, "messages": [messages]}

        r = http.request("POST", url, body=json.dumps(body), headers=headers)
        if r.status != 200:
            print(f"failed to send message to LINE: {r.data.decode('utf-8')}")
