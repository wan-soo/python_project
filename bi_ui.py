import time
import datetime
from datetime import date, timedelta
from time import localtime, strftime

from pathlib import Path
import os
from xmlrpc.client import FastParser
import cx_Oracle
#####################
# ui 띄워줌
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import *
import subprocess

import configparser

import sys
import subprocess
import threading
import ctypes

try:
    form_class = uic.loadUiType("./bi_ui.ui")[0]
except:
    form_class = uic.loadUiType("C:/Users/wansoo.kim/python/Project1/label_validation/BI_UI/bi_ui.ui")[0]


######################
global meslot
meslot = ""
global sCustDevice
sCustDevice = ""
global sLead
sLead = ""

global sOper 
global sQty
sOper = ""
sQty = ""

global sCust
sCust = ""
global val_type
val_type = ""
global partial_qty
partial_qty = 0
#####################

#WIP_SITDEF2 - INT_BOMINF -> MM#, IPN, SPEC, MAX_REFLOW 값 조회

#################
global program_type
global program_ver
global program_name

program_type = 'BI UI Validation System' 
program_ver = " - v0.0.0.0" 
program_name = "bi_ui_validation"
#################################
global ui_path
global ui_prog
global path
global full_filename
global lot_flag    
global qty_flag

lot_flag = False
qty_flag = False

config = configparser.ConfigParser()    
config.read('./config_ui.ini', encoding='utf-8')

ui_path = config['target']['ui_path']
ui_prog = config['target']['ui_prog']

