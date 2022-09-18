import time
import datetime
from datetime import date, timedelta
from time import localtime, strftime

from pathlib import Path
import os

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


#from pyglet import Gtk, Gdk, GObject
######################
# 프로그램  version check and update
#os.system("TASKKILL /F /IM label_update.exe")

#C:\Users\82102\Project1\label_validation
#form_class = uic.loadUiType("C:/Users/82102/Project1/label_validation/sip_rohs_tnr.ui")[0]

try:
    form_class = uic.loadUiType("./qul_label_validation.ui")[0]
except:
    form_class = uic.loadUiType("C:/Users/wansoo.kim/python/Project1/label_validation/QUL/qul_label_validation.ui")[0]

######################
global meslot
meslot = ""
global sCustDevice
sCustDevice = ""
global sLead
sLead = ""

global sch_type

global sqty
sgty = ""

global label_standard_qty
label_standard_qty = ""

global sCust
sCust = ""
global val_type
val_type = ""
global partial_qty
partial_qty = 0
global chk_count
chk_count = 0

global count_str
count_str = 0
#####################
global program_type
global program_ver
global program_name

program_type = 'QUL LABEL Validation System' 
program_ver = " - v2.1.1.2" 
program_name = "qul_label_validation"
#################################
global label_lot 

global dic_label_list
dic_label_list = {}
dic_label_list.clear()
global dic_dup_list
dic_dup_list = {}
dic_dup_list.clear()
global lpn_list
lpn_list = []
global sitem_id
global sdate_code
global spart_id
############
# tab1 flag

global flag_user_tab1
global flag_tcard_tab1
global flag_reel_pink_tab1
global flag_reel_2d_tab1
global flag_mbb_pink_tab1
global flag_mbb_2d_tab1

######################
# tab2
global flag_user_tab2
global flag_tcard_tab2
global flag_bin_label_tab2
global flag_2d_tab2
######################
# tab3 
global flag_user_tab3
global flag_tcard_tab3
global flag_mbb_2d_tab3
global flag_box_2d_tab3
####################=====
        
