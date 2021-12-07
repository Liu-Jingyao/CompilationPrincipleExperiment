import os
from lexical_analysis.lexicalAnalyzer import *
from lexical_analysis.Input import InputCache
from multiprocessing import Process, Queue

from syntax_analysis.SLR1Analyzer import token_analysis
from syntax_analysis.tokenReceiver import TokenReceiveCache


def lexical_analyze(q):
    inputCache = InputCache("test/test_lexical_input.txt")
    token = token_scan(inputCache)
    while token[0] != EOF_TOKEN:
        q.put(token)
        token = token_scan(inputCache)
    q.put((EOF_TOKEN, 0))
    q.close()


def syntax_analyze(q):
    tokenReceiveCache = TokenReceiveCache(q)
    token_analysis(tokenReceiveCache)


if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=lexical_analyze, args=(q,))
    p2 = Process(target=syntax_analyze, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
