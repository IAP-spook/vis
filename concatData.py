#-*- coding:utf-8 -*-
#*   Copyright (C) 2020 WYN. All rights reserved.
#*   文件名称：concatData.py
#*   创 建 者：WangYinan
#*   创建日期：2020年09月14日

import os
import pandas as pd
import numpy as np
import datetime



def getExtinctionData(fileDir,timeInterval=None,averTime=None):
    if timeInterval is None:
        timeInterval=60
    else:
        timeInterval=timeInterval
    if averTime is None:
        averTime = '30s'
    else:
        averTime = averTime
    data=os.popen("tail -"+str(timeInterval)+" "+fileDir).read()
    datalst = data.split('\n')
    # 数据列表最后一行为空去掉
    # 如果数据记录不完整，或者为空就忽略，采用完整数据进行平均
    bscdata = []
    timedata = []
    for da in datalst:
        datemp = da.split(' ')
        if len(da)==59:
            bscdata.append(int(datemp[3]))
            timedata.append(pd.to_datetime(datemp[1]+datemp[2]))
    # 将能见度转为相关系数，sigma=-np.log(0.05)/bsc*1000,单位：km-1
    sigdata = [-np.log(0.05)/b*1000 for b in bscdata]
    # 创建DataFrame
    dataFrame = pd.DataFrame({'Time':timedata,'Extinction':sigdata})
    dataFrame.index=dataFrame['Time']
    # 对数据进行平均
    resampleData = dataFrame.resample(averTime).mean() 
    # 保证数据个数，避免出现大于时间间隔的数值
    averTime = int(averTime.split('s')[0])
    dataNum = int(timeInterval/averTime)
    # 返回数据为np.array
    result = resampleData[-dataNum::].values
    return result


def getTPHData(fileDir,timeInterval=None,averTime=None):
    if timeInterval is None:
        timeInterval=60
    else:
        timeInterval=timeInterval
    if averTime is None:
        averTime = '30s'
   #aa 为gps，bb,cc,dd是探空数据，先把timeInterval内数据合并
    dataAll = os.popen("tail -"+str(timeInterval)+" "+fileDir).read()
    datalst=dataAll.split('\n')
    dataall = ''.join(datalst)
    # 分别提取各个数据放入列表中，有可能数据长度不一致
    aa=[]
    bb=[]
    cc=[]
    dd=[]
    rawdata_len=len(dataall)
    countIndex  = 0
    while countIndex<rawdata_len:
        char_str = dataall[countIndex]
        if char_str=='a':
            # aa 后面有52个字符为数据，去掉a还有51个,算入aa为54个
            aa.append(dataall[countIndex:countIndex+54])
            countIndex = countIndex+53
        elif char_str =='b':
            bb.append(dataall[countIndex:countIndex+36])
            countIndex = countIndex+35
        elif char_str == 'c':
            cc.append(dataall[countIndex:countIndex+36])
            countIndex = countIndex+35
        elif char_str == 'd':
            dd.append(dataall[countIndex:countIndex+36])
            countIndex = countIndex+35
        countIndex += 1
    #提取需要的数据，整合进DataFrame
    # aa 提取时间，经纬度，高度，风向，风速 
    lat = []
    lon = []
    timedata = []
    height = []
    windSpeed = []
    windDirec = []
    dateStr = datetime.datetime.now().strftime("%Y%m%d")
    for a in aa:
        if len(a) == 54:
            timedata.append(pd.to_datetime(dateStr+a[2:8]))
            temp_lon = a[8:18]
            if temp_lon[0]=='0':
                lon.append(int(temp_lon)/100000.0)
            else:
                lon.append(-int(temp_lon[1::])/100000.0)
            temp_lat = a[18:28]
            if temp_lat[0]=='0':
                lat.append(int(temp_lat)/100000.0)
            else:
                lat.append(-int(temp_lat[1::])/100000.0)
            height.append(int(a[28:36])/10.0)
            windDirec.append(int(a[36:40])-180)
            windSpeed.append(int(a[40:44])/10.0)
    aDataFrame = pd.DataFrame({'Time':timedata,'Lon':lon,'Lat':lat,'H':height,'WindDir':windDirec,'WindSpeed':windSpeed})
    btemper = []
    bpress  = []
    bhumity = []
    for b in bb:
        if len(b) == 36:
            temp_temp = b[8:14]
            if temp_temp[0]=='0':
                btemper.append(int(temp_temp)/100.0)
            else:
                btemper.append(-int(temp_temp[1::])/100.0)
            # 气压单位为hPa
            bpress.append(int(b[14:20])/100.0)
            # 湿度单位为%
            bhumity.append(int(b[26:30])/10.0)
    bDataFrame=pd.DataFrame({'Temp':btemper,'Press':bpress,'Humi':bhumity})
    ctemper = []
    cpress  = []
    chumity = []
    for c in cc:
        if len(c) == 36:
            temp_temp = c[8:14]
            if temp_temp[0]=='0':
                ctemper.append(int(temp_temp)/100.0)
            else:
                ctemper.append(-int(temp_temp[1::])/100.0)
            # 气压单位为hPa
            cpress.append(int(c[14:20])/100.0)
            # 湿度单位为%
            chumity.append(int(c[26:30])/10.0)
    cDataFrame=pd.DataFrame({'Temp':ctemper,'Press':cpress,'Humi':chumity})

    dtemper = []
    dpress  = []
    dhumity = []
    for d in dd:
        if len(d) == 36:
            temp_temp = d[8:14]
            if temp_temp[0]=='0':
                dtemper.append(int(temp_temp)/100.0)
            else:
                dtemper.append(-int(temp_temp[1::])/100.0)
            # 气压单位为hPa
            dpress.append(int(d[14:20])/100.0)
            # 湿度单位为%
            dhumity.append(int(d[26:30])/10.0)

    dDataFrame=pd.DataFrame({'Temp':dtemper,'Press':dpress,'Humi':dhumity})
    # 数据拼接（暂时）

    aDataFrame.index=aDataFrame['Time']
    bDataFrame.index=aDataFrame.index[0:len(bDataFrame)]
    cDataFrame.index=aDataFrame.index[0:len(cDataFrame)]
    dDataFrame.index=aDataFrame.index[0:len(dDataFrame)]
    a=aDataFrame.resample(averTime).mean()
    b=bDataFrame.resample(averTime).mean()
    c=cDataFrame.resample(averTime).mean()
    d=dDataFrame.resample(averTime).mean()
    # 保证数据个数，避免出现大于时间间隔的数值
    averTime = int(averTime.split('s')[0])
    dataNum = int(timeInterval/averTime)
    result_a = a[-dataNum::].values
    result_b = b[-dataNum::].values
    result_c = c[-dataNum::].values
    result_d = d[-dataNum::].values
    # 最后生成若干时间间隔数据列表，如有2组：[[lon,lat,height,winddir,windspeed,temp,press,humi],[]]
    mean_bcd = (result_d+result_b+result_c)/3.0
    # 组合数据
    result_arr = np.hstack([result_a,mean_bcd])
    return result_arr

