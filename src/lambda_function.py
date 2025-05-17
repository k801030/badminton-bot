import multiprocessing
import time
from configuration import Configuration, Slot
import main
from client import Client


def add_court_val(client, location, activity, date, start, end, keyword):
    main.add_court(client, location, activity, date, start, end, keyword)


def lambda_handler(event, context):
    config = main.read_from_yaml("config.yaml")
    client = Client()
    client.login(config.username, config.password)

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
    main.print_cart(data)

    # hold the items in cart
    if len(data["data"]["items"]) == 0:
        print("cart is empty, exit")
        return
    ids = main.get_ids_from_cart(client, data)
    main.check_cart_then_add(client, ids)
