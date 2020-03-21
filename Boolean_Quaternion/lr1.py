# coding:utf-8

from queue import Queue
import operator
import copy
import string

EG_VTS = ['and', 'or', 'not', '(', ')', 'relop']
grams = []  # 文法表
vt = []  # 终结符
vn = []  # 非终结符
sim_grams = []  # 简化后的语句(去除或)
first_lang = {}  # 非终结符的first集合
collections = []  # 项目集
can_cols = []  # 项目集族
action = []  # 动作表
goto = []  # 转移表
action_heading = []  # 动作表首行
goto_heading = []  # 转移表首行

step_list = []  # 步骤表
status_stack_list = []  # 分析栈(状态)表
symbol_stack_list = []  # 分析栈(符号)表
input_string_list = []  # 输入串表
action_list = []  # 动作表


class Stack(object):
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def peek(self):
        if not self.is_empty():
            return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)


# 初始化(清空)各个表与其中的数据
def init_list():
    grams.clear()  # 初始化文法表
    vt.clear()  # 初始化终结符
    vn.clear()  # 初始化非终结符
    sim_grams.clear()  # 初始化简化后的语句(去除或)
    first_lang.clear()  # 初始化非终结符的first集合
    collections.clear()  # 初始化项目集
    can_cols.clear()  # 初始化项目集族
    action.clear()  # 初始化动作表
    goto.clear()  # 初始化转移表
    action_heading.clear()  # 初始化动作表首行
    goto_heading.clear()  # 初始化转移表首行
    step_list.clear()  # 初始化步骤表
    status_stack_list.clear()  # 初始化分析栈(状态)表
    symbol_stack_list.clear()  # 初始化分析栈(符号)表
    input_string_list.clear()  # 初始化输入串表
    action_list.clear()  # 初始化动作表
    print('All the info on the list were wiped out!!')


# 建立文法(读文件)
def create_grammar_list(filename):
    file = open(filename, 'r')
    lines = file.read().split('\n')
    for line in lines:
        if line != '':  # 不为空行
            grams.append(line)
    file.close()
    # print('grams', grams)  # test
    print('Grammar list was created!!')


# 提取终结符与非终结符
def extract_terminal_symbol():
    # 遍历文法表g[], 提取终结符与非终结符
    for gram in grams:
        ext_gram = str(gram)
        if ext_gram != '':  # 非空行
            ext_gram = ext_gram.replace('->', '')
            for eg_vt in EG_VTS:
                if eg_vt in ext_gram and eg_vt not in vt:
                    vt.append(eg_vt)  # eg_vts中的符号加入vt[]
                    ext_gram = ext_gram.replace(eg_vt, '')
            for elem in ext_gram:
                if elem not in vt+vn:
                    if elem.isupper():
                        vn.append(elem)  # 非终结符加入vn{}
                    elif elem not in ('ε', '|'):
                        vt.append(elem)  # 终结符加入vt{}
    # print('vn', vn, 'vt', vt)  # test
    print('Terminal & non-terminal symbols were extracted!!')


# 生成拓广文法
def extend_grammar():
    extend_vn = ''
    for upper in string.ascii_uppercase:
        if upper not in vn:
            extend_vn = upper
            break
    vn.insert(0, extend_vn)  # 加入新的vn
    extend_gram = extend_vn + '->' + grams[0][0]
    grams.insert(0, extend_gram)  # 添加拓广到文法头部
    # print('vn', vn, 'vt:', vt, 'grams:', grams)
    print('The grammar was extended!!')


# 生成简化语句的列表sim_grams[]
def create_simplified_grammar():
    for gram in grams:
        if '|' not in gram:  # 已经是最简语句(没有或)
            sim_grams.append(gram)
        else:  # 不是最简语句(有或)
            after_arrow = gram.split('->')  # 分割'->'左右, 为下一次分割作准备
            rules = after_arrow[1].split('|')  # 分割'|'左右
            for rule in rules:
                simp_gram = after_arrow[0] + '->' + rule
                sim_grams.append(simp_gram)
    # print(sim_grams)  # test
    print('The grammar was simplified!!')


