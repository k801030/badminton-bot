import json
import threading

import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs="CERT_NONE", assert_hostname=False)


class LineClient:
    def __init__(self, access_token):
        self.access_token = access_token

    def _send_request(self, messages: json, group_id: str):

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        body = {"to": group_id, "messages": [messages]}

        try:
            r = http.request("POST", url, body=json.dumps(body), headers=headers)
            if r.status != 200:
                print(f"failed to send LINE message: {r.data.decode('utf-8')}")
        except Exception as e:
            print(f"failed to send LINE message: {e}")

    def send_notification_async(self, messages: json, group_id: str):
        threading.Thread(
            target=self._send_request, args=(messages, group_id), daemon=False
        ).start()
