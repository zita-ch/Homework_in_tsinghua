# coding=utf-8
import time
import tkinter as tk
import ini_and_func

def run():
    window = tk.Tk()  # 主窗口
    window.title('不挂科-search version -1.0')  # 窗口标题
    window.geometry('800x600')  # 窗口尺寸

    wel=tk.Label(window,text="welcome to 不挂科-search V-1.0\n support word/phrase with wild-card i.e.\n on* of t*e, bool(qu*tion&a|!have&has)")
    wel.place(width=300,height=60,x=250,y=0)

    e = tk.Entry(window)  # 输入框
    e.place(width=200,height=20,x=250,y=60)

    tnum=tk.Text(window,bg="grey")
    tnum.place(width=600,height=20,x=100,y=80)

    l=tk.Label(window,text="results:")
    l.place(width=200,height=20,x=300,y=100)

    tres=tk.Text(window)
    tres.place(width=600,height=440,x=100,y=120)

    def search():
        s = e.get()
        aa=time.time()
        if s[0:5]=="bool(" and s[-1]==")":
            print("searching for:", s[5:-1])
            r=ini_and_func.bool_calculate(s[5:-1])
        else:
            print("searching for:", s)
            r=ini_and_func.final_search(s)

        aaa=time.time()-aa
        tnum.delete(0.1,2.0)
        tnum.insert("insert","time used: "+str(aaa)+" s, return "+str(len(r))+" results")
        tres.delete(0.1,9000.0)
        tres.insert("insert","\n".join(r))

    c = tk.Button(window,
                  text='search',  # 显示按钮上的文字
                  command=search)  # 点击按钮执行的命令
    c.place(width=80,height=20,x=470,y=60)

    window.mainloop()

if __name__=="__main__":
    run()