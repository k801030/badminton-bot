import json

from models.shopping_cart import Cartable

SUCCESS_TITLE = "場地已加入購物車 🛒"
FAILURE_TITLE = "❌ 訂場失敗 😭😭😭"


def generate_header(title: str, date: str) -> json:
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "通知",
                "color": "#06C755",
                "weight": "bold",
                "size": "md",
                "margin": "sm",
            },
            {
                "type": "text",
                "text": f"{title}",
                "weight": "bold",
                "size": "xl",
                "margin": "md",
            },
            {
                "type": "text",
                "text": f"{date}",
                "color": "#999999",
                "margin": "md",
            },
        ],
        "paddingBottom": "0px",
    }


def generate_body(items: list[Cartable]) -> json:
    formatted_contents = []
    for index, item in enumerate(items):
        formatted_contents.append(
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": item.get_time(),
                        "size": "md",
                        "color": "#555555",
                        "flex": 0,
                    },
                    {
                        "type": "text",
                        "text": item.get_location(),
                        "size": "md",
                        "color": "#999999",
                        "align": "end",
                        "wrap": True,
                    },
                ],
                "margin": "10px",
            }
        )
    return {
        "type": "box",
        "layout": "vertical",
        "contents": formatted_contents,
    }


def generate_footer(username: str) -> json:
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "text",
                "text": "會員帳號：",
                "size": "sm",
                "color": "#999999",
                "flex": 0,
            },
            {
                "type": "text",
                "text": f"{username}",
                "size": "sm",
                "color": "#999999",
                "align": "end",
                "wrap": True,
            },
        ],
        "margin": "20px",
    }


def generate_messages(items: list[Cartable], date: str, username: str) -> json:
    if items:
        title = SUCCESS_TITLE
        body = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "margin": "md"},
                generate_body(items),
                {"type": "separator", "margin": "md"},
                generate_footer(username),
            ],
            "paddingTop": "10px",
        }
    else:
        title = FAILURE_TITLE
        body = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "margin": "md"},
                generate_footer(username),
            ],
            "paddingTop": "10px",
        }

    return {
        "type": "flex",
        "altText": f"{title}",
        "contents": {
            "type": "bubble",
            "header": generate_header(title, date),
            "body": body,
        },
    }
