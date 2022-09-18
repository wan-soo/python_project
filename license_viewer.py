import paramiko
import time
import datetime
from datetime import date, timedelta
from time import localtime, strftime
from scp import SCPClient
from pathlib import Path
import os
#####################
# ui 띄워줌
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt
#from pyglet import Gtk, Gdk, GObject
######################

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
#form_class = uic.loadUiType("license_viewer.ui")[0]
# C:\Users\wansoo.kim\python\Project1\license_management
#form_class = uic.loadUiType("lic.ui")[0]

try:
    form_class = uic.loadUiType("lic.ui")[0]
except:
    form_class = uic.loadUiType("C:/Users/wansoo.kim/python/Project1/license_management/lic.ui")[0]
    
#form_class = uic.loadUiType("C:/Users/wansoo.kim/python/Project1/license_management/license_viewer.ui")[0]
#form_class = uic.loadUiType("C:/Users/wansoo.kim/python/Project1/license_management/lic.ui")[0]

dstfolder = 'c:/temp/V93K_LICENSE/'
slicense_log = ""
 ####################
# license 저장을 위해 dic 선언
dic_license = {}
dic_license.clear()
dic_eqp = {}
dic_eqp.clear()

####################
# license sub 에 장비별 license 수량 저장을 위해 리스트 선언
list_eq_name = []
list_lic_name = []
####################
# license name / eq name 별 license 수
dic_lic_eq = {}
dic_lic_eq.clear()
####################
dstfilename = ""
       
search_lic = ""
search_eqp = ""
        
