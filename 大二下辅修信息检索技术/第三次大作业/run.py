# coding=utf-8
import time
import tkinter as tk
import ini_and_func
import re
import tkinter.messagebox as messagebox
from bs4 import  BeautifulSoup
mayaim=""
current_articles=[]
rank_art=0
def run():

    window = tk.Tk()  # 主窗口
    window.title('不挂科-search version 3.0')  # 窗口标题
    window.geometry('800x700')  # 窗口尺寸

    wel=tk.Label(window,text="welcome to 不挂科-search V3.0\n support word/phrase with wild-card (null str unsupported)\ni.e. on* of t*e, bool(qu*tion&a|!have&has)")
    wel.place(width=400,height=60,x=200,y=0)

    e = tk.Entry(window)  # 输入框
    e.place(width=200,height=20,x=250,y=60)

    tcomplete=tk.Text(window,bg="orange")
    tcomplete.place(width=360,height=20,x=100,y=80)

    tcorrect=tk.Text(window,bg="yellow")
    tcorrect.place(width=600,height=20,x=100,y=100)

    tnum=tk.Text(window,bg="orange")
    tnum.place(width=600,height=20,x=100,y=120)

    l=tk.Label(window,text="results:")
    l.place(width=200,height=20,x=300,y=140)

    tres=tk.Text(window)
    tres.place(width=600,height=340,x=100,y=265)
    tres2=tk.Text(window)
    tres2.place(width=600,height=100,x=100,y=160)
    def dynamic_search():
        s = e.get()
        if s!='' and "*" not in s:
            if s[0:5]=="bool(" and s[-1]==")":
                #print("searching for:", s[5:-1])
                r=ini_and_func.bool_calculate(s[5:-1])
            else:
                r = ini_and_func.final_search(s)

            tres2.delete(0.1,9000.0)
            tres2.insert("insert","1Hz即时搜索\""+s+"\"中，启用其他功能请点击上方搜索按钮\n"+"\n".join(r))
        window.after(1000, dynamic_search)

    def search():
        global rank_art
        rank_art=0
        s = e.get()
        if s=="":
            messagebox.showerror('error', 'searching for null is not allowed')
        aa=time.time()
        if s[0:5]=="bool(" and s[-1]==")":
            print("searching for:", s[5:-1])
            r=ini_and_func.bool_calculate(s[5:-1])
            tcomplete.delete(0.1,2.0)
            tcomplete.insert("insert","不对布尔表达式进行补全")
            tcorrect.delete(0.1,2.0)
            tcorrect.insert('insert',"不对布尔表达式进行修正")
        else:
            print("searching for:", s)
            correct_ = ini_and_func.correct_wild_phrase_search(s)
            correct_tip=correct_[0]
            correct_results=correct_[1]
            global mayaim
            mayaim=ini_and_func.auto_complete(s)
            tcomplete.delete(0.1,2.0)
            tcomplete.insert("insert","补全提示：是否想要搜索\""+mayaim+"\"?")
            r=ini_and_func.num2doc(correct_results)
            global current_articles
            current_articles=correct_results

            tcorrect.delete(0.1,2.0)
            if len(correct_results)>0 and correct_tip!="":
                tcorrect.insert('insert',"原搜索无结果，为您显示"+correct_tip+"的搜索结果")
            elif correct_tip=="" and len(correct_results)==0:
                tcorrect.insert('insert', "原搜索无结果，请尝试其他搜索")
            elif correct_tip=="" and len(correct_results)>0:
                tcorrect.insert('insert', "原搜索无需修正")

        aaa=time.time()-aa
        tnum.delete(0.1,2.0)
        tnum.insert("insert","time used: "+str(aaa)+" s, return "+str(len(r))+" results")
        tres.delete(0.1,9000.0)
        tres.insert("insert","\n".join(r))

    def search2():
        global rank_art
        rank_art=0
        global mayaim
        s = mayaim
        if s=="":
            messagebox.showerror('error', 'searching for null is not allowed')
        e.delete(0,'end')
        e.insert('insert',mayaim)
        aa=time.time()
        if s[0:5]=="bool(" and s[-1]==")":
            print("searching for:", s[5:-1])
            r=ini_and_func.bool_calculate(s[5:-1])
            tcomplete.delete(0.1,2.0)
            tcomplete.insert("insert","不对布尔表达式进行补全")
            tcorrect.delete(0.1,2.0)
            tcorrect.insert('insert',"不对布尔表达式进行修正")
        else:
            print("searching for:", s)
            correct_ = ini_and_func.correct_wild_phrase_search(s)
            correct_tip=correct_[0]
            correct_results=correct_[1]
            mayaim=ini_and_func.auto_complete(s)
            tcomplete.delete(0.1,2.0)
            tcomplete.insert("insert","补全提示：是否想要搜索\""+mayaim+"\"?")
            r=ini_and_func.num2doc(correct_results)
            global current_articles
            current_articles=correct_results

            tcorrect.delete(0.1,2.0)
            if len(correct_results)>0 and correct_tip!="":
                tcorrect.insert('insert',"原搜索无结果，为您显示"+correct_tip+"的搜索结果")
            elif correct_tip=="" and len(correct_results)==0:
                tcorrect.insert('insert', "原搜索无结果，无法修正")
            elif correct_tip=="" and len(correct_results)>0:
                tcorrect.insert('insert', "原搜索无需修正")

        aaa=time.time()-aa
        tnum.delete(0.1,2.0)
        tnum.insert("insert","time used: "+str(aaa)+" s, return "+str(len(r))+" results")
        tres.delete(0.1,9000.0)
        tres.insert("insert","\n".join(r))

    c = tk.Button(window,
                  text='search',  # 显示按钮上的文字
                  command=search)  # 点击按钮执行的命令
    c.place(width=80,height=20,x=470,y=60)

    c2 = tk.Button(window,
                  text='search for this',  # 显示按钮上的文字
                  command=search2)  # 点击按钮执行的命令
    c2.place(width=180,height=20,x=485,y=80)

    def view_article():
        global rank_art
        global current_articles
        try:
            art_win = tk.Toplevel()
            f_name=ini_and_func.filelist[current_articles[rank_art]]
            art_win.title(ini_and_func.file_title[f_name.replace('.html','')])
            art_win.geometry('600x400')

            def get_art():
                global rank_art
                global current_articles
                name=ini_and_func.filelist[current_articles[rank_art]]
                f = open(ini_and_func.path + "\\" + name, 'r',encoding='utf-8')
                content = f.read()
                soup=BeautifulSoup(content,features="lxml")
                s=soup.get_text().replace('\n\n\n','\n')
                return s

            tart = tk.Text(art_win)
            tart.place(width=500, height=320, x=50, y=20)
            tart.insert('insert',get_art())

            def refresh_art_pre():
                global rank_art
                global current_articles
                rank_art -= 1
                rank_art = rank_art % len(current_articles)
                tart.delete(0.1,99999.0)
                f_name = ini_and_func.filelist[current_articles[rank_art]]
                art_win.title(ini_and_func.file_title[f_name.replace('.html', '')])
                tart.insert('insert',get_art())
            def refresh_art_next():
                global rank_art
                global current_articles
                rank_art += 1
                rank_art=rank_art%len(current_articles)
                tart.delete(0.1,99999.0)
                f_name = ini_and_func.filelist[current_articles[rank_art]]
                art_win.title(ini_and_func.file_title[f_name.replace('.html', '')])
                tart.insert('insert',get_art())

            c4 = tk.Button(art_win,
                           text='view the previous searched page',  # 显示按钮上的文字
                           command=refresh_art_pre)  # 点击按钮执行的命令
            c4.place(width=200, height=30, x=50, y=350)

            c5 = tk.Button(art_win,
                           text='view the next searched page',  # 显示按钮上的文字
                           command=refresh_art_next)  # 点击按钮执行的命令
            c5.place(width=200, height=30, x=350, y=350)

        except:
            messagebox.showerror('error','no results for viewing')

    c3 = tk.Button(window,
                  text='view the searched pages',  # 显示按钮上的文字
                  command=view_article)  # 点击按钮执行的命令
    c3.place(width=200,height=30,x=300,y=640)

    def complete_tip():
        s = e.get()
        if s!="":
            global mayaim
            mayaim=ini_and_func.auto_complete(s)
            tcomplete.delete(0.1,2.0)
            tcomplete.insert("insert","补全提示：是否想要搜索\""+mayaim+"\"?")
        window.after(500, complete_tip)

    window.after(1000,dynamic_search)
    window.after(500,complete_tip)
    window.mainloop()

if __name__=="__main__":
    run()