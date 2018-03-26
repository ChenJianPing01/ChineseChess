'''
中国象棋棋谱文件转换类型
'''

import cProfile, os, sys, glob, re
import struct, shutil #, chardet
import xml.etree.ElementTree as ET    
import sqlite3
import base


from walks import MoveNode


global movecount, remlenmax
movecount = 0
remlenmax = 0
 

class ChessFile(object):
    '象棋文件类'
    
    def __init__(self, filename=''):
        self.info = {'Author': '',
                    'Black': '',
                    'BlackTeam': '',
                    'Date': '',
                    'ECCO': '',
                    'Event': '',
                    'FEN': '',
                    'Format': "ICCS",
                    'Game': 'Chinese Chess',
                    'Opening': '',
                    'PlayType': '',
                    'RMKWriter': '',
                    'Red': '',
                    'RedTeam': '',
                    'Result': '',
                    'Round': '',
                    'Site': '',
                    'Title': '',
                    'Variation': '',
                    'Version': ''}
        self.rootmvnode = MoveNode()
        self.readfile(filename)

    def __strstruct(self, size):
        return struct.Struct('{}s'.format(size))
                
    def __readxqf(self, filename):    
        
        def __tostr(bstr):
            return bstr.decode('GBK', errors='ignore').strip()
            '''
            try:  # encoding=GB2312 GB18030 utf-8 GBK
                return bstr.decode('GBK', errors='ignore')
            except:
                coding = chardet.detect(bstr)
                print(coding)
                return bstr.decode(coding['encoding'], errors='ignore')                
            '''
            
        def __subbyte(a, b):
            return (a - b + 1024) % 256
            
        def __readinfo(data):
        
            def __calkey(bKey, cKey):
                return (((((bKey*bKey)*3+9)*3+8)*2+1)*3+8) * cKey % 256 # 保持为<256
                
            piechars = 'RNBAKABNRCCPPPPPrnbakabnrccppppp' # QiziXY设定的棋子顺序 
            #self.Signature = data[:2] # 2字节 文件标记 'XQ' = $5158;
            self.info['Version'] = data[2] # 版本号
            headKeyMask = data[3] # 加密掩码
            #self.ProductId = data[4] # 4字节 产品号(厂商的产品号)
            headKeyOrA = data[5] #
            headKeyOrB = data[6] #
            headKeyOrC = data[7] #
            headKeyOrD = data[8] #
            headKeysSum = data[9] # 加密的钥匙和
            headKeyXY = data[10] # 棋子布局位置钥匙       
            headKeyXYf = data[11] # 棋谱起点钥匙
            headKeyXYt = data[12] # 棋谱终点钥匙
            #// = 16 bytes
            headQiziXY = list(data[13:45]) # 32个棋子的原始位置
            #// 用单字节坐标表示, 将字节变为十进制数, 十位数为X(0-8)个位数为Y(0-9),
            #// 棋盘的左下角为原点(0, 0). 32个棋子的位置从1到32依次为:
            #// 红: 车马相士帅士相马车炮炮兵兵兵兵兵 (位置从右到左, 从下到上)
            #// 黑: 车马象士将士象马车炮炮卒卒卒卒卒 (位置从右到左, 从下到上)        
            #// = 48 bytes
            #self.PlayStepNo = data[45] # 棋谱文件的开始步数
            headWhoPlay = data[46] # 该谁下 0-红先, 1-黑先
            headPlayResult = data[47] # 最终结果 0-未知, 1-红胜 2-黑胜, 3-和棋
            #self.PlayNodes = data[48] # 本棋谱一共记录了多少步
            #self.PTreePos = data[49] # 对弈树在文件中的起始位置
            #self.Reserved1 = data[50:54] # : array [1..4] of dTByte;        
            #// = 64 bytes
            headCodeA = data[54] # 对局类型(开,中,残等)
            #self.CodeB = data[55] # 另外的类型
            #self.CodeC = data[56] #
            #self.CodeD = data[57] #
            #self.CodeE = data[58] #
            #self.CodeF = data[59] #
            #self.CodeH = data[60] #
            #self.CodeG = data[61] #
            #// = 80  bytes
            self.info['Title'] = __tostr(data[62]) # 标题
            #self.TitleB = __tostr(data[63]) #
            #// = 208 bytes
            self.info['Event'] = __tostr(data[64]) # 比赛名称
            self.info['Date'] = __tostr(data[65]) # 比赛时间
            self.info['Site'] = __tostr(data[66]) # 比赛地点
            self.info['Red'] = __tostr(data[67]) # 红方姓名
            self.info['Black'] = __tostr(data[68]) # 黑方姓名
            #// = 336 bytes
            self.info['Opening'] = __tostr(data[69]) # 开局类型
            #self.RedTime = __tostr(data[70]) #
            #self.BlkTime = __tostr(data[71]) #
            #self.Reservedh = __tostr(data[72]) #        
            #// = 464 bytes
            self.info['RMKWriter'] = __tostr(data[73]) # 棋谱评论员
            self.info['Author'] = __tostr(data[74]) # 文件的作者
            
            '''
            if self.Signature != (0x58, 0x51):
                print('文件标记不对。xqfinfo.Signature != (0x58, 0x51)')
            if (headKeysSum + headKeyXY + headKeyXYf + headKeyXYt) % 256 != 0:
                print('检查密码校验和不对，不等于0。')
            if self.info['Version'] > 18: 
                print('这是一个高版本的XQF文件，您需要更高版本的XQStudio来读取这个文件')
            '''            
            if self.info['Version'] <= 10: # 兼容1.0以前的版本
                KeyXY = 0
                KeyXYf = 0
                KeyXYt = 0
                KeyRMKSize = 0
            else:
                KeyXY = __calkey(headKeyXY, headKeyXY)
                KeyXYf = __calkey(headKeyXYf, KeyXY)
                KeyXYt = __calkey(headKeyXYt, KeyXYf)
                KeyRMKSize = ((headKeysSum * 256 + headKeyXY) % 65536 % 32000) + 767
                if self.info['Version'] >= 12: # 棋子位置循环移动
                    for i, xy in enumerate(headQiziXY[:]):
                        headQiziXY[(i + KeyXY + 1) % 32] = xy
                for i in range(32): # 棋子位置解密           
                    headQiziXY[i] = __subbyte(headQiziXY[i], KeyXY)
                    # 保持为8位无符号整数，<256
                    
            KeyBytes = [(headKeysSum & headKeyMask) | headKeyOrA,
                        (headKeyXY & headKeyMask) | headKeyOrB,
                        (headKeyXYf & headKeyMask) | headKeyOrC,
                        (headKeyXYt & headKeyMask) | headKeyOrD]
            F32Keys = [ord(c) & KeyBytes[i % 4]
                        for i, c in enumerate('[(C) Copyright Mr. Dong Shiwei.]')]

            charls = [['_' for _ in range(9)] for row in range(10)]
            for i, xy in enumerate(headQiziXY):
                if xy < 90:
                    charls[xy%10][(8 - xy//10) if i < 16 else xy//10] = piechars[i]
            afen = '/'.join([''.join(chars) for chars in charls[::-1]])
            for _str, nstr in base.linetonums():
                afen = afen.replace(_str, nstr)
            self.info['FEN'] = '{} {} - - 0 0'.format(afen,
                    'b' if headWhoPlay == 1 else 'r')
            
            self.info['PlayType'] = {0: '全局', 1: '开局', 2: '中局', 3: '残局'}[headCodeA]
            self.info['Result'] = {0: '未知', 1: '红胜',
                    2: '黑胜', 3: '和棋'}[headPlayResult]            
            return (KeyXYf, KeyXYt, KeyRMKSize, F32Keys)            

        def __readmove(mvnode):
            '递归添加着法节点'
            
            def __bytetoseat(a, b):
                xy = __subbyte(a, b)
                return (xy % 10, xy // 10)
                    
            def __readbytes(size):
                pos = fileobj.tell()
                bytestr = fileobj.read(size)                
                if self.info['Version'] <= 10:
                    return bytestr 
                else: # '字节串解密'
                    barr = bytearray(len(bytestr))  # 字节数组才能赋值，字节串不能赋值
                    for i, b in enumerate(bytestr):
                        barr[i] = __subbyte(int(b), F32Keys[(pos + i) % 32])
                    return barr
                    
            def __readremarksize():
                bytestr = __readbytes(4)
                return movestruct2.unpack(bytestr)[0] - KeyRMKSize
                
            data = movestruct1.unpack(__readbytes(4))
            # 一步棋的起点和终点有简单的加密计算，读入时需要还原
            mvnode.fseat = __bytetoseat(data[0], 0X18 + KeyXYf) # 一步棋的起点
            mvnode.tseat = __bytetoseat(data[1], 0X20 + KeyXYt) # 一步棋的终点
            ChildTag = data[2]
            
            RemarkSize = 0
            if self.info['Version'] <= 0x0A:
                b = 0
                if (ChildTag & 0xF0) != 0: 
                    b = b | 0x80
                if (ChildTag & 0x0F) != 0: 
                    b = b | 0x40
                ChildTag = b
                RemarkSize = __readremarksize()
            else:
                ChildTag = ChildTag & 0xE0
                if (ChildTag & 0x20) != 0:                        
                    RemarkSize = __readremarksize()
                    
            if RemarkSize > 0: # 如果有注解
                bytestr = __readbytes(RemarkSize)
                mvnode.remark = __tostr(self.__strstruct(RemarkSize).unpack(bytestr)[0])
                    
            if (ChildTag & 0x80) != 0: # 有左子树
                next_ = MoveNode(mvnode)
                mvnode.setnext(next_)
                __readmove(next_)
            if (ChildTag & 0x40) != 0: # 有右子树
                other = MoveNode(mvnode)
                mvnode.setother(other)
                __readmove(other)

        infofmt = '2B2BL8B32BH2B2L4B8H64p64p64p16p16p16p16p64p16p16p32p16p16p528B'
        #206个元素
        infostruct = struct.Struct(infofmt)
        #print('infostruct：', struct.calcsize(infofmt))
        movestruct1 = struct.Struct('4B')
        movestruct2 = struct.Struct('L')
        with open(filename, 'rb') as fileobj:
            self.__init__()
            self.dirname = os.path.splitdrive(os.path.dirname(filename))[1]
            self.filename = os.path.splitext(os.path.basename(filename))[0]
            bytestr = infostruct.unpack(fileobj.read(1024))
            KeyXYf, KeyXYt, KeyRMKSize, F32Keys = __readinfo(bytestr)
            __readmove(self.rootmvnode)
        self.info['Version'] = str(self.info['Version'])
            
    def __readbin(self, filename):
    
        def __readmove(mvnode):
            hasothernextrem, fint, tint = movestruct1.unpack(fileobj.read(3))
            mvnode.setseat_i(fint, tint)
            if hasothernextrem & 0x20:
                rlength = movestruct2.unpack(fileobj.read(2))[0]
                mvnode.remark = fileobj.read(rlength).decode()
            if hasothernextrem & 0x80:
                mvnode.setother(MoveNode())
                __readmove(mvnode.other)
            if hasothernextrem & 0x40:
                mvnode.setnext(MoveNode())
                __readmove(mvnode.next_)
                
        infokstruct = struct.Struct('20B')
        infovfmt = '{}s' * 20
        movestruct1 = struct.Struct('3B')
        movestruct2 = struct.Struct('H')
        with open(filename, 'rb') as fileobj:
            self.__init__()
            self.dirname = os.path.splitdrive(os.path.dirname(filename))[1]
            self.filename = os.path.splitext(os.path.basename(filename))[0]
            infoks = infokstruct.unpack(fileobj.read(20))
            infovstruct = struct.Struct(infovfmt.format(*infoks))
            infovs = infovstruct.unpack(fileobj.read(sum(infoks)))
            for n, key in enumerate(sorted(self.info)):
                self.info[key] = infovs[n].decode()
            __readmove(self.rootmvnode)
        
    def __readpgn(self, filename):
        pass

    def __readxml(self, filename):
            
        def __readelem(elem, i, mvnode):
            mvnode.stepno = int(elem[i].tag[1:]) # 元素名
            if mvnode.stepno > 0:
                mvnode.setseat_s(elem[i].text.strip())
            mvnode.remark = elem[i].tail.strip()
            if len(elem[i]) > 0: # 有子元素(变着)
                mvnode.setother(MoveNode())
                __readelem(elem[i], 0, mvnode.other)
            i += 1
            if len(elem) > i:
                mvnode.setnext(MoveNode())
                __readelem(elem, i, mvnode.next_)
                
        self.dirname = os.path.splitdrive(os.path.dirname(filename))[1]
        self.filename = os.path.splitext(os.path.basename(filename))[0]
        etree = ET.ElementTree(ET.Element('root'), filename)
        rootelem = etree.getroot()
        infoelem = rootelem.find('info')
        for elem in infoelem.getchildren():
            text = elem.text.strip() if elem.text else ''
            self.info[elem.tag] = text
        
        movelem = rootelem.find('moves')
        if len(movelem) > 0:
            __readelem(movelem, 0, self.rootmvnode)
        
    def readfile(self, filename):
        if not (os.path.exists(filename) and os.path.isfile(filename)):
            return
        ext = os.path.splitext(os.path.basename(filename))[1]
        if ext == '.xqf':
            self.__readxqf(filename) 
        elif ext == '.bin':
            self.__readbin(filename)
        elif ext == '.pgn':
            self.__readpgn(filename)
        elif ext == '.xml':
            self.__readxml(filename)
    
    def __saveasbin(self, filename):
    
        def __addmoves(mvnode):
            fint, tint = mvnode.coordint
            rembytes = mvnode.remark.strip().encode()
            hasothernextrem = ((0x80 if mvnode.other else 0) |
                                (0x40 if mvnode.next_ else 0) |
                                (0x20 if rembytes else 0))
            global movecount, remlenmax
            movecount += 1 # 着法步数 
            reslutbytes.extend(movestruct1.pack(hasothernextrem, fint, tint))
            if rembytes:
                remlenmax = max(remlenmax, len(mvnode.remark.strip()))
                
                reslutbytes.extend(movestruct2.pack(len(rembytes)))
                reslutbytes.extend(rembytes)  # rbytes已经是字节串，不需要再pack
            if mvnode.other:
                __addmoves(mvnode.other)
            if mvnode.next_:
                __addmoves(mvnode.next_)
    
        reslutbytes = bytearray()
        infobytes = [value.encode() for key, value in sorted(self.info.items())]
        lenbytes = [len(infob) for infob in infobytes]
        reslutbytes.extend(lenbytes)
        reslutbytes.extend(b''.join(infobytes))
            
        movestruct1 = struct.Struct('3B')
        movestruct2 = struct.Struct('H')
        __addmoves(self.rootmvnode)
        try:
            open(filename, 'wb').write(reslutbytes)
        except:
            print('错误：写入 {} 文件不成功！'.format(filename))

    def __saveaspgn(self, filename):

        def __remarkstr(remark):
            rem = remark.strip()
            global remlenmax
            remlenmax = max(remlenmax, len(rem))
            return '' if not rem else '\n{{{}}}\n '.format(rem)
        
        def __addstrl(mvnode, isother=False):
            prestr = ('({0}. {1}'.format((mvnode.stepno + 1) // 2, 
                    '... ' if mvnode.stepno % 2 == 0 else '')
                    if isother else
                    ('' if mvnode.stepno % 2 == 0 else 
                    '{}. '.format((mvnode.stepno + 1) // 2)))
            mergestr = '{0}{1} {2}'.format(prestr,
                    mvnode.coordstr, __remarkstr(mvnode.remark))
            movestrl.append(mergestr)
            if mvnode.other:
                __addstrl(mvnode.other, True)
                movestrl.append(') ')
                global movecount
                movecount -= 1 # 修正着法步数
                
            if mvnode.next_:
                __addstrl(mvnode.next_)
    
        infostrl = ['[{} "{}"]'.format(name, value)
                for name, value in sorted(self.info.items())]
        movestrl = []
        __addstrl(self.rootmvnode)
        global movecount
        movecount += len(movestrl) # 计算着法步数
        
        data = '{}\n{}'.format('\n'.join(infostrl), ''.join(movestrl))
        try:
            open(filename, 'w', encoding='utf-8').write(data)
        except:
            print('错误：写入 {} 文件不成功！'.format(filename))
        
    def __saveasxml(self, filename):
            
        def __createlem(name, value='', remark=''):
            reselem = ET.Element(name) # 元素名
            reselem.text = value
            reselem.tail = remark
            return reselem
            
        def __addelem(elem, mvnode):    
            thissub = __createlem('m{0:02d}'.format(mvnode.stepno),
                    mvnode.coordstr, mvnode.remark.strip())
            global movecount, remlenmax
            movecount += 1  # 计算着法步数
            remlenmax = max(remlenmax, len(mvnode.remark.strip()))
            
            if mvnode.other: # 有变着
                __addelem(thissub, mvnode.other)                
            elem.append(thissub)
            if mvnode.next_:
                __addelem(elem, mvnode.next_)     
        
        rootelem = ET.Element('root')
        infoelem = __createlem('info')
        for name, value in sorted(self.info.items()):
            infoelem.append(__createlem(name, value))
        rootelem.append(infoelem)
        
        movelem = __createlem('moves', '', '')
        __addelem(movelem, self.rootmvnode)
        rootelem.append(movelem)
        base.xmlindent(rootelem)  # 美化
        ET.ElementTree(rootelem).write(filename, encoding='utf-8')
        
    def writefile(self, filename, ext='.bin'):
        if ext == '.bin':
            self.__saveasbin(filename)
        elif ext == '.pgn':
            self.__saveaspgn(filename)
        elif ext == '.xml':
            self.__saveasxml(filename)        
    
    def trandir(self, text, dirfrom, dirto='.\\'):
        fcount = dcount = 0
        if not os.path.exists(dirto):
            os.mkdir(dirto)
        for subname in os.listdir(dirfrom):
            subname = os.path.normcase(subname)
            pathfrom = os.path.join(dirfrom, subname)          
            pathto = os.path.join(dirto, subname)
            if os.path.isfile(pathfrom): # 文件
                extension = os.path.splitext(os.path.basename(pathfrom))[1]
                if extension in ('.xqf', '.bin', '.pgn', '.xml'):
                    self.readfile(pathfrom)
                    self.writefile(os.path.join(dirto, 
                            os.path.splitext(os.path.basename(pathfrom))[0] + text), text)
                    fcount += 1
                elif extension == '.txt':
                    data = open(pathfrom).read()
                    open(pathto, 'w').write(data)
                    fcount += 1
            else:
                below = self.trandir(text, pathfrom, pathto)
                fcount += below[0]
                dcount += below[1]
                dcount += 1
        return (fcount, dcount)
        
    def tranxqftodb(self, dirnamefrom, dirto='.\\'):

        def __addinfomove():
        
            def __addmove(mvnode, preid):
                self.moves.append((None, self.manid, preid, mvnode.stepno,
                            mvnode.coordstr, mvnode.remark))
                self.lastmovid += 1
                mvnode.movid = self.lastmovid # 重要!保存当前move的id
                if mvnode.other:
                    __addmove(mvnode.other, preid)
                if mvnode.next_:
                    __addmove(mvnode.next_, mvnode.movid)
                    
            info = ([None, self.dirname, self.filename, self.rootmvnode.remark] + 
                    [value for key, value in sorted(self.info.items())])
            self.infos.append(info)
            self.manid += 1            
            __addmove(self.rootmvnode, 0)
            
        def __getinfomove(dirfrom):
            fcount = dcount = 0        
            for subname in os.listdir(dirfrom):
                subname = os.path.normcase(subname)
                pathfrom = os.path.join(dirfrom, subname)
                if os.path.isfile(pathfrom):
                    extension = os.path.splitext(os.path.basename(pathfrom))[1]
                    if extension == '.xqf':
                        self.__readxqf(pathfrom)
                        __addinfomove()
                        fcount += 1
                    elif extension == '.txt':
                        content = open(pathfrom).read()
                        cur.execute(base.insertmanual,
                                (None, os.path.splitdrive(dirfrom)[1], subname, content))
                        fcount += 1
                else:
                    below = __getinfomove(pathfrom)
                    fcount += below[0]
                    dcount += below[1]
                    dcount += 1
            return (fcount, dcount)

        #if not os.path.exists(dirto):
        #    os.mkdir(dirto)
        dbname = dirto + '\\chessmanual.db'
        #if os.path.exists(dbname):
        #    os.remove(dbname)
        con = sqlite3.connect(dbname)
        con.execute('PRAGMA synchronous = OFF')
        cur = con.cursor()
        cur.executescript(base.initdbsql) # 执行sql脚本，多个sql语句
        
        cur.execute(base.getlastmanid)
        res = cur.fetchone()
        self.manid = 0 if res is None else res[0]
        cur.execute(base.getlastmovid)
        res = cur.fetchone()
        self.lastmovid = 0 if res is None else res[0]
        
        self.infos = []
        self.moves = []
        fcount, dcount = __getinfomove(dirnamefrom)
        con.execute('BEGIN;')
        cur.executemany(base.insertinfo, self.infos)
        cur.executemany(base.insertmove, self.moves)
        
        cur.close()
        con.commit()
        con.close()
        return (fcount, dcount)   
   

def testtransdir(num, fext, text):

    dirfrom = ['C:\\360Downloads\\棋谱文件\\示例文件',
                'C:\\360Downloads\\棋谱文件\\象棋杀着大全',
                'C:\\360Downloads\\棋谱文件\\疑难文件',
                'C:\\360Downloads\\棋谱文件\\中国象棋棋谱大全'
                ]                
    xqfile = ChessFile()
    for i in range(num):
        if text == '.db':
            fc, dc = xqfile.tranxqftodb(dirfrom[i], dirto='C:\\360Downloads\\棋谱文件')
        else:
            fc, dc = xqfile.trandir(text, dirfrom[i]+fext, dirfrom[i]+text)
        print('{}： {}个文件，{}个目录'.format(dirfrom[i], fc, dc))
    global movecount, remlenmax
    print('movecount:', movecount, 'remlenmax:', remlenmax) # 计算着法步数 
            
if __name__ == '__main__':

    import time
    start = time.time()
    
    #cProfile.run('trandir(2)')
    #testtransdir(2, '.xqf', '.bin')
    #testtransdir(2, '.xqf', '.pgn')
    #testtransdir(2, '.xqf', '.xml')
    #testtransdir(2, '.bin', '.pgn')
    #testtransdir(2, '.bin', '.xml')
    #testtransdir(2, '.xml', '.bin')
    testtransdir(2, '.xml', '.pgn')
    #testtransdir(2, '.pgn', '.bin')
    #testtransdir(2, '.pgn', '.xml')
    #testtransdir(2, '.xqf', '.db') # 第3级目录生产文件超过1G，不具备可操作性.
    
    #cProfile.run("testtransdir(2, '.xqf', '.xml')")
    
    end = time.time()
    print('usetime: %0.3fs' % (end - start))    
    
    #shutil.rmtree('C:\\中国象棋棋谱大全')
    pass
    
#