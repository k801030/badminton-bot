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

        print(f"Sending LINE message to group {group_id}...", flush=True)
        try:
            r = http.request("POST", url, body=json.dumps(body), headers=headers)
            if r.status == 200:
                print("Successfully sent LINE message.", flush=True)
            else:
                print(
                    f"Failed to send LINE message: status={r.status}, response={r.data.decode('utf-8')}",
                    flush=True,
                )
        except Exception as e:
            print(f"Failed to send LINE message error: {e}", flush=True)

    def send_notification(self, messages: json, group_id: str):
        """
        Sends the message synchronously (blocks until the request is done).
        """
        self._send_request(messages, group_id)

    def send_notification_async(
        self, messages: json, group_id: str
    ) -> threading.Thread:
        """
        Sends the message in a background thread and returns the thread.
        Callers MUST join() it before the Lambda handler returns, otherwise the
        execution environment may be frozen before the request is sent.
        """
        thread = threading.Thread(
            target=self._send_request, args=(messages, group_id), daemon=False
        )
        thread.start()
        return thread
