from syntax_analysis.table_generator import item_closure_list, production_list, AnalysisTable
from utils import EOF, EOF_TOKEN, fill_production, print_production


def token_analysis(tokenReceiveCache):
    analysis_table = AnalysisTable()
    state_stack = [item_closure_list[0]]
    token_stack = [(EOF_TOKEN, 0)]
    token = tokenReceiveCache.gettoken()
    while token[0] != EOF_TOKEN:
        a = (token[0], 0)
        s = state_stack[-1]
        if analysis_table.action[(s.num, a)][0] == 'S':
            i = int(analysis_table.action[(s.num, a)][1])
            token_stack.append(a)
            state_stack.append(item_closure_list[i])
        elif analysis_table.action[(s.num, a)][0] == 'r':
            k = int(analysis_table.action[(s.num, a)][1])
            len_beta = len(production_list[k][1])
            pop_token = token_stack[:len_beta+1]
            token_stack = token_stack[:-len_beta]
            state_stack = state_stack[:-len_beta]
            s = state_stack[-1]
            token_stack.append(production_list[k][0])
            state_stack.append(analysis_table.goto[(s.num, production_list[k][0])])
            production = fill_production(production_list[k], pop_token)
            print_production(production)
        elif analysis_table.action[(s.num, a)] == "acc":
            return
        else:
            print("error!")
            return
        token = tokenReceiveCache.gettoken()
