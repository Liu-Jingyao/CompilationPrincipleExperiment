from lexical_analysis.states import STATES
from utils import *


def token_scan(inputCache):
    """
    ch: 存放当前读入的输入字符。
    token: 存放构成单词的字符串。
    :return: 当前token的(类别码，属性值)二元组
    """
    state_now = 0
    # 如果是基本状态，继续读取字符进行状态转移
    while STATES[state_now].state_type() == NORMAL_TYPE:
        ch = inputCache.getchar()
        state_now = STATES[state_now].next_state(ch)
        # 到达文件末尾，退出循环处理最后一个token
        if ch == EOF:
            break
        # 转移至ERROR_STATE，返回错误token的二元组
        if state_now == ERROR_STATE:
            return UNRECOGNIZED_TOKEN, inputCache.pop_token()
    # 如果最后转移到了终止状态，调用该状态获取二元组的方法并返回
    if STATES[state_now].state_type() == FINAL_TYPE:
        return STATES[state_now].get_value(inputCache.pop_token())
    # 如果最后转移到了需要回退的终止状态，先回退读入指针再返回二元组
    if STATES[state_now].state_type() == ROLLBACK_FINAL_TYPE:
        inputCache.retract(1)
        return STATES[state_now].get_value(inputCache.pop_token())
    # 否则当前没有任何token可识别，到达文件末尾
    return EOF_TOKEN, 0
