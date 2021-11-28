from lexicalAnalyze.lexicalAnalyzer import *
from lexicalAnalyze.Input import InputCache
from lexicalAnalyze.utils import EOF
import yaml

if __name__ == '__main__':
    inputCache = InputCache("test/test_input.txt")
    token = token_scan(inputCache)
    while token[0] != EOF_TOKEN:
        print(token, end=" ")
        token = token_scan(inputCache)