#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        
        self.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon('./python_18894.png'))
        # 버턴에 기능연결
        #self.bt_search.clicked.connect(self.searchFunction)
                
        #self.bt_close.clicked.connect(self.closeFunction)
        #self.tbl_label.verticalHeader().setVisible(False) # 행번호 안나오게 하는 코드        
        ################
        # tab1
        self.ed_user_tab1.returnPressed.connect(self.check_user_all)   
        self.ed_tcard_tab1.returnPressed.connect(self.check_tcard_all)
        
        self.ed_reel_pink_tab1.returnPressed.connect(self.check_pink_all)
        self.ed_reel_2d_tab1.returnPressed.connect(self.check_2d_all)
        self.ed_mbb_pink_tab1.returnPressed.connect(self.check_pink_all)
        self.ed_mbb_2d_tab1.returnPressed.connect(self.check_2d_all)
        #########################                
        # tab2
        self.ed_user_tab2.returnPressed.connect(self.check_user_all)   
        self.ed_tcard_tab2.returnPressed.connect(self.check_tcard_all)
        self.ed_bin_label_tab2.returnPressed.connect(self.check_pink_all)
        self.ed_2d_tab2.returnPressed.connect(self.check_2d_all)        
        #########################
        # tab3
        self.ed_user_tab3.returnPressed.connect(self.check_user_all)   
        self.ed_tcard_tab3.returnPressed.connect(self.check_tcard_all)
        self.ed_mbb_2d_tab3.returnPressed.connect(self.check_2d_all)        
        self.ed_box_2d_tab3.returnPressed.connect(self.check_2d_all)
        
        ##############################
        self.bt_reset.clicked.connect(self.resetFunction)        
        self.tabWidget.currentChanged.connect(self.tab_chk)
        #######################
        
        # tab1    
        header_item = QTableWidgetItem("No.")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(0, header_item)
        
        header_item = QTableWidgetItem("User_ID") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(1, header_item)
        
        header_item = QTableWidgetItem("T-card") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(2, header_item)
        
        header_item = QTableWidgetItem("REEL PINK") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(3, header_item)
        
        header_item = QTableWidgetItem("REEL 2D") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(4, header_item)
        
        header_item = QTableWidgetItem("MBB PINK") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(5, header_item)        
        
        header_item = QTableWidgetItem("MBB 2D") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(6, header_item)        
        
        header_item = QTableWidgetItem("Create Time") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab1.setHorizontalHeaderItem(7, header_item)        
        ########################
        # tab2
        header_item = QTableWidgetItem("No.")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab2.setHorizontalHeaderItem(0, header_item)
        
        header_item = QTableWidgetItem("User_ID") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab2.setHorizontalHeaderItem(1, header_item)
        
        header_item = QTableWidgetItem("T-card") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab2.setHorizontalHeaderItem(2, header_item)
        
        header_item = QTableWidgetItem("BIN Label") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab2.setHorizontalHeaderItem(3, header_item)
        
        header_item = QTableWidgetItem("2D") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab2.setHorizontalHeaderItem(4, header_item)
        
        header_item = QTableWidgetItem("Create Time") 
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab2.setHorizontalHeaderItem(5, header_item)
               
        ########################   
        # tab3
        header_item = QTableWidgetItem("No.")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab3.setHorizontalHeaderItem(0, header_item)
        
        header_item = QTableWidgetItem("User_ID")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab3.setHorizontalHeaderItem(1, header_item)
        
        header_item = QTableWidgetItem("T-card")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab3.setHorizontalHeaderItem(2, header_item)
        
        header_item = QTableWidgetItem("MBB 2D")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab3.setHorizontalHeaderItem(3, header_item)     
           
        header_item = QTableWidgetItem("BOX 2D")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab3.setHorizontalHeaderItem(4, header_item)
        
        header_item = QTableWidgetItem("Create Time")         
        header_item.setBackground(QtGui.QColor(85, 255, 255))
        self.tbl_tab3.setHorizontalHeaderItem(5, header_item)           
        #####################        
        self.setWindowTitle(program_type + program_ver)
        ####################
             
        # 셀 복사가 안되서 주석처리
        #self.tbl_lic.setSelectionBehavior(QAbstractItemView.SelectRows)  # Row 단위 선택
        #self.tbl_lic.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 셀 edit 금지
        ##########################
        # in time table
        self.tbl_tab1.setColumnWidth(0, 30)
        self.tbl_tab1.setColumnWidth(1, 70)
        self.tbl_tab1.setColumnWidth(2, 100)
        self.tbl_tab1.setColumnWidth(3, 200)
        self.tbl_tab1.setColumnWidth(4, 400)
        self.tbl_tab1.setColumnWidth(5, 200)
        self.tbl_tab1.setColumnWidth(6, 400)        
        self.tbl_tab1.setColumnWidth(7, 150)        
        #################################
        # tab2
        self.tbl_tab2.setColumnWidth(0, 30)
        self.tbl_tab2.setColumnWidth(1, 70)
        self.tbl_tab2.setColumnWidth(2, 100)
        self.tbl_tab2.setColumnWidth(3, 200)
        self.tbl_tab2.setColumnWidth(4, 400)
        self.tbl_tab2.setColumnWidth(5, 150)
        ##########################
        # tab3
        self.tbl_tab3.setColumnWidth(0, 30)
        self.tbl_tab3.setColumnWidth(1, 70)
        self.tbl_tab3.setColumnWidth(2, 100)
        self.tbl_tab3.setColumnWidth(3, 250)
        self.tbl_tab3.setColumnWidth(4, 350)
        self.tbl_tab3.setColumnWidth(5, 150)
        
        ##################
        #self.error_return()
        self.error_tab1_return('ALL')
        self.error_tab2_return('ALL')
        self.error_tab3_return('ALL')        
        self.resetFunction()
        ######################
        self.ed_user_tab1.setFocus()
        self.tabWidget.setCurrentIndex(0)
        #######################
        
    ######################
    #program_type = 'INT TRAY Validation System' 
    #program_ver = " - v0.0.0.1" 
    #10.86.254.36
    #test / hp2035
    def msgbox_ok(self, title, message):
        #msg_str = '<h1 style="font-size:17pt; color: #4e9a06;">' + message + '</h1>'
        message = 'OK ------------ \n' + message
        message = message.replace('\n' , '<br>')
        msg_str = '<p style="font-size:15pt; color: mediumblue; text-align:center;border:0;">' + message + '</p>'
                    
        msg = QMessageBox(9, title, msg_str, QMessageBox.Ok)
        msg.setStyleSheet("QLabel {min-width: 600px; min-height: 200px;}")
        msg.exec()
    
    def msgbox_critical(self, title, message):
        message = 'ERROR !!!!!!!!!!!!!!!!!!!! \n' + message
        message = message.replace('\n' , '<br>')
        msg_str = '<h1 style="font-size:15pt; color: #cc0000; text-align:center;border:0;">' + message + '</h1>'
                    
        msg = QMessageBox(9, title, msg_str, QMessageBox.Ok)
        msg.setStyleSheet("QLabel {min-width: 600px; min-height: 200px;}")
        msg.exec()    
        
    def app_upgrade(self) :
        
        global program_type
        global program_ver
        global program_name
        
        stemp = program_ver.split('-')
        stemp = stemp[-1].strip()
        cur_path = os.getcwd()
        
        update_full_name =  os.path.join(cur_path, "label_update.exe")     
        #update_full_name = "C:/Users/wansoo.kim/python/Project1/label_validation/instantclient_21_3/label_update.exe"
        
        conn_mes = cx_Oracle.connect('MPMGR/sckmes0$@210.118.145.240:1521/cpkmes1')
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
            
            reply = QMessageBox.question(self, 'Warning Message', program_name.upper() + ' ] 프로그램이 old version 입니다.. upgrade 하시겠습니까?' ,
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.No:
                QMessageBox.critical(self, 'Program update Cancel !! ','old version 프로그램 종료합니다.')                        
                sys.exit(0)
                return False
            else :    
                self.resetFunction()
                result = subprocess.run(update_full_name + " " + program_name , shell = True)                
                if result.returncode != 0 :
                    QMessageBox.critical(self, 'Program update Fail !! ','old version 프로그램 upgrade 실패하였습니다. IT 팀에 문의하세요.')                        
                    sys.exit(0)
                    
        else :            
            return True
    ####################################    
    def ed_tab1_ini(self, mode) :
        
        if mode == "ALL" :
            self.ed_user_tab1.setText('')
            self.ed_tcard_tab1.setText('')
            #--------------------------------
            self.ed_user_tab1.setEnabled(True)
            self.ed_tcard_tab1.setEnabled(True)
        
        self.ed_reel_pink_tab1.setText('')
        self.ed_reel_2d_tab1.setText('')        
        self.ed_mbb_pink_tab1.setText('')        
        self.ed_mbb_2d_tab1.setText('')
        #-----------------------
        self.ed_reel_pink_tab1.setEnabled(True)
        self.ed_reel_2d_tab1.setEnabled(True)        
        self.ed_mbb_pink_tab1.setEnabled(True)
        self.ed_mbb_2d_tab1.setEnabled(True)                
        
    ###############################
    
    def ed_tab2_ini(self , mode) :
        if mode == "ALL" :            
            self.ed_user_tab2.setText('')
            self.ed_tcard_tab2.setText('')
            #-------------------------
            self.ed_user_tab2.setEnabled(True)
            self.ed_tcard_tab2.setEnabled(True)
            
        
        self.ed_bin_label_tab2.setText('')
        self.ed_2d_tab2.setText('')        
        #---------------------------------
        self.ed_bin_label_tab2.setEnabled(True)
        self.ed_2d_tab2.setEnabled(True)  
                
    ####################################    
    def ed_tab3_ini(self, mode) :
        if mode == "ALL" :
            self.ed_user_tab3.setText('')
            self.ed_tcard_tab3.setText('')
            #--------------------------
            self.ed_user_tab3.setEnabled(True)
            self.ed_tcard_tab3.setEnabled(True)
            
        #------------------    
        self.ed_mbb_2d_tab3.setText('')         
        self.ed_box_2d_tab3.setText('')
        #----------------------------
        self.ed_mbb_2d_tab3.setEnabled(True)        
        self.ed_box_2d_tab3.setEnabled(True)
        
    ###############################  
    def tab1_flag_ini(self, mode)  :
        
        global flag_user_tab1
        global flag_tcard_tab1
        global flag_reel_pink_tab1
        global flag_reel_2d_tab1
        global flag_mbb_pink_tab1
        global flag_mbb_2d_tab1
        
        if mode == "ALL" :
            flag_user_tab1 = False
            flag_tcard_tab1 = False
        
        flag_reel_pink_tab1 = False 
        flag_reel_2d_tab1 = False 
        flag_mbb_pink_tab1 = False 
        flag_mbb_2d_tab1 = False
                     
    ###############################  
    def tab2_flag_ini(self , mode)  :
        
        global flag_user_tab2
        global flag_tcard_tab2
        global flag_bin_label_tab2    
        global flag_2d_tab2
        
        #################
        if mode == "ALL" :
            flag_user_tab2 = False
            flag_tcard_tab2 = False
        
        flag_bin_label_tab2 = False   
        flag_2d_tab2 = False
        
    ###############################  
    def tab3_flag_ini(self, mode)  :
        global flag_user_tab3
        global flag_tcard_tab3
        global flag_mbb_2d_tab3
        global flag_box_2d_tab3
        #################
        if mode == "ALL" :
            flag_user_tab3 = False
            flag_tcard_tab3 = False
        
        flag_mbb_2d_tab3 = False
        flag_box_2d_tab3 = False
        
    def error_tab1_return(self , mode) :
                
        self.tab1_flag_ini(mode)
        self.ed_tab1_ini(mode)
        
        if mode == 'ALL' :
            self.ed_user_tab1.setFocus()
        else :
            self.ed_reel_pink_tab1.setFocus()    
        return
    #######################
    def error_tab2_return(self, mode) :
                
        self.tab2_flag_ini(mode)
        self.ed_tab2_ini(mode)
        
        if mode == 'ALL' :
            self.ed_user_tab2.setFocus()
        else :
            self.ed_bin_label_tab2.setFocus()    
        return
    #####################
    def error_tab3_return(self, mode) :
                
        self.tab3_flag_ini(mode)
        self.ed_tab3_ini(mode)
        
        if mode == 'ALL' :
            self.ed_user_tab3.setFocus()
        else :
            self.ed_mbb_2d_tab3.setFocus()    
        return
    #####################        
    def tab_chk(self) :
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        
        if currentIndex == 0 :
            self.ed_user_tab1.setFocus()
        #if val_type == "IN TIME" :
        if currentIndex == 1 :
            self.ed_user_tab2.setFocus()
        #if val_type == "OUT TIME" :
        if currentIndex == 2 :
            self.ed_user_tab3.setFocus()  
    #####################        
    def tab_chk_add(self) :
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        
        if currentIndex == 0 :
            self.ed_reel_pink_tab1.setFocus()
        #if val_type == "IN TIME" :
        if currentIndex == 1 :
            self.ed_bin_label_tab2.setFocus()
        #if val_type == "OUT TIME" :
        if currentIndex == 2 :
            self.ed_mbb_2d_tab3.setFocus()  
    #####################                          
    def resetFunction(self) :
        
        global dic_label_list
        global dic_dup_list
        
        self.tbl_tab1.clearContents()
        self.tbl_tab1.setRowCount(0)
        self.tbl_tab2.clearContents()
        self.tbl_tab2.setRowCount(0)
        self.tbl_tab3.clearContents()
        self.tbl_tab3.setRowCount(0)
        
        self.ed_count.setText('')
        ##########
        dic_label_list = {}
        dic_label_list.clear()
        dic_dup_list = {}
        dic_dup_list.clear()
        ############
        
        self.ed_tab1_ini('ALL')        
        self.error_tab1_return('ALL')
        #################
        self.ed_tab2_ini('ALL')        
        self.error_tab2_return('ALL')        
        ##############################        
        self.ed_tab3_ini('ALL')        
        self.error_tab3_return('ALL')                
        self.tab_chk()    
    #################################
    def resetFunction_add(self) :
        
        global dic_label_list
        global dic_dup_list
        global count_str
        
        self.tbl_tab1.clearContents()
        self.tbl_tab1.setRowCount(0)
        self.tbl_tab2.clearContents()
        self.tbl_tab2.setRowCount(0)
        self.tbl_tab3.clearContents()
        self.tbl_tab3.setRowCount(0)
        
        self.ed_count.setText(str(count_str))
        ##########
        dic_label_list = {}
        dic_label_list.clear()
        dic_dup_list = {}
        dic_dup_list.clear()
        ############
        
        self.ed_tab1_ini('ADD')        
        self.error_tab1_return('ADD')
        #################
        self.ed_tab2_ini('ADD')        
        self.error_tab2_return('ADD')        
        ##############################        
        self.ed_tab3_ini('ADD')        
        self.error_tab3_return('ADD')                
        self.tab_chk_add()    
    #################################
    
    def save_history(self , dic_list , opt1 ):
        
        global meslot
        global val_type
        global program_type
        global program_ver
        global sCust
        
        try :
            
            conn_sip = cx_Oracle.connect('rts/rts4sck0@10.86.255.11:1521/sipprd')
            cur_sip = conn_sip.cursor()
            
            #for k in dic_tnr_box_list.keys() :
            for k in dic_list.keys() :
                souttime_data = dic_list.get(k)
                souttime_data = souttime_data.split('~')
                
                screate_on = souttime_data[opt1]
                
                #tbl_01 + '~' + tbl_02 + '~' + tbl_03 + '~' + tbl_04 + '~' + tbl_05 + '~' + tbl_06 + '~' + tbl_07 + '~' + tbl_08 + '~' + tbl_09 + '~' + tbl_10 + '~' + tbl_11
                #    0             1               2              
                sql = "INSERT INTO T_LABEL_VALIDATION_HISTORY ( "
                sql = sql + " HISTORY_ID, LOT_ID, CUST_ID, RESV_FIELD1, RESV_FIELD2, RESV_FIELD3, RESV_FIELD4, RESV_FIELD5, RESV_FIELD6, RESV_FIELD7, "
                sql = sql + " RESV_FIELD8, RESV_FIELD9, RESV_FIELD10, RESV_FIELD11, VALIDATION_TYPE, CREATED_ON, USER_ID, PROGRAM_TYPE) "
                sql = sql + " VALUES ( "
                sql = sql + " T_LABEL_VALIDATION_HISTORY_SEQ.NEXTVAL , '" + meslot + "' , '" + sCust + "' "  
                sql = sql + " , '" + souttime_data[2] + "' , '" + souttime_data[3] + "' , '" + souttime_data[4] + "' , '" + souttime_data[5] + "' "
                #                      RESV_FIELD1               RESV_FIELD2                 RESV_FIELD3               RESV_FIELD4
                sql = sql + " , '" + souttime_data[6] + "' , '" + souttime_data[7] + "' , '" + souttime_data[8] + "' , '" + souttime_data[9]  + "' , '" + souttime_data[10] + "' "
                #                     RESV_FIELD5                 RESV_FIELD6                   RESV_FIELD7                RESV_FIELD8                 RESV_FIELD9
                sql = sql + " , '" + souttime_data[11] + "' , '" + souttime_data[12] + "' " 
                sql = sql + " , '" + val_type + "' , '" + screate_on + "' , '" + souttime_data[0] + "' , '" + program_type + program_ver + "' "
                sql = sql + " ) "
                
                cur_sip.execute(sql)
                
            
            conn_sip.commit()
            #####################
            #####################
            if val_type == "REEL" or val_type == "TRAY"  :
                conn_mes = cx_Oracle.connect('MPMGR/sckmes0$@210.118.145.240:1521/cpkmes1')
                cur_mes = conn_mes.cursor()
                sql = "SELECT KEY1 FROM WIP_SITDEF2 "
                sql = sql + "WHERE  FACTORY = 'MESPLUS' "
                sql = sql + "AND DATA_TYPE = 'BAKE_CON' "
                sql = sql + "AND KEY1 = '" + meslot + "' "
                            
                cur_mes.execute(sql)
                rows = cur_mes.fetchall()            
                if cur_mes.rowcount  >  0 :
                    sql = "UPDATE MPMGR.WIP_SITDEF2@CPKMES1 "
                    sql = sql + "SET DATA9 = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS') "
                    sql = sql + "WHERE  FACTORY = 'MESPLUS' "
                    sql = sql + "AND DATA_TYPE = 'BAKE_CON' "
                    sql = sql + "AND KEY1 = '" + meslot + "' "
                    cur_mes.execute(sql)
                    conn_mes.commit()
                
                conn_mes.close()      
                #########################  
            if val_type == "BOX"  : 
                conn_mes = cx_Oracle.connect('MPMGR/sckmes0$@210.118.145.240:1521/cpkmes1')
                cur_mes = conn_mes.cursor()
                sql = "SELECT KEY1 FROM WIP_SITDEF2 "
                sql = sql + "WHERE  FACTORY = 'MESPLUS' "
                sql = sql + "AND DATA_TYPE = 'BAKE_CON' "
                sql = sql + "AND KEY1 = '" + meslot + "' "
                            
                cur_mes.execute(sql)
                rows = cur_mes.fetchall()
                if cur_mes.rowcount  >  0 :
                    sql = "UPDATE MPMGR.WIP_SITDEF2@CPKMES1 "
                    sql = sql + "SET DATA10 = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS') "
                    sql = sql + "WHERE  FACTORY = 'MESPLUS' "
                    sql = sql + "AND DATA_TYPE = 'BAKE_CON' "
                    sql = sql + "AND KEY1 = '" + meslot + "' "
                    cur_mes.execute(sql)
                    conn_mes.commit()                
                conn_mes.close()     
                #########################   
            
            if val_type == "BOX"  :
                # NEW TABLE INSERT
                sql = "SELECT LOT_ID FROM LABEL_VALIDATION_TBL "
                sql = sql + "WHERE LOT_ID = '" + meslot + "' "
                            
                cur_sip.execute(sql)
                rows = cur_sip.fetchall()            
                if cur_sip.rowcount  >  0 :
                    sql = "UPDATE LABEL_VALIDATION_TBL "
                    sql = sql + "SET VAL_FLAG = 'Y' , UPDATE_TIME = TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS') , USER_ID = '" + program_type + "' " 
                    sql = sql + "WHERE LOT_ID = '" + meslot + "' "                
                    cur_sip.execute(sql)
                    conn_sip.commit()
                else :
                    sql = "INSERT INTO LABEL_VALIDATION_TBL ( "
                    sql = sql + " LOT_ID, VAL_FLAG ,CREATE_TIME,  USER_ID) "
                    sql = sql + " VALUES ( "
                    sql = sql + "'" + meslot + "' , 'Y' , TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS') ,  '" + program_type + "' "                  
                    sql = sql + " ) "
                    cur_sip.execute(sql)
                    conn_sip.commit()
             
            #########################
        except :
            
            conn_sip.close()   
                     
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 라벨 validation  저장시 에러가 발생하였습니다. \n validation 을 다시 진행하세요.')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 라벨 validation  저장시 에러가 발생하였습니다. \n validation 을 다시 진행하세요.'
            self.msgbox_critical(title, message)

            self.resetFunction_add()
            return False                                 
        
        conn_sip.close()
        
        return True;
    
    ###################################################
    def tab1_complete(self) :
        
        global flag_user_tab1
        global flag_tcard_tab1
        global flag_reel_pink_tab1
        global flag_reel_2d_tab1
        global flag_mbb_pink_tab1
        global flag_mbb_2d_tab1

        global dic_label_list
        global dic_dup_list
        
        global chk_count

        save_history_flag = False
        #################################
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        
        #################################
        if (flag_user_tab1 == True) and  (flag_tcard_tab1  == True) and (flag_reel_pink_tab1 == True)  and \
           (flag_reel_2d_tab1 == True) and  (flag_mbb_pink_tab1  == True) and  (flag_mbb_2d_tab1  == True) :
            
            now = datetime.datetime.now()
            sCreated_on = now.strftime('%Y-%m-%d %H:%M:%S')
                      
            #########################
            srow = self.tbl_tab1.rowCount() 
            tbl_00 = str(srow)
            tbl_01 = self.ed_user_tab1.text()     # 0
            tbl_02 = meslot                  # 1 
            tbl_03 = self.ed_reel_pink_tab1.text()  #  2 tray bundle
            
            tbl_04 = self.ed_reel_2d_tab1.text()  # 3 mbb lot
            tbl_05 = self.ed_mbb_pink_tab1.text()    # 4 mbb mm
            tbl_06 = self.ed_mbb_2d_tab1.text()    # 4 mbb mm
            tbl_07 = sCreated_on
            tbl_08 = " "    # 7 mbb box
            tbl_09 = " "
            tbl_10 = " "
            tbl_11 = " "
            tbl_12 = " "
            tbl_13 = " "
            tbl_14 = " "
            ###################### 
            cur_label_dat = tbl_01 + '~' + tbl_02 + '~' + tbl_03 + '~' + tbl_04 + '~' + tbl_05 + '~' + tbl_06 + '~' + tbl_07 + '~' + tbl_08 + '~' + tbl_09 + '~' + tbl_10 + '~' + tbl_11 + '~' + tbl_12 + '~' + tbl_13 + '~' + tbl_14
                #          0 user          1 meslot     2reel label     3 mbb label   4 mbb lot       5 mbb mm      6 mbb qty       7 mbb date      8 mbb box    9 created 
            label_dat = tbl_02 + '~' + tbl_03 + '~' + tbl_04 + '~' + tbl_05 + '~' + tbl_06
            ####################
            
            if srow > 0 :
                for k in dic_dup_list.keys() :
                    old_dup_data = dic_dup_list.get(k)
                    split_old_dup_data = old_dup_data.split('~')
                    split_label_dat = label_dat.split('~')
                    
                    
                    if (old_dup_data == label_dat) :
                        #QMessageBox.critical(self,'Validation Error', ' REELL LABEL  \n [' + cur_label_dat + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                        #    '라벨 중복 여부를 확인하세요.!!')
                        
                        title = 'Validation Error'
                        message = ' REELL LABEL  \n [' + cur_label_dat + '] \n 는 이미 스캔 완료되었습니다. \n'
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    #-----------------------------
                    if split_old_dup_data[2] != split_old_dup_data[4] :
                        #QMessageBox.critical(self,'Validation Error', ' REEL 2D 와 MBB 2D 가 일치하지 않습니다. !! ')
                        
                        title = 'Validation Error'
                        message = 'REEL 2D 와 MBB 2D 가 일치하지 않습니다. !! '
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    if split_old_dup_data[1] == split_old_dup_data[3] :
                        #QMessageBox.critical(self,'Validation Error', ' REEL PINK 와 MBB PINK 가 중복됩니다. !! ')
                        
                        title = 'Validation Error'
                        message = 'REEL PINK 와 MBB PINK 가 중복됩니다. !! '
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    #-----------------------------------
                    if (split_label_dat[1] == split_old_dup_data[1]) or (split_label_dat[1] == split_old_dup_data[3]) :                        
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[1] + ' ] REEL PINK 라벨은 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[1] + ' ] REEL PINK 라벨은 이미 스캔 완료되었습니다. !! '
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    if (split_label_dat[3] == split_old_dup_data[1]) or (split_label_dat[3] == split_old_dup_data[3]) :
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[3] + ' ]MBB PINK 라벨은 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[3] + ' ]MBB PINK 라벨은 이미 스캔 완료되었습니다. !! '
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    if (split_label_dat[2] == split_old_dup_data[2]) or (split_label_dat[2] == split_old_dup_data[4]) :                        
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[2] + ' ] REEL 2D 라벨은 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[2] + ' ] REEL 2D 라벨은 이미 스캔 완료되었습니다. !! '
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    if (split_label_dat[4] == split_old_dup_data[2]) or (split_label_dat[4] == split_old_dup_data[4]) :
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[4] + ' ]MBB 2D 라벨은 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[4] + ' ]MBB 2D 라벨은 이미 스캔 완료되었습니다. !! '
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    
            ##################
            dic_label_list[tbl_00] = cur_label_dat
            dic_dup_list[tbl_00] = label_dat        
            ####################            
            label_count = int(self.ed_count.text()) -1
            self.ed_count.setText(str(label_count)) 
            ####################   
            if int(label_count) == 0  :
                
                ## label 개수 완료후 history 저장
                if self.save_history(dic_label_list, 6) == True :
                    save_history_flag = True                
                else :                    
                    QMessageBox.critical(self,'Validation Error', ' REEL LABEL data 저장시 에러발생하였습니다.. \n' + \
                            '라벨을 다시 스캔해 주세요. !!')
                    
                    self.resetFunction_add()
                    return False
            
            else :                
                self.ed_tab1_ini('add')
                
                self.tab1_flag_ini('add')
                self.ed_reel_pink_tab1.setFocus()
                                
            ################            
            self.tbl_tab1.insertRow(srow)                        
            self.tbl_tab1.setItem(srow,0,QTableWidgetItem(tbl_00))   # seq
            self.tbl_tab1.setItem(srow,1,QTableWidgetItem(tbl_01))  # user id            
            self.tbl_tab1.setItem(srow,2,QTableWidgetItem(tbl_02))   # mes lot
            self.tbl_tab1.setItem(srow,3,QTableWidgetItem(tbl_03))   # 1ST ROW
            self.tbl_tab1.setItem(srow,4,QTableWidgetItem(tbl_04))      # 2ND ROW
            self.tbl_tab1.setItem(srow,5,QTableWidgetItem(tbl_05))      # 2D
            self.tbl_tab1.setItem(srow,6,QTableWidgetItem(tbl_06))      # 2D
            self.tbl_tab1.setItem(srow,7,QTableWidgetItem(tbl_07))      # 2D
            ############################
            
            if (flag_mbb_2d_tab1 == True) and (save_history_flag == True) and (label_count == 0) :                                
                #QMessageBox.information(self, 'REEL Validation Complete', 'REEL validation check 완료하였습니다.')
                title = 'REEL Validation Complete'
                message = 'REEL validation check 완료하였습니다.'
                self.msgbox_ok(title, message)
                
                self.resetFunction()
        else :
            #QMessageBox.critical(self,'Validation Error', ' In Time data 중 승인되지 않은 data 가 있습니다. ')                                        
            #QMessageBox.critical(self,'Validation Error', ' REEL validation check 중 승인되지 않은 data 가 있습니다. ')
            
            title = 'Validation Error'
            message = 'REEL validation check 중 승인되지 않은 data 가 있습니다. '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False 
        
        return True  
    ##########################
    def tab2_complete(self) :
        # mbb        
        global flag_user_tab2
        global flag_tcard_tab2
        global flag_bin_label_tab2
        global flag_2d_tab2
         
        global dic_label_list
        global dic_dup_list

        save_history_flag = False        
        #################################
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        #################################
        if (flag_user_tab2 == True) and  (flag_tcard_tab2  == True) and (flag_bin_label_tab2 == True) and (flag_2d_tab2 == True) :
            
            now = datetime.datetime.now()
            sCreated_on = now.strftime('%Y-%m-%d %H:%M:%S')
                      
            #########################
            srow = self.tbl_tab2.rowCount() 
            tbl_00 = str(srow)
            tbl_01 = self.ed_user_tab2.text()     # 0
            tbl_02 = meslot 
            # 1 
            tbl_03 = self.ed_bin_label_tab2.text()  #  2 tray bundle            
            tbl_04 = self.ed_2d_tab2.text() # 3 mbb lot
            tbl_05 = sCreated_on
            tbl_06 = " "
            tbl_07 = " "
            tbl_08 = " "
            tbl_09 = " " 
            tbl_10 = " "
            tbl_11 =  " "
            tbl_12 = " "
            tbl_13 = " "
            tbl_14 = " "
            ###################### 
            cur_label_dat = tbl_01 + '~' + tbl_02 + '~' + tbl_03 + '~' + tbl_04 + '~' + tbl_05 + '~' + tbl_06 + '~' + tbl_07 + '~' + tbl_08 + '~' + tbl_09 + '~' + tbl_10 + '~' + tbl_11 + '~' + tbl_12 + '~' + tbl_13 + '~' + tbl_14
                #          0 user          1 meslot     2reel label     3 mbb label   4 mbb lot       5 mbb mm      6 mbb qty       7 mbb date      8 mbb box    9 created 
            label_dat = tbl_02 + '~' + tbl_03 + '~' + tbl_04 
                #       0 meslot      1 reel pink   2 mbb pink      3 reel 1st    4 reel 2nd       5 ree 2d      6 mbb 1st      7 mbb2nd         8 mbb2d   
            ####################            
            
            if srow > 0 :
                for k in dic_dup_list.keys() :
                    old_dup_data = dic_dup_list.get(k)
                    split_old_dup_data = old_dup_data.split('~')
                    split_label_dat = label_dat.split('~')
                    
                    if (old_dup_data == label_dat) :
                        #QMessageBox.critical(self,'Validation Error', ' TRAY Label \n [' + cur_label_dat + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                        #    '라벨 중복 여부를 확인하세요.!!')
                        
                        title = 'Validation Error'
                        message = ' TRAY Label \n [' + cur_label_dat + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                            '라벨 중복 여부를 확인하세요.!!'
                        
                        self.msgbox_critical(title, message)

                        self.resetFunction_add()
                        return False
                    #----------------------------------
                    # 중복체크
                    # 1row 는 동일, 2row, 2d 에 seq 가 중복되면 안됨
                    if (split_label_dat[1] == split_old_dup_data[1]) :
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[1] + ' ] TRAY BIN LABEL 은 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[1] + ' ] TRAY BIN LABEL 은 이미 스캔 완료되었습니다. !! \n ' + '라벨 중복 여부를 확인하세요.!!'                        
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    if (split_label_dat[2] == split_old_dup_data[2]) :
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[2] + ' ] TRAY 2D LABEL 은 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[2] + ' ] TRAY 2D LABEL 은 이미 스캔 완료되었습니다. !! \n'  + '라벨 중복 여부를 확인하세요.!!'                     
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                                            
            ##################
            dic_label_list[tbl_00] = cur_label_dat
            dic_dup_list[tbl_00] = label_dat        
            ####################            
            label_count = int(self.ed_count.text()) -1
            self.ed_count.setText(str(label_count)) 
            ####################   
            if int(label_count) == 0  :
                
                ###################################
                if int(self.tbl_tab2.rowCount())+1 != int(chk_count) :
                    #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' Label 의 수량이 MES Label data 의 box 수량과 일치하지 않습니다. !!')                        
                    
                    title = val_type + 'Validation Error'
                    message = val_type + ' Label 의 수량이 MES Label data 의 box 수량과 일치하지 않습니다. !!'      
                    self.msgbox_critical(title, message)
                    
                    self.resetFunction_add()
                    return
                ########################                
                ## label 개수 완료후 history 저장
                if self.save_history(dic_label_list, 4) == True :
                    save_history_flag = True                
                else :                    
                    #QMessageBox.critical(self,'Validation Error', ' TRAY data 저장시 에러발생하였습니다.. \n' + \
                    #        '라벨을 다시 스캔해 주세요. !!')
                    
                    title = 'Validation Error'
                    message = ' TRAY data 저장시 에러발생하였습니다.. \n' + '라벨을 다시 스캔해 주세요. !!'
                    self.msgbox_critical(title, message)
                    
                    self.resetFunction_add()
                    return False
            
            else :                
                self.ed_tab2_ini('add')                
                self.tab2_flag_ini('add')
                self.ed_bin_label_tab2.setFocus()
                                
            ################            
            self.tbl_tab2.insertRow(srow)                        
            self.tbl_tab2.setItem(srow,0,QTableWidgetItem(tbl_00))   # seq
            self.tbl_tab2.setItem(srow,1,QTableWidgetItem(tbl_01))  # user id            
            self.tbl_tab2.setItem(srow,2,QTableWidgetItem(tbl_02))   # mes lot
            self.tbl_tab2.setItem(srow,3,QTableWidgetItem(tbl_03))   # bundle
            self.tbl_tab2.setItem(srow,4,QTableWidgetItem(tbl_04))   # bundle
            self.tbl_tab2.setItem(srow,5,QTableWidgetItem(tbl_05))   # bundle
            
            
            if (flag_2d_tab2 == True) and (save_history_flag == True) and (label_count == 0) :                                
                #QMessageBox.information(self, 'TRAY Validation Complete', 'TRAY validation 을 완료하였습니다.')
                
                title = 'TRAY Validation Complete'
                message = 'TRAY validation 을 완료하였습니다.'
                self.msgbox_ok(title, message)

                self.resetFunction()
        else :
            #QMessageBox.critical(self,'Validation Error', ' In Time data 중 승인되지 않은 data 가 있습니다. ')                                        
            #QMessageBox.critical(self,'Validation Error', ' TRAY validation 중 승인되지 않은 data 가 있습니다. ')
            
            title = 'Validation Error'
            message = ' TRAY validation 중 승인되지 않은 data 가 있습니다. '            
            self.msgbox_critical(title, message)

            self.resetFunction_add()
            return False 
        
        return True  
    ##########################
    ##########################
    def tab3_complete(self) :
        # mbb
        
        global flag_user_tab3     
        global flag_tcard_tab3    

        global flag_mbb_2d_tab3
        global flag_box_2d_tab3
 
        global dic_label_list
        global dic_dup_list
        global meslot
        
        save_history_flag = False
        #################################
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        #################################
        if (flag_user_tab3 == True) and  (flag_tcard_tab3  == True) and (flag_mbb_2d_tab3  == True) and (flag_box_2d_tab3 == True)     :
            
            now = datetime.datetime.now()
            sCreated_on = now.strftime('%Y-%m-%d %H:%M:%S')
                      
            #########################
            srow = self.tbl_tab3.rowCount() 
            tbl_00 = str(srow)
            tbl_01 = self.ed_user_tab3.text()     # 0
            tbl_02 = meslot                  # 1 
            tbl_03 = self.ed_mbb_2d_tab3.text()     # 4 mbb mm
            tbl_04 = self.ed_box_2d_tab3.text()# 5 mbb qty
            tbl_05 = sCreated_on
            tbl_06 = " "
            tbl_07 = " "
            tbl_08 = " "            
            tbl_09 = " "
            tbl_10 = " "
            tbl_11 = " "
            tbl_12 = " "
            tbl_13 = " "
            tbl_14 = " "
            ###################### 
            cur_label_dat = tbl_01 + '~' + tbl_02 + '~' + tbl_03 + '~' + tbl_04 + '~' + tbl_05 + '~' + tbl_06 + '~' + tbl_07 + '~' + tbl_08 + '~' + tbl_09 + '~' + tbl_10 + '~' + tbl_11 + '~' + tbl_12 + '~' + tbl_13 + '~' + tbl_14
                #          0 user          1 meslot     2reel label     3 mbb label   4 mbb lot       5 mbb mm      6 mbb qty       7 mbb date      8 mbb box    9 created 
            label_dat = tbl_02 + '~' + tbl_03 + '~' + tbl_04 
                #       0 meslot       1 reel 1st   2 reel 2nd      3 reel 2d     4 mbb 1st        5 mbb2nd       6 mbb2d
            ####################
            
            if srow > 0 :
                for k in dic_dup_list.keys() :
                    old_dup_data = dic_dup_list.get(k)
                    split_old_dup_data = old_dup_data.split('~')
                    split_label_dat = label_dat.split('~')
                    
                    if (old_dup_data == label_dat) :
                        #QMessageBox.critical(self,'Validation Error', ' BOX Label \n [' + cur_label_dat + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                        #    '라벨 중복 여부를 확인하세요.!!')
                        
                        title = 'Validation Error'
                        message = 'BOX Label \n [' + cur_label_dat + '] \n 는 이미 스캔 완료되었습니다. \n' +  + '라벨 중복 여부를 확인하세요.!!'                            
                        self.msgbox_critical(title, message)

                        self.resetFunction_add()
                        return False
                    #----------------------------------
                    # 중복체크
                    if split_old_dup_data[1] != split_old_dup_data[2] :
                        #QMessageBox.critical(self,'Validation Error', ' BOX - MBB 2D 와 BOX 2D 가 일치하지 않습니다. !! ')
                        
                        title = 'Validation Error'
                        message = 'BOX - MBB 2D 와 BOX 2D 가 일치하지 않습니다. !!'                    
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    if (split_label_dat[1] == split_old_dup_data[1]) or (split_label_dat[1] == split_old_dup_data[2]) :
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[1] + ' ] BOX 2D 는 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[1] + ' ] BOX 2D 는 이미 스캔 완료되었습니다. !! '           
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    if (split_label_dat[2] == split_old_dup_data[1]) or (split_label_dat[2] == split_old_dup_data[2]) :
                        #QMessageBox.critical(self,'Validation Error', split_label_dat[2] + ' ] BOX 2D 는 이미 스캔 완료되었습니다. !! ')
                        
                        title = 'Validation Error'
                        message = split_label_dat[2] + ' ] BOX 2D 는 이미 스캔 완료되었습니다. !! '  
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
            ##################
            dic_label_list[tbl_00] = cur_label_dat
            dic_dup_list[tbl_00] = label_dat        
            ####################            
            label_count = int(self.ed_count.text()) -1
            self.ed_count.setText(str(label_count)) 
            ####################   
            if int(label_count) == 0  :
                ###################################
                if int(self.tbl_tab3.rowCount())+1 != int(chk_count) :
                    #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' Label 의 수량이 MES Label data 의 box 수량과 일치하지 않습니다. !!')                        
                    
                    title = val_type +  'Validation Error'
                    message = val_type + ' Label 의 수량이 MES Label data 의 box 수량과 일치하지 않습니다. !!'
                    self.msgbox_critical(title, message)
                        
                    self.resetFunction_add()
                    return
                ########################
                # 처음에 사번, T-Card Scan후 마지막 2D Scan까지 완료 되었지만 최종 완료하려면 다시 처음으로 돌아와서 T-Card Scan이 필요하기에 한번 더 육안 검사 진행됨.
                
                #time.sleep(2)
                
                while True:
                    
                    text, ok = QInputDialog.getText(self, 'T-CARD SCAN - Assembled in Label 부착 확인', '  *** Assembled in Label 부착 확인 *************************** \n \n  T-CARD SCAN : ')
                    
                    if ok == False :
                        #QMessageBox.critical(self,'Validation Error', ' BOX Label validation 을 다시 진행해주세요.')
                        
                        title = 'Validation Error'
                        message = ' BOX Label validation 을 다시 진행해주세요.'
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                    
                    if text.strip() == ''  :
                        continue
                    if text.strip() == meslot  :
                        break
                    else :
                        #QMessageBox.critical(self,'Validation Error', ' T-card scan lotid 가 일치하지 않습니다 !! BOX Label validation 을 다시 진행해주세요.')
                        
                        title = 'Validation Error'
                        message = ' BOX Label validation 을 다시 진행해주세요.'
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return False
                        break
                                        
                    ################################    
                
                ## label 개수 완료후 history 저장
                if self.save_history(dic_label_list, 4) == True :
                    save_history_flag = True                
                else :                    
                    #QMessageBox.critical(self,'Validation Error', ' REEL_MBB data 저장시 에러발생하였습니다.. \n' + \
                    #        '라벨을 다시 스캔해 주세요. !!')
                    
                    title = 'Validation Error'
                    message = ' REEL_MBB data 저장시 에러발생하였습니다.. \n' + '라벨을 다시 스캔해 주세요. !!'
                    self.msgbox_critical(title, message)
                        
                    self.resetFunction_add()
                    return False
            
            else :                
                self.ed_tab3_ini('add')                
                self.tab3_flag_ini('add')
                self.ed_mbb_2d_tab3.setFocus()
                                
            ################            
            self.tbl_tab3.insertRow(srow)                        
            self.tbl_tab3.setItem(srow,0,QTableWidgetItem(tbl_00))   # seq
            self.tbl_tab3.setItem(srow,1,QTableWidgetItem(tbl_01))  # user id            
            self.tbl_tab3.setItem(srow,2,QTableWidgetItem(tbl_02))   # mes lot
            self.tbl_tab3.setItem(srow,3,QTableWidgetItem(tbl_03))   # bundle
            self.tbl_tab3.setItem(srow,4,QTableWidgetItem(tbl_04))      # mbb lot
            self.tbl_tab3.setItem(srow,5,QTableWidgetItem(tbl_05))      # mbb mm
            
            if (flag_box_2d_tab3 == True) and (save_history_flag == True) and (label_count == 0) :                                
                #QMessageBox.information(self, 'BOX Validation Complete', 'BOX validation 을 완료하였습니다.')
                title = 'BOX Validation Complete'
                message = 'BOX validation 을 완료하였습니다.'
                self.msgbox_ok(title, message)
                
                self.resetFunction()
        else :
            #QMessageBox.critical(self,'Validation Error', ' In Time data 중 승인되지 않은 data 가 있습니다. ')                                        
            #QMessageBox.critical(self,'Validation Error', ' BOX validation 중 승인되지 않은 data 가 있습니다. ')
            
            title = 'Validation Error'
            message = 'BOX validation 중 승인되지 않은 data 가 있습니다. '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False 
        
        return True  
       
    ############################################
    def prefix_chk(self, label_type , spre_val, sed_val,slen):
        global val_flag
        prefix_chk_falg = False
        
        if spre_val != sed_val[0:slen] :
            prefix_chk_falg = False
            val_flag = False
            #QMessageBox.critical(self, label_type + ' Validation Error', label_type + '라벨 Prefix(' +  spre_val + ') 값과 스캔한 라벨의 Prefix 값이 일치하지 않습니다.')
            
            title = label_type + ' Validation Error'
            message = label_type + '라벨 Prefix(' +  spre_val + ') 값과 스캔한 라벨의 Prefix 값이 일치하지 않습니다.'
            self.msgbox_critical(title, message)

        else:
            prefix_chk_falg = True
        
        return prefix_chk_falg        
    ##### 
    def predata_chk_tab1(self, cur_item) :
        
        global flag_user_tab1
        global flag_tcard_tab1
        global flag_reel_pink_tab1
        global flag_reel_2d_tab1
        global flag_mbb_pink_tab1
        global flag_mbb_2d_tab1
                
        if flag_user_tab1 == False :
            #QMessageBox.critical(self,'UserID Validation Error',' USER ID 를 먼저 스캔하세요.')
            
            title = 'UserID Validation Error'
            message = ' USER ID 를 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
                        
            self.ed_user_tab1.setFocus()
            return False
        #---------------------
        if  cur_item == "flag_tcard_tab1"  :   
            return True
        #---------------------    
        if flag_tcard_tab1 == False :
            #QMessageBox.critical(self,'Tcard Validation Error',' TCARD 를 먼저 스캔하세요.')
            
            title = 'Tcard Validation Error'
            message = ' TCARD 를 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_tcard_tab1.setFocus()
            return False
        
        if  cur_item == "flag_reel_pink_tab1"  :   
            return True
        #---------------------        
        if flag_reel_pink_tab1 == False :
            #QMessageBox.critical(self,'REEL PINK Barcode Validation Error',' REEL PINK Barcode 을 먼저 스캔하세요.')
            
            title = 'REEL PINK Barcode Validation Error'
            message = ' REEL PINK Barcode 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_reel_pink_tab1.setFocus()
            return False
        
        if cur_item == "flag_reel_2d_tab1" :
            return True
        
        if flag_reel_2d_tab1 == False :
            #QMessageBox.critical(self,'REEL 2D Barcode Validation Error',' REEL 2D Barcode 을 먼저 스캔하세요.')
            
            title = 'REEL 2D Barcode Validation Error'
            message = ' REEL 2D Barcode 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_reel_2d_tab1.setFocus()
            return False
        
        if cur_item == "flag_mbb_pink_tab1" :
            return True
        if flag_mbb_pink_tab1 == False :
            #QMessageBox.critical(self,'MBB PINK BARCODE Validation Error',' MBB PINK Barcode 을 먼저 스캔하세요.')
            
            title = 'MBB PINK BARCODE Validation Error'
            message = ' MBB PINK Barcode 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_mbb_pink_tab1.setFocus()
            return False
        
        if cur_item == "flag_mbb_2d_tab1" :
            return True
        if flag_mbb_2d_tab1 == False :
            #QMessageBox.critical(self,'MBB 2D BARCODE Validation Error',' MBB 2D Barcode 을 먼저 스캔하세요.')
            
            title = 'MBB 2D BARCODE Validation Error'
            message = ' MBB 2D Barcode 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_mbb_2d_tab1.setFocus()
            return False
        
    ##########################    
    def predata_chk_tab2(self, cur_item) :
        
        global flag_user_tab2
        global flag_tcard_tab2
        global flag_bin_label_tab2
        global flag_2d_tab2
                
        if flag_user_tab2 == False :
            #QMessageBox.critical(self,'UserID Validation Error',' USER ID 를 먼저 스캔하세요.')
            
            title = 'UserID Validation Error'
            message = ' USER ID 를 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_user_tab2.setFocus()
            return False
        #---------------------
        if  cur_item == "flag_tcard_tab2"  :   
            return True
        #---------------------    
        if flag_tcard_tab2 == False :
            #QMessageBox.critical(self,'Tcard Validation Error',' TCARD 를 먼저 스캔하세요.')
            
            title = 'Tcard Validation Error'
            message = ' TCARD 를 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_tcard_tab2.setFocus()
            return False
        
        if  cur_item == "flag_bin_label_tab2"  :   
            return True
        #---------------------        
        if flag_bin_label_tab2 == False :
            #QMessageBox.critical(self,'BIN Label Validation Error',' BIN Label 을 먼저 스캔하세요.')
            
            title = 'BIN Label Validation Error'
            message = ' BIN Label 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_bin_label_tab2.setFocus()
            return False
        
        if cur_item == "flag_2d_tab2" :
            return True
        if flag_2d_tab2 == False :
            #QMessageBox.critical(self,'2D Label Validation Error',' 2D Label 을 먼저 스캔하세요.')
            
            title = '2D Label Validation Error'
            message = ' 2D Label 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_2d_tab2.setFocus()
            return False
        
    ##########################    
    def predata_chk_tab3(self, cur_item) :
        
        global flag_user_tab3
        global flag_tcard_tab3
        global flag_mbb_2d_tab3
        global flag_box_2d_tab3
                
        if flag_user_tab3 == False :
            #QMessageBox.critical(self,'UserID Validation Error',' USER ID 를 먼저 스캔하세요.')
            
            title = 'UserID Validation Error'
            message = ' USER ID 를 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_user_tab3.setFocus()
            return False
        #---------------------
        if  cur_item == "flag_tcard_tab3"  :   
            return True
        #---------------------    
        if flag_tcard_tab3 == False :
            #QMessageBox.critical(self,'Tcard Validation Error',' TCARD 를 먼저 스캔하세요.')
            
            title = 'Tcard Validation Error'
            message = ' TCARD 를 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_tcard_tab3.setFocus()
            return False
        
        if  cur_item == "flag_mbb_2d_tab3"  :   
            return True
        #---------------------        
        if flag_mbb_2d_tab3 == False :
            #QMessageBox.critical(self,'MBB 2D Barcode Label Validation Error',' MBB 2D Barcode Label 을 먼저 스캔하세요.')
            
            title = 'MBB 2D Barcode Label Validation Error'
            message = ' MBB 2D Barcode Label 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_mbb_2d_tab3.setFocus()
            return False
        
        if cur_item == "flag_box_2d_tab3" :
            return True
        if flag_box_2d_tab3 == False :
            #QMessageBox.critical(self,'BOX 2D Barcode Label Validation Error',' BOX 2D Barcode Label 을 먼저 스캔하세요.')
            
            title = 'BOX 2D Barcode Label Validation Error'
            message = ' BOX 2D Barcode Label 을 먼저 스캔하세요.'
            self.msgbox_critical(title, message)
            
            self.ed_box_2d_tab3.setFocus()
            return False
        
    #############################    
    def chk_user(self, suser) :
        
        user_flag = False
        
        if self.app_upgrade() == False :
            sys.exit(0)
            return False
        
        conn_mes = cx_Oracle.connect('MPMGR/sckmes0$@210.118.145.240:1521/cpkmes1')
        cur_mes = conn_mes.cursor()
        sql = "SELECT USER_NAME FROM SECUSR "        
        sql = sql + "WHERE USER_NAME = '" + str(suser) + "' "

        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        if cur_mes.rowcount > 0 :
            user_flag = True
                                
        conn_mes.close()
        
        return user_flag
    ########################   
    def check_user_all(self ) :
        
        global flag_user_tab1
        global flag_user_tab2
        global flag_user_tab3
        
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        
        sflag = self.focusWidget().objectName()
        
        if val_type == 'REEL' :
            flag_user_tab1 = False
            suser = str(self.ed_user_tab1.text())
        elif val_type == 'TRAY' :
            flag_user_tab2 = False
            suser = str(self.ed_user_tab2.text())
        elif val_type == 'BOX'  :
            flag_user_tab3 = False
            suser = str(self.ed_user_tab3.text())
            
        ######################
        if self.chk_user(suser) == False :            
            #QMessageBox.critical(self,'User Validation Error',str(suser) + ' ] 등록되지 않은 사번입니다.')            
            
            title = 'User Validation Error'
            message = str(suser) + ' ] 등록되지 않은 사번입니다. '            
            self.msgbox_critical(title, message)
        
            self.resetFunction()
            return False       
        else:
            if val_type == 'REEL' :
                flag_user_tab1 = True
                self.ed_user_tab1.setEnabled(False)
                self.ed_tcard_tab1.setFocus()  
            elif val_type == 'TRAY' :
                flag_user_tab2 = True
                self.ed_user_tab2.setEnabled(False)
                self.ed_tcard_tab2.setFocus()  
            elif val_type == 'BOX'  :
                flag_user_tab3 = True
                self.ed_user_tab3.setEnabled(False)
                self.ed_tcard_tab3.setFocus()      
        return True      
          
    ##############################
    def already_val_history(self):
                
        global meslot
        global val_type
        global program_type
        
        already_pass_flag = False
        
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        ###################
        
        conn_sip = cx_Oracle.connect('rts/rts4sck0@10.86.255.11:1521/sipprd')
        cur_sip = conn_sip.cursor()
            
        sql = "SELECT LOT_ID FROM T_LABEL_VALIDATION_HISTORY "
        sql = sql + "WHERE LOT_ID = '" + meslot + "' " 
        sql = sql + "AND VALIDATION_TYPE = '" + val_type + "' " 
        sql = sql + "AND PROGRAM_TYPE LIKE '" + program_type + "%' "
        cur_sip.execute(sql)
        rows = cur_sip.fetchall()
        
        if cur_sip.rowcount > 0 :            
            
            reply = QMessageBox.question(self, 'Warning Message', '이미 ' + val_type + ' Validation이 완료된 이력이 있는 Lot 입니다. Validation을 계속 진행하시겠습니까?' ,
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.No:
                already_pass_flag = False
            else:
                already_pass_flag = True                
        else:
            already_pass_flag = True
        
        conn_sip.close()
                        
        return already_pass_flag;
    #################################################
    ##############################
    def chk_val_history(self , stab):
        
        global val_flag
        global meslot
        global val_type
        global program_type
        
        chk_val_history_flag = False
        
        conn_sip = cx_Oracle.connect('rts/rts4sck0@10.86.255.11:1521/sipprd')
        cur_sip = conn_sip.cursor()
            
        sql = "SELECT LOT_ID FROM T_LABEL_VALIDATION_HISTORY "
        sql = sql + "WHERE LOT_ID = '" + meslot + "' " 
        sql = sql + "AND VALIDATION_TYPE IN ( 'REEL' , 'TRAY' ) "
        sql = sql + "AND PROGRAM_TYPE LIKE '" + program_type + "%' "
        cur_sip.execute(sql)
        rows = cur_sip.fetchall()
        
        if cur_sip.rowcount > 0 :            
            chk_val_history_flag = True
        else :            
            #QMessageBox.critical(self,'Validation Error', stab + ' ] 이전 tab 의 validation 을 진행하지 않았습니다. \n 이전 tab 의 validation 을 진행하세요.')
            
            title = 'Validation Error'
            message = stab + ' ] 이전 tab 의 validation 을 진행하지 않았습니다. \n 이전 tab 의 validation 을 진행하세요.'
            self.msgbox_critical(title, message)
            
        conn_sip.close()
                    
        return chk_val_history_flag;
    #################################################    
    def chk_tcard(self, sTcard_lot ) :
        global meslot        
        global sCustDevice
        global sLead
        global label_standard_qty
        global sCust
        global partial_qty
        
        global label_lot
        global val_type
        
        global chk_count
        global count_str
        
        global mes_label_list
        global lpn_list
        global sitem_id
        global sdate_code
        global spart_id
                
        tcard_flag = False
        label_lot = ""
        mes_label_list = []
        lpn_list = []
        
        ####################
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
                
        #######
        conn_mes = cx_Oracle.connect('MPMGR/sckmes0$@210.118.145.240:1521/cpkmes1')
        cur_mes = conn_mes.cursor()
        sql = "SELECT KSY_GET_LOT_FROM_BRC('" + sTcard_lot + "') FROM DUAL "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount  ==  0 :
            tcard_flag = False
            #QMessageBox.critical(self,'Tcard Validation Error', sTcard_lot + ' ] MES 에 등록되지 않은 lot 입니다.')            
            
            title = 'Tcard Validation Error'
            message = sTcard_lot + ' ] MES 에 등록되지 않은 lot 입니다.'
            self.msgbox_critical(title, message)

            conn_mes.close()            
            return tcard_flag
        else :    
            for row in rows:  # 202029
                sLot = row[0]
                if sLot.find('ERROR') > -1:
                    tcard_flag = False
                    #QMessageBox.critical(self,'Validation Error', sTcard_lot + ' ] MES 에 등록되지 않은 lot 입니다.')                    
                    
                    title = 'Validation Error'
                    message = sTcard_lot + ' ] MES 에 등록되지 않은 lot 입니다.'
                    self.msgbox_critical(title, message)
                    
                    conn_mes.close()                    
                    return tcard_flag
        ###################################        
        cur_mes = conn_mes.cursor()        
        sql = "SELECT LOT_ID, LEAD_ID , CUST_DEVICE , CUST_ID , SCH_TYPE  FROM WIP_LOTINF WHERE LOT_ID =  '" + sLot + "' "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount  ==  0 :
            tcard_flag = False
            #QMessageBox.critical(self,'Tcard Validation Error', sTcard_lot + ' ] MES 에 등록되지 않은 lot 입니다.')            
            
            title = 'Tcard Validation Error'
            message = sTcard_lot + ' ] MES 에 등록되지 않은 lot 입니다.'
            self.msgbox_critical(title, message)
            
            conn_mes.close()            
            return tcard_flag       
        else:
            meslot = sLot
            for row in rows :
                sLead = row[1]
                sCustDevice = row[2]
                sCust = row[3]
                 
        ####################                        
        cur_mes = conn_mes.cursor()
        sql = "SELECT CUR_DIE_QTY , INBOX_BOX_STD_QTY , MOD(COM_DIE_QTY, INBOX_BOX_STD_QTY) , INBOX_BOX_FROM_ID , "
        #                 0                 1                        2                             3
        sql = sql + " RESV_FIELD4 ITEM_ID, RESV_FIELD2 DATE_CODE , RESV_FIELD9 PART_ID FROM WIP_IBXINF "
        #              ITEMD   4         ,       DATACODE 5      ,    PARTID 6
        sql = sql + "WHERE LOT_ID = '" + sLot + "' AND FACTORY = 'TEST' AND DELETE_FLAG = ' ' "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount  ==  0 :
            tcard_flag = False
            #QMessageBox.critical(self,'Validation Error', sTcard_lot + ' ] MES Label 이 등록되지 않아 validation 을 진행할 수 없습니다.')  
            
            title = 'Validation Error'
            message = sTcard_lot + ' ] MES Label 이 등록되지 않아 validation 을 진행할 수 없습니다.'
            self.msgbox_critical(title, message)
                      
            conn_mes.close()            
            return  tcard_flag  
        
        else :
            for row in rows:                    
                totalQuantity = row[0]
                boxQuantity = row[1]
                partial_qty = row[2]
                label_lot = row[3]
                label_lot = label_lot[0:30].strip()
                sitem_id = row[4]
                sdate_code = row[5]
                spart_id = row[6]
                
                label_standard_qty = boxQuantity
                
                a = (int(totalQuantity) // int(boxQuantity))
                b = (int(totalQuantity) % int(boxQuantity))
                if b > 0 :
                    chk_count = a + 1
                else :
                    chk_count = a
            ####################
            # label 전체 check 는 한번만 진행
            if val_type == "LABEL_CHECK" :
                self.ed_count.setText("1")
                count_str = 1
            else :    
                self.ed_count.setText(str(chk_count)) 
                count_str = chk_count
        ####################
        sql = "SELECT KEY1, KEY2 FROM UPTDAT2 "        
        sql = sql + "WHERE FACTORY = 'MESPLUS' "
        sql = sql + "AND TABLE_NAME = 'QUL_LPN_CODE' " 
        sql = sql + "AND KEY1 = '" +  sLot + "' "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount  ==  0 :
            tcard_flag = False
            #QMessageBox.critical(self,'Validation Error', sTcard_lot + ' ] MES UPT - QUL_LPN_CODE 에 LPN CODE 가 등록되지 않아 validation 을 진행할 수 없습니다.')            
            
            title = 'Validation Error'
            message = sTcard_lot + ' ] MES UPT - QUL_LPN_CODE 에 LPN CODE 가 등록되지 않아 validation 을 진행할 수 없습니다.'
            self.msgbox_critical(title, message)
            
            conn_mes.close()            
            return  tcard_flag  
        
        else :
            for row in rows:  
                lpn_list.append(row[1])
        
        '''
        sql = "SELECT BARCODE_01, BARCODE_02, MATRIX_DATA_01 FROM WIP_LABINF "
        sql = sql + "WHERE FACTORY = 'TEST' "
        sql = sql + "AND LOT_ID = '" + sLot + "' "
        sql = sql + "AND DELETE_FLAG =' ' "
        sql = sql + "AND LABEL_TYPE = 'INBOX' "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount > 0 : 
            for row in rows:  # 202029
                label_1row = row[0].strip()
                label_2row = row[1].strip()
                label_2d = row[2].strip()
                mes_label_list = row
                
        else:
            QMessageBox.critical(self, 'Tcard Validation Error', 'MES Label 정보가 등록되어 있지 않습니다.')
            return False
        '''
        #######################
            
        tcard_flag = True    
        return tcard_flag    
    ###################################################  
    def get_upt(self, barcode_01, barcode_02, barcode_matrix) :
        
        global meslot
        global label_1row
        global label_2row
        global label_2d
        
        
        conn_mes = cx_Oracle.connect('MPMGR/sckmes0$@210.118.145.240:1521/cpkmes1')
        cur_mes = conn_mes.cursor()
        
        sql = "SELECT BARCODE_01, BARCODE_02, MATRIX_DATA_01 FROM WIP_LABINF "
        sql = sql + "WHERE FACTORY = 'TEST' "
        sql = sql + "AND LOT_ID = '" + meslot + "' "
        #-------------------
        if barcode_01.strip() != '' :
            sql = sql + "AND BARCODE_01 = '" + barcode_01 + "' "
        if barcode_02.strip() != '' :
            sql = sql + "AND BARCODE_02 = '" + barcode_02 + "' "
        if barcode_matrix.strip() != '' :    
            sql = sql + "AND MATRIX_DATA_01 = '" + barcode_matrix + "'"
        #-------------------    
        sql = sql + "AND DELETE_FLAG = ' ' "
        sql = sql + "AND LABEL_TYPE = 'INBOX' "
        
        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
        
        if cur_mes.rowcount > 0 : 
            for row in rows:  # 202029
                label_1row = row[0].strip()
                label_2row = row[1].strip()
                label_2d = row[2].strip()
                 
        else:
            #QMessageBox.critical(self, '[' + barcode_01 + '][' + barcode_02 + '][' + barcode_matrix + '] Label Validation Error', 'MES Label 정보가 등록되어 있지 않습니다.')
            #
            title = '[' + barcode_01 + '][' + barcode_02 + '][' + barcode_matrix + '] Label Validation Error'
            message = 'MES Label 정보가 등록되어 있지 않습니다.'
            self.msgbox_critical(title, message)

            return False
        
        return True
    
    ##########################    
        
    def check_tcard_all(self) :
         
        global meslot  
        global flag_tcard_tab1
        global flag_tcard_tab2
        global flag_tcard_tab3
        
        ##############################
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        sflag = self.focusWidget().objectName()
        ###############################            
        if val_type == "REEL" :
            flag_tcard_tab1 = False
            predata_flag = self.predata_chk_tab1('flag_tcard_tab1')
        elif val_type == "TRAY" :
            flag_tcard_tab2 = False
            predata_flag = self.predata_chk_tab2('flag_tcard_tab2')
        elif val_type == "BOX" :
            flag_tcard_tab3 = False
            predata_flag = self.predata_chk_tab3('flag_tcard_tab3')    
            
        if predata_flag == False:                        
            self.resetFunction()            
            return False
        #############################
        # 대문자로 변환
        if val_type == "REEL" :
            sTcard_lot = self.ed_tcard_tab1.text().upper()
            self.ed_tcard_tab1.setText(sTcard_lot)    
        elif val_type == "TRAY" :
            sTcard_lot = self.ed_tcard_tab2.text().upper()
            self.ed_tcard_tab2.setText(sTcard_lot)    
        elif val_type == "BOX" :
            sTcard_lot = self.ed_tcard_tab3.text().upper()        
            self.ed_tcard_tab3.setText(sTcard_lot)  
        
        else :
            QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            self.resetFunction()
            return
              
        #######
        if self.chk_tcard(sTcard_lot) == False :
            self.resetFunction()            
            return False
        
        if currentIndex == 2 :
            stab = self.tabWidget.tabText(currentIndex-1)
            stab = stab.upper()
        
            if self.chk_val_history(stab) == False :
                self.resetFunction()            
                return False
        
        salready_flag = self.already_val_history()
        
        if salready_flag == False :
            self.resetFunction()            
            return False    
        
        
        if val_type == "REEL" :
            flag_tcard_tab1 = True
            self.ed_tcard_tab1.setText(meslot)        
            self.ed_tcard_tab1.setEnabled(False)        
            self.ed_reel_pink_tab1.setFocus()
        
        elif val_type == "TRAY" :
            flag_tcard_tab2 = True
            self.ed_tcard_tab2.setText(meslot)        
            self.ed_tcard_tab2.setEnabled(False)        
            self.ed_bin_label_tab2.setFocus()
                
        elif val_type == "BOX" :
            flag_tcard_tab3 = True
            self.ed_tcard_tab3.setText(meslot)        
            self.ed_tcard_tab3.setEnabled(False)        
            self.ed_mbb_2d_tab3.setFocus()
        
        else :
            QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            self.resetFunction()
            return
                
        return True ;    
    ###################################    
    
 ###################################################  
      
    def check_2d_all(self) :
         
        global meslot 
        global flag_reel_2d_tab1
        global flag_mbb_2d_tab1
        global flag_2d_tab2
        global flag_mbb_2d_tab3
        global flag_box_2d_tab3
        global lpn_list
        global label_lot
        global sitem_id
        global sdate_code
        global spart_id
        global label_standard_qty
        global partial_qty
        
        check_2d_all = False
        
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        ed_flag = self.focusWidget().objectName()
        ###############################
        if ed_flag == "ed_reel_2d_tab1" :
            flag_reel_2d_tab1 = False
            sflag = "flag_reel_2d_tab1"
            predata_flag = self.predata_chk_tab1(sflag)
            
            if predata_flag == False: 
                self.resetFunction_add()
                #self.resetFunction()
                return False
                 
            s2d = self.ed_reel_2d_tab1.text().upper()
            self.ed_reel_2d_tab1.setText(s2d)
            
        elif ed_flag == "ed_mbb_2d_tab1" :
            flag_mbb_2d_tab1 = False
            sflag = "flag_mbb_2d_tab1"
            predata_flag = self.predata_chk_tab1(sflag)            
            
            if predata_flag == False: 
                #self.error_tab1_return('add')
                self.resetFunction_add()
                return False     
            
            s2d = self.ed_mbb_2d_tab1.text().upper()
            self.ed_mbb_2d_tab1.setText(s2d)
            
            #--------------------
            # 2st 끼리는 동일 
            if self.ed_mbb_2d_tab1.text().upper() != self.ed_reel_2d_tab1.text() :
                #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' Reel 2D 와 MBB 2D barcode 가 일치하지 않습니다. !! ')
                #self.error_tab1_return('add')
                
                title = val_type + ' Validation Error'
                message = val_type + ' Reel 2D 와 MBB 2D barcode 가 일치하지 않습니다. !! '
                self.msgbox_critical(title, message)
                
                self.resetFunction_add()
                return False     
            #######################
        
        elif ed_flag == "ed_2d_tab2" :
            flag_2d_tab2 = False
            sflag = "flag_2d_tab2"
            predata_flag = self.predata_chk_tab2(sflag)            
            
            if predata_flag == False: 
                #self.error_tab2_return('add')
                self.resetFunction_add()
                return False     
            
            s2d = self.ed_2d_tab2.text().upper()
            self.ed_2d_tab2.setText(s2d)
            
        elif ed_flag == "ed_mbb_2d_tab3" :
            flag_mbb_2d_tab3 = False
            sflag = "flag_mbb_2d_tab3"
            predata_flag = self.predata_chk_tab3(sflag)            
            
            if predata_flag == False: 
                #self.error_tab3_return('add')
                self.resetFunction_add()
                return False     
            
            s2d = self.ed_mbb_2d_tab3.text().upper() 
            self.ed_mbb_2d_tab3.setText(s2d)  
        
        elif ed_flag == "ed_box_2d_tab3" :
            flag_box_2d_tab3 = False
            sflag = "flag_box_2d_tab3"
            predata_flag = self.predata_chk_tab3(sflag)            
            
            if predata_flag == False: 
                #self.error_tab3_return('add')
                self.resetFunction_add()
                return False     
            
            s2d = self.ed_box_2d_tab3.text().upper()  
            self.ed_box_2d_tab3.setText(s2d)
            #--------------------
            # 2st 끼리는 동일 
            if self.ed_box_2d_tab3.text().upper()   != self.ed_mbb_2d_tab3.text().upper()  :
                #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' BOX 2D 와 MBB 2D barcode 가 일치하지 않습니다. !! ')
                #self.error_tab3_return('add')
                
                title = val_type + ' Validation Error'
                message = val_type + ' BOX 2D 와 MBB 2D barcode 가 일치하지 않습니다. !! '
                self.msgbox_critical(title, message)

                self.resetFunction_add()
                return False     
            #######################
            
              
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.'
            self.msgbox_critical(title, message)
                
            self.resetFunction_add()
            return
        ###########################################
        # 2d data parsing 체크
        #1JUN144356508SBL07YMR,1PIPQ-8071A-0-772FCBGA-MT-00-0,1T000HH1463H6.0H005,9D21462146A,Q500,30PCP90-YC971-1
        stemp = s2d.split(',')
        
        if len(stemp) == 6 :
            pass
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', s2d + '\n 2D 바코드 format 이 맞지 않습니다.')
            
            title = val_type + ' Validation Error'
            message = s2d + '\n 2D 바코드 format 이 맞지 않습니다.'
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return
            
        
        s2d_lpn = stemp[0]        
        s2d_item_id = stemp[1]
        s2d_lot_code = stemp[2]
        s2d_data_code = stemp[3]
        s2d_qty = stemp[4]
        s2d_part = stemp[5]
        #----------------------
        # lpn
        s2d_lpn_pre = s2d_lpn[0:2]
        if s2d_lpn_pre == '1J' :
            pass
        else:
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D barcode LPN prefix 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D barcode LPN prefix 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------        
        s2d_lpn_val = s2d_lpn[2:]
        if s2d_lpn_val in lpn_list :
            pass                
        else:
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D barcode LPN DATA 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D barcode LPN DATA 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------
        # ITEM ID
        if s2d_item_id == '1P' + str(sitem_id) :
            pass 
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D barcode ITEM ID 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D barcode ITEM ID 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------
        # LOT CODE
        if s2d_lot_code == '1T' + label_lot :
            pass 
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D barcode LOT CODE 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D barcode LOT CODE 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------
        #  DATE CODE
        if s2d_data_code == '9D' + str(sdate_code) :
            pass 
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D barcode DATE CODE 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D barcode DATE CODE 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------
        # QTY
        s2d_qty_val = s2d_qty[1:]
        
        # 2022/09/12 partial qty 와 불일치할 때 에러발생
        # partial qty 비교로직추가
        if (s2d_qty == 'Q' + str(label_standard_qty)) or (s2d_qty == 'Q' + str(partial_qty)) :
            pass 
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D barcode QTY 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D barcode QTY 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------
        # PART ID
        if s2d_part == '30P' + str(spart_id) :
            pass 
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 2D PART_ID 가 일치하지 않습니다. !! ')
            
            title = val_type + ' Validation Error'
            message = val_type + ' 2D PART_ID 가 일치하지 않습니다. !! '
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return False   
        #-------------------------
        ##############################
        # 2d 중복체크
        if (ed_flag == "ed_reel_2d_tab1" or ed_flag == "ed_mbb_2d_tab1" ) :
        
            srow = self.tbl_tab1.rowCount() 
            ###################
            # partial 일 때는 partial 수량 먼저 스캔한다.
            if srow == 0 :
                if int(partial_qty) > 0 :
                    if int(s2d_qty_val) == int(partial_qty) :
                        pass
                    else :
                        #QMessageBox.critical(self, val_type + ' Validation Error', ' PARTIAL LABEL 을 먼저 스캔하세요. !!')                        
                        #self.error_tab1_return('add')
                        
                        title = val_type + ' Validation Error'
                        message = ' PARTIAL LABEL 을 먼저 스캔하세요. !!'
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return                        
                
            ##############################    
            if ed_flag == "ed_mbb_2d_tab1"  :
                if self.ed_reel_2d_tab1.text() != self.ed_mbb_2d_tab1.text() :
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' Reel 과 MBB 2D barcode 가 서로 불일치합니다. .!!')                        
                    #self.error_tab1_return('add')
                    
                    title = val_type + ' Validation Error'
                    message = ' Reel 과 MBB 2D barcode 가 서로 불일치합니다. .!!'
                    self.msgbox_critical(title, message)
                    
                    self.resetFunction_add()
                    return
                    
            for i in range(0,srow):                
                sreel_2d = self.tbl_tab1.item(i, 4).text()  # REEL 2D
                smbb_2d = self.tbl_tab1.item(i, 6).text()   # MBB 2D
                
                #if (tbl_data.strip() != '') and ((spink == tbl_data3) or (spink == tbl_data4)) :
                if ((s2d == sreel_2d) or (s2d == smbb_2d)) :
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' 2D label \n [' + s2d + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                    #                    '라벨 중복 여부를 확인하세요.!!')
                    
                    title = val_type + ' Validation Error'
                    message = ' 2D label \n [' + s2d + '] \n 는 이미 스캔 완료되었습니다. \n' + '라벨 중복 여부를 확인하세요.!!'
                    self.msgbox_critical(title, message)
                    
                    #self.error_tab1_return('add')
                    self.resetFunction_add()
                    return
                
        elif ed_flag == "ed_2d_tab2" :
            srow = self.tbl_tab2.rowCount() 
            ##############################    
            ###################
            # partial 일 때는 partial 수량 먼저 스캔한다.
            if srow == 0 :
                if int(partial_qty) > 0 :
                    if int(s2d_qty_val) == int(partial_qty) :
                        pass
                    else :
                        #QMessageBox.critical(self, val_type + ' Validation Error', ' PARTIAL LABEL 을 먼저 스캔하세요. !!')                        
                        #self.error_tab2_return('add')
                        title = val_type + ' Validation Error'
                        message = ' PARTIAL LABEL 을 먼저 스캔하세요. !!'
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return   
                            
            for i in range(0,srow):                
                s_2d = self.tbl_tab2.item(i, 4).text()  #   2D
                
                if s2d == s_2d  :
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' 2D label \n [' + s2d + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                    #                    '라벨 중복 여부를 확인하세요.!!')
                        
                    #self.error_tab2_return('add')
                    title = val_type + ' Validation Error'
                    message = ' 2D label \n [' + s2d + '] \n 는 이미 스캔 완료되었습니다. \n' + '라벨 중복 여부를 확인하세요.!!'
                    self.msgbox_critical(title, message)
                    
                    self.resetFunction_add()
                    return
            
        elif (ed_flag == "ed_mbb_2d_tab3" or ed_flag == "ed_box_2d_tab3" ) :
        
            srow = self.tbl_tab3.rowCount() 
            ###################
            # partial 일 때는 partial 수량 먼저 스캔한다.
            if srow == 0 :
                if int(partial_qty) > 0 :
                    if int(s2d_qty_val) == int(partial_qty) :
                        pass
                    else :
                        #QMessageBox.critical(self, val_type + ' Validation Error', ' PARTIAL LABEL 을 먼저 스캔하세요. !!')                        
                        #self.error_tab1_return('add')
                        
                        title =  val_type + ' Validation Error'
                        message = ' PARTIAL LABEL 을 먼저 스캔하세요. !!'
                        self.msgbox_critical(title, message)
                        
                        self.resetFunction_add()
                        return   
                    
            ##############################    
            if ed_flag == "ed_box_2d_tab3"  :
                if self.ed_mbb_2d_tab3.text() != self.ed_box_2d_tab3.text() :
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' BOX 와 MBB 2D barcode 가 서로 불일치합니다. .!!')                        
                    #self.error_tab3_return('add')
                    
                    title =  val_type + ' Validation Error'
                    message = ' BOX 와 MBB 2D barcode 가 서로 불일치합니다. .!!'
                    self.msgbox_critical(title, message)
                    
                    self.resetFunction_add()
                    return
                
            for i in range(0,srow):                
                smbb_2d = self.tbl_tab3.item(i, 3).text()  # mbb 2d
                sbox_2d = self.tbl_tab3.item(i, 4).text()  # box 2d
                
                if ((s2d == smbb_2d) or (s2d == sbox_2d)) :
                    
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' 2D label \n [' + s2d + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                    #                    '라벨 중복 여부를 확인하세요.!!')
                    
                    title =  val_type + ' Validation Error'
                    message = ' 2D label \n [' + s2d + '] \n 는 이미 스캔 완료되었습니다. \n' + '라벨 중복 여부를 확인하세요.!!'
                    self.msgbox_critical(title, message)
                        
                    #self.error_tab3_return('add')
                    self.resetFunction_add()
                    return        
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            
            title =  val_type + ' Validation Error'
            message = val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.'
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return    
        #----------------------------        
        ########################
        #if s2d != label_2d :
        '''
        if self.get_upt(s1row, s2row, s2d) == False :
            if val_type == "LABEL_CHECK" :
                self.error_tab1_return('add')
                return
            elif val_type == "REEL_MBB" :
                self.error_tab2_return('add')
                return
            elif val_type == "MBB_BOX" :
                self.error_tab3_return('add')
                return 
            else :
                QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
                self.resetFunction()
                return               
        '''
        ############################    
        
        check_2d_all = True
        
        if sflag == 'flag_2d_tab2' :
            # complete
            self.ed_2d_tab2.setEnabled(False)
            
            flag_2d_tab2 = True
            if self.tab2_complete() == True :
                pass
            else :                
                self.resetFunction_add()
                return 
            
        elif sflag == 'flag_reel_2d_tab1' :  
            flag_reel_2d_tab1 = True          
            self.ed_reel_2d_tab1.setEnabled(False)        
            self.ed_mbb_pink_tab1.setFocus()
            
        elif sflag == 'flag_mbb_2d_tab1' : 
            # complete
            self.ed_mbb_2d_tab1.setEnabled(False)        
            
            flag_mbb_2d_tab1 = True 
            if self.tab1_complete() == True :
                pass
            else :
                self.resetFunction_add()
                return 
            
        elif sflag == 'flag_mbb_2d_tab3' :
            flag_mbb_2d_tab3 = True
            self.ed_mbb_2d_tab3.setEnabled(False)        
            self.ed_box_2d_tab3.setFocus()
        
        elif sflag == 'flag_box_2d_tab3' :
            
            self.ed_box_2d_tab3.setEnabled(False)    
            
            flag_box_2d_tab3 = True
            if self.tab3_complete() == True :
                pass
            else :                
                self.resetFunction_add()
                return 
                
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            
            title =  val_type + ' Validation Error'
            message = val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.'
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return     
          
        return True 
    
    ################### 
    def check_pink_all(self) :
        global meslot 
        
        global flag_reel_pink_tab1
        global flag_mbb_pink_tab1
        global flag_bin_label_tab2
        global label_lot
                
        #flag_reel_pink_tab2 = False
        
        currentIndex = self.tabWidget.currentIndex()
        cur_tab_txt = self.tabWidget.tabText(currentIndex)
        val_type = cur_tab_txt.upper()
        ed_flag = self.focusWidget().objectName()
        
        ###############################
        if ed_flag == "ed_reel_pink_tab1" :
            flag_reel_pink_tab1 = False
            sflag = "flag_reel_pink_tab1"
            predata_flag = self.predata_chk_tab1(sflag)
            
            if predata_flag == False: 
                #self.error_tab1_return('add')
                self.resetFunction_add()
                return False
                 
            spink = self.ed_reel_pink_tab1.text().upper()
            self.ed_reel_pink_tab1.setText(spink)
            
        elif ed_flag == "ed_mbb_pink_tab1" :
            flag_mbb_pink_tab1 = False
            sflag = "flag_mbb_pink_tab1"
            predata_flag = self.predata_chk_tab1(sflag)            
            
            if predata_flag == False: 
                #self.error_tab1_return('add')
                self.resetFunction_add()
                return False     
            
            spink = self.ed_mbb_pink_tab1.text().upper()
            self.ed_mbb_pink_tab1.setText(spink)
            
        elif ed_flag == "ed_bin_label_tab2" :
            flag_bin_label_tab2 = False
            sflag = "flag_bin_label_tab2"
            predata_flag = self.predata_chk_tab2(sflag)            
            
            if predata_flag == False: 
                #self.error_tab2_return('add')
                self.resetFunction_add()
                return False     
            
            spink = self.ed_bin_label_tab2.text().upper()
            self.ed_bin_label_tab2.setText(spink)
                
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            
            title =  val_type + ' Validation Error'
            message = val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.'
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return
        ########################
        sprefix = 'Q'        
        
        if spink[0:1] != sprefix :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' Prefix(' +  spink[0:1] + ') 값이 일치하지 않습니다.')
            
            title =  val_type + ' Validation Error'
            message = val_type + ' Prefix(' +  spink[0:1] + ') 값이 일치하지 않습니다.'
            self.msgbox_critical(title, message)
            
            if currentIndex == 0 :
                #self.error_tab1_return('add')
                self.resetFunction_add()
            elif currentIndex == 1 :
                #self.error_tab2_return('add')
                self.resetFunction_add()
            elif currentIndex == 2 :
                #self.error_tab3_return('add')   
                self.resetFunction_add()
            return
        
        stemp = spink.split('-')
        sseq_input = stemp[0][1:]   # Q1-xxxxx
        slot_input = spink[spink.find('-')+1 : ]
        
        
        if (len(str(sseq_input)) >= 1) and (len(str(sseq_input)) <= 4) :
            pass
        else:
            #QMessageBox.critical(self,'Reel Pink Label Validation Error', spink + ' ] Reel Pink Label 자리수가 맞지 않습니다.')
            
            title =  'Reel Pink Label Validation Error'
            message = spink + ' ] Reel Pink Label 자리수가 맞지 않습니다.'
            self.msgbox_critical(title, message)
            
            if currentIndex == 0 :
                #self.error_tab1_return('add')
                self.resetFunction_add()
            elif currentIndex == 1 :
                #self.error_tab2_return('add')
                self.resetFunction_add()
            elif currentIndex == 2 :
                #self.error_tab3_return('add')   
                self.resetFunction_add()
            return
        
        if (int(sseq_input) >= 1) and (int(sseq_input) <= 9000) :
            pass
        else:
            #QMessageBox.critical(self,'Reel Pink Label Validation Error', spink + ' ] Reel Pink Label 자리수가 맞지 않습니다.')
            
            title =  'Reel Pink Label Validation Error'
            message = spink + ' ] Reel Pink Label 자리수가 맞지 않습니다.'
            self.msgbox_critical(title, message)
            
            if currentIndex == 0 :
                #self.error_tab1_return('add')
                self.resetFunction_add()
            elif currentIndex == 1 :
                #self.error_tab2_return('add')
                self.resetFunction_add()
            elif currentIndex == 2 :
                #self.error_tab3_return('add')   
                self.resetFunction_add()
            return
        ###############################        
        if slot_input != label_lot :
            #QMessageBox.critical(self,'Pink Label Validation Error', spink + ' ] Pink Label 가 MES Label data 와 일치하지 않습니다.')
            
            title =  'Pink Label Validation Error'
            message = spink + ' ] Pink Label 가 MES Label data 와 일치하지 않습니다.'            
            self.msgbox_critical(title, message)
            
            if currentIndex == 0 :
                #self.error_tab1_return('add')
                self.resetFunction_add()
            elif currentIndex == 1 :
                #self.error_tab2_return('add')
                self.resetFunction_add()
            elif currentIndex == 2 :
                #self.error_tab3_return('add')   
                self.resetFunction_add()
            return
        ##############################
        if (ed_flag == "ed_reel_pink_tab1" or ed_flag == "ed_mbb_pink_tab1" ) :
            srow = self.tbl_tab1.rowCount() 
            ##############################    
            if self.ed_reel_pink_tab1.text() == self.ed_mbb_pink_tab1.text() :
                #QMessageBox.critical(self, val_type + ' Validation Error', ' pink label \n [' + spink + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                #                        '라벨 중복 여부를 확인하세요.!!')
                
                title =  val_type + ' Validation Error'
                message = ' pink label \n [' + spink + '] \n 는 이미 스캔 완료되었습니다. \n' + '라벨 중복 여부를 확인하세요.!!'         
                self.msgbox_critical(title, message)
                        
                #self.error_tab1_return('add')
                self.resetFunction_add()
                return
                
            for i in range(0,srow):                
                tbl_data3 = self.tbl_tab1.item(i, 3).text()  # reel pink 
                tbl_data5 = self.tbl_tab1.item(i, 5).text()  # mbb pink
               
                if ((spink == tbl_data3) or (spink == tbl_data5)) :
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' pink label \n [' + spink + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                    #                    '라벨 중복 여부를 확인하세요.!!')
                    
                    title =  val_type + ' Validation Error'
                    message = ' pink label \n [' + spink + '] \n 는 이미 스캔 완료되었습니다. \n' + '라벨 중복 여부를 확인하세요.!!'      
                    self.msgbox_critical(title, message)
                        
                    #self.error_tab1_return('add')
                    self.resetFunction_add()
                    return
        
        elif ed_flag == "ed_bin_label_tab2"  :
            srow = self.tbl_tab2.rowCount() 
            ##############################                    
            for i in range(0,srow):                
                tbl_data3 = self.tbl_tab2.item(i, 3).text()  # bin label
                               
                if spink == tbl_data3 :
                    #QMessageBox.critical(self, val_type + ' Validation Error', ' bin label \n [' + spink + '] \n 는 이미 스캔 완료되었습니다. \n' + \
                    #                    '라벨 중복 여부를 확인하세요.!!')
                    
                    title =  val_type + ' Validation Error'
                    message =  'bin label \n [' + spink + '] \n 는 이미 스캔 완료되었습니다. \n' + '라벨 중복 여부를 확인하세요.!!'     
                    self.msgbox_critical(title, message)
                        
                    #self.error_tab2_return('add')
                    self.resetFunction_add()
                    return
                
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            
            title =  val_type + ' Validation Error'
            message =  val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.'  
            self.msgbox_critical(title, message)
                    
            self.resetFunction_add()
            return    
        #----------------------------
        if sflag == "flag_reel_pink_tab1" :            
            flag_reel_pink_tab1 = True                        
            self.ed_reel_pink_tab1.setEnabled(False)        
            self.ed_reel_2d_tab1.setFocus()
        
        elif sflag == "flag_mbb_pink_tab1" :            
            flag_mbb_pink_tab1 = True                        
            self.ed_mbb_pink_tab1.setEnabled(False)        
            self.ed_mbb_2d_tab1.setFocus()        
        
        elif sflag == "flag_bin_label_tab2" :            
            flag_bin_label_tab2 = True                        
            self.ed_bin_label_tab2.setEnabled(False)        
            self.ed_2d_tab2.setFocus()
    
        else :
            #QMessageBox.critical(self, val_type + ' Validation Error', val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.')
            
            title =  val_type + ' Validation Error'
            message =  val_type + ' 현재 라벨 입력란이 정의되어 있지 않습니다.'
            self.msgbox_critical(title, message)
            
            self.resetFunction_add()
            return     
            
        return True
    ####################
        
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