# Author: Johnson Chan
# Date: 2018/5/23
#!/usr/bin/python


from aip import AipSpeech
import os
""" 你的 APPID AK SK """
APP_ID = '11220380'
API_KEY = 'FMalerGcUNGzHxFlAYyQ3EQQ'
SECRET_KEY = '0p3ow1RASkLcs3MFCWwxV8Kb4HUaaqhi'


client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

result = client.synthesis('新年好', 'zh', 1, {
    'vol': 5, 'aue': 6
})

# 识别正确返回语音二进制 错误则返回dict 参照下面错误码
if not isinstance(result, dict):
    with open('auido.wav', 'wb') as f:
        f.write(result)

# # 读取文件
# def get_file_content(filePath):
#     with open(filePath, 'rb') as fp:
#         return fp.read()
#
#
# path = 'D:\\'
#
# print('请输入文件名')
# name = input()
#
# print(path+'\\'+name)
# # 识别本地文件
# if os.path.exists(path+'\\'+name):
#     ret = client.asr(get_file_content(path+'\\'+name), 'wav')
#     print(ret)