# 创建first{}集
def create_first_assemble():
    for i in vn:
        first_lang[i] = set()
    old_first_lang = {}
    while not operator.eq(old_first_lang, first_lang):
        old_first_lang = copy.deepcopy(first_lang)
        for sim_gram in sim_grams:
            lang = sim_gram.split('->')  # 分割得到潜在first集合元素 (first[1][0])
            head = lang[0]
            loc = 0
            cur_elem = lang[1][loc]
            if operator.eq(cur_elem, 'ε'):  # ep
                first_lang[head].add('ε')
            elif cur_elem.isupper:  # vn
                while cur_elem in vn and 'ε' in first_lang[cur_elem]:
                    for elem in first_lang[cur_elem]:
                        first_lang[head].add(elem)
                    loc += 1
                if cur_elem in vn:
                    for v in first_lang[cur_elem]:
                        first_lang[head].add(v)
                else:
                    for v in vt:
                        if operator.eq(lang[1][loc:loc+len(v)], v):
                            first_lang[head].add(v)
            else:  # vt
                for v in vt:
                    if operator.eq(lang[1][0:len(v)], v):
                        first_lang[head].add(v)
    # print(first_lang)  # test
    print('First assemble was created successfully!!')


# 构造带点位置的项目集(展望占位)
def create_collections():
    for sim_gram in sim_grams:
        elem = sim_gram.split('->')
        if 'ε' in elem[1]:
            item = elem[0] + '->' + '•'  # M->•
            collections.append([item, '#', 3])  # 空值为#, 3为生成式左端 e.g.'X->'造成的偏移
            continue
        else:
            item = elem[0] + '->' + '•' + elem[1][0:]
            collections.append([item, '#', 3])  # 空值为#, 3为生成式左端 e.g.'X->'造成的偏移
        loc = 0
        while len(elem[1]) > loc:
            for v in vt+vn:
                if v in elem[1] and operator.eq(elem[1][loc:loc+len(v)], v):
                    item = elem[0] + '->' + elem[1][0:loc+len(v)] + '•' + elem[1][loc+len(v):]
                    collections.append([item, '#', loc+3+len(v)])  # [项目, 展望, 点的位置]
                    loc += len(v)
                    break
    # print(collections)  # test
    print('The collections were created!!')


# 找到点后元素
def elem_after_dot(col, loc):  # [项目, 点的位置]
    for v in vt+vn+['ε']:
        if v in col and operator.eq(col[loc+1:loc+1+len(v)], v):
            return v


# 找到展望元素
def elem_viewer(col, loc):  # [项目, 点的位置]
    for v in vt+vn+['ε']:
        if v in col and operator.eq(col[loc+1:loc+1+len(v)], v):
            for vr in vt+vn+['ε']:
                if vr in col and operator.eq(col[loc+1+len(v):loc+1+len(v)+len(vr)], vr):
                    return vr


# 生成展望串
def create_viewer_string(i):
    if len(i[0]) > i[2] + 2:  # 点后第二个元素存在, 生成并继承展望符
        viewer = elem_viewer(i[0], i[2])  # 用展望头求first集
        if viewer in vt:  # 展望头为终结符
            return viewer + i[1]
        elif viewer in vn:  # 展望头为非终结符
            return str("".join(first_lang[viewer])) + i[1]
    else:  # 点后第二个元素不存在, 继承展望符
        return i[1]


# 构造闭包函数(递归)
def closure(i, c):  # i为项目,c为闭包集
    next_elem = elem_after_dot(i[0], i[2])
    if len(i[0]) > i[2]+1 and next_elem in vn:  # 点不是最后一个元素且下个元素为vn
        vr_str = create_viewer_string(i)  # 生成展望
        for cols in collections:  # col不在c中, 且下一个元素与项目首元素相同且项目刚开始
            new_cols = (cols[0], vr_str, cols[2])
            if new_cols not in c and (next_elem == cols[0][0] and cols[2] == 3):
                c.append(new_cols)  # 此项目加入闭包c
                if len(cols[0]) > cols[2]+1 and cols[0][cols[2]+1] in vn:  # 点不为最后元素且点后为非终结符
                    closure(new_cols, c)  # 构造新闭包


