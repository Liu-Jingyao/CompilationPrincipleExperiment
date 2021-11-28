from lexicalAnalyze.utils import EOF


class InputCache:
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

    def beginning_forward(self):
        self.__beginning += 1