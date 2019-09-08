#Author: Johnson Chan
#Date: 2018/2/28
'''
    功能：用于下载对应设备的日志和数据库
    modify：     20180301    1.0版本
                可以成功解析配置文件，下载对应目录下的文件到本地对应目录
                当前只支持Tvm设备
                20180312
                修复FTP连接异常时奔溃

'''
#!/usr/bin/python
# -*- conding: utf-8 -*-

import os
from xml.dom.minidom import parse
import xml.dom.minidom
import time

import PubulicFunc


'''open xml file'''
if os.path.exists('./StationsInfo.xml'):
    DOMtree1 = xml.dom.minidom.parse("StationsInfo.xml")
else:
    print("缺少StationsInfo1.xml文件，无法工作")
    print("输入q退出")
    while (True):
        ch = input()
        if ch != 'q':
            print("输入q退出")
        else:
            exit()

if os.path.exists('./StationsInfo.xml'):
    DOMtree2 = xml.dom.minidom.parse("DownLoadInfo.xml")
else:
    print("缺少DownLoadInfo.xml文件，无法工作")
    print("输入q退出")
    while (True):
        ch = input()
        if ch != 'q':
            print("输入q退出")
        else:
            exit()

'''站点信息 root'''
stationsinfo = DOMtree1.documentElement

'''所有站点list'''
stations = stationsinfo.getElementsByTagName("station")

'''需要下载的信息'''
stations_download = DOMtree2.documentElement.getElementsByTagName("devices")


'''站点字典'''
stationslist = {}
'''对应站点的Tvm字典'''
tvmlist = {}

'''下载信息字典  ['ip' = ['date','date','date']]'''
stations_download_list = {}
ip_to_download_path_list = {}

'''遍历'''
for station in stations:
    name = station.getAttribute("name")
    # print("站点 = ", station.getAttribute("name"))
    tvms = station.getElementsByTagName("tvm")
    for tvm in tvms:
        # print(" Tvm", tvm.getAttribute("no"), ",IP=", tvm.getAttribute("ip"))
        Key = name + "Tvm" + tvm.getAttribute("id")
        tvmlist[Key] = tvm.getAttribute("ip")
    stationslist[station.getAttribute("name")] = tvmlist

'''文件夹创建'''
currentDate = time.strftime("%Y%m%d")
currentPath = './' + currentDate + '日志下载'
pathlen = len(currentPath)
cnt = 1
while(True):
    if not os.path.exists(currentPath):
        os.mkdir(currentPath)
        break
    else:
        if 1 == cnt:
            currentPath = currentPath[:pathlen] + str(cnt)
            cnt += 1
        else:
            currentPath = currentPath[:pathlen] + str(cnt)
            cnt += 1


stationPath = {}
DevicePath = {}

''' 
20180301日志下载
    实验室
        Tvm1
            20180224
            20180225
            sledb.db
    贵阳北
        Tvm1
            20180224
            sledb.db
        Tvm2
            20180222
            sledb.db
'''



'''解析需要下载的设备和日期'''
for station in stations_download:
    stationname = station.getAttribute("name")
    # print("下载站点：", stationname)
    # stationPath[stationname] = currentPath + '/' + stationname
    '''创建对应站点文件夹'''
    tvms = station.getElementsByTagName("tvminfo")
    if (not os.path.exists(currentPath + '/' + stationname)) & (len(tvms) > 0):
        os.mkdir(currentPath + '/' + stationname)

    for tvm in tvms:
        Id = tvm.getAttribute("id")
        Dates = tvm.getAttribute("date")
        # print(" Tvm", Id, "date =", Date)
        # print(stationslist[stationname][stationname + "Tvm" + Id])
        stations_download_list[stationslist[stationname][stationname + "Tvm" + Id]] = Dates.split("/")
        ip_to_download_path_list[stationslist[stationname][stationname + "Tvm" + Id]] = currentPath + '/' + stationname + '/Tvm'+ Id
        '''创建对应设备文件夹'''
        # DevicePath[stationname + "Tvm" + Id] = "Tvm" + Id
        if not os.path.exists(currentPath + '/' + stationname + "/Tvm" + Id):
            os.mkdir(currentPath + '/' + stationname + "/Tvm" + Id)
        '''对应日期文件夹创建'''
        for date in Dates.split("/"):
            if not os.path.exists(currentPath + '/' + stationname + "/Tvm" + Id + '/' + date):
                os.mkdir(currentPath + '/' + stationname + "/Tvm" + Id + '/' + date)

# print(ip_to_download_path_list)
# print(stations_download_list)

'''开始下载工作'''
ftp = PubulicFunc.FtpSync()

for ip in stations_download_list.keys():
    print('准备连接  ' + ip)
    if not PubulicFunc.IsConnect(ip):
        print(ip + '无法连接')
        continue
    else:
        if not ftp.connect(ip):
            print('连接' + ip + "失败")
            continue
        print('\n连接' + ip + "成功")
        '''下载数据库'''
        sledb = ['sledb.db']
        ret = ftp.setPath('/Afc/Data', ip_to_download_path_list[ip])
        if not ret[0]:
            ret = ftp.downloadFilesByList(sledb)
            print(ret[1])
        else:
            print(ret[1])

        '''下载日志'''
        for downloaddir in stations_download_list[ip]:
            print(downloaddir)
            '''设置路径'''
            ret = ftp.setPath('/Afc/Log/' + downloaddir, ip_to_download_path_list[ip] + '/' + downloaddir)
            if not ret[0]:
                '''获取文件列表'''
                files = ftp.getFiles()
                if None != files:
                    '''下载'''
                    ret = ftp.downloadFilesByList(files)
                    print(ret[1])
            else:
                print(ret[1])
    ftp.disconnect()


print("\n下载结束，输入q退出")
while(True):
    ch = input()
    if ch != 'q':
        print("输入q退出")
    else:
        break