# 构造项目带展望的闭包Closure(I)
def create_closure(i):  # i为状态的项目集头
    c = [i]  # 首项目加入Closure(i)
    closure(i, c)  # 计算i的闭包, 项目加入c
    return c


# 构造Go(I, x)
def go(front_c, x):  # I为项目集, x为元素
    c = []  # 下一个状态的闭包(c建立于函数头, 防止状态内出现多个点后相同元素的项目无法合并)
    for f_c in front_c:
        if (len(f_c[0]) > f_c[2]+1) and (f_c[0][f_c[2]+1:f_c[2]+1+len(str(x))] == x):  # 点不为最后元素且点下一个元素为x
            vr_str = create_viewer_string(f_c)  # 生成展望串
            next_i = (f_c[0][0:f_c[2]]+x+'•'+f_c[0][f_c[2]+1+len(str(x)):], vr_str, f_c[2]+len(str(x)))
            c.append(next_i)
            if len(next_i[0]) > next_i[2]+1 and elem_after_dot(next_i[0], next_i[2]) in vn:  # 点不为最后一个符号且点后为非终结符
                closure(next_i, c)  # 构建闭包, 结果返回c
    return c


# 构造LR(1)项目集规范族族
def create_can_cols():
    # 第一个状态的状态拓展
    clos = create_closure(collections[0])  # 从拓广语句开始首个状态
    ct = 0  # 状态计数
    # 第一个参数表示状态数, 第二个参数表示是否拓展过, 第三个参数表示该状态的项目集
    can_cols.append([ct, clos])  # 加入初始状态I0
    # 拓展剩余状态, 直到所有状态都经过拓展
    old_can_cols = []
    while not operator.eq(old_can_cols, can_cols):  # 当新旧c_cs不等, 表示仍有未访问的状态
        old_can_cols = copy.deepcopy(can_cols)  # 将c_cs赋给旧c_cs
        for can_col in can_cols:
            elem = []  # 用于消除不同项目的同元素产生的重复状态
            for c_col in can_col[1]:  # 遍历状态中的项目集
                if len(c_col[0]) > c_col[2]+1:  # 项目中的点不为最后一个元素(其他情况无下一状态)
                    x = elem_after_dot(c_col[0], c_col[2])
                    go_result = go(can_col[1], x)  # go运算结果(减少重复运算)
                    new_result = True  # 新状态标记
                    for can_col2 in can_cols:
                        if operator.eq(go_result, can_col2[1]):  # 与已有状态相等, 为旧状态(重复状态)
                            new_result = False
                    # go非空且不属于c且为新状态
                    if go_result != [] and go_result not in clos and new_result:
                        if x not in elem:  # 该状态的触发元素第一次出现(合并同状态中, 不同项目的同个触发条件, 以合并下个状态)
                            elem.append(x)  # 加入元素
                            can_cols.append([ct + elem.index(x) + 1, go_result])  # 加入状态In, 新状态设置为True
            ct += len(elem)  # 前进elem个状态(len(elem)为当前状态新产生的状态数量)
    # print(can_cols)  # test
    print('The canonical collections were created!!')


# 文法预处理(提取, 拓广, 简化)
def pre_process():
    extract_terminal_symbol()
    extend_grammar()
    create_simplified_grammar()
    create_first_assemble()


