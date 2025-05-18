import multiprocessing

import helper
from client import Client


client = Client()


def add_court_val(client, location, activity, date, start, end, keyword):
    helper.add_court(client, location, activity, date, start, end, keyword)


def handler(event, context):
    print("receive event: " + str(event))

    config = helper.read_json_event(event)
    account = helper.get_account(config.account_id)

    client.login(account.username, account.password)

    processes = []
    for slot in config.slots:
        p = multiprocessing.Process(
            target=add_court_val,
            args=(
                client,
                config.location,
                config.activity,
                config.date,
                slot.start_time,
                slot.end_time,
                config.keyword,
            ),
        )
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

    # print cart
    data = client.cart()
    helper.print_cart(data)

    # hold the items in cart
    if len(data["data"]["items"]) == 0:
        print("cart is empty, exit")
        return
    ids = helper.get_ids_from_cart(client, data)
    helper.reserve_the_items_in_cart(client, ids)
