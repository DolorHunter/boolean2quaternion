# boolean2quaternion

[![LICENSE](https://img.shields.io/badge/License-EPL--2.0-green.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-v3.8.0-blue.svg?style=flat-square)](https://github.com/DolorHunter/llsociety/releases)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-yellow.svg?style=flat-square)](https://github.com/DolorHunter/llSociety/releases)

__[LR1_Analyzer](#LR1_Analyzer)__ | __[Boolean_Quaternion](#Boolean_Quaternion)__
-|-
-| __[布尔表达式的文法](#布尔表达式的文法)__
__[lr1 输入](#lr1-输入)__ | __[b2q 输入](#b2q-输入)__
__[lr1 输出](#lr1-输出)__ | __[b2q 输出](#b2q-输出)__

## LR1_Analyzer

> 40． 题目： LR(1)分析表自动构造程序的实现 设计内容及要求：对任意给定的文法 G 构造 LR(1)项目集规范族（按教材 P.115 所述方法构造，要求实现 CLOSURE(I)、GO(I,X)、FIRST（集合 FIRST 的构 造方法参见教材 P.78）；然后实现 LR(1)分析表构造算法。以教材 P.115 例 5.13 为输入，构造并输出其 LR(1)分析表 5.5。

### lr1 输入

输入串: `notirelopvorvand(irelopv)#`

输入文法:

```plain
S->AandMB
A->notC
B->(D)
C->DorMF
D->ErelopF
E->i
F->v
M->ε
```

### lr1 输出

![lr1_mainwindows](https://res.cloudinary.com/dfb5w2ccj/image/upload/v1586001378/temp/lr1-mainwindows_xbzu4k.png)

![lr1_analysis_list](https://res.cloudinary.com/dfb5w2ccj/image/upload/v1586001378/temp/lr1-analysis-list_dyvut8.png)

![lr1_analysis_process](https://res.cloudinary.com/dfb5w2ccj/image/upload/v1586001378/temp/lr1-analysis-process_m46mbh.png)

## Boolean2Quaternion

> 50． 题目：将布尔表达式转换成四元式的程序实现 设计内容及要求：设计一个语法制导翻译器，将布尔表达式翻译成四元式。 要求：先确定一个定义布尔表达式的文法，为其设计一个语法分析程序，为每条 产生式配备一个语义子程序，按照一遍扫描的语法制导翻译方法，实现翻译程序。 对用户输入的任意一个正确的布尔表达式，程序将其转换成四元式输出(可按一 定格式输出到指定文件中)。

### 布尔表达式的文法

1. E -> E1 or M E2
2. E ->  E1 and M E2
3. E ->  not E1
4. E ->  (E1)
5. E ->  id1 relop id2
6. E ->  id
7. M -> ε

### b2q 输入

输入串: `notirelopvoryand(irelopv)#`

输入文法:

```plain
S->AandMB
A->notC
B->(D)
C->DorME
D->irelopv
E->y
M->ε
```

### b2q 输出

![b2q_mainwindows](https://res.cloudinary.com/dfb5w2ccj/image/upload/v1586001378/temp/b2q-mainwindows_avgedq.png)

![b2q_analysis_list](https://res.cloudinary.com/dfb5w2ccj/image/upload/v1586001378/temp/b2q-analysis-list_jyajbc.png)

![b2q_quaternion](https://res.cloudinary.com/dfb5w2ccj/image/upload/v1586001378/temp/b2q-quaternion_dfdxgn.png)
