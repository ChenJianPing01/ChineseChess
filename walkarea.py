﻿'''
中国象棋软件着法区域类型
'''

from config_et import *
from crossbase import *
from walk import *

       
class WalkArea(View, ttk.Frame):

    def __init__(self, master, models): 
        View.__init__(self, models)
        ttk.Frame.__init__(self, master, padding=2)
        
        self.create_widgets()
        self.create_layout()
        self.create_bindings()    
         
    def create_widgets(self):

        def create_topfrm():        
            topfrm = ttk.Frame(self, padding=2)
            Label(topfrm, text='棋局信息', font='Helvetica -14 bold').pack(side=TOP) #
            Label(topfrm, text='非比赛').pack(side=TOP) #, fill=X
            Label(topfrm, text='%s  %s  %s' % ('Red', 'Result', 'Black')).pack(side=TOP)#, fill=X
            Label(topfrm, text='%s 奕于 %s' % ('Date','Site')).pack(side=TOP) #, fill=BOTH
            topfrm.pack(side=TOP) # 顶部区域 , fill=X     
        
        def create_midfrm(): 
        
            def create_midleftfrm(midfrm):        
                midleftfrm = ttk.LabelFrame(midfrm, relief=GROOVE, text=' 着法列表 ',
                            labelanchor='nw', padding=2) # padx=6, pady=3, 
                scrollbar = Scrollbar(midleftfrm, orient=VERTICAL)
                walklistbox = Listbox(midleftfrm, width=15, listvariable = self.listvar,
                            activestyle='dotbox', yscrollcommand=scrollbar.set) # width=13
                scrollbar.config(command=walklistbox.yview)
                walklistbox.config(selectmode=SINGLE, selectbackground='blue',
                            selectforeground='white', font=('Consolas', '10')) #
                            # 'gray', setgrid=1, #activestyle='dotbox', #,'underline'
                scrollbar.pack(side=RIGHT, fill=Y)        
                walklistbox.pack(side=LEFT, fill=BOTH)
                midleftfrm.pack(side=LEFT, fill=BOTH)
                self.walklistbox = walklistbox
        
            def create_midrightfrm(midfrm): 
                midrightfrm = ttk.Frame(midfrm, padding=2)
                Button(midrightfrm, text='最后局面', width=8,
                       command=lambda: self.onEndKey(None)).pack(side=BOTTOM)
                Button(midrightfrm, text='下一着', width=8,
                       command=lambda: self.onDownKey(None)).pack(side=BOTTOM)
                Button(midrightfrm, text='上一着', width=8,
                       command=lambda: self.onUpKey(None)).pack(side=BOTTOM)
                Button(midrightfrm, text='起始局面', width=8,
                       command=lambda: self.onHomeKey(None)).pack(side=BOTTOM)
                Label(midrightfrm, text='-------------').pack(side=BOTTOM)
                Button(midrightfrm, text='对换位置', width=8,
                       command=lambda: self.chessboard.changeside('rotate')).pack(side=BOTTOM)
                Button(midrightfrm, text='左右对称', width=8,
                       command=lambda: self.chessboard.changeside('symmetry')).pack(side=BOTTOM)       
                Button(midrightfrm, text='对换棋局', width=8,
                       command=lambda: self.chessboard.changeside()).pack(side=BOTTOM)           
                Button(midrightfrm, text='打印棋局', width=8,
                       command=lambda: print(self.board)).pack(side=BOTTOM)           
                midrightfrm.pack(side=RIGHT, expand=YES) #, fill=BOTH
            
            self.listvar = StringVar()
            midfrm = ttk.Frame(self, padding=2)
            create_midleftfrm(midfrm)
            create_midrightfrm(midfrm)
            midfrm.pack(side=TOP, expand=YES, fill=Y) # 顶部区域  
            
        def create_bottomfrm():        
            bottomfrm = LabelFrame(self, relief=GROOVE, text='评注：',
                                    padx=6, pady=6, labelanchor='nw')        
            self.remarktext = Text(bottomfrm, padx=3, pady=3, height=12, width=25, relief=GROOVE) 
            self.remarktext.pack() # side=TOP, expand=YES, fill=BOTH
            bottomfrm.pack(side=BOTTOM) # 底部区域
            
        create_topfrm() # 先打包的最后被裁切
        create_midfrm()
        create_bottomfrm()
        
    def create_layout(self):
        self.pack(side=RIGHT, expand=YES, fill=Y) # BOTH      

    def create_bindings(self):
        self.bind('<Up>', self.onUpKey) 
        self.bind('<Down>', self.onDownKey) 
        self.bind('<Prior>', self.onPgupKey) 
        self.bind('<Next>', self.onPgdnKey) 
        self.bind('<Home>', self.onHomeKey) 
        self.bind('<End>', self.onEndKey) 
        self.walklistbox.bind('<Double-1>', self.onMouseLeftclick) # 用buttom-1不成功！        

    def onUpKey(self, event): 
        self.move_walk(-1)
        
    def onDownKey(self, event): 
        self.move_walk(1)

    def onPgupKey(self, event): 
        self.move_walk(-20)
        
    def onPgdnKey(self, event): 
        self.move_walk(20)

    def onHomeKey(self, event): 
        self.walks.location(Walks.StartNumber)
        
    def onEndKey(self, event): 
        self.walks.location(self.walks.length-1)

    def onMouseLeftclick(self, event):
        # 接收点击信息
        self.focus_set()
        self.move_walk()

    def move_walk(self, inc=0):
        # 移动至某步着法
        selections = self.walklistbox.curselection()
        if selections:
            self.walks.location(int(selections[0]) - 1 + inc)

    def updateview(self):
        # 更新视图
        def __setboutstr():
            boutstr = self.walks.getboutstr(True)
            boutstr.insert(0, '=====开始======')
            self.listvar.set(boutstr)
        
        def __selection():
            no = self.walks.number + 1 
            wklb = self.walklistbox
            wklb.selection_clear(0, wklb.size())
            wklb.selection_set(no)
            wklb.see(no)
        
        def __setremark():
            self.remarktext.delete('1.0', END)
            if not self.walks.isstart:
                self.remarktext.insert('1.0', self.walks.getremark(self.walks.number))

        __setboutstr()
        __selection()
        __setremark()


        