import os
import re

from functools import reduce
from utils import initial_production_list, EMPTY_TOKEN, EOF_TOKEN_CATEGORY, GrammarVarEnum, print_first_or_follow, \
    print_item_closure, CATEGORY_DICT_REVERSE, print_action_or_goto

production_list = []
# 获取产生式列表，将initial_production_list中多个右部合写的产生式拆解为多个单右部的产生式
for production in initial_production_list:
    production_list.extend([(production[0], right) for right in production[1]])

# 检索产生式中所有文法变量获得非终结符集V
V = list(set([production[0] for production in production_list]))
# 检索产生式中所有非文法变量符号，获得终结符集T
T = list(reduce(lambda a, b: a | b,
                [set([token for token in production[1] if token not in V]) for production in production_list]))
# item_closure_list: 项目集规范族列表
item_closure_list = []
# closure_count: 用于有序生成项目集规范族的计数器
closure_count = 0


class AnalysisTable:
    """
    SLR(1)状态分析表
    属性:
    action: 动作表, 表示一个状态面临输入符号时应采取的动作，可能动作包括: 移进、归约、接受和报错
    goto: 转移表, 表示一个状态刚归约出文法变量时应转向的下一个状态
    follow: 后继符号集，表示一个文法变量后面所有可能跟随的文法符号
    方法:
    构造函数: 根据产生式列表求解action、goto分析表，包含四个步骤，每个步骤都有结果输出：
        1. 求单个文法符号的FIRST集
        2. 求文法变量的FOLLOW集
        3. 建立项目集规范族
        4. 建立SLR(1)分析表
    """

    def __init__(self):
        self.action = {}
        self.goto = {}
        self.follow = {}
        first = {}
        # 求单个文法符号的FIRST集
        # 终结符的first集只有自身
        for x in T:
            first[x] = {x}
        for x in V:
            # 对于每个非终结符，找出其能直接推导出的以终结符开头的右部，first集中加入此终结符
            first[x] = first.get(x, set()) | {production[1][0] for production in production_list
                                              if production[0] == x and production[1][0] in T}
            # 如果该文法变量能推出epsilon，将epsilon加入first集
            if (x, (EMPTY_TOKEN, 0)) in production_list:
                first[x] = first.get(x, set()) | {(EMPTY_TOKEN, 0)}
        flag = True
        # 不断利用文法变量间的关系扩展first集，直到所有first集不变为止
        while flag:
            flag = False
            for production in production_list:
                pre_len = len(first[production[0]])
                # 对于每一个产生式，若右部以非终结符开头，则将开头变量的first集并入左部的first(去除epsilon)
                if production[1][0] in V:
                    first[production[0]] |= first[production[1][0]] - {(EMPTY_TOKEN, 0)}
                i = 0
                # 若右部以若干连续的能推出epsilon的非终结符开头，则将这些非终结符的first集都并入左部的first(去除epsilon)
                for i in range(0, len(production[1])):
                    if not (production[1][i] in V and (production[1][i], (EMPTY_TOKEN, 0)) in production_list):
                        break
                for j in range(1, i):
                    first[production[0]] |= first[production[1][j]] - {(EMPTY_TOKEN, 0)}
                # 若整个右部可以推为一个epsilon, 将epsilon并入左部的first集
                if i == len(production[1]):
                    first[production[0]] |= {(EMPTY_TOKEN, 0)}
                if pre_len < len(first[production[0]]):
                    flag = True
        # 打印first集
        print_first_or_follow(first, "FIRST")
        # 求文法变量的FOLLOW集
        # 将终止符token加入初始符号的follow集
        self.follow[GrammarVarEnum.ROOT] = {(EOF_TOKEN_CATEGORY, 0)}
        flag = True
        # 不断扩展FOLLOW集直到所有文法变量的FOLLOW集都不变为止
        while flag:
            flag = False
            for production in production_list:
                for i in range(0, len(production[1])):
                    token_or_var = production[1][i]
                    if token_or_var in V:
                        # 对于列表中每一个产生式，遍历其右部每一个文法变量
                        pre_len = len(self.follow.get(token_or_var, set()))
                        if i < len(production[1]) - 1:
                            beta = tuple(production[1][i + 1:]) if i + 2 < len(production[1]) else production[1][i + 1]
                            if beta not in first.keys():
                                # 求当前文法变量的后续文法符号串beta的first集
                                # 将beta首字符first集并入beta的first集(去除epsilon)
                                first[beta] = first[beta[0]] - {(EMPTY_TOKEN, 0)}
                                for beta_token_or_var in beta:
                                    # 如果beta以连续能推出epsilon的文法变量为起始，依次将这些变量的first集并入beta的first集
                                    if (EMPTY_TOKEN, 0) not in first[beta_token_or_var]:
                                        break
                                    first[beta] |= first[beta_token_or_var] - {(EMPTY_TOKEN, 0)}
                                else:
                                    # 如果beta完全由能推出epsilon的文法变量组成，将epsilon加入beta的first集
                                    first[beta] |= {(EMPTY_TOKEN, 0)}
                            # 将后续文法符号串beta的first集并入当前文法变量的follow集
                            self.follow[token_or_var] = self.follow.get(token_or_var, set()) | first[beta] - {
                                (EMPTY_TOKEN, 0)}
                        if i == len(production[1]) - 1 \
                                or all(
                            b in V and (b, (EMPTY_TOKEN, 0)) in production_list for b in production[1][i + 1:]) \
                                and production[0] != token_or_var:
                            # 如果当前文法变量是右部的末尾字符或后续文法符号串能推为epsilon，将产生式左部的follow集并入当前文法变量的follow集
                            # 这一条表示，任何一个终结符如果可以紧跟着右部末尾变量出现，那么该终结符也可以紧跟着左部出现(反之不然!)
                            self.follow[token_or_var] = self.follow.get(token_or_var, set()) | self.follow.get(
                                production[0], set())
                        if pre_len < len(self.follow.get(token_or_var, set())):
                            flag = True
        # 打印follow集
        print_first_or_follow(self.follow, "FOLLOW")
        # 建立项目集规范族
        ItemClosure.make_canonical_collection()
        # 建立SLR(1)分析表
        for item_closure in item_closure_list:
            # 对于项目集规范族中的每一个状态(闭包)构造分析表
            k = item_closure.num
            for item in item_closure.closure_list:
                if item.left == GrammarVarEnum.ROOT and item.is_reduce():
                    # 规范族中存在归约项目S'->S, 置接收终止符的动作为分析完成
                    self.action[(k, (EOF_TOKEN_CATEGORY, 0))] = "acc"
                elif item.is_reduce():
                    # 规范族中存在其它归约项目, 置接收归约项目左部follow中终结符的动作为归约
                    for a in self.follow[item.left]:
                        self.action[(k, a)] = "r" + str(item.production_num)
                elif item.is_wait_reduce():
                    # 规范族中存在待约项目(点号后是非终结符), 置归约出所需非终结符后的转移目标为闭包的go
                    a = item.get_next_token_or_var()
                    self.goto[(k, a)] = item_closure.go[a].num
                else:
                    # 项目集中存在移进项目(点号后是终结符), 置接收所需终结符后的动作为移入
                    a = item.get_next_token_or_var()
                    self.action[(k, a)] = "S" + str(item_closure.go[a].num)
        # 打印action表与goto表
        print_action_or_goto(self.action, "ACTION")
        print_action_or_goto(self.goto, "GOTO")