# 生成分析表
def create_analysis_list():
    action_heading.extend(vt)
    action_heading.append('#')
    action.append(action_heading)  # 写入首行信息
    for c in can_cols:  # 初始化action表
        line_info = ['' for f in action_heading]
        action.append(line_info)

    goto_heading.extend(vn)
    goto_heading.remove(sim_grams[0][0])  # vn删去拓广产生的元素
    goto.append(goto_heading)  # 写入首行信息
    for c in can_cols:  # 初始化goto表
        line_info = ['' for f in goto_heading]
        goto.append(line_info)

    # 填写action表, goto表
    for can_col in can_cols:  # 遍历项目集规范族中的每个状态
        for c_col in can_col[1]:  # 遍历该状态的每个项目
            if len(c_col[0]) > c_col[2]+1:  # 点不为尾元素(潜在移进)
                x = elem_after_dot(c_col[0], c_col[2])  # 点后的元素
                go_result = go(can_col[1], x)  # go(Ik, x)下一个状态的项目集 Ij
                for c_c in can_cols:
                    j = c_c[0]  # j为新状态状态序号(c_c[0]), 新状态Ij为c_c[1]
                    if operator.eq(go_result, c_c[1]):  # Go(Ik,a)=Ij
                        # 情况一: A->a•ab属于Ik且Go(Ik,x)=Ij, x为终结符
                        if x in vt:
                            if action[can_col[0]+1][action_heading.index(x)] and \
                                    action[can_col[0]+1][action_heading.index(x)][0] != 's'+str(j):
                                print('[ERROR]: NOT LR(1) GRAMMAR!! Code: 1')
                                return False  # 存在多重入口, 不是LR(1)文法
                            action[can_col[0]+1][action_heading.index(x)] = 's'+str(j)  # ACTION[k,a]=sj
                        # 情况四: Go(Ik,X)=Ij, X为非终结符, Goto[k,X]=j
                        elif x in vn:
                            if goto[can_col[0]+1][goto_heading.index(x)] and \
                                    goto[can_col[0]+1][goto_heading.index(x)] != j:
                                print('[ERROR]: NOT LR(1) GRAMMAR!! Code 4')
                                return False  # 存在多重入口, 不是LR(1)文法
                            goto[can_col[0]+1][goto_heading.index(x)] = j  # Goto[k,A]=j
            else:  # 点为最后元素(潜在规约)
                # 情况三: (拓广文法)若项目S'→S·属于Ik，则置ACTION[k,#]为“acc”
                if operator.eq(c_col[0], sim_grams[0]+'•') and c_col[1] == '#':  # 项目为拓广文法(状态启动文法)
                    if action[can_col[0]+1][action_heading.index('#')] and \
                            action[can_col[0]+1][action_heading.index('#')] != 'acc':
                        print('[ERROR]: NOT LR(1) GRAMMAR!! Code 3')
                        return False  # 存在多重入口, 不是LR(1)文法
                    action[can_col[0]+1][action_heading.index('#')] = 'acc'  # 完成标志(移进-规约完成)
                else:  # 情况二: [A→d•, a]属于Ik, 置ACTION[k,a]为rj. (假定A->a为文法G'的第j个产生式)
                    row_gram = str(c_col[0]).replace('•', '')  # 消去点(得到产生式)
                    for j in range(len(sim_grams)):
                        if operator.eq(row_gram, sim_grams[j]) or operator.eq(row_gram+'ε', sim_grams[j]):
                            loc = 0
                            while len(c_col[1]) > loc:
                                for v in vt+['#', 'ε']:
                                    if v in c_col[1] and operator.eq(c_col[1][loc:loc+len(v)], v):
                                        loc += len(v)
                                        if v != 'ε':  # action列元素无ep
                                            if action[can_col[0]+1][action_heading.index(v)] and \
                                                    action[can_col[0]+1][action_heading.index(v)] != 'r'+str(j):
                                                print('[ERROR]: NOT LR(1) GRAMMAR!! Code 2')
                                                return False  # 存在多重入口, 不是LR(1)文法
                                            action[can_col[0]+1][action_heading.index(v)] = 'r'+str(j)  # ACTION[k,a]=rj
    # print(action)  # test
    # print(goto)  # test
    print('Analysis list was created!!')
    return True  # 是LR(1)文法


# 逆序串
def reverse(str):
    rev = Stack()
    loc = 0
    while len(str) > loc:
        for v in vn+vt+['ε', '#']:
            if v in str and operator.eq(str[loc:loc+len(v)], v):
                rev.push(v)
                loc += len(v)
    return rev


