import os
import re

# 读入产生式列表
from functools import reduce

from utils import initial_production_list, EMPTY_TOKEN, EOF_TOKEN, GrammarVarEnum, print_first_or_follow, \
    print_item_closure, CATEGORY_DICT_REVERSE, print_action_or_goto

# with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "SLR1_test_grammar.txt"), "r", encoding="utf-8") as f:
#     production_list = [("S'", "S")]
#     for (left, right) in re.findall(r"(.+) (.+)", f.read()):
#         # 消解右部简写
#         production_list.extend([(left, r) for r in right.split("|")])
production_list = []
for production in initial_production_list:
    production_list.extend([(production[0], right) for right in production[1]])


V = list(set([production[0] for production in production_list]))
T = list(reduce(lambda a, b: a | b, [set([token for token in production[1] if token not in V]) for production in production_list]))
item_closure_list = []
closure_count = 0


class AnalysisTable:
    def __init__(self):
        self.action = {}
        self.goto = {}
        first = {}
        follow = {}
        # 求单个文法符号的FIRST集
        for x in T:
            first[x] = {x}
        for x in V:
            first[x] = first.get(x, set()) | {production[1][0] for production in production_list
                                              if production[0] == x and production[1][0] in T}
            if (x, (EMPTY_TOKEN, 0)) in production_list:
                first[x] = first.get(x, set()) | {(EMPTY_TOKEN, 0)}
        flag = True
        while flag:
            flag = False
            for production in production_list:
                pre_len = len(first[production[0]])
                if production[1][0] in V:
                    first[production[0]] |= first[production[1][0]] - {(EMPTY_TOKEN, 0)}
                i = 0
                for i in range(0, len(production[1])):
                    if not (production[1][i] in V and (production[1][i], (EMPTY_TOKEN, 0)) in production_list):
                        break
                for j in range(1, i):
                    first[production[0]] |= first[production[1][j]] - {(EMPTY_TOKEN, 0)}
                if i == len(production[1]):
                    first[production[0]] |= {(EMPTY_TOKEN, 0)}
                if pre_len < len(first[production[0]]):
                    flag = True
        print_first_or_follow(first, "FIRST")
        # 求FOLLOW集
        follow[GrammarVarEnum.ROOT] = {(EOF_TOKEN, 0)}
        flag = True
        while flag:
            flag = False
            for production in production_list:
                for i in range(0, len(production[1])):
                    token_or_var = production[1][i]
                    if token_or_var in V:
                        pre_len = len(follow.get(token_or_var, set()))
                        if i < len(production[1]) - 1:
                            # 求剩余文法符号串的first集
                            beta = tuple(production[1][i + 1:]) if i + 2 < len(production[1]) else production[1][i + 1]
                            if beta not in first.keys():
                                first[beta] = first[beta[0]] - {(EMPTY_TOKEN, 0)}
                                for beta_token_or_var in beta:
                                    if (EMPTY_TOKEN, 0) not in first[beta_token_or_var]:
                                        break
                                    first[beta] |= first[beta_token_or_var] - {(EMPTY_TOKEN, 0)}
                                else:
                                    first[beta] |= {(EMPTY_TOKEN, 0)}
                            follow[token_or_var] = follow.get(token_or_var, set()) | first[beta] - {(EMPTY_TOKEN, 0)}
                        if i == len(production[1]) - 1 \
                                or all(b in V and (b, (EMPTY_TOKEN, 0)) in production_list for b in production[1][i + 1:]) \
                                and production[0] != token_or_var:
                            follow[token_or_var] = follow.get(token_or_var, set()) | follow.get(production[0], set())
                        if pre_len < len(follow.get(token_or_var, set())):
                            flag = True
        print_first_or_follow(follow, "FOLLOW")
        # 建立项目集规范族
        ItemClosure.make_canonical_collection()
        # 求分析表
        for item_closure in item_closure_list:
            k = item_closure.num
            for item in item_closure.closure_list:
                if item.left == GrammarVarEnum.ROOT and item.is_reduce():
                    self.action[(k, (EOF_TOKEN, 0))] = "acc"
                elif item.is_reduce():
                    for a in follow[item.left]:
                        self.action[(k, a)] = "r" + str(item.production_num)
                else:
                    a = item.get_next_token_or_var()
                    if a in V:
                        self.goto[(k, a)] = item_closure.go[a].num
                    else:
                        self.action[(k, a)] = "S" + str(item_closure.go[a].num)
        print_action_or_goto(self.action, "ACTION")
        print_action_or_goto(self.goto, "GOTO")


class ItemClosure:
    @staticmethod
    def make_canonical_collection():
        # 得到初始项目集闭包I0
        item_closure_list.append(ItemClosure(0, [Item(production, num) for num, production in enumerate(production_list)]))
        queue_head = 0
        # 计算GO函数，递推地建立项目集规范族C
        while queue_head < len(item_closure_list):
            closure = item_closure_list[queue_head]
            x2item_list = {}
            for item in closure.closure_list:
                if not item.is_reduce():
                    x2item_list[item.get_next_token_or_var()] = x2item_list.get(item.get_next_token_or_var(), []) + [item.get_next_item()]
            item_closure_initial_list = [item_closure.initial_list for item_closure in item_closure_list]
            for x, item_list in x2item_list.items():
                if item_list not in item_closure_initial_list:
                    new_closure = ItemClosure(len(item_closure_list), item_list)
                    item_closure_list.append(new_closure)
                    closure.go[x] = new_closure
                else:
                    closure.go[x] = item_closure_list[item_closure_initial_list.index(item_list)]
            queue_head += 1
            print_item_closure(closure)

    def __init__(self, num, initial_item_list):
        self.num = num
        self.initial_list = initial_item_list
        self.closure_list = initial_item_list[:]
        self.go = {}
        flag = True
        # 计算项目集闭包
        while flag:
            flag = False
            for item in self.closure_list:
                for production_num, production in enumerate(production_list):
                    if not item.is_reduce() and item.get_next_token_or_var() == production[0] \
                            and Item(production, production_num) not in self.closure_list:
                        self.closure_list.append(Item(production, production_num))
                        flag = True

    def __eq__(self, other):
        if isinstance(other, ItemClosure):
            return other.initial_list == self.initial_list
        return False


class Item:
    def __init__(self, production, production_num):
        self.left = production[0]
        self.right = production[1]
        self.dot = 0
        self.production_num = production_num

    def __eq__(self, other):
        if isinstance(other, Item):
            return other.production_num == self.production_num and other.dot == self.dot
        return False

    def __repr__(self):
        output = str(self.left) + "->"
        for i in range(0, len(self.right)):
            if i == self.dot:
                output += "."
            token_or_var = self.right[i]
            if isinstance(token_or_var, tuple):
                output += CATEGORY_DICT_REVERSE[token_or_var[0]] + " "
            elif isinstance(token_or_var, GrammarVarEnum):
                output += token_or_var.name + " "
            else:
                output += "{ERROR} "
        if self.dot == len(self.right):
            output += "."
        return output

    def is_shift(self):
        return not self.dot

    def is_wait_reduce(self):
        return 0 < self.dot < len(self.right)

    def is_reduce(self):
        return self.dot == len(self.right)

    def get_next_token_or_var(self):
        return self.right[self.dot]

    def get_next_item(self):
        new_item = Item((self.left, self.right), self.production_num)
        new_item.dot = self.dot + 1
        return new_item
