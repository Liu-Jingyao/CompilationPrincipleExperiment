import os
from lexical_analysis.lexicalAnalyzer import *
from lexical_analysis.Input import InputCache
from multiprocessing import Process, Queue

from syntax_analysis.SLR1Analyzer import token_analysis
from syntax_analysis.tokenReceiver import TokenReceiveCache


def lexical_analyze(q):
    """
    词法分析进程
    :param q:
    :return:
    """
    inputCache = InputCache("test/test_lexical_input.txt")
    token = token_scan(inputCache)
    # 读入token直到到达文件末尾
    while token[0] != EOF_TOKEN_CATEGORY:
        # 忽略识别失败的单词并输出
        while token[0] == UNRECOGNIZED_TOKEN_CATEGORY:
            print("[ERROR] 检测到词法错误, 无法识别单词%s" % token[1])
            token = token_scan(inputCache)
        # 将识别成功的token放入队列进行语法分析
        q.put(token)
        token = token_scan(inputCache)
    # 将结束符放入队列
    q.put((EOF_TOKEN_CATEGORY, 0))
    q.close()


def syntax_analyze(q):
    """
    语法分析进程
    :param q:
    :return:
    """
    tokenReceiveCache = TokenReceiveCache(q)
    token_analysis(tokenReceiveCache)


if __name__ == '__main__':
    """
    SLR(1)语法分析程序入口函数
    输入文件：test/test_lexical_input.txt
    启动两个进程p1, p2分别进行词法与语法分析。进程间通过队列传递token，提高运行效率。
    """
    q = Queue()
    p1 = Process(target=lexical_analyze, args=(q,))
    p2 = Process(target=syntax_analyze, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
