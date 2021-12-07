import re

from syntax_analysis.SLR1Analyzer import token_analysis
from syntax_analysis.table_generator import AnalysisTable
from syntax_analysis.table_generator import item_closure_list

if __name__ == '__main__':
    token_analysis(None)