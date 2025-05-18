class Configuration:
    def __init__(self, account_id, location, activity, keyword, date, slots):
        self.account_id = account_id
        self.location = location
        self.activity = activity
        self.keyword = keyword
        self.date = date
        self.slots = slots


class Slot:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
