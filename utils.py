# 词法分析器

# 特殊状态下标
from enum import Enum, unique, auto

ERROR_STATE = -1

# 状态类型
NORMAL_TYPE = 1
FINAL_TYPE = 2
ROLLBACK_FINAL_TYPE = 3

# 特殊字符
EOF = "EOF"

# 特殊token类别码
EOF_TOKEN = -1
UNRECOGNIZED_TOKEN = 0
IDENTIFIER = 1
INTEGER = 2
REAL_NUMBER = 3
SPLIT = 4
CHAR = 5
STRING = 6
# 仅语法分析阶段
EMPTY_TOKEN = 7

# token类别码表
CATEGORY_DICT = {
    # 特殊类别
    "#": -1,
    "未识别单词": 0,
    "标识符": 1,
    "整数": 2,
    "实数": 3,
    ";": 4,
    "字符": 5,
    "字符串": 6,
    "ε": 7,
    # 字符
    "<=": 11,
    "<": 12,
    ">=": 13,
    ">": 14,
    "==": 15,
    "=": 16,
    "!=": 17,
    "!": 18,
    "+": 19,
    "-": 20,
    "/": 21,
    "*": 22,
    "%": 23,
    ",": 24,
    "(": 25,
    ")": 26,
    "[": 27,
    "]": 28,
    "{": 29,
    "}": 30,
    "'": 31,
    '"': 32,
    '&&': 33,
    '||': 34,

    # 关揵字
    "auto": 100,
    "break": 101,
    "case": 102,
    "char": 103,
    "const": 104,
    "continue": 105,
    "default": 106,
    "do": 107,
    "double": 108,
    "else": 109,
    "enum": 110,
    "extern": 111,
    "float": 112,
    "for": 113,
    "goto": 114,
    "if": 115,
    "int": 116,
    "long": 117,
    "register": 118,
    "return": 119,
    "short": 120,
    "signed": 121,
    "static": 122,
    "sizeof": 123,
    "struct": 124,
    "switch": 125,
    "typedef": 126,
    "union": 127,
    "unsigned": 128,
    "void": 129,
    "volatile": 130,
    "while": 131,
    "true": 132,
    "false": 133,
    "string": 134
}

CATEGORY_DICT_REVERSE = dict((v, k) for k, v in CATEGORY_DICT.items())


# 字符集合判断函数


def judge_space(token):
    return token.isspace()


def judge_letter(token):
    return token.isalpha()


def judge_digit(token):
    return token.isdigit()


def judge_letter_or_digit(token):
    return token.isalnum()


def judge_split(token):
    return token == ";"


# 字符集合-判断函数字典
CHARSET_FUNC_DICT = {
    'space': judge_space,
    'letter': judge_letter,
    'digit': judge_digit,
    'split': judge_split
}


# 语法分析器
# 文法变量
@unique
class GrammarVarEnum(Enum):
    ROOT = auto()  # S'
    PROG_BLOCK = auto()  # S
    FUNC_DEF = auto()
    FUNC_BLOCK = auto()
    FUNC_CALL = auto()
    VAR_DECLARE = auto()
    VAR_ASSIGN = auto()
    VALUE_EXPRESSION = auto()
    BOOL_EXPRESSION = auto()
    TYPE = auto()
    CMP_OPT = auto()
    CAL_OPT = auto()
    LOOP = auto()
    BRANCH = auto()
    FORM_PARAM = auto()
    REAL_PARAM = auto()

    def __repr__(self):
        return self.name


