class Snapshot:
    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp

def get_data():
    return [Snapshot(1, "2019-08-18 00:24:03")]