from syntax_analysis.table_generator import item_closure_list, production_list, AnalysisTable, V
from utils import EOF, EOF_TOKEN, fill_production, print_production, CATEGORY_DICT_REVERSE, token2str, \
    print_item_closure


def token_analysis(tokenReceiveCache):
    analysis_table = AnalysisTable()
    state_stack = [item_closure_list[0]]
    token_stack = [(EOF_TOKEN, 0)]
    token = tokenReceiveCache.gettoken()
    while True:
        a = (token[0], 0)
        s = state_stack[-1]
        if (s.num, a) not in analysis_table.action:
            print("[ERROR] 检测到语法错误，状态%d在第%d个输入符号\"%s\"上的动作为空:" % (s.num, tokenReceiveCache.count, token2str(token)))
            print_item_closure(s)
            print("正在执行恢复程序......\n")
            while token_stack[-1] not in V or (state_stack[-1].num, token_stack[-1]) not in analysis_table.goto.keys():
                token_stack.pop()
                state_stack.pop()
            while a not in analysis_table.follow[token_stack[-1]]:
                token = tokenReceiveCache.gettoken()
                a = (token[0], 0)
            s = state_stack[-1]
            state_stack.append(item_closure_list[analysis_table.goto[(s.num, token_stack[-1])]])
        if analysis_table.action[(s.num, a)][0] == 'S':
            i = int(analysis_table.action[(s.num, a)][1:])
            token_stack.append(token)
            state_stack.append(item_closure_list[i])
            token = tokenReceiveCache.gettoken()
        elif analysis_table.action[(s.num, a)][0] == 'r':
            k = int(analysis_table.action[(s.num, a)][1:])
            len_beta = len(production_list[k][1])
            pop_token = token_stack[-len_beta:]
            token_stack = token_stack[:-len_beta]
            state_stack = state_stack[:-len_beta]
            s = state_stack[-1]
            token_stack.append(production_list[k][0])
            state_stack.append(item_closure_list[analysis_table.goto[(s.num, production_list[k][0])]])
            production = fill_production(production_list[k], pop_token)
            print_production(production)
        elif analysis_table.action[(s.num, a)] == "acc":
            print("分析完成！")
            return
        else:
            print("分析表填写错误!")
            return
