from models.booking_result import BookingResult
from models.shopping_cart import Cartable

SUCCESS_TITLE = "場地已加入購物車 🛒"
FAILURE_TITLE = "❌ 訂場失敗 😭😭😭"


def generate_header(title: str, date: str) -> dict:
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


def generate_body(items: list[Cartable]) -> dict:
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


def generate_footer(username: str) -> dict:
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


def generate_slot_results(results: list[BookingResult]) -> dict:
    """
    One row per requested slot: time | status.
    """
    rows = []
    for r in results:
        rows.append(
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": r.slot_name,
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0,
                    },
                    {
                        "type": "text",
                        "text": r.label,
                        "size": "sm",
                        "color": r.color,
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
        "contents": [
            {
                "type": "text",
                "text": "各時段結果",
                "size": "sm",
                "weight": "bold",
                "color": "#555555",
                "margin": "md",
            },
            *rows,
        ],
    }


def generate_messages(
    items: list[Cartable],
    date: str,
    username: str,
    results: list[BookingResult] | None = None,
) -> dict:
    contents = [{"type": "separator", "margin": "md"}]
    if items:
        title = SUCCESS_TITLE
        contents += [generate_body(items), {"type": "separator", "margin": "md"}]
    else:
        title = FAILURE_TITLE
    if results:
        contents += [
            generate_slot_results(results),
            {"type": "separator", "margin": "md"},
        ]
    contents.append(generate_footer(username))

    body = {
        "type": "box",
        "layout": "vertical",
        "contents": contents,
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


ERROR_TITLE = "⚠️ 訂場程式執行失敗"
MAX_ERROR_LENGTH = 200


def generate_error_message(date: str, account_id: str, error: Exception) -> dict:
    """
    Plain text message sent when the booking flow crashes before the
    normal result notification could be sent (e.g. login failure).
    """
    reason = f"{type(error).__name__}: {error}"[:MAX_ERROR_LENGTH]
    return {
        "type": "text",
        "text": f"{ERROR_TITLE}\n日期：{date}\n帳號：{account_id}\n原因：{reason}",
    }
