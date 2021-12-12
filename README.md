# 编译原理实验：词法分析器、SLR(1)语法分析器

总体架构图：

<img src="https://user-images.githubusercontent.com/53286995/145677020-f7a15cf8-c866-4fec-a265-e6fdbc58939f.png" width="80%" height="80%">


## 1 词法分析器
基于yaml配置文件的词法分析器。根据配置文件建立状态转移图，从初始状态依次读入字符进行状态的转移。

### 1.1 配置文件编写示例
状态图:

<img src="https://user-images.githubusercontent.com/53286995/143730558-e007e197-c59a-4393-baaa-9e8bb5eb6443.png" width="50%" height="50%">
对应的yaml语句:

<img src="https://user-images.githubusercontent.com/53286995/143731226-5bf68854-c4ce-4f60-b617-d9181e772326.png" width="75%" height="75%">

### 1.2 本Demo使用的词法状态转换图
<img src="https://user-images.githubusercontent.com/53286995/145676764-23eb4f8d-3bbf-4e77-9514-3e4782713f3d.png" width="60%" height="60%">
最终实现时合并了具有相同动作的节点，最终的状态转换图如下：

<img src="https://user-images.githubusercontent.com/53286995/145676783-94d6f92c-754b-4433-84eb-93cb9f433479.png" width="75%" height="75%">

### 1.3 测试
使用test包下的test_lexical_analyzer.py脚本进行词法分析模块单独测试。输入文件为test/test_lexical_input.txt
Input:
``` Cpp
int main() {
    1EC
    int a;
    a a;
    a = 10;
    t;
    if(a == 10) {
        char c;
        c = 'a';
        printf("Hello World!%c", c);
    }
    while(a>=10) {
        printf("Hello World!%c", c);
    }
}
```
output:
```
(116, 'int') (1, 'main') (25, '(') (26, ')') (29, '{') (0, '1EC') (116, 'int') (1, 'a') (4, ';') (1, 'a') (1, 'a') (4, ';') (1, 'a') (16, '=') (2, 10.0) (4, ';') (1, 't') (4, ';') (115, 'if') (25, '(') (1, 'a') (15, '==') (2, 10.0) (26, ')') (29, '{') (103, 'char') (1, 'c') (4, ';') (1, 'c') (16, '=') (5, 'a') (4, ';') (1, 'printf') (25, '(') (6, 'Hello World!%c') (24, ',') (1, 'c') (26, ')') (4, ';') (30, '}') (131, 'while') (25, '(') (1, 'a') (13, '>=') (2, 10.0) (26, ')') (29, '{') (1, 'printf') (25, '(') (6, 'Hello World!%c') (24, ',') (1, 'c') (26, ')') (4, ';') (30, '}') (30, '}') 
```

## 2 SLR(1)语法分析器

语法分析器完全采用高等教育出版社《编译原理（第二版）》的设计，具有SLR(1)文法分析与紧急方法错误处理功能。详情请见教材或代码注释。


### 2.1 文法说明
本次实验我尝试实现了一个C语言的子集，文法产生式包括：
```
程序块->函数定义|变量声明 分号|程序块 程序块
函数定义->类型 标识符 左括号 形式参数 右括号 左大括号 函数块 右大括号|类型 标识符 左括号 右括号 左大括号 函数块 右大括号
变量声明->类型 标识符
形式参数->类型 标识符|类型 标识符 逗号 形式参数
函数块->变量声明 分号|变量赋值 分号|函数调用 分号|循环结构|分支结构|函数块 函数块
变量赋值->标识符 等号 常量
常量->算术表达式|布尔表达式|整数|实数|字符|字符串
算术表达式->算术表达式 算术运算符 算术表达式|负号 算术表达式|函数调用|左括号 算术表达式 右括号|标识符|整数|实数
布尔表达式->算术表达式 比较运算符 算术表达式|布尔表达式 与符号 布尔表达式|布尔表达式 或符号 布尔表达式|非符号 布尔表达式|函数调用|左括号 布尔表达式 右括号|标识符|真|假
函数调用->标识符 左括号 实际参数 右括号|标识符 左括号 右括号
实际参数->标识符|实际参数->常量|实际参数 逗号 实际参数
循环结构->关揵字while 左括号 布尔表达式 右括号 左大括号 函数块 右大括号
分支结构->关键字if 左括号 布尔表达式 右括号 左大括号 函数块 右大括号|关键字if 左括号 布尔表达式 右括号 左大括号 函数块 右大括号 关键字else 左大括号 函数块 右大括号
类型->关联字int|关键字char|关键字string|关键字float
算术运算符->加号|减号|乘号|除号|百分号
比较运算符->大于|小于|等于|大于等于|小于等于|不等于
```

### 2.2 示例
使用根目录下的main.py脚本进行词法与语法分析集成测试。输入文件为test/test_lexical_input.txt。

输出包括：FIRST集与FOLLOW集，词法错误提示，项目集闭包规范族，语法错误提示，解析出的产生式序列