class ItemClosure:
    """
    项目集闭包类
    属性:
    num: 项目集闭包序号
    initial_list: 求闭包之前的项目集
    closure_list: 项目集闭包
    go: 表示当前状态面临文法符号的转移状态，存储的是后继状态的引用而非序号
    """

    @staticmethod
    def make_canonical_collection():
        """
        构建项目集规范族列表
        :return:
        """
        # 得到初始项目集闭包I0
        item_closure_list.append(
            ItemClosure(0, [Item(production, num) for num, production in enumerate(production_list)]))
        queue_head = 0
        # 维护一个待扩展闭包队列, 用BFS的思想递推建立项目集规范族C
        while queue_head < len(item_closure_list):
            # 每次取出队首待扩展闭包
            closure = item_closure_list[queue_head]
            # 建立对于当前闭包，输入文法符号与后继闭包的映射x2item_list
            x2item_list = {}
            # 对于当前闭包中每一个非归约项目
            for item in closure.closure_list:
                if not item.is_reduce():
                    x2item_list[item.get_next_token_or_var()] = x2item_list.get(item.get_next_token_or_var(), []) + [
                        item.get_next_item()]
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
        # 由初始项目集计算项目集闭包
        # 持续扩展直到结果不再扩大
        while flag:
            flag = False
            # 对中间结果中每一个非归约项目B->alpha.A beta，寻找所有形如A->gama的产生式加入中间结果
            for item in self.closure_list:
                for production_num, production in enumerate(production_list):
                    if item.is_wait_reduce() and item.get_next_token_or_var() == production[0] \
                            and Item(production, production_num) not in self.closure_list:
                        self.closure_list.append(Item(production, production_num))
                        flag = True

    def __eq__(self, other):
        """
        重载项目集闭包对象判断相等的方法，便于查询一个闭包是否已存在于项目集规范族列表中
        :param other:
        :return:
        """
        if isinstance(other, ItemClosure):
            return other.initial_list == self.initial_list
        return False


class Item:
    """
    LR(1)项目类
    属性：
    left: 语法项目左部
    right: 语法项目右部
    dot: 待推导位置
    production_num: 对应产生式的序号
    """

    def __init__(self, production, production_num):
        self.left = production[0]
        self.right = production[1]
        self.dot = 0
        self.production_num = production_num

    def __eq__(self, other):
        """
        重载语法项目对象判断相等的方法，便于查询一个项目是否存在于项目集中
        :param other:
        :return:
        """
        if isinstance(other, Item):
            return other.production_num == self.production_num and other.dot == self.dot
        return False

    def __repr__(self):
        """
        重载语法项目到字符串的转换函数，便于直接输出
        :return:
        """
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
        """
        判断是否为移进项目
        :return:
        """
        return self.dot < len(self.right) and self.get_next_token_or_var() in T

    def is_wait_reduce(self):
        """
        判断是否为待约项目
        :return:
        """
        return self.dot < len(self.right) and self.get_next_token_or_var() in V

    def is_reduce(self):
        """
        判断是否为归约项目
        :return:
        """
        return self.dot == len(self.right)

    def get_next_token_or_var(self):
        """
        获取下一个待推导的字符
        :return:
        """
        return self.right[self.dot]

    def get_next_item(self):
        """
        获取成功接受一个字符后, 点号右移一位的LR(1)项目
        :return:
        """
        new_item = Item((self.left, self.right), self.production_num)
        new_item.dot = self.dot + 1
        return new_item
