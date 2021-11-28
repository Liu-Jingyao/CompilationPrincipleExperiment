import yaml

from lexicalAnalyze.utils import *


class State:
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

    def next_state(self, str):
        for f, s in self.func_edges:
            if f(str):
                return s
        if str in self.char_edges:
            return self.char_edges[str]
        return self.other_next


class EndState(State):
    def __init__(self, num, need_rollback=False, value_func=lambda token: (CATEGORY_DICT[token], token),
                 value_func_str=''):
        super().__init__(num, func_edges=None, char_edges=None)
        self.type = ROLLBACK_FINAL_TYPE if need_rollback else FINAL_TYPE
        self.value_func_str = value_func_str
        if value_func_str:
            value_func_str = value_func_str.format(token='token')
            self.value_func = lambda token: eval(value_func_str)
        else:
            self.value_func = value_func

    def get_value(self, ch):
        return self.value_func(ch)

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