##############################################################
#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        
        self.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon('python_18894.png'))
        
        ######################
        # 버턴에 기능연결
        self.bt_search.clicked.connect(self.searchFunction)
        self.bt_close.clicked.connect(self.closeFunction)
        self.tbl_lic.verticalHeader().setVisible(False) # 행번호 안나오게 하는 코드
        
        #self.cb_lic.activated[str].connect(self.cb_lic_Event)
        #self.cb_eqp.activated[str].connect(self.cb_eqp_Event)
      
        
        #self.cb_lic.currentIndexChanged.connect(함수)
        # #55ffff
        header_item = QTableWidgetItem("No.") 
        #header_item.setBackground(Qt.yellow) # 헤더 배경색 설정 --> app.setStyle() 설정해야만 작동한다. self.table.setHorizontalHeaderItem(2, header_item)
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_lic.setHorizontalHeaderItem(0, header_item)
        header_item = QTableWidgetItem("License_Name") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_lic.setHorizontalHeaderItem(1, header_item)
        header_item = QTableWidgetItem("Equipment_Name") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_lic.setHorizontalHeaderItem(2, header_item)
        header_item = QTableWidgetItem("User_Name") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_lic.setHorizontalHeaderItem(3, header_item)
        header_item = QTableWidgetItem("Total_Qty") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_lic.setHorizontalHeaderItem(4, header_item)
        header_item = QTableWidgetItem("Used_Qty") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_lic.setHorizontalHeaderItem(5, header_item)

        # 셀 복사가 안되서 주석처리
        #self.tbl_lic.setSelectionBehavior(QAbstractItemView.SelectRows)  # Row 단위 선택
        #self.tbl_lic.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 셀 edit 금지

        self.tbl_lic.setColumnWidth(0, 50)
        self.tbl_lic.setColumnWidth(1, 200)
        self.tbl_lic.setColumnWidth(2, 110)
        self.tbl_lic.setColumnWidth(3, 100)
        self.tbl_lic.setColumnWidth(4, 70)
        self.tbl_lic.setColumnWidth(5, 70)
        ##########################
        pal = self.cb_lic.palette()
        pal.setColor(self.cb_lic.backgroundRole(),QtGui.QColor(255,255,255))
        self.cb_lic.setPalette(pal)
        self.cb_lic.setAutoFillBackground(True)
        ###########################
    
    #def cb_lic_Event(self, text):
    #    self.cb_lic.setCurrentText(text)
        #self.ed_lic.adjustSize()
    #def cb_eqp_Event(self, text):
    #    self.cb_eqp.setCurrentTex(text)    
    ###########################    
    #btn_1이 눌리면 작동할 함수
    def searchFunction(self) :
        print("search clicked")
        
        global search_lic
        global search_eqp
        
        search_lic = self.cb_lic.currentText()
        search_eqp = self.cb_eqp.currentText()
        
        ######################
        # Change the cursor to hour Glass
        self.setCursor(Qt.WaitCursor)
        ##########################
        #self.ed_lic.setText("tet")
        #self.ed_lic.setText(self.ed_lic.text() + " 추가")
        self.tbl_lic.clearContents()
        self.tbl_lic.setRowCount(0)
        ####################
        global dic_license
        dic_license = {}
        dic_license.clear()
        
        global dic_eqp 
        dic_eqp = {}
        dic_eqp.clear()
        ##################
        global list_eq_name
        list_eq_name = []
        self.cb_lic.clear()
        
        global list_lic_name
        list_lic_name = []
        self.cb_eqp.clear()
        ####################
        self.download_lic()
        self.dataparsing_all()
        #self.cb_eqp.addItem('ALL')
        #self.cb_lic.addItem('ALL')
                
        self.dataparsing()
        #######################
        
        d1 = dict(sorted(dic_license.items()))
        for k in d1.keys():
            self.cb_lic.addItem(k)
        self.cb_lic.insertItem(0, 'ALL')    
        self.cb_lic.setCurrentText(search_lic)
        #################
        
        d1 = dict(sorted(dic_eqp.items()))    
        for k in d1.keys():
            self.cb_eqp.addItem(k)
        self.cb_eqp.insertItem(0, 'ALL')         
        self.cb_eqp.setCurrentText(search_eqp)
        ######################## 
        ######################################
        # Set the cursor to normal Arrow
        self.unsetCursor() 
        ######################################
        
    
    def download_lic(self) :
        now = datetime.datetime.now()
        nowtime = now.strftime('%Y%m%d%H%M%S')   
        global slicense_log
        slicense_log = 'license_summary_log_' + nowtime

        tmp_day = date.today() - timedelta(1)
        yesterday = tmp_day.strftime('%Y%m%d')
        #sdel_log = 'license_summary_log_' + yesterday
        ####################
        #dstfolder = 'c:/temp/V93K_LICENSE/'
        p = Path('c:/temp')  # 로컬 다운받은 폴더
        p.mkdir(exist_ok=True)
        ######################
        p = Path(dstfolder)  # 로컬 다운받은 폴더
        p.mkdir(exist_ok=True)
        path = os.path.abspath(dstfolder)
        
        try:
            for filename in os.listdir(dstfolder):
                del_filename = os.path.join(path, filename)
                os.remove(del_filename)  # result file delete
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            
            ssh.connect("equipIP", username="root", password= "redhat")
            print("ssh connected.")
            #########################
            #ssh.exec_command("cd /opt/flexlm/bin")
            #stdin, stdout, stderr = ssh.exec_command("ls -l")
            channel = ssh.invoke_shell()
            channel.send('cd /opt/flexlm/bin \n')
            time.sleep(1.0)
            output = channel.recv(65535).decode("utf-8")    
            print(output)
            ###########################
            channel.send('./lmutil lmstat -a > log/' + slicense_log + '\n')
            time.sleep(1.0)
            output = channel.recv(65535).decode("utf-8")    
            print(output)
            ##########################
            # 원격서버에서 로컬로 파일복사
            #channel.send('scp -P 32222 root@equipIP:/opt/flexlm/bin/log/' + slicense_log + ' C:\\' + '\n')
            #channel.send('scp -P 32222  /opt/flexlm/bin/log/' + slicense_log + ' C:' + '\n')
            #dstfolder = 'c:/temp/V93K_LICENSE/'
            srcfilename = '/opt/flexlm/bin/log/' + slicense_log 
            global dstfilename
            dstfilename = dstfolder + slicense_log
            scp = SCPClient(ssh.get_transport())
            time.sleep(2.0)
            scp.get(srcfilename,dstfilename)
            print(dstfilename + '\n' + 'license file 복사완료')
            ##########################
            time.sleep(2)
                
            ssh.close()
        except Exception as err:
            print(err)
            ssh.close()
        
    #btn_2가 눌리면 작동할 함수
    def closeFunction(self) :
        print("close clicked") 
        sys.exit()
           
    ########################## 
    def Information_event(self) : 
        QMessageBox.information(self,'license qty error','use license 와 장비별 license 수가 일치하지 않습니다.')
    
    def dataparsing(self) :
        
        #################################
        # 파일 파싱
        # test  로 파일명 변경
        #slicense_log = "license_summary_log_20211227154702"
        dstfilename = dstfolder + slicense_log
         ####################
        # license 저장을 위해 dic 선언
        #global dic_license
        #dic_license = {}
        #dic_license.clear()
        ####################
        
        ####################
        # license name / eq name 별 license 수
        global dic_lic_eq
        dic_lic_eq = {}
        dic_lic_eq.clear()
        ####################
        self.tbl_lic.clearContents()
        
        print(dstfilename + '\n' + 'parsing start')
        try:
            count = 0
            lic_seq = 0
            lic_eq_tot = 0
            eqp_seq = 0
            iss_cnt = 0
            use_cnt = 0 
            pass_flag = False
            eqp_flag = False  
            
            with open(dstfilename) as fp:
                for line in fp:
                    count += 1
                    print("Line{}: {}".format(count, line.strip()))
                    sTemp = line
                    #Users of SmarTestOffline_SOC:  (Total of 10 licenses issued;  Total of 0 licenses in use)
                    #############################
                    # 라이센스이름 , 라이센스 발행 , 사용 수
                    if sTemp.find('Users of') > -1:
                        eqp_seq = 0
                        
                        #########################
                        #############################
                        #if (self.ed_eqp.text().strip() != '') and (self.ed_eqp.text().strip() != 'ALL') :
                        temp_eqp = search_eqp.strip()
                        
                        if (temp_eqp != '') and (temp_eqp != 'ALL') :
                            eqp_flag = True
                        else:
                            eqp_flag = False   
                        ##########################    
                        if eqp_flag == False:
                            if int(lic_eq_tot) != int(use_cnt) :
                                self.Information_event(self)
                                sys.exit()
                        ########################    
                        slicens_name = ""
                        lic_eq_tot = 0
                        use_cnt = 0
                        iss_cnt = 0
                            
                        slicens_name = sTemp.split(":")[0].strip()
                        slicens_name = slicens_name.split(" ")[2].strip()
                        ##########################
                        
                        #############################
                        #if eqp_flag == True :
                        #    pass_flag = True   
                        #    #lic_seq = lic_seq + 1
                        #    pass
                        
                        #elif self.ed_lic.text().strip() == "":
                        #if (self.ed_lic.text().strip() == '') or (self.ed_lic.text().strip().upper() == 'ALL'):
                        #if (self.cb_lic.curentText() == '') or (self.cb_lic.currentText().upper() == 'ALL'):
                        temp_lic = search_lic.upper()
                        if (temp_lic == '') or (temp_lic == 'ALL'):
                            pass_flag = True
                            if eqp_flag == True :
                                pass
                            else:
                                lic_seq = lic_seq + 1
                                                        
                        #elif (slicens_name.upper().find(self.ed_lic.text().upper()) > -1) :
                        elif (slicens_name.upper().find(temp_lic) > -1) :
                            pass_flag = True
                            if eqp_flag == True :
                                pass
                            else:
                                lic_seq = lic_seq + 1
                                
                        else :     
                            pass_flag = False                       
                            continue                     
                        ##############################                         
                        ####################
                        right_part = sTemp.split("(")[-1].strip()
                        iss_cnt = right_part.split(";")[0].strip()                
                        use_cnt = right_part.split(";")[-1].strip()
                        ####################
                        iss_cnt = iss_cnt.split(" ")[2].strip()
                        use_cnt = use_cnt.split(" ")[2].strip()
                        ####################
                        # dic 에 license 등록
                        #dic_license[slicens_name] = iss_cnt + "/" + use_cnt                                                    
                        #############################
                        if eqp_flag == False :
                            srow = self.tbl_lic.rowCount() 
                            self.tbl_lic.insertRow(srow)                        
                            self.tbl_lic.setItem(srow,0,QTableWidgetItem(str(lic_seq)))
                            self.tbl_lic.setItem(srow,1,QTableWidgetItem(str(slicens_name)))
                            self.tbl_lic.setItem(srow,4,QTableWidgetItem(str(iss_cnt)))
                            self.tbl_lic.setItem(srow,5,QTableWidgetItem(str(use_cnt)))                        
                        ##############################
                        # license 레코드 색깔 다르게
                        
                    ###################################
                    # 장비이름과 장비별 라이센스 수
                    if (sTemp.find('start') > -1) and (slicens_name != '') and (pass_flag == True) :
                        
                        sTemp = sTemp.strip() 
                        user_name = sTemp.split(" ")[0].strip()
                        eq_name = sTemp.split(" ")[1].strip()
                        
                        ##########################
                        # eqp 검색시에는 
                        if eqp_flag == True :
                            #if (eq_name.upper().find(self.ed_eqp.text().upper()) > -1) :
                            if (eq_name.upper().find(search_eqp.upper()) > -1) :
                                eqp_seq = eqp_seq + 1
                                lic_seq = lic_seq + 1
                                srow = self.tbl_lic.rowCount() 
                                self.tbl_lic.insertRow(srow)                        
                                self.tbl_lic.setItem(srow,0,QTableWidgetItem(str(lic_seq)))
                                self.tbl_lic.setItem(srow,1,QTableWidgetItem(str(slicens_name)))
                                self.tbl_lic.setItem(srow,4,QTableWidgetItem(str(iss_cnt)))
                                self.tbl_lic.setItem(srow,5,QTableWidgetItem(str(use_cnt)))                                   
                                pass
                            else:
                                continue
                        else :
                            eqp_seq = eqp_seq + 1    
                        #########################    
                        
                        if sTemp.find('licenses') > -1:
                            lic_eq_cnt = int(sTemp.split(" ")[-2].strip())
                        else :
                            lic_eq_cnt = 1
                        ######################
                        # eq tot 수량체크 , license use qty 와 일치해야함.
                        lic_eq_tot = lic_eq_tot + lic_eq_cnt
                        print(str(lic_eq_tot) + " " + sTemp)
                                                
                        ########################
                        # 장비이름 별 라이센스별 사용라이센스 수 dic 에 저장
                        lic_eq = slicens_name + "*" + eq_name                
                        dic_lic_eq[lic_eq] = lic_eq_cnt
                        ##########################
                        srow = self.tbl_lic.rowCount() 
                        self.tbl_lic.insertRow(srow)                        
                        self.tbl_lic.setItem(srow,1,QTableWidgetItem(str(eqp_seq)))
                        self.tbl_lic.setItem(srow,2,QTableWidgetItem(str(eq_name)))
                        self.tbl_lic.setItem(srow,3,QTableWidgetItem(str(user_name)))
                        self.tbl_lic.setItem(srow,5,QTableWidgetItem(str(lic_eq_cnt)))   
                    ##################################
            
            print("read complete")
                        
                    
        except Exception as err:   
            print(err)
            
        ###############################    
    def dataparsing_all(self) :
        
        #################################
        # 파일 파싱
        # test  로 파일명 변경
        #slicense_log = "license_summary_log_20211227154702"
        dstfilename = dstfolder + slicense_log
        temp_cb = ""
        ####################
        # license sub 에 장비별 license 수량 저장을 위해 리스트 선언
        global list_eq_name
        list_eq_name = []
        global list_lic_name
        list_lic_name = []
        #####################
        global dic_license
        dic_license = {}
        dic_license.clear()
        global dic_eqp
        dic_eqp = {}
        dic_eqp.clear()
        ####################
        
        print(dstfilename + '\n' + 'parsing all start')
        try:
            
            with open(dstfilename) as fp:
                for line in fp:
                    
                    
                    sTemp = line
                    #Users of SmarTestOffline_SOC:  (Total of 10 licenses issued;  Total of 0 licenses in use)
                    #############################
                    # 라이센스이름 , 라이센스 발행 , 사용 수
                    if sTemp.find('Users of') > -1:
                        
                        slicens_name = ""
                        lic_eq_tot = 0
                        use_cnt = 0
                        iss_cnt = 0
                            
                        slicens_name = sTemp.split(":")[0].strip()
                        slicens_name = slicens_name.split(" ")[2].strip()
                        ##########################
                        dic_license[slicens_name] = "license"
                        
                    ###################################
                    # 장비이름과 장비별 라이센스 수
                    if (sTemp.find('start') > -1)  :
                        
                        sTemp = sTemp.strip() 
                        user_name = sTemp.split(" ")[0].strip()
                        eq_name = sTemp.split(" ")[1].strip()
                        ##########################
                        list_eq_name.append(eq_name) 
                        dic_eqp[eq_name] = "equipment"
                        #############################
                        
                #####################
                #temp_cb = self.cb_lic.currentText()
                #self.ed_lic.setText(temp_cb.strip())
                '''
                d1 = dict(sorted(dic_license.items()))
                for k in d1.keys():
                    self.cb_lic.addItem(k)
                self.cb_lic.insertItem(0, 'ALL')    
                #self.cb_lic.setCurrentText(temp_cb)
                #################
                #temp_cb = self.cb_eqp.currentText()
                #self.ed_eqp.setText(temp_cb.strip())
                
                d1 = dict(sorted(dic_eqp.items()))    
                for k in d1.keys():
                    self.cb_eqp.addItem(k)
                self.cb_eqp.insertItem(0, 'ALL')         
                #self.cb_eqp.setCurrentText(temp_cb)
                ########################    
                '''        
            print("all list read complete")
                        
                    
        except Exception as err:   
            print(err)
            
        ###############################    


#############################     
if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
###############################################################
    