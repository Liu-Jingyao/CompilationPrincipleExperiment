# 编译原理实验：词法分析器、语法分析器
## 词法分析器
基于yaml配置文件的词法分析器。

原理是根据配置文件建图，从初始状态依次读入字符进行状态的转移，有点Lex（词法分析器生成器）的意思在里面。

采用了一些函数式编程的思想，所以代码整体看起来会有些难以理解。

### 配置文件编写示例
![image](https://user-images.githubusercontent.com/53286995/143730558-e007e197-c59a-4393-baaa-9e8bb5eb6443.png)
<img src="https://user-images.githubusercontent.com/53286995/143731226-5bf68854-c4ce-4f60-b617-d9181e772326.png" width="75%" height="75%">

### 状态转换图
原始的状态转换图：
![image](https://user-images.githubusercontent.com/53286995/143731011-b75c8dba-fd74-49ea-ad1d-43758c611345.png)
引入函数式编程思想后合并了具有相同动作的节点，如下：
![image](https://user-images.githubusercontent.com/53286995/143731060-c0d70d4b-76de-4cb8-ba98-87fe4e7457ea.png)

### 测试
请使用lexicalAnalyze/test/下的脚本及测试文件进行测试。

![image](https://user-images.githubusercontent.com/53286995/143730817-aadbb6a5-db12-4942-ac56-3bbcb9968c57.png)

HITWH 柳景耀
