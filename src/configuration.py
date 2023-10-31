class Configuration:
    def __init__(self, username, password, location, activity, keyword, date, slots):
        self.username = username
        self.password = password
        self.location = location
        self.activity = activity
        self.keyword = keyword
        self.date = date
        self.slots = slots


class Slot:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
