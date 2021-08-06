import datetime

class Node:
    id = False
    last_seen = None

    def __init__(self):
        self.update_last_seen()
        return

    def update_last_seen(self):
        self.last_seen = datetime.datetime.now()
        return True

    
