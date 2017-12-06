﻿'''
中国象棋棋盘类型
'''

from piece import *


class Board(Model):
    # 棋盘类
    
    def __init__(self):
        super().__init__()
        self.__crosses = dict.fromkeys(all_rowcols, BlankPie)
        self.__pieces = Pieces()
        self.bottomside = BLACK_SIDE
        
    def __str__(self):
        blankboard = '''
            ┏━┯━┯━┯━┯━┯━┯━┯━┓
            ┃　│　│　│╲│╱│　│　│　┃
            ┠─┼─┼─┼─╳─┼─┼─┼─┨
            ┃　│　│　│╱│╲│　│　│　┃
            ┠─╬─┼─┼─┼─┼─┼─╬─┨
            ┃　│　│　│　│　│　│　│　┃
            ┠─┼─╬─┼─╬─┼─╬─┼─┨
            ┃　│　│　│　│　│　│　│　┃
            ┠─┴─┴─┴─┴─┴─┴─┴─┨
            ┃　　　　　　　　　　　　　　　┃
            ┠─┬─┬─┬─┬─┬─┬─┬─┨
            ┃　│　│　│　│　│　│　│　┃
            ┠─┼─╬─┼─╬─┼─╬─┼─┨
            ┃　│　│　│　│　│　│　│　┃
            ┠─╬─┼─┼─┼─┼─┼─╬─┨
            ┃　│　│　│╲│╱│　│　│　┃
            ┠─┼─┼─┼─╳─┼─┼─┼─┨
            ┃　│　│　│╱│╲│　│　│　┃
            ┗━┷━┷━┷━┷━┷━┷━┷━┛
        '''
        # 边框粗线
        
        def __getname(piece):
            rookcannonpawn_name = {'车': '車', '马': '馬', '炮': '砲'}
            name = piece.name
            return (rookcannonpawn_name.get(name, name)
                    if piece.side == BLACK_SIDE else name)
        
        def __fillingname():
            linestr = [list(line.strip()) for line in blankboard.strip().splitlines()]
            for (row, col), piece in self.getlivecrosses().items():
                linestr[(MaxRowNo_T - row) * 2][col * 2] = __getname(piece)
            return [''.join(line) for line in linestr]

        frontstr = '\n　　　　'
        return '{}{}{}'.format(frontstr, frontstr.join(__fillingname()), '\n')
    
    @property
    def pieces(self):
        return self.__pieces
    
    @property
    def crosses(self):
        return self.__crosses
    
    def getboardside(self, side):
        return BOTTOM_SIDE if self.bottomside == side else TOP_SIDE
    
    def setbottomside(self):
        self.bottomside = (RED_SIDE if self.getkingrowcol(RED_SIDE)[0] < 4 else BLACK_SIDE)
    
    def isbottomside(self, side):
        return BOTTOM_SIDE == self.getboardside(side)
    
    def isblank(self, rowcol):
        return self.__crosses[rowcol] is BlankPie
              
    def getpiece(self, rowcol):
        return self.__crosses[rowcol]
    
    def getside(self, rowcol):
        return self.getpiece(rowcol).side
    
    def getrowcol(self, piece):
        for rowcol, pie in self.getlivecrosses().items():
            if pie is piece:
                return rowcol
        #assert False, '没有发现棋子：{}'.format(str(self))
    
    def getkingrowcol(self, side):    
        return self.getrowcol(self.__pieces.getkingpiece(side))
    
    def setpiece(self, rowcol, piece):
        self.__crosses[rowcol] = piece

    def movepiece(self, fromrowcol, torowcol, backpiece=BlankPie):
        eatpiece = self.__crosses[torowcol]
        self.setpiece(torowcol, self.__crosses[fromrowcol])
        self.setpiece(fromrowcol, backpiece)
        return eatpiece
    
    def setpieces(self, charls):
        [self.setpiece(rowcol, BlankPie) for rowcol in self.__crosses.keys()]
        for n, char in enumerate(charls):
            self.setpiece(CrossTrans.getrowcol(n),
                self.__pieces.getpiece(char, self))
        self.setbottomside()
            
    def getlivecrosses(self):
        return {rowcol: piece for rowcol, piece in self.__crosses.items()
                if piece is not BlankPie}
    
    def geteatedpieces(self):
        return set(self.__pieces.pieces) - set(self.getlivecrosses().values())
    
    def getlivesidecrosses(self, side):
        return {rowcol: piece for rowcol, piece in self.getlivecrosses().items()
                if piece.side == side}
    
    def getlivesidenamecrosses(self, side, name):
        return {rowcol: piece for rowcol, piece in self.getlivesidecrosses(side).items()
                if piece.name == name}
                
    def getlivesidenamecolcrosses(self, side, name, col):
        return {rowcol: piece for rowcol, piece in
                self.getlivesidenamecrosses(side, name).items() if rowcol[1] == col}
                
    def canmovepiece(self, rowcol, piece):
        return self.getpiece(rowcol).side != piece.side
        
    def iskilled(self, side):
        def __isfaced():
            if kingcol != othercol:
                return False
            step = 1 if kingrow < otherrow else -1
            return all([self.isblank((row, kingcol))
                    for row in range(kingrow + step, otherrow, step)])
                    
        def __iskilled():
            for rowcol, piece in self.getlivesidecrosses(otherside).items():
                if (piece.isStronge() and (kingrow, kingcol)
                    in piece.getmoverowcols(rowcol, self)):
                    return True
            return False 
            
        otherside = CrossTrans.getotherside(side)
        kingrow, kingcol = self.getkingrowcol(side)
        otherrow, othercol = self.getkingrowcol(otherside)
        return __isfaced() or __iskilled()
        
    def isdied(self, side):
        for rowcol, piece in self.getlivesidecrosses(side).items():
            if bool(self.canmoverowcols(rowcol)):
                return False # 有子可走，避免被将
        return True

    def canmoverowcols(self, fromrowcol):
        # 获取棋子可走的位置, 不能被将军
        result = []
        piece = self.getpiece(fromrowcol)
        side = piece.side
        #print(sorted(piece.getmoverowcols(fromrowcol, self)))
        for torowcol in piece.getmoverowcols(fromrowcol, self):            
            topiece = self.movepiece(fromrowcol, torowcol)            
            if not self.iskilled(side): 
                result.append(torowcol)                 
            self.movepiece(torowcol, fromrowcol, topiece)
        return result
        
    def loadpieces(self, fen):
        # 将一个FEN格式串载入棋盘局面
        def __numtolines():
            # 数字字符: 下划线字符串           
            numtolines = {}
            for i in range(1, 10):
                numtolines[str(i)] = '_' * i
            return numtolines
            
        def __isvalid(charls):
            # 判断棋子列表是否有效
            if len(charls) != 90:
                return False, '棋局的位置个数不等于90，有误！'
            chars = [c for c in charls if c != BlankChar]
            if len(chars) > 32:
                return False, '全部的棋子个数大于32个，有误！'
            for c in chars:
                if chars.count(c) > Chars.count(c):
                    return False, '棋子: %s 的个数大于规定个数，有误！' % c
            return True, ''           
        
        afens = fen.split()
        fenstr = ''.join(afens[0].split('/')[::-1])
        charls = list(multrepl(fenstr, __numtolines()))
        
        assert __isvalid(charls)[0], __isvalid(charls)[1]
        
        self.setpieces(charls) 

        
        