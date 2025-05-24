import datetime


def get_date(day):
    """
    Gets the future date offset by a given number of days.
    """
    today = datetime.date.today()
    return str(today + datetime.timedelta(days=day))


def now():
    return datetime.datetime.now().isoformat().split(".")[0]
