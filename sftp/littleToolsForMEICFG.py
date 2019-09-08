# Author: Johnson Chan
# Date: 2018/3/29
#!/usr/bin/python



import os
from xml.dom.minidom import parse
import xml.dom.minidom
import PubulicFunc
import paramiko
# import socket
import time

# socket.setdefaulttimeout(3)

'''open xml file'''
if os.path.exists('./file2DeviceConfig.xml'):
    DOMtree1 = xml.dom.minidom.parse("file2DeviceConfig.xml")
else:
    print("缺少StationsInfo1.xml文件，无法工作")
    print("输入q退出")
    while (True):
        ch = input()
        if ch != 'q':
            print("输入q退出")
        else:
            exit()

'''站点信息 root'''
stationsinfo = DOMtree1.documentElement

cmdBefore = ''
sourceFile = ''
destFile = ''
cmdAfter = ''
'''命令和源文件和目标文件'''
command = stationsinfo.getElementsByTagName("command")
for cmd in command:
    cmdBefore = cmd.getAttribute("cmdBefore")
    sourceFile = cmd.getAttribute("sourceFile")
    destFile = cmd.getAttribute("destFile")
    cmdAfter = cmd.getAttribute("cmdAfter")

'''所有站点list'''
stations = stationsinfo.getElementsByTagName("station")
'''站点字典'''
stationslist = {}

'''失败站点'''
stationFailedList = []

'''对应站点的Tvm字典'''
tvmlist = {}

iplist = []

successStaton = open("successfulStaion.txt", 'w')
failedfile = open("failed.txt", 'w')
'''遍历'''
for station in stations:
    # name = station.getAttribute("name")
    # print("站点 = ", station.getAttribute("name"))
    tvms = station.getElementsByTagName("tvm")
    for tvm in tvms:
        # print(" Tvm", tvm.getAttribute("no"), ",IP=", tvm.getAttribute("ip"))
        # iplist.append(tvm.getAttribute("ip"))
        # print(tvm.getAttribute("ip"))
        iplist.append(tvm.getAttribute("ip"))

'''遍历上传内容'''
Ssh = paramiko.SSHClient()
Ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

for ip in iplist:
    print('正在处理 ' + ip)
    if not PubulicFunc.IsConnect(ip):
        print(ip + '无法连接')
        failedfile.write(ip + ' ' + time.ctime() + "\n")
        continue
    try:
        Ssh.connect(hostname=ip, port=22, username='root', password='afcsle')
    except TimeoutError:
        print(ip + '连接超时')
        failedfile.write(ip + ' ' + time.ctime() + "\n")
        continue
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication failed")
        continue
    if len(cmdBefore):
        print("exce " + cmdBefore)
        stdin, stdout, stderr = Ssh.exec_command(cmdBefore)
        while True:
            respStr = stdout.readline()
            if respStr == '':
                break
            print(respStr)

    if len(sourceFile):
        sftp = paramiko.SFTPClient.from_transport(Ssh.get_transport())
        if not os.path.exists(sourceFile):
            print(sourceFile + '文件不存在')
            Ssh.close()
            continue
        # try:
        ret = sftp.put(sourceFile, destFile)
        print(ret.asbytes())
        # except:
        #     print("put failed , please check the name of file is right or not")
        #     print(ip + '处理失败\n')
        #     failedfile.write(ip + ' ' + time.ctime() + "\n")
        #     pass
        # else:
        print(ip + '处理成功\n')
        successStaton.write(ip + ' ' + time.ctime() + "\n")
        sftp.close()
    if len(cmdAfter):
        stdin, stdout, stderr = Ssh.exec_command(cmdAfter)
        print("exce " + cmdAfter)
    Ssh.close()

print('\n处理完毕')
successStaton.close()
failedfile.close()
input()
