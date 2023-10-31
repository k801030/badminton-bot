import datetime
import time
import multiprocessing
from configuration import Configuration, Slot
import requests
import yaml
import main


def lambda_handler(event, context):
    starttime = time.time()
    config = main.read_from_yaml()
    user = main.login(config.username, config.password)
    token = user["token"]

    processes = []
    for slot in config.slots:
        p = multiprocessing.Process(
            target=main.add_court,
            args=(
                token,
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

    output = "That took {} seconds".format(time.time() - starttime)
    print(output)
    return output
