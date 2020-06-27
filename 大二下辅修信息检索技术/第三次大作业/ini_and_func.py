# coding=utf-8
import re
import itertools
from functools import reduce
import time
from pyhanlp import *
from bs4 import BeautifulSoup
import csv
csv.field_size_limit(500 * 1024 * 1024)
path="htmls"
filelist = os.listdir(path)
print("initializing...")
#建立倒排索引
a=time.time()
words=[]

file_title={}
reader = csv.reader(open('title.csv','r',encoding='utf-8'),delimiter=',',quotechar='雘')
for row in reader:
    file_title[row[0]]=",".join(row[1:])
del reader

file_url_baidu={} #{file_name:[url,baidu_find]}
reader = csv.reader(open('url_table.csv','r',encoding='utf-8'),delimiter=',',quotechar='雘')
for row in reader:
    file_url_baidu[row[0]]=[",".join(row[1:-1]),eval(row[-1])]
del reader

word_num_dict = {}  # 词-编号 hash
word_doc_dict = {}  # 倒排索引
reader = csv.reader(open('inverted_index.csv','r',encoding='utf-8'),delimiter='`',quotechar='雘')
for row in reader:
    word_num_dict[row[1]]=eval(row[0])
    words.append(row[1])
    word_doc_dict[row[1]]=[eval(x) for x in row[2:]]
del reader
#给倒排索引增加位置信息
num_words = len(words)
num_docs = len(filelist)

positional_index = {}  # 位置信息  {词:{文档：[位置]}的形式
reader = csv.reader(open('pos_index.csv', 'r', encoding='utf-8'), delimiter='`',quotechar='雘')
for w in words:
    positional_index[w] = {}
for row in reader:
    w_d=row[0]
    i=-1
    while w_d[i]!='@':
        i-=1
    w=w_d[:i]
    doc=eval(w_d[i+1:])
    positional_index[w][doc]=[eval(x) for x in row[1:]]
del reader

lines=0#############debug

inv_index=open("inverted_index.csv",'r',encoding='utf-8')
inv_index=inv_index.readlines()
inv_index=[(s.strip()).split('`')[2:] for s in inv_index]
for i in range(len(inv_index)):
    lines+=1
    for j in range(len(inv_index[i])):
        inv_index[i][j]=eval(inv_index[i][j])

####################################and query
def and_query_skip(a, b):
    answer = []
    try:
        if type(a) == str:
            lista = inv_index[word_num_dict[a]]
        else:
            lista = a
        indice1 = 0
        indice1max = len(lista)  # unreachable
        step1 = int(indice1max ** 0.5)

        if type(b) == str:
            listb = inv_index[word_num_dict[b]]
        else:
            listb = b
        indice2 = 0
        indice2max = len(listb)
        step2 = int(indice2max ** 0.5)

        while (indice1 < indice1max and indice2 < indice2max):
            if lista[indice1] == listb[indice2]:
                answer.append(lista[indice1])
                indice1 += 1
                indice2 += 1
            elif lista[indice1] < listb[indice2]:
                if indice1 % step1 == 0 and indice1 + step1 < indice1max and lista[indice1 + step1] <= listb[indice2]:
                    # has_skip and smaller
                    indice1 += step1
                else:
                    indice1 += 1
            elif indice2 % step2 == 0 and indice2 + step2 < indice2max and lista[indice1] >= listb[indice2 + step2]:
                indice2 += step2
            else:
                indice2 += 1
    except:
        1
    return answer


def and_query(a, b):
    answer = []
    try:
        if type(a) == str:
            lista = inv_index[word_num_dict[a]]
        else:
            lista = a
        indice1 = 0
        indice1max = len(lista)  # unreachable

        if type(b) == str:
            listb = inv_index[word_num_dict[b]]
        else:
            listb = b
        indice2 = 0
        indice2max = len(listb)

        while (indice1 < indice1max and indice2 < indice2max):
            if lista[indice1] == listb[indice2]:
                answer.append(lista[indice1])
                indice1 += 1
                indice2 += 1
            elif lista[indice1] < listb[indice2]:
                indice1 += 1
            else:
                indice2 += 1
    except:
        1
    return answer


