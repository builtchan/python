#Author: Johnson Chan
#Date: 2018/2/26

# -*- encoding: utf8 -*-
import os
import sys
import ftplib

class FTPSync(object):
    def __init__(self):
        self.ip = '10.15.121.39'
        self.path = '/Afc/Log/20180307'
        self.downloadpath = '.'
        self.conn = ftplib.FTP(self.ip, 'root', 'afcsle')
        self.conn.cwd(self.path)
        os.chdir(self.downloadpath)

    def get_dirs_files(self):
        u''' 得到当前目录和文件, 放入dir_res列表 '''
        dir_res = []
        self.conn.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
        return (files, dirs)

    # 递归文件夹
    def walk(self, next_dir):
        print('Walking to', next_dir)
        self.conn.cwd(next_dir)
        try:
            os.mkdir(next_dir)
        except OSError:
            pass
        os.chdir(next_dir)

        ftp_curr_dir = self.conn.pwd()
        local_curr_dir = os.getcwd()
        files, dirs = self.get_dirs_files()
        # print "FILES: ", files
        # print "DIRS: ", dirs
        for f in files:
            # print next_dir, ':', f
            print('download :', os.path.abspath(f))
            outf = open(f, 'wb')
            try:
                self.conn.retrbinary('RETR %s' % f, outf.write)
            finally:
                outf.close()
        for d in dirs:
            os.chdir(local_curr_dir)  # 切换本地的当前工作目录为d的父文件夹
            self.conn.cwd(ftp_curr_dir)  # 切换ftp的当前工作目录为d的父文件夹
            self.walk(d)  # 在这个递归里面，本地和ftp的当前工作目录都会被更改

    def run(self):
        self.walk('.')

    def distroy(self):
        self.conn.quit()

def main():
    f = FTPSync()

    f.run()
    f.distroy()
    print("输入q退出")
    while(True):
        ch = input()
        if ch != 'q':
            print("输入q退出")
        else:
            break

if __name__ == '__main__':
    main()