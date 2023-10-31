class Configuration:
    def __init__(self, username, password, url, keyword, date, slots):
        self.username = username
        self.password = password
        self.url = url
        self.keyword = keyword
        self.date = date
        self.slots = slots


class Slot:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