def multi_and_query_skip(t):
    if len(t) > 1:
        return reduce(and_query_skip, t)
    else:
        try:
            return word_doc_dict[t[0]]
        except:
            return []


def multi_and_query(t):
    if len(t) > 1:
        return reduce(and_query, t)
    else:
        try:
            return word_doc_dict[t[0]]
        except:
            return []


###################################time
def run_time(func, epoch):
    a = time.time()
    for i in range(epoch):
        eval(func)
    return (time.time() - a)


##########################################phrase
def inverted_untuple_descartes(c):
    ans = []
    while type(c) != int and type(c) != str:
        ans.append(c[-1])
        c = c[0]
    ans.append(c)
    return ans


def strict_desc(numlist):
    for i in range(len(numlist) - 1):
        if numlist[i] <= numlist[i + 1]:
            return 0
    return 1


def judge_adaj(positions):
    n_w = len(positions)
    flag = 0
    all_c = reduce(itertools.product, positions)
    for c in all_c:
        temp = inverted_untuple_descartes(c)
        dis = max(temp) - min(temp)
        if dis == n_w - 1 and strict_desc(temp):
            flag = 1
    return flag


def phrase_search(s):
    answer = []
    single_words = s.split()
    common_docs = multi_and_query_skip(single_words)
    for d in common_docs:
        positions = []
        for w in single_words:
            positions.append(positional_index[w][d])  # 2d-list
        if judge_adaj(positions):
            answer.append(d)
    return answer


#########################通配符
#####build bigram
def generate_bigram(w):
    ans=[]
    w_len=len(w)
    ans.append('$'+w[0])
    for i in range(w_len-1):
        ans.append(w[i:i+2])
    ans.append(w[-1]+"$")
    return ans

bigram_word={}
reader = csv.reader(open('inverted_index.csv','r',encoding='utf-8'),delimiter='`',quotechar='雘')
for row in reader:
    bigram_word[row[0]]=row[1:]
del reader

def search_two_bigram(b1, b2):
    answer = []
    try:
        if type(b1) == str:
            lista = bigram_word[b1]
        else:
            lista = b1
        indice1 = 0
        indice1max = len(lista)  # unreachable
        step1 = int(indice1max ** 0.5)

        if type(b2) == str:
            listb = bigram_word[b2]
        else:
            listb = b2
        indice2 = 0
        indice2max = len(listb)
        step2 = int(indice2max ** 0.5)

        while (indice1 < indice1max and indice2 < indice2max):
            if lista[indice1] == listb[indice2]:
                answer.append(lista[indice1])
                indice1 += 1
                indice2 += 1
            elif lista[indice1] < listb[indice2]:
                if indice1 % step1 == 0 and indice1 + step1 < indice1max and lista[indice1 + step1] <= listb[indice2]:
                    # has_skip and smaller
                    indice1 += step1
                else:
                    indice1 += 1
            elif indice2 % step2 == 0 and indice2 + step2 < indice2max and lista[indice1] >= listb[indice2 + step2]:
                indice2 += step2
            else:
                indice2 += 1

    except:
        1
    return answer

def search_list_bigram(l):
    if len(l) > 1:
        return reduce(search_two_bigram, l)
    else:
        try:
            return bigram_word[l[0]]
        except:
            return []

def star_pos(s):
    poses = []
    p = re.finditer("\*", s)
    for i in p:
        poses.append(i.span()[0])
    return poses

def check(pattern, w):
    ps = re.match(pattern, w)
    if not ps:
        return 0
    if w in ps.group():
        return 1
    else:
        return 0

