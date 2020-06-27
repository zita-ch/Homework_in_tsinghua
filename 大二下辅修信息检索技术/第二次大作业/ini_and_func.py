# coding=utf-8
import os
import re
import nltk
import itertools
from functools import reduce
import time
path="cacm"
filelist = os.listdir(path)
print("initializing...")
#建立倒排索引
a=time.time()
words=[]
titles=[]#最后顺便输出标题
punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%','`','\"','\'','``']
for i in filelist:
    f=open(path+"\\"+i,'r')
    content=f.read()
    try:
        s = re.findall("<pre>\n\n\n([\S\s]*?)CACM", content)[0]
        title_s = re.findall('(.*?)\n', s)[0]
        titles.append(title_s)
        s = s.replace("\n", " ").strip()
        temp_words = [w.lower() for w in nltk.word_tokenize(s) if w not in punctuations]
    except:
        s = re.findall("<pre>\n\n\n([\S\s]*?)19[5|6|7]", content)[0]
        title_s = re.findall('(.*?)\n', s)[0]
        titles.append(title_s)
        s = s.replace("\n", " ").strip()
        temp_words = [w.lower() for w in nltk.word_tokenize(s) if w not in punctuations][:-1]
    for w in temp_words:
        if w not in words:
            words.append(w)
    f.close()

word_num_dict = {}  # 词-编号 hash
for i in range(len(words)):
    word_num_dict[words[i]] = i

#给倒排索引增加位置信息
num_words = len(words)
num_docs = len(filelist)
word_doc_dict = {}  # 倒排索引
positional_index = {}  # 位置信息  {词:{文档：[位置]}的形式
for w in words:
    word_doc_dict[w] = []
    positional_index[w] = {}
for i in range(num_docs):
    f = open(path + "\\" + filelist[i], 'r')
    content = f.read()
    try:
        s = re.findall("<pre>([\S\s]*?)CACM", content)[0].replace("\n", " ").strip()
        temp_words = [w.lower() for w in nltk.word_tokenize(s) if w not in punctuations]
    except:
        s = re.findall("<pre>([\S\s]*?)19[5|6|7]", content)[0].replace("\n", " ").strip()
        temp_words = [w.lower() for w in nltk.word_tokenize(s) if w not in punctuations][:-1]
    for n in range(len(temp_words)):
        w = temp_words[n]
        if i not in word_doc_dict[w]:
            word_doc_dict[w].append(i)
            positional_index[w][i] = [n]
        else:
            positional_index[w][i].append(n)

    f.close()

wr2=open("inverted_index.csv",'w')
skip_steps=[]
for i in range(num_words):
    word=words[i]
    index=word_doc_dict[word]
    skip_steps.append(int((len(index))**0.5))
    str_index=[str(x) for x in index]
    wr2.write(str(i)+"`"+word+"`"+"`".join(str_index)+"\n")
wr2.close()

wr4=open("pos_index.csv",'w')
for w in words:
    for d in word_doc_dict[w]:
        temp_poses=positional_index[w][d]
        temp_poses=[str(x) for x in temp_poses]
        wr4.write(w+"@"+str(d)+"`"+"`".join(temp_poses)+"\n")
wr4.close()
print("带位置信息的倒排索引建立时间：",time.time()-a,"s")

inv_index=open("inverted_index.csv",'r')
inv_index=inv_index.readlines()
inv_index=[(s.strip()).split('`')[2:] for s in inv_index]
for i in range(len(inv_index)):
    for j in range(len(inv_index[i])):
        inv_index[i][j]=eval(inv_index[i][j])

##################建立和记录skippoints
wr3=open("skip_points.csv","w")
for i in range(num_words):
    word=words[i]
    index=word_doc_dict[word]
    index=index[0::skip_steps[i]]
    str_index=[str(x) for x in index]
    wr3.write(str(i)+"`"+word+"`"+"`".join(str_index)+"\n")
wr3.close()


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
        return word_doc_dict[t[0]]


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

word_bigram={}
for w in words:
    word_bigram[w]=generate_bigram(w)
bigrams=[]
for b in word_bigram.values():
    for bi in b:
        if bi not in bigrams:
            bigrams.append(bi)

a=time.time()
bigram_word={}
for b in bigrams:
    bigram_word[b]=[]
for w,bs in word_bigram.items():
    for bi in bs:
        if w not in bigram_word[bi]:
            bigram_word[bi].append(w)
for b in bigrams:
    bigram_word[b].sort()
print("bigram_index building time:",time.time()-a,"s")

wrb=open('bigram_index.csv','w')
for key,value in bigram_word.items():
    wrb.write(key+"`"+"`".join(value)+'\n')
wrb.close()

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
    return [filelist[x]+" "+titles[x] for x in ans]

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
