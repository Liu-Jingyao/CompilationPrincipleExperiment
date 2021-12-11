class TokenReceiveCache:
    """
    token接收缓存
    queue: 需要进行语法分析的token队列
    count: 记录已读入的token数量
    """
    def __init__(self, q):
        self.queue = q
        self.count = 0

    def gettoken(self):
        self.count += 1
        return self.queue.get()