def search_star(s):
    ans = []
    result = []
    pos1 = star_pos(s)[0]
    pos2 = star_pos(s)[-1]
    left = s[:pos1]
    right = s[pos2 + 1:]
    if len(left) > 0 and len(right) > 0:
        left_bigrams = generate_bigram(left)[:-1]
        right_bigrams = generate_bigram(right)[1:]
        left_result = search_list_bigram(left_bigrams)
        right_result = search_list_bigram(right_bigrams)
        result = search_two_bigram(left_result, right_result)
    elif len(left) > 0:
        left_bigrams = generate_bigram(left)[:-1]
        result = search_list_bigram(left_bigrams)
    elif len(right) > 0:
        right_bigrams = generate_bigram(right)[1:]
        result = search_list_bigram(right_bigrams)
    else:  # *a.*b*  *a*  ** *
        if len(s) >= 4:  # *a.*b*
            if r"*" in s[1:-1]:
                result=words
            else:
                middle_bigrams = generate_bigram(s[1:-1])[1:-1]
                result = search_list_bigram(middle_bigrams)
        elif len(s) == 3:  # *a* ***
            if s[1]!=r"*":
                result = [w for w in words if s[1:2] in w]
            else:
                result=words
        else:  # **  *
            result = words

    spattern = re.compile(s.replace(r"*", r".*"))
    ans = [w for w in result if check(spattern, w) == 1]
    return ans

def single_word_wild_card_search(s):
    ans = {}
    try:
        l = search_star(s)
        for i in l:
            ans[i] = word_doc_dict[i]
    except:
        try:
            ans[s] = word_doc_dict[s]
        except:
            1
    return ans

def and_query_wild(a, b):
    ans = []
    a_choice = single_word_wild_card_search(a)
    b_choice = single_word_wild_card_search(b)
    if len(a_choice) * len(b_choice) == 0:
        return ans
    for pair in itertools.product(a_choice.keys(), b_choice.keys()):
        tempa = pair[0]
        tempb = pair[1]
        ans.extend(and_query_skip(tempa, tempb))
    return ans

def whole_wild_search(s):
    answer = []
    star_single_words = s.split()
    choices = [single_word_wild_card_search(x).keys() for x in star_single_words]
    for i in choices:
        if len(i) == 0:
            return answer
    choices_product = reduce(itertools.product, choices)

    for c in choices_product:
        single_words = inverted_untuple_descartes(c)
        single_words.reverse()
        answer.extend(phrase_search(" ".join(single_words)))

    new_ans=[]  # deduplicate
    for i in answer:
        if i not in new_ans:
            new_ans.append(i)
    return new_ans

def num2doc(ans):
    ans.sort()
    f_names=[filelist[x].replace('.html','') for x in ans]
    output=[]
    for f_name in f_names:
        f_title=file_title[f_name]
        f_url_baidu=file_url_baidu[f_name]
        if f_url_baidu[1]==1:
            output.append("百度已收录："+f_title+" "+f_url_baidu[0])
        else:
            output.append("百度未收录：" + f_title + " " + f_url_baidu[0])
    return output

def final_search(s):
    s = s.lower()
    return num2doc(whole_wild_search(s))


def OR_2(a, b):
    if type(a) == str:
        lista = single_word_wild_card_search(a).values()
        lista = list(itertools.chain.from_iterable(lista))
    else:
        lista = a
    if type(b) == str:
        listb = single_word_wild_card_search(b).values()
        listb = list(itertools.chain.from_iterable(listb))
    else:
        listb = b
    ans = []
    for i in lista:
        if i not in ans:
            ans.append(i)
    for i in listb:
        if i not in ans:
            ans.append(i)
    return ans


def NOT_1(a):
    if type(a) == str:
        lista = single_word_wild_card_search(a).values()
        lista = list(itertools.chain.from_iterable(lista))
    else:
        lista = a
    return [x for x in range(num_docs) if x not in lista]


