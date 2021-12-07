from lexical_analysis.lexicalAnalyzer import *
from lexical_analysis.Input import InputCache
from utils import EOF
import yaml

if __name__ == '__main__':
    inputCache = InputCache("test_lexical_input.txt")
    token = token_scan(inputCache)
    while token[0] != EOF_TOKEN:
        print(token, end=" ")
        token = token_scan(inputCache)
