class Event:
    def __init__(self, time: str, type: str, notes: str, cam: int, capture: str):
        self.timestamp = time
        self.type = type
        self.notes = ''
        self.cam = cam
        self.capture = capture 

    def __list__(self):
        return [self.timestamp, self.type, self.notes, self.cam, self.capture]
    
    def __str__(self):
        return str(list(self))
    


class EventManager:
    def __init__(self):
        self.data: list = []

    
    def log(self, data):
        self.data.append(data)
    
    @classmethod
    def fromDB():
        return EventManager()

    def save(self):
        pass