# 产生式列表
# todo 改造成右线性文法
initial_production_list = [
    # 程序->程序块
    (GrammarVarEnum.ROOT, [[GrammarVarEnum.PROG_BLOCK]]),
    # 程序块->函数定义|变量声明 分号|程序块 程序块
    (GrammarVarEnum.PROG_BLOCK, [[GrammarVarEnum.FUNC_DEF], [GrammarVarEnum.VAR_DECLARE, (SPLIT, 0)],
                                 [GrammarVarEnum.PROG_BLOCK, GrammarVarEnum.PROG_BLOCK]]),
    # 函数定义->类型 标识符 左括号 形式参数 右括号 左大括号 函数块 右大括号
    (GrammarVarEnum.FUNC_DEF, [
        [GrammarVarEnum.TYPE, (IDENTIFIER, 0), (25, 0), GrammarVarEnum.FORM_PARAM, (26, 0), (29, 0),
         GrammarVarEnum.FUNC_BLOCK, (30, 0)]]),
    # 变量声明->类型 标识符
    (GrammarVarEnum.VAR_DECLARE, [[GrammarVarEnum.TYPE, (IDENTIFIER, 0)]]),
    # 形式参数->类型 标识符|类型 标识符 逗号 形式参数
    (GrammarVarEnum.FORM_PARAM, [[GrammarVarEnum.TYPE, (IDENTIFIER, 0)],
                                 [GrammarVarEnum.TYPE, (IDENTIFIER, 0), (24, 0), GrammarVarEnum.FORM_PARAM]]),
    # 函数块->变量声明 分号|变量赋值 分号|函数调用 分号|循环结构|分支结构|函数块 函数块
    (GrammarVarEnum.FUNC_BLOCK, [[GrammarVarEnum.VAR_DECLARE, (SPLIT, 0)], [GrammarVarEnum.VAR_ASSIGN, (SPLIT, 0)],
                                 [GrammarVarEnum.FUNC_CALL, (SPLIT, 0)], [GrammarVarEnum.LOOP], [GrammarVarEnum.BRANCH],
                                 [GrammarVarEnum.FUNC_BLOCK, GrammarVarEnum.FUNC_BLOCK]]),
    # 变量赋值->标识符 等号 算术表达式|标识符 等号 布尔表达式
    (GrammarVarEnum.VAR_ASSIGN, [[(IDENTIFIER, 0), (16, 0), GrammarVarEnum.VALUE_EXPRESSION],
                                 [(IDENTIFIER, 0), (16, 0), GrammarVarEnum.BOOL_EXPRESSION]]),
    # 算术表达式->算术表达式 算术运算符 算术表达式|负号 算术表达式|函数调用|左括号 算术表达式 右括号|标识符|整数|实数
    (GrammarVarEnum.VALUE_EXPRESSION,
     [[GrammarVarEnum.VALUE_EXPRESSION, GrammarVarEnum.CAL_OPT, GrammarVarEnum.VALUE_EXPRESSION],
      [(20, 0), GrammarVarEnum.VALUE_EXPRESSION], [GrammarVarEnum.FUNC_CALL],
      [(25, 0), GrammarVarEnum.VALUE_EXPRESSION, (26, 0)], [(IDENTIFIER, 0)], [(INTEGER, 0)], [(REAL_NUMBER, 0)]]),
    # 布尔表达式->算术表达式 比较运算符 算术表达式|布尔表达式 与符号 布尔表达式|布尔表达式 或符号 布尔表达式|非符号 布尔表达式|函数调用|左括号 布尔表达式 右括号|标识符|真|假
    (GrammarVarEnum.BOOL_EXPRESSION,
     [[GrammarVarEnum.VALUE_EXPRESSION, GrammarVarEnum.CMP_OPT, GrammarVarEnum.VALUE_EXPRESSION],
      [GrammarVarEnum.BOOL_EXPRESSION, (33, 0), GrammarVarEnum.BOOL_EXPRESSION],
      [GrammarVarEnum.BOOL_EXPRESSION, (34, 0), GrammarVarEnum.BOOL_EXPRESSION],
      [(18, 0), GrammarVarEnum.BOOL_EXPRESSION], [GrammarVarEnum.FUNC_CALL],
      [(25, 0), GrammarVarEnum.BOOL_EXPRESSION, (26, 0)], [(IDENTIFIER, 0)], [(132, 0)], [(133, 0)]]),
    # 函数调用->标识符 左括号 实际参数 右括号
    (GrammarVarEnum.FUNC_CALL, [[(IDENTIFIER, 0), (25, 0), GrammarVarEnum.REAL_PARAM, (26, 0)]]),
    # 实际参数->标识符|标识符 逗号 实际参数
    (GrammarVarEnum.REAL_PARAM, [[(IDENTIFIER, 0)], [(IDENTIFIER, 0), (24, 0), GrammarVarEnum.REAL_PARAM]]),
    # 循环结构->关揵字while 左括号 布尔表达式 右括号 左大括号 函数块 右大括号
    (GrammarVarEnum.LOOP,
     [[(131, 0), (25, 0), GrammarVarEnum.BOOL_EXPRESSION, (26, 0), (29, 0), GrammarVarEnum.FUNC_BLOCK, (30, 0)]]),
    # 分支结构->关键字if 左括号 布尔表达式 右括号 左大括号 函数块 右大括号|关键字if 左括号 布尔表达式 右括号 左大括号 函数块 右大括号 关键字else 左大括号 函数块 右大括号
    (GrammarVarEnum.BRANCH,
     [[(115, 0), (25, 0), GrammarVarEnum.BOOL_EXPRESSION, (26, 0), (29, 0), GrammarVarEnum.FUNC_BLOCK, (30, 0)],
      [(115, 0), (25, 0), GrammarVarEnum.BOOL_EXPRESSION, (26, 0), (29, 0), GrammarVarEnum.FUNC_BLOCK, (30, 0),
       (109, 0), (29, 0), GrammarVarEnum.FUNC_BLOCK, (30, 0)]]),
    # 类型->关联字int|关键字char|关键字string|关键字float
    (GrammarVarEnum.TYPE, [[(116, 0)], [(103, 0)], [(134, 0)], [(112, 0)]]),
    # 算术运算符->加号|减号|乘号|除号|百分号
    (GrammarVarEnum.CAL_OPT, [[(19, 0)], [(20, 0)], [(21, 0)], [(22, 0)], [(23, 0)]]),
    # 比较运算符->大于|小于|等于|大于等于|小于等于|不等于
    (GrammarVarEnum.CMP_OPT, [[(14, 0)], [(12, 0)], [(15, 0)], [(13, 0)], [(11, 0)], [(17, 0)]])
]


