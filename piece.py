﻿'''
中国象棋棋子类型 by-cjp
'''

from crossbase import *


BlankChar = '_' 
CharToNames = {'K':'帅', 'A':'仕', 'B':'相', 'N':'马',
               'R':'车', 'C':'炮', 'P':'兵', 
               'k':'将', 'a':'士', 'b':'象', 'n':'马',
               'r':'车', 'c':'炮', 'p':'卒', BlankChar: ''}
# 全部棋子ch值与中文名称映射字典
PawnNames = {'兵', '卒'}
AdvisorBishopNames = {'仕', '相', '士', '象'}
StrongePieceNames = {'车', '马', '炮', '兵', '卒'}
LineMovePieceNames = {'帅', '将', '车', '炮', '兵', '卒'}


class Piece(object):
    # 棋子类
    def __init__(self, char):
        self.__side = (None if char == BlankChar
                    else (BLACK_SIDE if char.islower() else RED_SIDE))
        self.__char = char
        
    def __str__(self):
        return self.name
        
    @property
    def side(self):
        #return BLACK_SIDE if self.__char.islower() else RED_SIDE
        return self.__side
        
    @property
    def char(self):
        return self.__char
     
    @property
    def name(self):
        return CharToNames[self.__char]
        
    @property
    def isStronge(self):
        return self.name in StrongePieceNames        
        
    @classmethod
    def getotherside(cls, side):        
        return RED_SIDE if side == BLACK_SIDE else BLACK_SIDE
        
    def getallseats(self,  board):  
        # 全部活动范围集合(默认：车马炮的活动范围)
        return Cross.allseats
    
    def getmoveseats(self, seat, board):
        # 当前棋子所处位置的有效活动范围集合
        return {}
        

class King(Piece):

    def getallseats(self,  board):  
        return Cross.kingseats[board.getboardside(self.side)]
        
    def getmoveseats(self, seat, board):
        return Cross.getkingmoveseats(seat, self, board)
        
        
class Advisor(Piece):
    
    def getallseats(self,  board):  
        return Cross.advisorseats[board.getboardside(self.side)]
        
    def getmoveseats(self, seat, board):
        return Cross.getadvisormoveseats(seat, self, board)        
        
        
class Bishop(Piece):

    def getallseats(self,  board):  
        return Cross.bishopseats[board.getboardside(self.side)]
        
    def getmoveseats(self, seat, board):
        return Cross.getbishopmoveseats(seat, self, board)
                
        
class Knight(Piece):
        
    def getmoveseats(self, seat, board):
        return Cross.getknightmoveseats(seat, self, board)

                
class Rook(Piece):
        
    def getmoveseats(self, seat, board):
        return Cross.getrookmoveseats(seat, self, board)

        
class Cannon(Piece):
        
    def getmoveseats(self, seat, board):
        return Cross.getcannonmoveseats(seat, self, board)
 
        
class Pawn(Piece):
    
    def getallseats(self,  board):  
        return Cross.pawnseats[board.getboardside(self.side)]
        
    def getmoveseats(self, seat, board):
        return Cross.getpawnmoveseats(seat, self, board)
              
        
class Pieces(object):
    # 一副棋子类
    Chars = ['K', 'A', 'A', 'B', 'B', 'N', 'N', 'R', 'R', 
                'C', 'C', 'P', 'P', 'P', 'P', 'P',
            'k', 'a', 'a', 'b', 'b', 'n', 'n', 'r', 'r',
                'c', 'c', 'p', 'p', 'p', 'p', 'p']
    # 全部棋子ch值列表
    CharPieces = {'K': King, 'A': Advisor, 'B': Bishop, 'N': Knight,
                    'R': Rook, 'C': Cannon, 'P': Pawn}
    # 棋子类字典
    
    def __init__(self):    
        self.__pieces = [self.CharPieces[char.upper()](char) for char in self.Chars]
        
    def __str__(self):
        return str([str(piece) for piece in self.__pieces])
        
    def getpiece(self, char, board):
        if char == BlankChar:
            return BlankPie
        charpieces = list({piece for piece in self.__pieces if piece.char == char}
                        - set(board.getlivecrosses().values()))
        return charpieces[0]
        #assert False, '找不到空闲的棋子: ' + char        

    def getkingpiece(self, side):
        return self.__pieces[0 if side == RED_SIDE else 16]
        
    def getothersidepiece(self, piece):
        n = self.__pieces.index(piece)
        return self.__pieces[(n + 16) if n < 16 else (n - 16)]        
        
    def geteatedpieces(self, livepieces):
        return set(self.__pieces) - set(livepieces)
    
    def setpieimgids(self, imgids):
        for n, piece in enumerate(self.__pieces):
            piece.imgid = imgids[n]
            
        
BlankPie = Piece(BlankChar)

 