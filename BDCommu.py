#-*- coding:utf-8 -*-
#*   Copyright (C) 2020 WYN. All rights reserved.
#*   文件名称：BDCommu.py
#*   创 建 者：WangYinan
#*   创建日期：2020年09月14日

import serial
#import zlib

def xorVerify(BytesList):
    '''
    输入为bytes字节流，输出为字符串（16进制）
    '''
    for i in range(len(BytesList)):
        if i:
            t ^= BytesList[i]
        else:
            t  = BytesList[i]^0
    # t为整数，需要转换为16进制字符串
    hexstr=str(hex(t)).split('x')[-1] 
               
    if len(hexstr) == 1:
        hexstr='0'+hexstr
    else:
        hexstr=hexstr.upper()
    return hexstr

def genBytes4Serial(inputdata,bdID=None):
    '''
    data = genBytes4Serial('test')
    ser.write(data)
    '''

    if bdID is None:
        bdID='0316498'
    else:
        bdID=bdID
    if type(inputdata) is list:
        temp = [str(ida) for ida in inputdata]
        inputdata = ' '.join(temp)
    hexstr_input = bytes(inputdata,'gbk').hex()
    # 尝试对数据内容先压缩
    #hexstr_input = zlib.compress(hexstr_input)
    # sendStr需要计算校验码
    sendStr = "CCTXA,"+bdID+",1,2,A4"+hexstr_input
    bytessendStr = bytes(sendStr,'gbk')
    #计算校验码
    verifyCode   = xorVerify(bytessendStr)
    code2Ser  = "$"+sendStr+"*"+verifyCode.upper()+'\r\n'
    code2SerBytes = bytes(code2Ser,'gbk')
    return code2SerBytes



