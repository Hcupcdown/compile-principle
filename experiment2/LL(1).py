#create by cup&cdown
#2019-5-20
#compile principle LL(1)

import re
import copy

#分析表类
class analysis_table:
    grammar={}  #输入文法
    table=[[]]  #分析表
    nter=[]     #非终结符
    ter=[]      #终结符
    first={}    #first集
    follow={}   #follow集

    #初始化函数
    def __init__(self):
        num=int(input("请输入文法规则条数："))
        for i in range(num):
            key,value=input().split("::=")
            self.grammar[key]=value

    #消除左递归
    def eliminate_recursion(self):
        initial_nter=list(self.grammar.keys())
        new_grammar={}                              #新的文法
        j=0
        length=len(initial_nter)
        i=length-1
        while i>=0:
            self.grammar[initial_nter[i]]=self.grammar[initial_nter[i]].split('|')
            j=length-1
            while j>=i+1:
                for k in self.grammar[initial_nter[i]]:
                    #对于所有形如Ui::=Ujy的规则
                    if initial_nter[j]==k[0] and len(k)>=2:
                        #将Ui::=Ujy替换为Ui::=x1y|x2y|……|xny
                        self.grammar[initial_nter[i]].remove(k)
                        for new_list in self.grammar[initial_nter[j]]:
                            self.grammar[initial_nter[i]].append(new_list+k[1:])
                        self.grammar.pop(initial_nter[j])
                        self.grammar
                j-=1
            i-=1
        initial_nter=self.grammar.keys()
        #处理原文法，消除直接左递归
        for i in initial_nter:
            
            now_relu=self.grammar[i]                     #当前处理的那一条文法
            flag=False
            alpha=[]
            beta=[]
            for now_relu in self.grammar[i]:
                if i == now_relu[0]:               #如果是直接左递归
                    alpha.append(now_relu[1:])     #递归符号右的符号
                    flag=True
                else:
                    beta.append(now_relu)
            if flag:
                new_nter=i.lower()              #生成一个新的非终结符
                new_relu1=[b+new_nter for b in beta]#生成新非终结符的文法规则
                new_relu2=[a+new_nter for a in alpha]
                new_relu2.append('0')
                new_grammar[i]=new_relu1
                new_grammar[new_nter]=new_relu2
            else:
                new_grammar[i]=self.grammar[i]

        self.grammar=new_grammar

        #求终结符和非终结符集合
        self.nter=list(new_grammar.keys())     #非终结符
        for now_nter in self.nter:                    #查找终结符
            for now_relu in new_grammar[now_nter]:
                for k in now_relu:
                    if (not k in self.nter) and(not k== '0'):
                        if (not k in self.ter):
                            self.ter.append(k)        #终结符
        self.ter=list(set(self.ter))              #去除相同元素
        
    #求first集的递归函数
    def first_aggregate(self,i):

        new_first=[]
        now_relu=self.grammar[i]
        for j in now_relu:                          #如果j是非终结符
            for k in j:                         
                if k in self.nter:
                    if not ('0' in self.grammar[k]):
                        for m in self.first_aggregate(k):
                            new_first.append(m)
                        break
                elif k in self.ter or k=='0':        #如果是终结符
                    new_first.append(k)
                    break
                else:
                    continue
        return new_first

    #求取first集
    def first_agg(self):
        self.first={}
        for i in self.ter:
            self.first[i]=i
        for i in self.nter:
            self.first[i]=self.first_aggregate(i)
    
    #求取follow集
    def follow_agg(self):
        self.follow={}
        for i in self.nter:             #初始化nfollow集
            self.follow[i]=[]
        self.follow[self.nter[0]].append('#')                   #将'#'放到开始符号的follow集中

        for k in range(2):
            for i in self.nter:
                for now_relu in self.grammar[i]:
                    if len(now_relu)>=2:
                        if (now_relu[-2] in self.nter):                                                         #如果有A->aBb,b！='0'，将first(b)中所有非空符号加入follow（B）中
                            if  (now_relu[-1] in self.ter) or (not ['0']==self.grammar[now_relu[-1]]):          #如果是终结符或者可以不可以推倒到空
                                for m in self.first[now_relu[-1]]:
                                    if (not m=='0') and (m not in self.follow[now_relu[-2]]):
                                        self.follow[now_relu[-2]].append(m)                                     #将first集中所有非空元素都放入follow(B)中

                            if (now_relu[-1] in self.nter) and('0' in b for b in self.grammar[now_relu[-1]]):   #如果可以推倒到空
                                for m in self.follow[i]:
                                    if not (m  in self.follow[now_relu[-2]]):                                   #则将follow(A)中所有元素放到follow(B)中
                                        self.follow[now_relu[-2]].append(m)

                        if now_relu[-1] in self.nter:           #如果是A->aB的形式
                            for m in self.follow[i]:            #直接将follow(A)放到follow(B)中
                                if not (m in self.follow[now_relu[-1]]):
                                    self.follow[now_relu[-1]].append(m)

    #构造分析表
    def generate_analysis_table(self):
        
        self.ter.append('#')                                       #在终结符中加入’#‘
        self.table=[['error' for i in range(len(self.ter))] for i in range(len(self.nter))]             #生成存放表的二维数组
        temporary_firt=copy.deepcopy(self.first)                                                                     #临时用first集
        for now_nter in self.nter:                                                                      #遍历非终结符
            for now_relu in self.grammar[now_nter]:                                                     #对非终结符对应的规则A->@
                if now_relu[0] in self.ter:                                                             #如果该规则是以终结符a开头，直接将这条规则放到table[A][a]中，
                    self.table[self.nter.index(now_nter)][self.ter.index(now_relu[0])]= now_relu
                    temporary_firt[now_nter].pop(temporary_firt[now_nter].index(now_relu[0]))           #并从临时用first集中删除已经处理过的a
                else:                                                                                   #如果规则是非终结符开头
                    for now_ter in temporary_firt[now_nter]:        
                        if now_ter == '0':                                                              #对应规则是A->’0‘,则查询follow集
                            for now_follow in self.follow[now_nter]:
                                self.table[self.nter.index(now_nter)][self.ter.index(now_follow)]= now_relu
                        else:                                                                           #否则将对应的终结符所在列都置为@
                            self.table[self.nter.index(now_nter)][self.ter.index(now_ter)]= now_relu

    #总分析程序
    def analysis(self,str):        
        self.eliminate_recursion()          #消除左递归文法,生成新文法
        self.first_agg()                    #构造first集
        self.follow_agg()                   #构造follow集
        self.generate_analysis_table()
        self.show()
        analysis_stack=['#',self.nter[0]]           #初始化分析栈
        i=0
        print("分析过程为：")
        while i < len(str):
            print(analysis_stack,end="  ")
            m=i
            while m<len(str):
                print(str[m],end="")
                m+=1
            print()
            #当Xm=ai时
            if analysis_stack[-1]==str[i]:
                i+=1
                if analysis_stack.pop() =='#':
                  print("分析成功")
                  break

            #如果栈顶元素不在分析表中
            elif analysis_stack[-1] not in self.nter:
                print("不是该文法的句子")
                break

            #如果对应分析表为空
            elif self.table[self.nter.index(analysis_stack[-1])][self.ter.index(str[i])] == 'error':
                print("不是该文法的句子")
                break

            #如果在分析表中查找产生式
            else:
                j=0
                c=analysis_stack.pop(-1)            #弹出栈顶元素
                strin=self.table[self.nter.index(c)][self.ter.index(str[i])]          #查找分析表
                while j < len(strin):
                    if not (strin[-(j+1)] == '0'):
                        analysis_stack.append(strin[-(j+1)])
                    j+=1
    
    #输出分析表等
    def show(self):
        print("\n消除左递归后的文法为：")
        for i in self.grammar:
            print(i,end=" := ")
            flag=True
            for j in self.grammar[i]:
                if flag:
                    print(" "+j,end=" ")
                    flag=False
                else:
                    print("| "+j,end=" ")
            print("")

        print("\n非终结符为：")
        print(self.nter)
        print("\n终结符为：")
        print(self.ter)
        print("\nfirst集为：")
        for i in self.first:
            if  not i in self.ter:
                print("first("+i+") = { ",end="")
                for j in self.first[i]:
                    print(j,end=",")
                print("}")
        print("\nfollow集为:")
        for i in self.follow:
            print("follow("+i+") = { ",end="")
            for j in self.follow[i]:
                print(j,end=",")
            print("}")
        print()
        
#处理输入字符串 用于测试"age+(80*fd)"
def translate(str):
    str = re.sub(r"\w+",'i',str)+'#'           #输入字符串
    return str

#主程序段
if __name__=='__main__':
    analy_tab=analysis_table()
    #str=translate(input("请输入要判断的句子:"))
    str=input("请输入要判断的句子：")+'#'
    analy_tab.analysis(str)