full_filename = os.path.join(ui_path, ui_prog)
path = os.path.abspath(ui_path)

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        
        self.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon('./python_18894.png'))
       
        self.ed_lot.returnPressed.connect(self.lot_check)
        self.ed_qty.returnPressed.connect(self.qty_check)        
        self.bt_reset.clicked.connect(self.resetFunction)        
        
        #######################
        self.setWindowTitle(program_type + program_ver)        
        self.resetFunction("ini") 
               
    
    def app_upgrade(self) :
        
        global program_type
        global program_ver
        global program_name
        
        stemp = program_ver.split('-')
        stemp = stemp[-1].strip()
        cur_path = os.getcwd()
        
        update_full_name =  os.path.join(cur_path, "label_update.exe")     
        #update_full_name = "C:/Users/wansoo.kim/python/Project1/label_validation/instantclient_21_3/label_update.exe"
        
        conn_mes = cx_Oracle.connect('mesdb')
        cur_mes = conn_mes.cursor()

        sql = "SELECT DATA1 FROM UPTDAT "
        sql = sql + "WHERE FACTORY = 'TEST' "
        sql = sql + "AND TABLE_NAME = 'LABEL_VALIDATION_VER' "
        sql = sql + "AND UPPER(KEY1) = '" + program_name.upper() + "' "
                            
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()            
        if cur_mes.rowcount  >  0 :
            for row in rows:  # 202029
                db_ver = row[0].upper()
        
        if stemp.upper() != db_ver :            
            #os.system(update_full_name + " " + program_name)
            #subprocess.call(update_full_name + " " + program_name)
            
            reply = QMessageBox.question(self, 'Warning Message', program_name.upper() + ' ] 프로그램이 old version 입니다.. upgrade 하시겠습니까?' ,
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.No:
                QMessageBox.critical(self, 'Program update Cancel !! ','old version 프로그램 종료합니다.')                        
                sys.exit(0)
                return False
            else :    
                self.resetFunction('ini')
                result = subprocess.run(update_full_name + " " + program_name , shell = True)                
                if result.returncode != 0 :
                    QMessageBox.critical(self, 'Program update Fail !! ','old version 프로그램 upgrade 실패하였습니다. IT 팀에 문의하세요.')                        
                    sys.exit(0)
                    
        else :            
            return True
    ####################################    
    def ed_ini(self, mode) :
        
        if mode == "ALL" :
            self.ed_lot.setText('')
            self.ed_qty.setText('')
        
    ##########################    
    def ed_enable(self , mode) :
        if mode == "ALL" :
            self.ed_lot.setEnabled(True)
            self.ed_qty.setEnabled(True)
        
    ###############################                      
    def resetFunction(self, mode) :
        
        global lot_flag
        global qty_flag
        
        self.ed_ini('ALL')
        self.ed_enable('ALL')
        self.ed_lot.setFocus()          
        
        lot_flag = False
        qty_flag = False
        
        if mode == 'error' :
            os.system("TASKKILL /F /IM " + ui_prog)        
        
    #################################
    def save_history(self , sflag ):
        
        try :
            
            conn_mes = cx_Oracle.connect('mesdb')
            cur_mes = conn_mes.cursor()
                        
            sql = "INSERT INTO UPTDAT ( "
            sql = sql + " FACTORY, TABLE_NAME, KEY1, KEY2, DATA1, DATA2, DATA3, UPDATE_TIME, UPDATE_USER_NAME  ) "
            sql = sql + " VALUES ( "
            sql = sql + " 'TEST' , 'BI_UI', '" + self.ed_lot.text() + "' , '" + self.ed_qty.text() + "' , "             
            sql = sql + " '" + sflag + "' , '" + program_type + "' , '" + program_ver + "' , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "
            sql = sql + " 'BI_UI' "            
            sql = sql + " ) "
            
            cur_mes.execute(sql)
            
            conn_mes.commit()
            #####################
            
        except :
            
            conn_mes.close()            
            QMessageBox.critical(self, val_type + 'BI UI Validation Error', ' validation 저장시 에러가 발생하였습니다.')
            self.resetFunction()
            return False                                 
        
        conn_mes.close()
        
        return True;
            
    def lot_check(self) :
        
        global meslot        
        global sOper 
        global sQty
        global lot_flag
        global ui_path
        global ui_prog
        global path
        global full_filename
        
        
        sOper = ""                
        sQty = ""
        lot_flag = False
        
        if self.app_upgrade() == False :
            sys.exit(0)
            return False
        #####################
        
        ###############################
        if os.path.isfile(full_filename):
            pass
        else :
            QMessageBox.critical(self, 'UI File not found !! ',full_filename + ' \n BI UI 실행파일을 찾을 수 없습니다. \n\n 파일 경로 확인해주세요. ')                                    
            self.resetFunction('ini') 
            return
        #########################
        slot = self.ed_lot.text()
        
        conn_mes = cx_Oracle.connect('mesdb')
        cur_mes = conn_mes.cursor()
        sql = "SELECT KSY_GET_LOT_FROM_BRC('" + slot + "') FROM DUAL "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount  ==  0 :             
            QMessageBox.critical(self,'Tcard Validation Error', slot + ' ] MES 에 등록되지 않은 lot 입니다.')            
            conn_mes.close()            
            self.resetFunction('error')  
            return False
        else :    
            for row in rows:  # 202029
                mes_lot = row[0]
                if mes_lot.find('ERROR') > -1:
                    
                    QMessageBox.critical(self,'Validation Error', slot + ' ] MES 에 등록되지 않은 lot 입니다.')                    
                    conn_mes.close()
                    self.resetFunction('error')                      
                    return False
        ###################################        
        cur_mes = conn_mes.cursor()        
        sql = "SELECT OPER, QTY1 FROM WIPLOT WHERE LOT_ID =  '" + mes_lot + "' "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount  ==  0 :            
            QMessageBox.critical(self,'Tcard Validation Error', slot + ' ] MES 에 등록되지 않은 lot 입니다.')            
            conn_mes.close()   
            self.resetFunction('error')           
            return False
        else:             
            for row in rows :
                sOper = row[0]
                sQty = row[1]
                
        if (sOper == "310" or sOper == "323" or sOper == "326")  :
            pass            
        else:
            QMessageBox.critical(self,'Operation Error', 'BI 공정이 아닙니다. MES 공정 확인바랍니다.') 
            self.resetFunction('error')  
            
            return
        #########################            
        self.ed_qty.setFocus()
        
        lot_flag = True
        
        return True
    
    #########################
    def qty_check(self) :
        
        global meslot        
        global sOper 
        global sQty
        global lot_flag
        global ui_path
        global ui_prog
        global path
        global full_filename
                
        #######
        if  lot_flag == False :
            QMessageBox.critical(self,'Lot ID Error', 'lot id 를 입력후 엔터를 클릭해주세요.') 
            self.resetFunction('ini')  
            return
        ####################
        input_qty = self.ed_qty.text()
        
        
        if (sOper == "310" or sOper == "323" or sOper == "326")  :
            pass            
        else:
            QMessageBox.critical(self,'Operation Error', 'BI 공정이 아닙니다. MES 공정 확인바랍니다.') 
            self.resetFunction('error')  
            return
        #########################    
        if str(input_qty) ==  str(sQty) :
            pass
        else :
            QMessageBox.critical(self,'Qty Error', 'MES 수량과 일치하지 않습니다. MES 수량 확인바랍니다.') 
            self.resetFunction('error')  
            return   
            
        #self.save_history(sflag)    
        #########################
        QMessageBox.information(self,'OK', 'BI UI 공정과 수량이 일치합니다. \n' + ui_prog + ' 실행합니다. \n\n OK 버턴을 눌러주세요. ') 
        self.resetFunction('ini') 
        
        os.system("TASKKILL /F /IM " + ui_prog)
        os.chdir(path)
        #subprocess.Popen(ui_prog)
        #os.startfile(ui_prog)
        #threading.thread.start_new_thread(os.system, (ui_prog,))
        #p = subprocess.Popen(ui_prog , shell = True)
        p = subprocess.Popen(ui_prog , shell = True)

        time.sleep(3)
        p.kill()   
        #os.system("TASKKILL /F /IM " + "bi_ui.exe")
        #subprocess.call(ui_prog, shell=True)
        #p.kill()   
            
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