# 用分析表分析输入串
def analysis_input_string(input_string):
    # 建立输入串队列, 初始化符号串
    input_queue = Queue()
    loc = 0
    while len(input_string) > loc:
        for v in vt+vn+['ε', '#']:
            if v in input_string and operator.eq(input_string[loc:loc+len(v)], v):
                input_queue.put(v)  # 逐个输入符号入队
                loc += len(v)

    # 初始化分析栈
    analysis_stack = Stack()  # 分析栈(状态符号栈)
    analysis_stack.push(['0', '#'])  # 栈底放入初始状态, 符号

    # 各个表初始化
    current_step = 0  # 当前步骤
    status_stack_list.append(" ".join(item[0] for item in analysis_stack.items))
    symbol_stack_list.append(" ".join(item[1] for item in analysis_stack.items))
    input_string_list.append(" ".join(input_queue.queue))  # 输入串表初始化
    # 动作说明滞后一步, 故初始化时无动作说明

    while True:
        current_step += 1
        step_list.append(current_step)  # 当前步骤加入s_l表

        status = int(analysis_stack.peek()[0])  # 当前状态(int)
        string_head = input_queue.queue[0]  # 当前输入串头(str)

        # 情况三: 接受
        if action[status + 1][action[0].index(string_head)] == 'acc':
            action_list.append('Acc:分析成功')
            break  # 退出
        # 情况一: 移进
        elif 's' in action[status + 1][action[0].index(string_head)]:
            new_status = int(action[status + 1][action[0].index(string_head)][1:])  # 新状态为s后数字
            analysis_stack.push([str(new_status), string_head])  # 新状态, 新符号入栈
            input_queue.get()  # 输入串头出队
            status_stack_list.append(" ".join(item[0] for item in analysis_stack.items))
            symbol_stack_list.append(" ".join(item[1] for item in analysis_stack.items))
            input_string_list.append(" ".join(input_queue.queue))
            action_list.append('ACTION[{},{}]={},状态{}入栈'.format(status, string_head,
                                                                  action[status + 1][action[0].index(string_head)],
                                                                  action[status + 1][action[0].index(string_head)][1:]))
        # 情况二: 规约
        elif 'r' in action[status + 1][action[0].index(string_head)]:
            rule_number = int(action[status + 1][action[0].index(string_head)][1:])  # 规约使用的公式序号
            protocol_string = sim_grams[rule_number].split('->')[1]  # 切分语法
            protocol_string = str(protocol_string).replace('ε', '')  # 消除ep
            reverse_string = reverse(protocol_string)
            # 倒序规约串
            while not reverse_string.is_empty():
                elem = reverse_string.peek()
                if operator.eq(elem, analysis_stack.peek()[1]):  # 规约字符 = 栈顶字符, 出栈
                    reverse_string.pop()
                    analysis_stack.pop()  # 分析栈出栈
                else:  # 排错
                    print('[ERROR]: Protocol string not equal to symbol in stack!!')
                    break
            current_top_status = int(analysis_stack.peek()[0])  # 出栈后的临时栈顶
            new_symbol = sim_grams[rule_number][0]
            if goto[current_top_status + 1][goto[0].index(new_symbol)] == '':
                print('[ERROR]: No element in goto list!!')
                break
            new_status = int(goto[current_top_status + 1][goto[0].index(new_symbol)])  # 新状态为goto(临时栈顶状态, 规约获得符号)
            analysis_stack.push([str(new_status), new_symbol])  # 新状态, 新符号入栈
            status_stack_list.append(" ".join(item[0] for item in analysis_stack.items))
            symbol_stack_list.append(" ".join(item[1] for item in analysis_stack.items))
            input_string_list.append(" ".join(input_queue.queue))
            action_list.append('{}:{}规约,GOTO({},{})={}入栈'.format(action[status + 1][action[0].index(string_head)],
                                                                    sim_grams[rule_number], current_top_status,
                                                                    new_symbol, new_status))
        # 情况四: 报错
        elif action[status + 1][action[0].index(string_head)] == '':
            print('[ERROR]: No element in action list!!')
            action_list.append('ERROR')
            break  # 退出
    # print(step_list)  # test
    # print(status_stack_list)  # test
    # print(symbol_stack_list)  # test
    # print(input_string_list)  # test
    # print(action_list)  # test
    # print("Analysis grammar successfully!!")


'''
def main():
    create_grammar_list("./data/G(S).txt")
    pre_process()
    create_collections()
    #print(create_closure(collections[0]))  # test
    create_can_cols()
    create_analysis_list()
    analysis_input_string('notirelopvoryand(irelopv)#') #notirelopvorεvandε(irelopv)


if __name__ == '__main__':
    main()
'''
