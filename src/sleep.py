import datetime
import time


def now():
    return datetime.datetime.now()


def sleep(delta):
    if delta > datetime.timedelta(0):
        print("now is {}, will sleep for {}".format(now(), delta))
        time.sleep(delta.total_seconds())
        print("just woke up at {}".format(now()))
        return True


def sleep_until_10pm():
    now = datetime.datetime.now()
    target = now.replace(hour=21, minute=59, second=50)
    delta = target - now
    sleep(delta)
