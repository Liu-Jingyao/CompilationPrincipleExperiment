class TokenReceiveCache:

    def __init__(self, q):
        self.queue = q

    def gettoken(self):
        return self.queue.get()
