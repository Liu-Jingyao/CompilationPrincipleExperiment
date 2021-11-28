ERROR_STATE = -1

NORMAL_TYPE = 1
FINAL_TYPE = 2
ROLLBACK_FINAL_TYPE = 3

EOF = "EOF"

EOF_TOKEN = -1
UNRECOGNIZED_TOKEN = 0
IDENTIFIER = 1
INTEGER = 2
REAL_NUMBER = 3
SPLIT = 4

CATEGORY_DICT = {
    # 文件结束: -1
    # 识别出错: 0
    # 标识符: 1
    # 整数: 2
    # 实数: 3
    # 分隔符: 4
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
    "while": 131
}


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


CHARSET_FUNC_DICT = {
    'space': judge_space,
    'letter': judge_letter,
    'digit': judge_digit,
    'split': judge_split
}
