import datetime
import logging
import time

logger = logging.getLogger(__name__)


def get_date(day):
    """
    Gets the future date offset by a given number of days.
    """
    today = datetime.date.today()
    return str(today + datetime.timedelta(days=day))


def now():
    return datetime.datetime.now().isoformat().split(".")[0]


def wait_until_next_hour():
    """
    If the current time is in the 59th minute, sleeps until the top of the next hour (:00:00).
    """
    current = datetime.datetime.now(datetime.timezone.utc)
    if current.minute == 59:
        wait_seconds = 60 - current.second - (current.microsecond / 1_000_000)
        if wait_seconds > 0:
            logger.info("Waiting %.3fs until the top of the hour", wait_seconds)
            time.sleep(wait_seconds)