示例：
```
[ERROR] 检测到词法错误, 无法识别单词1EC
```
```
GrammarVarEnum.TYPE->int 
GrammarVarEnum.TYPE->int 
GrammarVarEnum.VAR_DECLARE->TYPE a 
GrammarVarEnum.FUNC_BLOCK->VAR_DECLARE ;  
[ERROR] 检测到语法错误，状态51在第10个输入符号"a"上的动作为空:
closure(51):
item_list: [GrammarVarEnum.VAR_ASSIGN->标识符 .= CONSTANT , GrammarVarEnum.FUNC_CALL->标识符 .( REAL_PARAM ) , GrammarVarEnum.FUNC_CALL->标识符 .( ) ]
go_list: {'=': 52, '(': 53}
正在执行恢复程序......

[ERROR] 检测到语法错误，状态51在第11个输入符号"; "上的动作为空:
closure(51):
item_list: [GrammarVarEnum.VAR_ASSIGN->标识符 .= CONSTANT , GrammarVarEnum.FUNC_CALL->标识符 .( REAL_PARAM ) , GrammarVarEnum.FUNC_CALL->标识符 .( ) ]
go_list: {'=': 52, '(': 53}
正在执行恢复程序......

GrammarVarEnum.VALUE_EXPRESSION->10.0 
GrammarVarEnum.CONSTANT->VALUE_EXPRESSION 
GrammarVarEnum.VAR_ASSIGN->a = CONSTANT 
GrammarVarEnum.FUNC_BLOCK->VAR_ASSIGN ;  
[ERROR] 检测到语法错误，状态51在第17个输入符号"; "上的动作为空:
closure(51):
item_list: [GrammarVarEnum.VAR_ASSIGN->标识符 .= CONSTANT , GrammarVarEnum.FUNC_CALL->标识符 .( REAL_PARAM ) , GrammarVarEnum.FUNC_CALL->标识符 .( ) ]
go_list: {'=': 52, '(': 53}
正在执行恢复程序......

GrammarVarEnum.VALUE_EXPRESSION->a 
GrammarVarEnum.CMP_OPT->== 
GrammarVarEnum.VALUE_EXPRESSION->10.0 
GrammarVarEnum.BOOL_EXPRESSION->VALUE_EXPRESSION CMP_OPT VALUE_EXPRESSION 
GrammarVarEnum.TYPE->char 
GrammarVarEnum.VAR_DECLARE->TYPE c 
GrammarVarEnum.FUNC_BLOCK->VAR_DECLARE ;  
GrammarVarEnum.CONSTANT->'a' 
GrammarVarEnum.VAR_ASSIGN->c = CONSTANT 
GrammarVarEnum.FUNC_BLOCK->VAR_ASSIGN ;  
GrammarVarEnum.CONSTANT->"Hello World!%c" 
GrammarVarEnum.REAL_PARAM->CONSTANT 
GrammarVarEnum.VALUE_EXPRESSION->c 
GrammarVarEnum.CONSTANT->VALUE_EXPRESSION 
GrammarVarEnum.REAL_PARAM->CONSTANT 
GrammarVarEnum.REAL_PARAM->REAL_PARAM , REAL_PARAM 
GrammarVarEnum.FUNC_CALL->printf ( REAL_PARAM ) 
GrammarVarEnum.FUNC_BLOCK->FUNC_CALL ;  
GrammarVarEnum.FUNC_BLOCK->FUNC_BLOCK FUNC_BLOCK 
GrammarVarEnum.FUNC_BLOCK->FUNC_BLOCK FUNC_BLOCK 
GrammarVarEnum.BRANCH->if ( BOOL_EXPRESSION ) { FUNC_BLOCK } 
GrammarVarEnum.FUNC_BLOCK->BRANCH 
GrammarVarEnum.VALUE_EXPRESSION->a 
GrammarVarEnum.CMP_OPT->>= 
GrammarVarEnum.VALUE_EXPRESSION->10.0 
GrammarVarEnum.BOOL_EXPRESSION->VALUE_EXPRESSION CMP_OPT VALUE_EXPRESSION 
GrammarVarEnum.CONSTANT->"Hello World!%c" 
GrammarVarEnum.REAL_PARAM->CONSTANT 
GrammarVarEnum.VALUE_EXPRESSION->c 
GrammarVarEnum.CONSTANT->VALUE_EXPRESSION 
GrammarVarEnum.REAL_PARAM->CONSTANT 
GrammarVarEnum.REAL_PARAM->REAL_PARAM , REAL_PARAM 
GrammarVarEnum.FUNC_CALL->printf ( REAL_PARAM ) 
GrammarVarEnum.FUNC_BLOCK->FUNC_CALL ;  
GrammarVarEnum.LOOP->while ( BOOL_EXPRESSION ) { FUNC_BLOCK } 
GrammarVarEnum.FUNC_BLOCK->LOOP 
GrammarVarEnum.FUNC_BLOCK->FUNC_BLOCK FUNC_BLOCK 
GrammarVarEnum.FUNC_BLOCK->FUNC_BLOCK FUNC_BLOCK 
GrammarVarEnum.FUNC_BLOCK->FUNC_BLOCK FUNC_BLOCK 
GrammarVarEnum.FUNC_BLOCK->{ FUNC_BLOCK 
GrammarVarEnum.FUNC_BLOCK->) FUNC_BLOCK 
GrammarVarEnum.FUNC_BLOCK->( FUNC_BLOCK 
GrammarVarEnum.FUNC_DEF-># TYPE main FUNC_BLOCK } 
GrammarVarEnum.PROG_BLOCK->FUNC_DEF 
分析完成！
```

by HITWH 柳景耀