def fill_production(production, pop_token):
    filled_production = (production[0], pop_token)
    return filled_production


def print_first_or_follow(first_or_follow, mode):
    print(mode + "集:")
    item_list = sorted([item for item in first_or_follow.items() if isinstance(item[0], GrammarVarEnum)],
                       key=lambda x: x[0].value)
    for key, value in item_list:
        if isinstance(key, GrammarVarEnum):
            print_value = {CATEGORY_DICT_REVERSE[token[0]] for token in value}
            print(key.name + ': ' + str(print_value))
    print("\n\n----------------------------------------------------------------\n\n")


def print_item_closure(item_closure):
    print("closure(%d):" % item_closure.num)
    print("item_list:", item_closure.closure_list)
    print("go_list:", {CATEGORY_DICT_REVERSE[token_or_var[0]] if isinstance(token_or_var, tuple) else token_or_var: s.num for token_or_var, s in item_closure.go.items()})


def print_production(production):
    output = str(production[0]) + "->"
    for token_or_var in production[1]:
        if isinstance(token_or_var, tuple):
            if token_or_var[0] in [1, 2, 3]:
                output += str(token_or_var[1])
            elif token_or_var[0] == 4:
                output += ';'
            elif token_or_var[0] == 5:
                output += "'%s'" % token_or_var[1]
            elif token_or_var[0] == 6:
                output += '"%s"' % token_or_var[1]
            else:
                output += CATEGORY_DICT_REVERSE[token_or_var[0]]
        elif isinstance(token_or_var, GrammarVarEnum):
            output += token_or_var.name
        else:
            output += "{ERROR}"
    print(output)
