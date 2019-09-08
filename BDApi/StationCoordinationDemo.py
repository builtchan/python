# Author: Johnson Chan
# Date: 2018/10/17
#!/usr/bin/python


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import xml.etree.ElementTree as ET
import sys
import os
import time
import json
import BDMapApi
import threading

class CStation(QtWidgets.QWidget):

    TipSignal = pyqtSignal(str)  # 信号

    def __init__(self):
        super(CStation, self).__init__()
        self.stationIdDict = {}             # 配置文件解析出来的站点和ID
        self.stationIdFinishDict = {}       # 完成了的站点
        self.needCornfirmStaionId = ''      # 待确认的站点id
        self.locationResultDict = []        # 地点结果
        self.stationCoordinationDict = {}   # 站点坐标
        self.resultCnt = 0                  # 地图API返回结果
        self.resultIndex = 0                #
        self.bConfirmMsg = False            # 待确认标记
        self.btnLock = False                # 搜索锁

        self.TipSignal.connect(self.TipShowSlot)
        self.btnStyle = 'QPushButton{background-color:rgb(85, 170, 255);color:black;border-radius:8px;border: 2px groove gray; \
                         border-style: outset;font-family:Arial;font-size:20px;} QPushButton:pressed{background-color:rgb(85, 170, 255);border-style:inset;}'
        self.lblStyleFont = 'QLabel{font-size:12pt;}'
        self.lblStyle = 'QLabel{background-color:rgba(155,255,193,90);font-size:15pt;border: 2px groove gray;}'
        self.edTStyle = 'QTextEdit{background-color:rgba(255,255,255,90);font-size:15pt;border: 2px groove gray;}'
        self.lnEStyle = 'QLineEdit{background-color:rgba(255,255,255,90);font-size:15pt;border: 2px groove gray;}'
        # 默认
        self.filterTip = '(e.g:轨道交通)'
        self.filterNewWords = []    # ['地铁', '轨道']
        self.cityTip = '(e.g:广州市)'
        self.cityList = []      # 城市列表
        self.baiduMapAk = 'CNQ3tzhnuupZY1v41lkBv8vGvMWNvc4T'
        self.jsonName = 'StationCoordination.json'

        self.pwd = os.getcwd().replace('/', '\\')
        self.needdel = False    # 用于判断是否需要删除copy过来的图片，因为decode貌似不能加路径
        self.setStyleSheet('QWidget{border-radius:5px;background-color:rgb(224,255,255);}')
        self.setFixedSize(800, 430)
        self.setWindowTitle('Demo(通过解析MapLineConfig.xml获取站点信息用于获取百度地图坐标  by Chenjc 20181019)')

        self.selectBtn = QtWidgets.QPushButton(self)
        self.selectBtn.setGeometry(5, 5, 90, 30)
        self.selectBtn.setText('打开')
        self.selectBtn.clicked.connect(self.getfilepathslot)
        self.selectBtn.setStyleSheet(self.btnStyle)

        self.pathEditText = QtWidgets.QTextEdit(self)
        self.pathEditText.setGeometry(100, 5, 695, 30)
        self.pathEditText.setStyleSheet(self.edTStyle)
        self.pathEditText.textChanged.connect(self.openFileSlot)

        '''百度地图API ak码'''
        self.akLabel = QtWidgets.QLabel(self)
        self.akLabel.setGeometry(5, 40, 180, 30)
        self.akLabel.setText('百度地图API ak码')
        self.akLabel.setStyleSheet(self.lblStyle)

        self.akLineEdit = QtWidgets.QLineEdit(self)
        self.akLineEdit.setGeometry(185, 40, 610, 30)
        self.akLineEdit.setText(self.baiduMapAk)
        self.akLineEdit.setStyleSheet(self.lnEStyle)

        '''筛选词'''
        self.filterLineText = QtWidgets.QLineEdit(self)
        self.filterLineText.setGeometry(5, 75, 100, 30)
        self.filterLineText.setStyleSheet(self.lnEStyle)

        self.addfilterBtn = QtWidgets.QPushButton(self)
        self.addfilterBtn.setGeometry(105, 75, 50, 30)
        self.addfilterBtn.setText('添加')
        self.addfilterBtn.clicked.connect(self.addfilterWordSlot)
        self.addfilterBtn.setStyleSheet(self.btnStyle)

        self.filterLable = QtWidgets.QLabel(self)
        self.filterLable.setGeometry(155, 75, 70, 30)
        self.filterLable.setText('筛选词')
        self.filterLable.setStyleSheet(self.lblStyle)

        self.filterLableShow = QtWidgets.QLabel(self)
        self.filterLableShow.setGeometry(230, 75, 400, 30)
        self.filterLableShow.setText(self.filterTip)
        self.filterLableShow.setStyleSheet(self.lblStyleFont)

        self.defaultBtn = QtWidgets.QPushButton(self)
        self.defaultBtn.setGeometry(705, 75, 90, 30)
        self.defaultBtn.setText('恢复默认')
        self.defaultBtn.clicked.connect(self.defaultSlot)
        self.defaultBtn.setStyleSheet(self.btnStyle)

        '''附加后缀'''
        self.postfixLable = QtWidgets.QLabel(self)
        self.postfixLable.setGeometry(5, 110, 90, 30)
        self.postfixLable.setText('搜索后缀')
        self.postfixLable.setStyleSheet(self.lblStyle)

        self.postfixLineText = QtWidgets.QLineEdit(self)
        self.postfixLineText.setText('站')
        self.postfixLineText.setGeometry(100, 110, 40, 30)
        self.postfixLineText.setStyleSheet(self.lnEStyle)

        '''城市'''
        self.cityLineText = QtWidgets.QLineEdit(self)
        self.cityLineText.setGeometry(150, 110, 80, 30)
        self.cityLineText.setStyleSheet(self.lnEStyle)

        self.btnAddCity = QtWidgets.QPushButton(self)
        self.btnAddCity.setGeometry(230, 110, 50, 30)
        self.btnAddCity.setText('添加')
        self.btnAddCity.clicked.connect(self.addCitySlot)
        self.btnAddCity.setStyleSheet(self.btnStyle)

        self.cityLbl = QtWidgets.QLabel(self)
        self.cityLbl.setGeometry(280, 110, 50, 30)
        self.cityLbl.setText('城市')
        self.cityLbl.setStyleSheet(self.lblStyle)

        self.cityLblShow = QtWidgets.QLabel(self)
        self.cityLblShow.setGeometry(330, 110, 350, 30)
        self.cityLblShow.setText(self.cityTip)
        self.cityLblShow.setStyleSheet(self.lblStyleFont)

        '''确认开始'''
        self.selectBtn = QtWidgets.QPushButton(self)
        self.selectBtn.setGeometry(705, 110, 90, 30)
        self.selectBtn.setText('开始搜索')
        self.selectBtn.clicked.connect(self.startSearchSlot)
        self.selectBtn.setStyleSheet(self.btnStyle)

        '''message'''
        self.backgroundLable = QtWidgets.QLabel(self)
        self.backgroundLable.setGeometry(2, 142, 795, 283)
        self.backgroundLable.setStyleSheet('QLabel{border: 2px groove gray;}')

        '''province , city , area , name , location , address'''
        # province
        self.provinceLable = QtWidgets.QLabel(self)
        self.provinceLable.setGeometry(5, 145, 30, 30)
        self.provinceLable.setText('省')
        self.provinceLable.setStyleSheet(self.lblStyle)

        self.provinceLableShow = QtWidgets.QLabel(self)
        self.provinceLableShow.setGeometry(35, 145, 80, 30)
        self.provinceLableShow.setText('--')
        self.provinceLableShow.setStyleSheet(self.lblStyleFont)

        # city
        self.cityLable = QtWidgets.QLabel(self)
        self.cityLable.setGeometry(120, 145, 30, 30)
        self.cityLable.setText('市')
        self.cityLable.setStyleSheet(self.lblStyle)

        self.cityLableShow = QtWidgets.QLabel(self)
        self.cityLableShow.setGeometry(150, 145, 80, 30)
        self.cityLableShow.setText('--')
        self.cityLableShow.setStyleSheet(self.lblStyleFont)

        # area
        self.areaLable = QtWidgets.QLabel(self)
        self.areaLable.setGeometry(230, 145, 30, 30)
        self.areaLable.setText('区')
        self.areaLable.setStyleSheet(self.lblStyle)

        self.areaLableShow = QtWidgets.QLabel(self)
        self.areaLableShow.setGeometry(260, 145, 100, 30)
        self.areaLableShow.setText('--')
        self.areaLableShow.setStyleSheet(self.lblStyleFont)

        # name
        self.nameLable = QtWidgets.QLabel(self)
        self.nameLable.setGeometry(365, 145, 50, 30)
        self.nameLable.setText('地点')
        self.nameLable.setStyleSheet(self.lblStyle)

        self.nameLableShow = QtWidgets.QLabel(self)
        self.nameLableShow.setGeometry(415, 145, 150, 30)
        self.nameLableShow.setText('--')
        self.nameLableShow.setStyleSheet(self.lblStyleFont)

        # coordanition
        self.coordLable = QtWidgets.QLabel(self)
        self.coordLable.setGeometry(570, 145, 50, 30)
        self.coordLable.setText('坐标')
        self.coordLable.setStyleSheet(self.lblStyle)

        self.coordLableShow = QtWidgets.QLabel(self)
        self.coordLableShow.setGeometry(620, 145, 175, 30)
        self.coordLableShow.setText('--')
        self.coordLableShow.setStyleSheet(self.lblStyleFont)

        # address
        self.addressLable = QtWidgets.QLabel(self)
        self.addressLable.setGeometry(5, 180, 50, 30)
        self.addressLable.setText('描述')
        self.addressLable.setStyleSheet(self.lblStyle)

        self.addressLableShow = QtWidgets.QLabel(self)
        self.addressLableShow.setGeometry(55, 180, 740, 30)
        self.addressLableShow.setText('--')
        self.addressLableShow.setStyleSheet(self.lblStyleFont)

        '''上一条信息按钮'''
        self.prevBtn = QtWidgets.QPushButton(self)
        self.prevBtn.setGeometry(5, 218, 90, 30)
        self.prevBtn.setText('上一条')
        self.prevBtn.hide()
        self.prevBtn.clicked.connect(self.btnPrevSlot)
        self.prevBtn.setStyleSheet(self.btnStyle)

        '''下一条信息按钮'''
        self.nextBtn = QtWidgets.QPushButton(self)
        self.nextBtn.setGeometry(100, 218, 90, 30)
        self.nextBtn.setText('下一条')
        self.nextBtn.hide()
        self.nextBtn.clicked.connect(self.btnNextSlot)
        self.nextBtn.setStyleSheet(self.btnStyle)

        '''确认取这条信息'''
        self.confirmBtn = QtWidgets.QPushButton(self)
        self.confirmBtn.setGeometry(195, 218, 180, 30)
        self.confirmBtn.setText('确认使用这条信息')
        self.confirmBtn.hide()
        self.confirmBtn.clicked.connect(self.btnConfirmMsgSlot)
        self.confirmBtn.setStyleSheet(self.btnStyle)

        '''进度'''
        self.processLbl = QtWidgets.QLabel(self)
        self.processLbl.setGeometry(390, 218, 160, 30)
        self.processLbl.setStyleSheet(self.lblStyleFont)

        '''清除信息'''
        self.clearBtn = QtWidgets.QPushButton(self)
        self.clearBtn.setGeometry(550, 218, 90, 30)
        self.clearBtn.setText('清除信息')
        self.clearBtn.clicked.connect(self.btnClearSlot)
        self.clearBtn.setStyleSheet(self.btnStyle)

        '''保存'''
        self.saveBtn = QtWidgets.QPushButton(self)
        self.saveBtn.setGeometry(645, 218, 150, 30)
        self.saveBtn.setText('保存已获取信息')
        self.saveBtn.clicked.connect(self.btnSaveSLot)
        self.saveBtn.setStyleSheet(self.btnStyle)

        '''提示'''
        self.tipTextEdit = QtWidgets.QTextEdit(self)
        self.tipTextEdit.setGeometry(5, 250, 790, 173)
        self.tipTextEdit.setStyleSheet(self.edTStyle)

    '''搜索线程'''
    def __sourchThread(self, arg):
        print('thread name = %s' % threading.current_thread().getName())
        print('deal = %s' % str(self.stationIdDict))
        print('arg = %s' % arg)
        bFind = False
        bFirst = False

        for stationid in list(self.stationIdDict.keys()):
            print('\nstart deal %s %s' % (stationid, self.stationIdDict[stationid]))
            self.TipShow('开始处理 ' + self.stationIdDict[stationid] + self.postfixLineText.text())
            if bFirst:
                # 并发量2秒一次
                time.sleep(1.5)
            # 多城市
            self.locationResultDict.clear()
            for city in self.cityList:
                print('处理城市' + city)
                bSuccess, locationResults = BDMapApi.LocationSearch(city, self.stationIdDict[stationid] + self.filterLineText.text(),
                                                                        self.akLineEdit.text())
                if not bSuccess and not len(self.locationResultDict):
                    self.TipShow('获取失败')
                    self.TipShow(locationResults[1])
                    self.btnLock = False
                    return
                self.locationResultDict.extend(locationResults)

            self.resultIndex = 0
            self.resultCnt = len(self.locationResultDict)
            print('self.resultCnt = %d' % self.resultCnt)
            bFirst = True

            # 地图返回结果遍历
            for i in range(0, self.resultCnt, 1):
                bFind = False
                # 关键词筛选
                if len(self.filterNewWords) > 0:
                    for word in self.filterNewWords:
                        print('search ' + word)
                        if ('address' in self.locationResultDict[i]) and (self.locationResultDict[i]['address'].find(word) >= 0):
                            print('find ' + word + ' in ' + self.locationResultDict[i]['address'])
                            # 已经完成的
                            self.stationIdFinishDict[stationid] = self.stationIdDict.pop(stationid)
                            lat = str(self.locationResultDict[i]['location']['lat'])
                            lng = str(self.locationResultDict[i]['location']['lng'])
                            self.stationCoordinationDict[stationid] = lat + ',' + lng
                            self.TipShow('坐标：' + lat + ',' + lng)

                            self.processLbl.setText('当前进度 %d / %d' % (
                                len(self.stationIdFinishDict), len(self.stationIdFinishDict) + len(self.stationIdDict)))

                            print("done " + lat + ',' + lng)
                            bFind = True
                            break   # 关键词筛选
                        else:
                            if 'address' in self.locationResultDict[i]:
                                print('not find ' + word + 'in ' + self.locationResultDict[i]['address'])
                            else:
                                print('no address')
                    if bFind:
                        break  # 地图返回结果遍历
                else:
                    self.TipShow('请自行选择当前站坐标点')
                    break   # 地图返回结果遍历
            if bFind:
                continue       # 遍历需要获取坐标的站点
            else:
                if len(self.filterNewWords):
                    self.TipShow('没能自动选择到坐标点，请自行选择')
                self.needCornfirmStaionId = stationid
                self.prevBtn.show()
                self.nextBtn.show()
                self.confirmBtn.show()
                break       # 遍历需要获取坐标的站点

        if 0 == len(self.stationIdDict):
            print('开始写文件')
            if len(self.cityList):
                filename = self.cityList[0] + self.stationCoordinationDict
            else:
                filename = self.stationCoordinationDict
            fp = open(self.jsonName, "w")
            json.dump(filename, fp, sort_keys=True, indent=2)
            self.TipShow('完成')
            self.btnLock = False
            return
        # 地点没能从筛选词中找到对应的错标，需人工进行选择
        if not bFind:
            self.bConfirmMsg = True
            print('bConfirmMsg = ')
            print(self.bConfirmMsg)
            self.ShowMessage()

        self.btnLock = False

    '''显示需要供选择的信息'''
    def ShowMessage(self):
        result = self.locationResultDict[self.resultIndex]
        if 'province' in result:
            self.provinceLableShow.setText(result['province'])
        if 'city' in result:
            self.cityLableShow.setText(result['city'])
        if 'area' in result:
            self.areaLableShow.setText(result['area'])
        if 'address' in result:
            self.addressLableShow.setText(result['address'])
        if 'name' in result:
            self.nameLableShow.setText(result['name'])
        self.coordLableShow.setText(str(result['location']['lat']) + ',' + str(result['location']['lng']))

    '''统一的text提示入口'''
    def TipShow(self, data):
        # print(data)
        # self.tipTextEdit.append(data)
        self.TipSignal.emit(data)

    '''slot'''
    def getfilepathslot(self):
        self.filepath, fileType = QFileDialog.getOpenFileName(self, '选择要识别的文件', '.')
        self.filepath = self.filepath.replace('/', '\\')
        self.pathEditText.setText(self.filepath)
        # print('FilePath', self.filepath)

    def openFileSlot(self):
        if not len(self.filepath):
            return
        self.stationIdDict.clear()
        try:
            eTree = ET.parse(self.filepath)
            root = eTree.getroot()
            for child in root:
                if "0" == child.attrib["lineId"]:
                    self.stationIdDict[child.attrib["stationId"]] = child.attrib["text_chs"].replace(' ', '')

            # ls = []
            # for l in self.stationIdDict.keys():
            #     ls.append(l)
            # self.stationIter = iter(ls)
            # self.TipShow('需要获取%d个站点的坐标' % (len(self.stationIdDict)))
            self.processLbl.setText('当前进度 0 / %d' % (len(self.stationIdDict)))
        except ET.ParseError:
             QMessageBox.question(self, "Question", "请检查XML文件格式是否正确",
                                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)

    def addfilterWordSlot(self):
        if not len(self.filterLineText.text()):
            return
        self.filterNewWords.append(self.filterLineText.text())
        self.filterNewWords = list(set(self.filterNewWords))
        self.filterLableShow.clear()
        self.filterLableShow.setText('、'.join(self.filterNewWords))
        self.filterLineText.clear()

    def addCitySlot(self):
        if not len(self.cityLineText.text()):
            return
        self.cityList.append(self.cityLineText.text())
        self.cityLineText.clear()
        self.cityLblShow.setText(','.join(self.cityList))

    def defaultSlot(self):
        self.filterNewWords.clear()
        self.filterLableShow.clear()
        self.filterLableShow.setText(self.filterTip)
        self.cityList.clear()
        self.cityLblShow.clear()
        self.cityLblShow.setText(self.cityTip)
        self.akLineEdit.setText(self.baiduMapAk)

    def startSearchSlot(self):
        if self.btnLock:
            QMessageBox.question(self, "warning", "请等待上一次处理完成")
            return
        if self.bConfirmMsg:
            QMessageBox.question(self, "warning", "请先从当前信息中选取")
            return
        if not len(self.stationIdDict):
            QMessageBox.question(self, "Error", "无查询内容")
            return
        if not len(self.cityList):
            QMessageBox.question(self, "warnning", "请输入城市")
            return
        if not len(self.akLineEdit.text()):
            QMessageBox.question(self, "warnning", "请输入百度地图API ak码")
            return

        self.btnLock = True
        myThread = threading.Thread(target=self.__sourchThread, args=(1,))
        myThread.start()

    def btnPrevSlot(self):
        if 0 == self.resultIndex:
            print('第一个')
            return
        self.resultIndex -= 1
        self.ShowMessage()

    def btnNextSlot(self):
        if self.resultIndex == (self.resultCnt - 1):
            print('最后一个')
            return
        self.resultIndex += 1
        self.ShowMessage()

    def btnConfirmMsgSlot(self):
        if not self.bConfirmMsg:
            QMessageBox.question(self, "warning", "请先开始搜索",
                                 QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return

        self.stationIdFinishDict[self.needCornfirmStaionId] = self.coordLableShow.text()
        self.stationCoordinationDict[self.needCornfirmStaionId] = self.coordLableShow.text()
        self.TipShow(self.stationIdDict[self.needCornfirmStaionId] + '坐标确认是' + self.coordLableShow.text())
        self.TipShow(self.stationIdDict.pop(self.needCornfirmStaionId) + '处理完成')

        self.processLbl.setText('当前进度 %d / %d' % (len(self.stationIdFinishDict), len(self.stationIdFinishDict) + len(self.stationIdDict)))
        # 清空内容
        self.provinceLableShow.setText('--')
        self.cityLableShow.setText('--')
        self.areaLableShow.setText('--')
        self.addressLableShow.setText('--')
        self.nameLableShow.setText('--')
        self.coordLableShow.setText('--')
        self.prevBtn.hide()
        self.nextBtn.hide()
        self.confirmBtn.hide()

        self.bConfirmMsg = False
        self.btnLock = True
        myThread = threading.Thread(target=self.__sourchThread, args=(1,))
        myThread.start()

    def btnClearSlot(self):
        self.provinceLableShow.setText('--')
        self.cityLableShow.setText('--')
        self.areaLableShow.setText('--')
        self.addressLableShow.setText('--')
        self.nameLableShow.setText('--')
        self.coordLableShow.setText('--')
        self.bConfirmMsg = False
        self.tipTextEdit.clear()
        self.locationResultDict.clear()
        self.prevBtn.hide()
        self.nextBtn.hide()
        self.confirmBtn.hide()

    def btnSaveSLot(self):
        if not len(self.stationIdFinishDict):
            QMessageBox.question(self, 'warning', '暂无数据保存')
            return
        print('开始写文件')
        fp = open(self.jsonName, "w")
        json.dump(self.stationCoordinationDict, fp, sort_keys=True, indent=2)
        QMessageBox.question(self, 'ok', '保存完成')

    def TipShowSlot(self, data):
        print(data)
        self.tipTextEdit.append(data)

if __name__ == '__main__':

    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    app = QtWidgets.QApplication(sys.argv)
    ui = CStation()
    ui.show()
    sys.exit(app.exec())
