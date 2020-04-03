# coding:utf-8

from queue import Queue
import operator
import lr1

quaternion = []  # 布尔四元式
attr = []  # 四元式属性

# 四元式(jnz, a, -, p)  表示 if  a  goto p
# 四元式(jrop, x, y, p) 表示 if  x rop y  goto p
# 四元式(j, -, -, p)    表示 goto p

# (1)    E→	E1 or M E2
# (2)               | E1 and M E2
# (3)               | not E1
# (4)               | (E1)
# (5)               | id1 relop id2
# (6)               | id
# (7)	M→


# 函数merge(p1,p2)，把以p1和p2为链首的两条链合并为一，作为函数值，回送合并后的链首。
def merge(p1, p2):
    return list(set(p1 + p2))


# 过程backpatch(p, t)，其功能是完成“回填”，把p所链接的每个四元式的第四区段都填为t。
def backpatch(p, t):
    for i in p:
        quaternion[i][3] = t


# (1) E→E1 or M E2
# { backpatch(E1.falselist, M.quad);
#   E.truelist:=merge(E1.truelist, E2.truelist);
#   E.falselist:=E2.falselist }
# e.g. 4: C -> D or M F
def rule1(attr):
    e1_false_list = attr[0]['false_list']
    e1_true_list = attr[0]['true_list']
    e2_false_list = attr[3]['false_list']
    e2_true_list = attr[3]['true_list']
    quad = attr[2]['quad']
    backpatch(e1_false_list, quad)
    return {'true_list': merge(e1_true_list, e2_true_list),
            'false_list': e2_false_list}


# (2) E→E1 and M E2
# { backpatch(E1.truelist, M.quad);
#   E.truelist:=E2.truelist;
#   E.falselist:=merge(E1.falselist,E2.falselist) }
# e.g. 1: S -> A and M B
def rule2(attr):
    e1_false_list = attr[0]['false_list']
    e1_true_list = attr[0]['true_list']
    e2_false_list = attr[3]['false_list']
    e2_true_list = attr[3]['true_list']
    quad = attr[2]['quad']
    backpatch(e1_true_list, quad)
    return {'true_list': e2_true_list,
            'false_list': merge(e1_false_list, e2_false_list)}


# (3) E→not E1
# { E.truelist:=E1.falselist;
#   E.falselist:=E1.truelist}
# e.g. 2: A -> not C
def rule3(attr):
    e1_true_list = attr[1]['true_list']
    e1_false_list = attr[1]['false_list']
    return {'true_list': e1_false_list,
            'false_list': e1_true_list}


# (4) E→(E1)
# { E.truelist:=E1.truelist;
#   E.falselist:=E1. falselist}
# e.g. 3: B -> ( D )
def rule4(attr):
    e1_true_list = attr[1]['true_list']
    e1_false_list = attr[1]['false_list']
    return {'true_list': e1_true_list,
            'false_list': e1_false_list}


# (5) E→id1 relop id2    { E.truelist:=makelist(nextquad);
# E.falselist:=makelist(nextquad+1);
# emit(‘j’ relop.op ‘,’ id 1.place ‘,’ id 2.place‘,’　‘0’);
# emit(‘j, －, －, 0’) }
# e.g. 5: D -> i relop v
def rule5(attr):
    relop = 'j' + attr[1]['relop']
    id1_place = attr[0]['place']
    id2_place = attr[2]['place']
    quaternion.append([relop, id1_place, id2_place, '0'])
    quaternion.append(['j', '-', '-', '0'])
    return {'true_list': [(len(quaternion)-2)],  # len()-2 为当前 nextquad 值
            'false_list': [(len(quaternion)-1)]}


# (6) E→id
# { E.truelist:=makelist(nextquad);
#   E.falselist:=makelist(nextquad+1);
#   emit(‘jnz’ ‘,’ id .place ‘,’ ‘－’ ‘,’　‘0’)；
#   emit(‘ j, -, -, 0’) }
# e.g. 6: F -> y
def rule6(attr):
    id_place = attr[0]['place']
    quaternion.append(['jnz', id_place, '-', '0'])
    quaternion.append(['j', '-', '-', '0'])
    return {'true_list': [(len(quaternion)-2)],  # len()-2 为当前 nextquad 值
            'false_list': [(len(quaternion)-1)]}


# (7) M→				{ M.quad:=nextquad }
# e.g. 7: M -> ep
def rule7():
    return {'quad': len(quaternion)}  # nextquad 始终为len(quaternion)


# 移进对应的动作和属性
def shift_action(elem=None):
    if elem == 'relop':
        return {'relop': elem}
    elif elem in lr1.vn or lr1.vt:
        new_temp = elem
        return {'place': new_temp}
    else:
        return {}