def AND_NOT(a, b):  # b  must be a word(maybe with wild-card)
    ans = []
    aandb = []
    if type(a) == str:
        a_choice = single_word_wild_card_search(a)
        b_choice = single_word_wild_card_search(b)
        if len(a_choice) * len(b_choice) != 0:
            for pair in itertools.product(a_choice.keys(), b_choice.keys()):
                tempa = pair[0]
                tempb = pair[1]
                aandb.extend(and_query_skip(tempa, tempb))

        lista = a_choice.values()
        lista = list(itertools.chain.from_iterable(lista))
        ans = [x for x in lista if x not in aandb]
    else:  # a is a list
        listb = single_word_wild_card_search(b).values()
        listb = list(itertools.chain.from_iterable(listb))
        ans = [x for x in a if x not in listb]
    return ans


def split_or(s):
    return s.split(r"|")


def dealwithand(s):
    words = s.split(r"&")
    ands = []
    andnot = []
    for w in words:
        if w[0] != r"!":
            ands.append(w)
        else:
            andnot.append(w[1:])  # 去掉！
    ans = []
    if len(ands) > 1:
        ans.extend(reduce(and_query_wild, ands))
    elif len(ands) == 1:
        templist = single_word_wild_card_search(ands[0]).values()
        templist = list(itertools.chain.from_iterable(templist))
        for i in templist:
            if i not in ans:
                ans.append(i)
    else:
        ans = range(num_docs)
    for an in andnot:
        ans = AND_NOT(ans, an)
    return ans


def multi_OR(l):
    templist = list(itertools.chain.from_iterable(l))
    ans = []
    for i in templist:
        if i not in ans:
            ans.append(i)
    return ans


def bool_calculate(s):
    s=s.lower()
    and_exps = split_or(s)
    WaitingForOR = []
    for i in and_exps:
        WaitingForOR.append(dealwithand(i))
    a=multi_OR(WaitingForOR)
    return num2doc(a)
#####################################
def find_like_phrase(w):
    """将字符串中连续的1~2个字符换成*，不换空格"""
    w=w.lower()
    substitutes=[]
    for i in range(len(w)-1,-1,-1):
        if w[i]!=' ':
            substitutes.append(w[:i]+'*'+w[i+1:])
    if len(w)>1:
        for i in range(len(w)-2,-1,-1):
            if w[i]!=' ' and w[i+1]!=' ':
                substitutes.append(w[:i]+'*'+w[i+2:])
    return substitutes

def correct_wild_phrase_search(p):
    """如果找不到答案且找到了相似短语的答案，返回相似短语和答案
    否则返回空字符串和答案"""
    p=p.lower()
    ans=whole_wild_search(p)
    if len(ans)==0:
        subs=find_like_phrase(p)
        for sub in subs:
            ans2=whole_wild_search(sub)
            if len(ans2)>0:
                return(sub,ans2)
    return ("",ans)

def candidates(w):
    """get the candidates of an unfinished word"""
    l=len(w)
    bis= generate_bigram(w)[:-1]#leave out 'x$'
    candis= search_list_bigram(bis)
    num_candis=len(candis)
    to_remove=[]
    for i in range(num_candis):
        if candis[i][:l]!=w:
            to_remove.append(candis[i])
    for i in to_remove:
        candis.remove(i)
    return candis

def auto_complete(p):
    """trying to complete the phrase which is not complete"""
    p=p.lower()
    if "*" in p:
        ws=p.split()
        last_word=ws[-1]
        try:
            ws[-1]=candidates(last_word)[0]
        except:
            ws.pop(-1)
        newp=" ".join(ws)
        return newp
    else:
        ws = p.split()
        last_word = ws[-1]
        candis = candidates(last_word)
        candi_flag=0
        for candi in candis:
            ws[-1]=candi
            temp_search=" ".join(ws)
            temp_ans=whole_wild_search(temp_search)
            if len(temp_ans)>0:
                candi_flag=1
                ws[-1]=candi
                break

        if candi_flag==0:
            ws.pop(-1)
        newp=" ".join(ws)
        return newp

print("initialized, time used: ",time.time()-a,'s')