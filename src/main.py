import multiprocessing
import multiprocessing
import sys
from multiprocessing import Pool

from client import Client
from helper import now, multi_run_wrapper, print_cart, get_ids_from_cart, reserve_the_items_in_cart, \
    read_from_json, get_account


sample_config = {
    "accountId": "1",
    "location": "queensbridge-sports-community-centre",
    "activity": "badminton-40min",
    "keyword": "Court 1, Court 2",
    "day": 3,
    "slots": [
        {
            "start_time": "16:00",
            "end_time": "16:40"
        },
        {
            "start_time": "18:00",
            "end_time": "18:40"
        }
    ]
}

if __name__ == "__main__":
    print("started at " + now())
    manager = multiprocessing.Manager()
    config = read_from_json(sample_config)

    client = Client()
    account = get_account(config.account_id)

    try:
        client.login(account.username, account.password)
    except:
        print("invalid username/password")
        sys.exit()

    numOfThreads = len(config.slots)
    args = []
    for slot in config.slots:
        args.append(
            (
                client,
                config.location,
                config.activity,
                config.date,
                slot.start_time,
                slot.end_time,
                config.keyword,
            )
        )
    with Pool(numOfThreads) as pool:
        results = pool.map(
            multi_run_wrapper,
            args,
        )

    print("Get results " + str(results))
    data = client.cart()
    print_cart(data)
    print("finished at " + now())

    ids = get_ids_from_cart(client, data)
    reserve_the_items_in_cart(client, ids)
