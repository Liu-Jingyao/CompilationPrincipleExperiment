import yaml

from lexicalAnalyze.utils import *


class State:
    """
    基本状态类
    属性：
    num: 状态编号
    func_edges: 以ch属于字符集合为转移条件的边，以方法引用形式保存
    char_edges: 以ch等于某个字符为转移条件的边，以键值对形式保存
    other_next: ch为其他情况下转移的目标状态，如果不存在other边则转移至ERROR_STATE
    type: 状态类型，基本状态为1，终止状态为2，需要回退的终止状态为3
    方法：
    state_type(): 获取状态类型
    next_state(): 对于当前字符ch，给出下一个状态的编号
    """

    def __init__(self, num, func_edges=None, char_edges=None, other_next=ERROR_STATE):
        if func_edges is None:
            func_edges = []
        if char_edges is None:
            char_edges = {}
        self.num = num
        self.func_edges = func_edges
        self.char_edges = char_edges
        self.other_next = other_next
        self.type = NORMAL_TYPE

    def state_type(self):
        return self.type

    def next_state(self, ch):
        for f, s in self.func_edges:
            if f(ch):
                return s
        if ch in self.char_edges:
            return self.char_edges[ch]
        return self.other_next


class EndState(State):
    """
    终止状态类（继承自基本状态类）
    属性：
    type: 状态类型，基本状态为1，终止状态为2，需要回退的终止状态为3
    need_rollback: 是否需要回退
    value_func: 得到(类别码，属性值)二元组的方法引用，默认为从CATEGORY_DICT取类别码
    value_func_str: 得到(类别码，属性值)二元组的命令语句，从yaml文件中读取
    方法：
    get_value(token): 获取当前单词的(类别码，属性值)二元组
    """

    def __init__(self, num, need_rollback=False, value_func_str='(CATEGORY_DICT[token], token)'):
        super().__init__(num, func_edges=None, char_edges=None)
        self.type = ROLLBACK_FINAL_TYPE if need_rollback else FINAL_TYPE
        self.value_func_str = value_func_str
        self.value_func = lambda token: eval(value_func_str)

    def get_value(self, token):
        return self.value_func(token)


# 解析yaml状态转换图
STATES = [None for _ in range(200)]
with open('stateProperties.yaml', 'r', encoding='utf-8') as f:
    file_data = f.read()
    data = yaml.load(file_data, Loader=yaml.FullLoader)
    state_data_list = data['states']
    for state_data in state_data_list:
        if 'final' in state_data.keys():
            if 'token' in state_data.keys():
                state = EndState(state_data['num'], state_data['rollback'], value_func_str=state_data['token'])
            else:
                state = EndState(state_data['num'], state_data['rollback'])
        else:
            func_edges = [(CHARSET_FUNC_DICT[key], state_data['edges'][key]) for key in
                          set(state_data['edges'].keys()) & set(CHARSET_FUNC_DICT.keys())]
            char_edges = {key: state_data['edges'][key] for key in
                          set(state_data['edges'].keys()) & set(CATEGORY_DICT.keys())}
            if 'other' in state_data['edges'].keys():
                state = State(state_data['num'], func_edges, char_edges, state_data['edges']['other'])
            else:
                state = State(state_data['num'], func_edges, char_edges)
        STATES[state_data['num']] = state
