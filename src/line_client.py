import json

import urllib3

import helper


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)


def _generate_flex_message(contents: list, title: str) -> json:
    formatted_contents = [{"type": "text", "text": f"• {content}", "size": "md"} for content in contents]
    return {
        "type": "flex",
        "altText": f"{title}",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{title}", "weight": "bold", "size": "lg"}
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": formatted_contents,
            }
        }
    }


def send_flex_message(contents: list, title="✅ 場地已加入購物車"):
    secret = helper.get_line_secret()

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {secret.access_token}'
    }
    body = {
        'to': secret.group_id,
        'messages': [_generate_flex_message(contents, title)]
    }

    r = http.request("POST", url, body=json.dumps(body), headers=headers)
    if r.status != 200:
        print(f"failed to send message to LINE: {r.data.decode('utf-8')}")
