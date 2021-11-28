from lexicalAnalyze.utils import EOF


class InputCache:
    """
    输入缓存类（按行缓存）
    属性:
    f: 输入文件
    cache: 行读入缓存
    beginning: 当前token起始位置
    forward: 待读取字符位置
    方法:
    getchar(): 从输入缓冲区中将下一个输入字符读入ch，并将读入指针前移。
    retract(num=1): 将数据缓冲区读入指针向前回退num个字符。
    pop_token(): 返回输入缓冲区开始指针到读入指针之间的字符串，并将开始指针与读入指针放到下一个token的位置。
    """
    def __init__(self, file):
        self.__cache = ""
        self.__beginning = 0
        self.__forward = 0
        self.__f = open(file, "r")

    def __del__(self):
        self.__f.close()

    def getchar(self):
        if self.__forward == len(self.__cache):
            if self.__beginning == self.__forward:
                self.__cache = self.__f.readline().strip()
                self.__beginning = 0
                self.__forward = 0
            else:
                self.__forward += 1
                return ""
        if not self.__cache:
            return EOF
        ch = self.__cache[self.__forward]
        self.__forward += 1
        return ch

    def retract(self, num=1):
        if self.__forward:
            self.__forward -= num

    def pop_token(self):
        token = self.__cache[self.__beginning: self.__forward]
        self.__beginning = self.__forward
        self.__forward = self.__beginning
        return token.lstrip()