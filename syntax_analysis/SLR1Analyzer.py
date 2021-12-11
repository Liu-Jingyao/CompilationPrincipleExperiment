from syntax_analysis.table_generator import item_closure_list, production_list, AnalysisTable, V
from utils import EOF, EOF_TOKEN_CATEGORY, fill_production, print_production, CATEGORY_DICT_REVERSE, token2str, \
    print_item_closure


def token_analysis(tokenReceiveCache):
    """
    语法分析程序
    analysis_table: 由文法动态生成的SLR(1)分析表
    state_stack: 状态栈，记录分析路径上的语法分析状态
    token_or_var_stack: 文法符号栈，记录已归约的文法变量及移入待归约的token
    token: 当前从输入缓冲区读取的token
    a: 保留了token的类别码，但把具体值用0掩盖以用作action表键值
    s: 状态栈的栈顶元素，即语法分析器当前状态
    :param tokenReceiveCache: 输入缓冲区，以终结符token结尾
    :return:
    """
    analysis_table = AnalysisTable()
    # 将初始状态S0和终结符token压入栈
    state_stack = [item_closure_list[0]]
    token_or_var_stack = [(EOF_TOKEN_CATEGORY, 0)]
    # 读取输入缓冲区的第一个token
    token = tokenReceiveCache.gettoken()
    while True:
        # 将token去值化以用于检索
        a = (token[0], 0)
        # 获取当前栈顶状态s
        s = state_stack[-1]

        # 当分析器处于某一状态S, 且当前输入符号为a时，就以符号对(S, a)查LR分析表。
        if (s.num, a) not in analysis_table.action:
            # 如果分析表元素action[S, a]为空，则表示检测到了一个语法错误
            print("[ERROR] 检测到语法错误，状态%d在第%d个输入符号\"%s\"上的动作为空:" % (s.num, tokenReceiveCache.count, token2str(token)))
            print_item_closure(s)
            print("正在执行恢复程序......\n")
            # 紧急方式的错误恢复
            # 从栈顶开始退栈，直到符号栈栈顶是一个语法变量，且状态栈栈顶状态可以在该变量上转移为止。
            while token_or_var_stack[-1] not in V or (state_stack[-1].num, token_or_var_stack[-1]) not in analysis_table.goto.keys():
                token_or_var_stack.pop()
                state_stack.pop()
            # 丢弃若干输入符号，找到栈顶语法变量的第一个后继作为新的当前输入
            while a not in analysis_table.follow[token_or_var_stack[-1]]:
                token = tokenReceiveCache.gettoken()
                a = (token[0], 0)
            # 分析器把转移后的状态压进栈并恢复正常分析
            s = state_stack[-1]
            state_stack.append(item_closure_list[analysis_table.goto[(s.num, token_or_var_stack[-1])]])
        if analysis_table.action[(s.num, a)][0] == 'S':
            # Si表示移进输入符号并转入新的状态i
            i = int(analysis_table.action[(s.num, a)][1:])
            # 移进当前输入（压入符号栈中）并将状态i作为新的当前状态（压入状态栈中）
            token_or_var_stack.append(token)
            state_stack.append(item_closure_list[i])
            # 获取下一个输入符号
            token = tokenReceiveCache.gettoken()
        elif analysis_table.action[(s.num, a)][0] == 'r':
            # ri表示按第k个产生式A->beta归约
            k = int(analysis_table.action[(s.num, a)][1:])
            # 从符号栈弹出产生式k需要的beta串
            len_beta = len(production_list[k][1])
            pop_token = token_or_var_stack[-len_beta:]
            token_or_var_stack = token_or_var_stack[:-len_beta]
            # 并从状态栈弹出相应len(beta)个路径状态,得到新的当前状态
            state_stack = state_stack[:-len_beta]
            s = state_stack[-1]
            # 将归约出的文法变量A和新状态在A上的转移分别压入栈中
            token_or_var_stack.append(production_list[k][0])
            state_stack.append(item_closure_list[analysis_table.goto[(s.num, production_list[k][0])]])
            # 将掩盖掉的token值填入产生式，输出填充后的产生式A->beta
            production = fill_production(production_list[k], pop_token)
            print_production(production)
        elif analysis_table.action[(s.num, a)] == "acc":
            print("分析完成！")
            return
        else:
            print("分析表填写错误!")
            return
