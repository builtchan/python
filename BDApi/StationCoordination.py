# Author: Johnson Chan
# Date: 2018/10/17
#!/usr/bin/python

import xml.etree.ElementTree as ET
import json
import urllib.request
import os
import threading
import time

if os.path.exists("MapLineConfig.xml"):
    print("exist MapLineConfig.xml")

fp = open("MapLineConfig.xml", encoding='utf-8')

'''id , stationName'''
stationID = {}
try:
    eTree = ET.parse("MapLineConfig.xml")
    root = eTree.getroot()
    for child in root:
        # print(child.tag, child.attrib)
        if "0" == child.attrib["lineId"]:
            stationID[child.attrib["stationId"]] = child.attrib["text_chs"]
except ET.ParseError:
    print("wrong xml")

print(stationID)

search = urllib.parse.quote(u'天河南'.encode('utf-8'))
region = urllib.parse.quote(u'广州'.encode('utf-8'))
# region = urllib.parse.quote(u'佛山'.encode('utf-8'))
url = u"http://api.map.baidu.com/place/v2/search?query=%s&region=%s&city_limit=true&output=json&ak=CNQ3tzhnuupZY1v41lkBv8vGvMWNvc4T"%(search, region)
req = urllib.request.urlopen(url)   # JSON格式的返回数据
res = req.read().decode("utf-8")    # 将其他编码的字符串解码成unicode
temp = json.loads(res)

lists = temp['results']
print(lists[1])



