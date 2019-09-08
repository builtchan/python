# Author: Johnson Chan
# Date: 2018/3/1

import os
import ftplib
import socket

'''设置FTP连接超时时间'''
# socket.setdefaulttimeout(60)


'''判断网络是否能够连接 响应超时200ms'''

def IsConnect(ip):
    cmd = 'ping ' + ip + ' -n 1 -w 200 > null'
    ret = os.system(cmd)
    os.system('del null')
    return not ret


'''---------------------------------------------------'''

'''通过Ftp获取指定文件'''


class FtpSync(object):
    '''初始化'''

    def __init__(self):
        self.name = 'root'
        self.psw = 'afcsle'
        self.connectFlag = 0  # 连接标记
        self.setPathFlag = 0  # 设置路径标记
        self.ftpPath = ''
        self.DownLoadPath = ''
        self.rootPath = os.getcwd()  # 绝对路径

    '''设置连接用户信息'''

    def setUsrInfo(self, name, psw):
        self.name = name
        self.psw = psw

    '''连接FTP'''

    def connect(self, ip):
        try:
            self.ftp = ftplib.FTP(ip, self.name, self.psw)
        except ConnectionRefusedError:
            print('ftp拒绝连接')
            return False
        except TimeoutError:
            print('ftp连接超时')
            return False

        self.connectFlag = 1
        return True

    '''设置目标路径和下载路径
        return(list): [0, '设置成功']  [1, '远端目录不对'] [2, '本地目录不对'] [3, '还没连接FTP']
    '''

    def setPath(self, ftppath, downloadpath):
        if self.connectFlag:
            filelist = self.ftp.nlst(ftppath)
            if 0 == len(filelist):
                return (1, '远端目录不对,没有该文件夹：' + ftppath)
            else:
                self.ftp.cwd(ftppath)  # 远端FTP目录
                self.ftpPath = ftppath

            ret = os.path.exists(self.rootPath + '/' + downloadpath)
            if ret:
                os.chdir(self.rootPath + '/' + downloadpath)  # 本地下载目录
                self.DownLoadPath = self.rootPath + '/' + downloadpath
            else:
                return (2, '本地目录不存在:' + downloadpath)
        else:
            return (3, '还没连接FTP')

        self.setPathFlag = 1
        return (0, '设置成功')

    '''获取当前文件夹的文件列表'''

    def getFiles(self):
        if 0 == self.setPathFlag:
            return None
        else:
            u''' 得到当前目录和文件, 放入dir_res列表 '''
            dir_res = []
            self.ftp.dir('.', dir_res.append)
            files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
            # dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
            return files

    '''下载文件 入参文件列表'''

    def downloadFilesByList(self, files):
        if 0 == self.setPathFlag:
            return (False, "请先设置目录")
        else:
            for f in files:
                # print('download :', os.path.abspath(f))
                outf = open(f, 'wb')
                try:
                    self.ftp.retrbinary('RETR %s' % f, outf.write)
                finally:
                    outf.close()
                str = "下载 " + f + " 成功"
                print(str)
            return (True, '')

    '''断开连接'''

    def disconnect(self):
        if self.connectFlag:
            self.ftp.close()


    '''上传文件'''
    def UpFile(self, upfile, remotePath):
        # self.ftp.set_debuglevel(2)
        if not os.path.exists(upfile):
            return (False, "本地文件不存在")
        fd = open(upfile, 'rb')
        self.ftp.storbinary('STOR %s' % remotePath, fd)
        # self.ftp.set_debuglevel(0)
        fd.close()
        return (True, 'Up seccess')


'''------------------------WOL-----------------------'''

import socket
import struct

'''wake on lan
    in[0]: MAC address
    in[1]: broadcast IP address
假设需要被唤醒PC网卡MAC地址为：01:02:03:04:05:06 则WOL魔法包结构如下：
FF FF FF FF FF FF | 01 02 03 04 05 06 ...重复16次... 01 02 03 04 05 06 | 00 00 00 00 00 00
前段的6字节0xff 和尾部的 6字节0x00 无需变化照抄即可，数据包总长度：108 字节
通过把以上数据包发送到本地子网的广播地址（代码中为：192.168.1.255）的UDP端口9即可唤醒该PC
'''


def WOL(MAC, BroadcastIP):
    mac = MAC
    if (not 12 == len(MAC)) & (17 == len(MAC)):
        mac = MAC.replace(MAC[2], '')

    dest = (BroadcastIP, 9)  # 广播IP 和 端口
    send_data_raw = 'FFFFFFFFFFFF' + mac * 16 + '0000000000000'
    magic_data = b''
    for i in range(0, len(send_data_raw), 2):
        byte_dat = struct.pack('B', int(send_data_raw[i: i + 2], 16))
        magic_data += byte_dat
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.sendto(magic_data, dest)
    except:
        print('发送失败，可能网络不通')
    else:
        print("Done")
    s.close()


import paramiko


def SshUp(ip, usrname, psw, upfile, destpath):
    try:
        transport = paramiko.Transport((ip, 22))
    except:
        print(ip + '无法连接')
        input()
        exit()

    transport.connect(username=usrname, password=psw)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print(upfile, ' to ', destpath)
    try:
        sftp.put(upfile, destpath)
    except:
        print("put failed , please check the name of file is right or not")
    else:
        print("success")
    transport.close()
