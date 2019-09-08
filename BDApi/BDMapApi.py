# Author: Johnson Chan
# Date: 2018/10/18
#!/usr/bin/python

import json
import urllib.request
import socket

socket.setdefaulttimeout(8)     # 8秒超时

def LocationSearch(city, searchWord, ak):

    search = urllib.parse.quote(u''.join(searchWord).encode('utf-8'))
    region = urllib.parse.quote(u''.join(city).encode('utf-8'))
    url = u"http://api.map.baidu.com/place/v2/search?query=%s&region=%s&city_limit=true&output=json&ak=%s" % (
    search, region, ak)
    try:
        print('开始发起请求')
        req = urllib.request.urlopen(url)  # JSON格式的返回数据
        print('after request')
        res = req.read().decode("utf-8")  # 将其他编码的字符串解码成unicode
        # print(res)
        temp = json.loads(res)
        print(temp)
        if 'status' in temp and 'results' in temp and 'message' in temp:
            if 0 == temp['status']:
                return True, temp['results']
            else:
                return False, (temp['status'], temp['message'])
        else:
            return False, ('-1', '返回数据异常')
    except:
        return False, ('0', '连接超时')


