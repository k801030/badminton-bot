import json

from models.shopping_cart import Cartable


SUCCESS_TITLE = "場地已加入購物車 🛒"
FAILURE_TITLE = "❌ 訂場失敗 😭😭😭"


def generate_messages(items: list[Cartable], date: str) -> json:
    if items:
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

        title = SUCCESS_TITLE
        body = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "separator", "margin": "md"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": formatted_contents,
                },
            ],
            "paddingTop": "10px",
        }
    else:
        title = FAILURE_TITLE
        body = {
            "type": "box",
            "layout": "vertical",
            "contents": [],
            "paddingTop": "10px",
        }

    return {
        "type": "flex",
        "altText": f"{title}",
        "contents": {
            "type": "bubble",
            "header": {
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
            },
            "body": body,
        },
    }
