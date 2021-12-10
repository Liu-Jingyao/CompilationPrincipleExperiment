class TokenReceiveCache:

    def __init__(self, q):
        self.queue = q
        self.count = 0

    def gettoken(self):
        self.count += 1
        return self.queue.get()