# 规约式对应动作和属性
def conv_action(num, attr=None):
    new_attr = {}
    if num == 1:
        new_attr = rule2(attr)
    elif num == 2:
        new_attr = rule3(attr)
    elif num == 3:
        new_attr = rule4(attr)
    elif num == 4:
        new_attr = rule1(attr)
    elif num == 5:
        new_attr = rule5(attr)
    elif num == 6:
        new_attr = rule6(attr)
    elif num == 7:
        new_attr = rule7()
    return new_attr


# 分析产生四元式
def analyzer(input_string):
    # 建立输入串队列, 初始化符号串
    global attr
    input_queue = Queue()
    loc = 0
    while len(input_string) > loc:
        for v in lr1.vt + lr1.vn + ['ε', '#']:
            if v in input_string and operator.eq(input_string[loc:loc + len(v)], v):
                input_queue.put(v)  # 逐个输入符号入队
                loc += len(v)

    analysis_stack = lr1.Stack()  # # 初始化分析栈(状态符号栈)
    analysis_stack.push(['0', '#'])  # 栈底放入初始状态, 符号

    while True:
        status = int(analysis_stack.peek()[0])  # 当前状态(int)
        string_head = input_queue.queue[0]  # 当前输入串头(str)

        # 情况三: 接受
        if lr1.action[status + 1][lr1.action[0].index(string_head)] == 'acc':
            qua_len = len(quaternion)-1
            if qua_len in attr[0]['true_list']:
                quaternion[qua_len][3] = attr[0]['true_list'][-2]
            elif qua_len in attr[0]['false_list']:
                quaternion[qua_len][3] = attr[0]['false_list'][-2]
            lr1.action_list.append('Acc:分析成功')
            break  # 退出
        # 情况一: 移进
        elif 's' in lr1.action[status + 1][lr1.action[0].index(string_head)]:
            new_status = int(lr1.action[status + 1][lr1.action[0].index(string_head)][1:])  # 新状态为s后数字
            analysis_stack.push([str(new_status), string_head])  # 新状态, 新符号入栈
            # 为元素创建属性
            new_attr = shift_action(string_head)
            attr.append(new_attr)
            input_queue.get()  # 输入串头出队
        # 情况二: 规约
        elif 'r' in lr1.action[status + 1][lr1.action[0].index(string_head)]:
            rule_num = int(lr1.action[status + 1][lr1.action[0].index(string_head)][1:])  # 规约使用的公式序号
            protocol_string = lr1.sim_grams[rule_num].split('->')[1]  # 切分语法
            protocol_string = str(protocol_string).replace('ε', '')  # 消除ep
            reverse_string = lr1.reverse(protocol_string)
            # 倒序规约串
            conv_len = 0
            while not reverse_string.is_empty():
                elem = reverse_string.peek()
                if operator.eq(elem, analysis_stack.peek()[1]):  # 规约字符 = 栈顶字符, 出栈
                    reverse_string.pop()
                    analysis_stack.pop()  # 分析栈出栈
                    conv_len += 1
                else:  # 排错
                    print('[ERROR]: Protocol string not equal to symbol in stack!!')
                    break
            current_top_status = int(analysis_stack.peek()[0])  # 出栈后的临时栈顶
            new_symbol = lr1.sim_grams[rule_num][0]
            if lr1.goto[current_top_status + 1][lr1.goto[0].index(new_symbol)] == '':
                print('[ERROR]: No element in goto list!!')
                break
            new_status = int(lr1.goto[current_top_status + 1][lr1.goto[0].index(new_symbol)])  # 新状态为goto(临时栈顶状态, 规约获得符号)
            analysis_stack.push([str(new_status), new_symbol])  # 新状态, 新符号入栈
            # 更新 attr 的内容, 删去规约的 attr
            new_attr = conv_action(rule_num, attr[-conv_len:])  # 新的属性
            attr = attr[0:len(attr)-conv_len]  # 删去规约属性
            attr.append(new_attr)  # 加入新属性
        # 情况四: 报错
        elif lr1.action[status + 1][lr1.action[0].index(string_head)] == '':
            print('[ERROR]: No element in action list!!')
            break  # 退出
    # print(quaternion)


'''
def main():
    lr1.create_grammar_list("./data/G(S).txt")
    lr1.pre_process()
    lr1.create_collections()
    #print(create_closure(collections[0]))  # test
    lr1.create_can_cols()
    lr1.create_analysis_list()
    analyzer('notirelopvoryand(irelopv)#') #notirelopvorεvandε(irelopv)


if __name__ == '__main__':
    main()
'''
