﻿'''
中国象棋棋谱类型
'''
from walk import *


class ChessBoard(Model):
    # 棋局类（含一副棋盘、棋子、棋谱）
    
    FEN = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1'
    # 新棋局 
     
    def __init__(self, pgn=''):
        super().__init__()
        self.board = Board()
        self.walks = Walks()
        self.info = {}  # 信息: pgn标签...
        self.remark = ''
        self.setpgn(pgn)
        
    def __str__(self):
        # 棋盘字符串函数
        return '{}\n{}'.format(str(self.board), str(self.walks))

    def __repr__(self):
        pass    
        
    def getfen(self):
        # 将一个棋盘局面写入FEN格式串
        def __linetonums():
            # 下划线字符串对应数字字符元组 列表
            return [('_' * i, str(i)) for i in range(9, 0, -1)]
    
        piecechars = [piece.char for rc, piece in sorted(self.board.crosses.items())]
        chars = [piecechars[rowno * NumCols: (rowno + 1) * NumCols]
                    for rowno in range(NumRows)]
        afen = '/'.join([''.join(char) for char in chars[::-1]])
        for _str, nstr in __linetonums():
            afen = afen.replace(_str, nstr)
        sidechar = 'b' if self.walks.currentside == BLACK_SIDE else 'r'
        return '{} {} {} {} {} {}'.format(afen, sidechar, '-', '-', '0', '0')

    def setfen(self, fen):                
        afens = fen.split()
        self.walks.setcurrentside(BLACK_SIDE
                if (len(afens) > 1 and afens[1] == 'b') else RED_SIDE) 
        self.board.loadpieces(fen)
        
    def getpgn(self):
        # 将一个棋局着棋过程，写入pgn字符串
        offset = self.walks.cursor + 1        
        self.walks.move(-offset)
        
        strinfo = '\n'.join(['[{} "{}"]'.format(key, self.info[key])
                    for key in self.info])
        sfen, gfen = self.info.get('FEN'), self.getfen()
        if sfen:
            assert sfen.split()[0] == gfen.split()[0], '\n棋谱FEN：%s, \n生成FEN: %s' % (sfen.split()[0], gfen.split()[0])                        
        self.info['FEN'] = gfen
        
        self.walks.move(offset)
        return '{}\n{}\n{}\n'.format(strinfo, self.remark, str(self.walks))      
        
    def setpgn(self, pgn=''):
        # 将一个pgn棋局文件载入棋局
        
        def __getinfo():
            self.info = {}
            infolist = re.findall('\[(\w+) "(.*)"\]', pgn)
            for key, value in infolist:
                self.info[key] = value  # 棋局信息（pgn标签）                
            remark = re.findall('\]\s+(\{[\s\S]*\})?\s+1\. ', pgn)
            if remark:
                self.remark = remark[0]  # 棋谱评注                
            result = re.findall('\s(1-0|0-1|1/2-1/2|\*)\s?', pgn)
            if result:
                self.info['Result'] = result[0]    # 棋局结果
        
        def __createwalks():        
            #s = '(\d+)\. (\S{4})\s+(\{.*\})?\s*(\S{4})?\s+(\{.*\})?'
            s = '(\d+)\.\s+(\S{4})\s+(\{.*\})?\s*(\S{4})?\s*(\{.*\})?'
            description_remarks = re.findall(s, pgn)  # 走棋信息, 字符串元组
                
            descriptiones, remarks = [], []
            for n, des1, remark1, des2, remark2 in description_remarks:
                descriptiones.extend([des1, des2])
                remarks.extend([remark1, remark2])
                
            for n, des in enumerate(descriptiones):
                if des:
                    (fromseat, toseat) = self.board.chinese_moveseats(
                            self.walks.currentside, des)
                    self.walks.append(self.createwalk(fromseat, toseat, remarks[n]))
                    self.walks.move(1)
            self.walks.move(-self.walks.length)
        
        __getinfo()
        self.setfen(self.info.get('FEN', self.FEN))
        self.walks.clear()
        if pgn:
            __createwalks()        
        if hasattr(self, 'views'):
            self.notifyviews()
    
    def createwalk(self, fromseat, toseat, remark=''):
        # 生成一步着法命令
        '''
        canmoveseats = self.board.canmoveseats(self.board.getpiece(fromseat))
        assert toseat in canmoveseats, ('该走法不符合规则，或者可能自己被将军、将帅会面！\nfrom: {}\nto: {}\ncanmove: {}\n{}'.format(fromseat, toseat, sorted(canmoveseats), self.board))
        '''        
        
        def go():
            back.eatpiece = self.board.movepiece(fromseat, toseat)
            # 给函数back添加一个属性:被吃棋子!
            self.walks.transcurrentside()
            
        def back():
            self.board.movepiece(toseat, fromseat, back.eatpiece)
            self.walks.transcurrentside()
            
        description = self.board.moveseats_chinese(fromseat, toseat)
        return Walk(go, back, fromseat, toseat, remark, description)
            
    def changeside(self, changetype='exchange'):
    
        def __crosses_moveseats(changetype):        
            if changetype == 'exchange':
                self.walks.currentside = Piece.otherside(self.walks.currentside)
                return ({piece.seat: self.board.pieces.getothersidepiece(piece)
                                for piece in self.board.getlivepieces()},
                                self.walks.moveseats())
            else:
                if changetype == 'rotate':
                    transfun = CrossT.getrotateseat
                elif changetype == 'symmetry':
                    transfun = CrossT.getsymmetryseat
                return ({transfun(piece.seat): piece
                        for piece in self.board.getlivepieces()},
                        [(transfun(fromseat), transfun(toseat))
                        for fromseat, toseat in self.walks.moveseats()])
            
        offset = self.walks.cursor + 1 
        remarkes = self.walks.remarkes  # 备注里如有棋子走法，则未作更改？        
        self.walks.move(-self.walks.length)
        
        crosses, moveseats = __crosses_moveseats(changetype)        
        self.board.loadcrosses(crosses)
        
        self.walks.clear()
        for n, (fromseat, toseat) in enumerate(moveseats):        
            self.walks.append(self.createwalk(fromseat, toseat, remarkes[n])) 
            self.walks.move(1)
        self.walks.move(offset-self.walks.length)
        
        self.notifyviews()
        
#        