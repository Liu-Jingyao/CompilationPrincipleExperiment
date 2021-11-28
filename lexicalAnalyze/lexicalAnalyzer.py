from lexicalAnalyze.states import STATES
from lexicalAnalyze.utils import *


def token_scan(inputCache):
    """
    ch: 存放当前读入的输入字符。
    token: 存放构成单词的字符串。
    getchar(): 从输入缓冲区中将下一个输入字符读入ch，并将读入指针前移。
    retract(): 将数据缓冲区读入指针向前回退一个字符，并置空ch。
    copy_token(): 返回输入缓冲区开始指针到读入指针之间的字符串。
    :return: 单词二元组 (类别，属性值)
    """
    state_now = 0
    while STATES[state_now].state_type() == NORMAL_TYPE:
        ch = inputCache.getchar()
        state_now = STATES[state_now].next_state(ch)
        if ch == EOF:
            break
        if state_now == ERROR_STATE:
            return UNRECOGNIZED_TOKEN, inputCache.pop_token()
    if STATES[state_now].state_type() == FINAL_TYPE:
        return STATES[state_now].get_value(inputCache.pop_token())
    elif STATES[state_now].state_type() == ROLLBACK_FINAL_TYPE:
        inputCache.retract(1)
        return STATES[state_now].get_value(inputCache.pop_token())
    return EOF_TOKEN, 0
