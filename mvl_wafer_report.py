
import csv
import os
import cx_Oracle

import os
import shutil
from pathlib import Path
import sys

import datetime
from datetime import date, timedelta

import email
import smtplib
from email.mime.text import MIMEText
import socket
import ftplib

from time import localtime, strftime ,strptime
import time


global mail_success_flag
global mail_text

mail_success_flag = True

mail_text = "mvl wafermap report generation " + '\n' + '\n'
msg = ""

source_dir = r"C:\temp\mvl_wafer_report"
log_dest = source_dir + "log/"

##################
# ip 구하기
def ipcheck():
    return socket.gethostname()

# email 전송
def send_mail(m_text):
    
    global mail_success_flag
    print("mail sending")
    smtp = smtplib.SMTP("Mrelay.jkr.jcetglobal.com", 25)
    
    m_text = ipcheck() + '\n' + m_text    
    msg = MIMEText(m_text)
    if mail_success_flag == True:
        msg['Subject'] = 'MVL WAFERMAP REPORT success !! ' + ipcheck()
    else:
        msg['Subject'] = 'MVL WAFERMAP REPORT Error !! ' + ipcheck() + ' - ' + ' check equipment '

    msg['To'] = 'wansoo.kim@jcetglobal.com'
    
    smtp.sendmail('sckcim@jcetglobal.com', 'wansoo.kim@jcetglobal.com', msg.as_string())
    print("mail sending complete !! ")
    
    smtp.quit()
    
## log 파일 쓰기 함수
def writeLog(strLog):
    now = datetime.datetime.now()
    logDate = now.strftime('%Y%m%d')
    nowtime = now.strftime('%Y%m%d %H:%M:%S')
    f = open(log_dest + 'log_' + logDate + '.txt' , 'a')
    f.write(nowtime + ' :: ' + strLog + '\n')
    f.close()
################################
def get_tot_test_time(s, soper) :
    
    sLot_end_time = ''
    sLot_start_time = ''
    sTot_test_time = ''
    
    conn_tpas1 = cx_Oracle.connect('tpasdb' )        
    cur_tpas1 = conn_tpas1.cursor()
        
    sql = "SELECT MAX(END_TIME) , MIN(START_TIME) , ROUND((TO_DATE(MAX(END_TIME), 'YYYYMMDDHH24MISS') - TO_DATE(MIN(START_TIME), 'YYYYMMDDHH24MISS'))*24*60,2) FROM TPAS_WAFERSUM_INF "
    sql = sql + "WHERE NORMAL_LOTID = '" + s + "' "    
    sql = sql + "AND CUSTOMER = 'INP' "    
    sql = sql + "AND OPER = '" + soper + "' "
    sql = sql + "ORDER BY LOT_ID, WAFER_ID "
    cur_tpas1.execute(sql)
    rows = cur_tpas1.fetchall()
    
    for row in rows:
        sLot_end_time = row[0]
        sLot_start_time = row[1]
        sTot_test_time = row[2]
        
        
        start_time_date = datetime.datetime.strptime(sLot_start_time, "%Y%m%d%H%M%S")
        end_time_date = datetime.datetime.strptime(sLot_end_time, "%Y%m%d%H%M%S")
        sLot_start_time_f = start_time_date.strftime('%Y-%m-%d %H:%M:%S')
        sLot_end_time_f = end_time_date.strftime('%Y-%m-%d %H:%M:%S')
        
        
    return sLot_end_time_f, sLot_start_time_f , sTot_test_time

###############################
def get_mes_lot_list() :
    
    conn_mes1 = cx_Oracle.connect('tpasdb')
    cur_mes1 = conn_mes1.cursor()
    mes_lot_list = []
    wafer_out_list = []
    wafer_split_list = []
    wafer_hold_list = []
    
    #sql = "SELECT TOT_YIELD_LIMIT FROM  WIPBIN "
    sql = "SELECT DISTINCT LOT_ID FROM WIPLTH "
    sql = sql + "WHERE TRANS_TIME BETWEEN TO_CHAR(SYSDATE-10, 'YYYYMMDD') AND TO_CHAR(SYSDATE+1, 'YYYYMMDDHH')  "
    sql = sql + "AND CREATE_CMF2 = 'MVL' "
    sql = sql + "AND HIS_DELETE_FLAG <> 'Y' "
    sql = sql + "AND OPER_OLD = '340' "
    sql = sql + "AND OPER <> '340' "
    sql = sql + "ORDER BY LOT_ID "
    
    cur_mes1.execute(sql)
    mes_rows = cur_mes1.fetchall()    
    if cur_mes1.rowcount  >  0 :
        for row in mes_rows:
            wafer_out_list.append(row[0])
    #-----------------------------
    sql = "SELECT DISTINCT FROM_TO_LOT_ID FROM WIPLTH "
    sql = sql + "WHERE LOT_ID IN ( "
    sql = sql + "  SELECT LOT_ID FROM WIPLTH "
    sql = sql + "  WHERE TRANS_TIME BETWEEN TO_CHAR(SYSDATE-10, 'YYYYMMDD') AND TO_CHAR(SYSDATE+1, 'YYYYMMDDHH') "
    sql = sql + "  AND CREATE_CMF2 = 'MVL' "
    sql = sql + "  AND HIS_DELETE_FLAG <> 'Y' "
    sql = sql + "  AND OPER_OLD = '340' "
    sql = sql + "  AND OPER <> '340' "
    sql = sql + " ) "
    sql = sql + "AND OPER = '340' "
    sql = sql + "AND TRANS_CODE = 'SPLIT' "
    sql = sql + "AND FROM_TO_FLAG = 'T' " 
    sql = sql + "AND HIS_DELETE_FLAG <> 'Y' "
    sql = sql + "ORDER BY FROM_TO_LOT_ID "
        
    cur_mes1.execute(sql)
    mes_rows = cur_mes1.fetchall()    
    if cur_mes1.rowcount  >  0 :
        for row in mes_rows:
            wafer_split_list.append(row[0])
    
    #----------------------------
    sql = "SELECT DISTINCT LOT_ID FROM WIPLTH "
    sql = sql + "WHERE TRANS_TIME BETWEEN TO_CHAR(SYSDATE-10, 'YYYYMMDD') AND TO_CHAR(SYSDATE+1, 'YYYYMMDDHH')  "
    sql = sql + "AND CREATE_CMF2 = 'MVL' "
    sql = sql + "AND HIS_DELETE_FLAG <> 'Y' "
    sql = sql + "AND TRANS_CODE = 'HOLD' "
    sql = sql + "AND OPER = '340' "    
    sql = sql + "ORDER BY LOT_ID "
    
    cur_mes1.execute(sql)
    mes_rows = cur_mes1.fetchall()    
    if cur_mes1.rowcount  >  0 :
        for row in mes_rows:
            wafer_hold_list.append(row[0])
    #--------------------------------        
    
    
    mes_lot_list = list(set(wafer_out_list) | set(wafer_split_list) | set(wafer_hold_list))
    
    '''
    for s in mes_lot_list:
        result = result + s + ","
    
    result = result[:-1]   # 마지막 쉼표제거  
    result = '(' + result + ")"
    '''
    conn_mes1.close()
    
    return mes_lot_list
    

def get_yield_limit(sOper, smes_family_name) :
    conn_mes1 = cx_Oracle.connect('tpasdb')
    cur_mes1 = conn_mes1.cursor()
    tot_yield_limit = ""    
    
    #sql = "SELECT TOT_YIELD_LIMIT FROM  WIPBIN "
    sql = "SELECT RESV_FIELD2 FROM  WIPBIN "
    sql = sql + "WHERE OPER = '" + sOper + "' "
    sql = sql + "AND CREATE_CMF2 = 'MVL' " 
    sql = sql + "AND CREATE_CMF5 = '" + smes_family_name + "' "
    sql = sql + "AND RESV_FIELD2 <> ' ' "
    cur_mes1.execute(sql)
    mes_rows = cur_mes1.fetchall()    
    if cur_mes1.rowcount  >  0 :
        for row in mes_rows:
            tot_yield_limit = row[0]
    
    
    conn_mes1.close()
    
    return tot_yield_limit

def get_sort_type(slot, swafer_id) :
    
    conn_mes1 = cx_Oracle.connect('tpasdb')
    cur_mes1 = conn_mes1.cursor()
    sort_type = "FS"    
    
    #sql = "SELECT TOT_YIELD_LIMIT FROM  WIPBIN "
    sql = "SELECT DATA1 FROM UPTDAT "
    sql = sql + "WHERE FACTORY = 'TEST' "
    sql = sql + "AND TABLE_NAME = 'WAFER_SORT_TYPE' "
    sql = sql + "AND KEY1 = '" + slot + "' "
    sql = sql + "AND KEY2 = '" + swafer_id + "' "
    
    cur_mes1.execute(sql)
    mes_rows = cur_mes1.fetchall()    
    if cur_mes1.rowcount  >  0 :
        for row in mes_rows:
            sort_type = row[0]
    
    conn_mes1.close()
    
    return sort_type

def get_hold_criteria(sOper, smes_family_name) :
    conn_mes1 = cx_Oracle.connect('tpasdb')
    cur_mes1 = conn_mes1.cursor()
    dic_hold_criteria = {}
    i = 0
    min_bin = ""
    max_bin = ""
    shold_criteria = ""
    #sql = "SELECT TOT_YIELD_LIMIT FROM  WIPBIN "
    sql = "SELECT KEY3, DATA1 FROM WIP_SITDEF "
    sql = sql + "WHERE DATA_TYPE = 'QUALCOMM_SBL' "
    sql = sql + "AND FACTORY = 'TEST' "
    sql = sql + "AND KEY1 = '" + smes_family_name + "' "
    sql = sql + "AND KEY2 = '" + sOper + "' "
    sql = sql + "ORDER BY KEY3 "
    
    cur_mes1.execute(sql)
    mes_rows = cur_mes1.fetchall()    
    if cur_mes1.rowcount  >  0 :
        for row in mes_rows:
            i = i + 1
            dic_hold_criteria[row[0]] = row[1]
            if i == 1 :
                min_bin = row[0]
            max_bin = row[0]    
            
    if min_bin !=  "" :
        shold_criteria = min_bin + "-" + max_bin + " > " 
        
    conn_mes1.close()
    
    return dic_hold_criteria , shold_criteria

############################
def get_pdms_wafer_size(sdev, snormal_lot , soper , sprog_name) :
    
    global mail_text
    #-------------------
    x_size = 0
    y_size = 0
    itmsdev = ""
    sPDMS_notch = ""
    smes_family_name = ""
    sflow_code = ""
    sprobe_card_type = ""
    
    #-------------------
    conn_tpas1 = cx_Oracle.connect('tpasdb')    
    cur_tpas1 = conn_tpas1.cursor()

    # 1. get itms device using cust device
    sql = "SELECT DEVICENAME FROM INT_LINKAGE_DEVICES@wsprd_new "
    sql = sql + "WHERE SITEID = 'SCK' "
    sql = sql + "AND CUSTDEVICENAME = '" + sdev + "' "
    sql = sql + "AND STATUS = 'ACT' "

    cur_tpas1.execute(sql)
    tpas_rows = cur_tpas1.fetchall()
    if tpas_rows == None:
        pass
    else:
        for tpas_row in tpas_rows:  # 202029
            itmsdev = tpas_row[0]
    #------------------------------
    # 2. get x size , y size using itms device
    if itmsdev != "" :
        sql = "SELECT XMAX, YMAX, WAFER_TEST_MAP_DIRECTION FROM VW_MES_HEADER@WSPRD_NEW "
        sql = sql + "WHERE SITE_CODE = 'SCK' "
        sql = sql + "AND ITMS_DEVICE_NAME = '" + itmsdev + "' "
        #sql = sql + "AND STATUS = 'ACT' "

        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()
        if tpas_rows == None:
            pass
        else:
            for tpas_row in tpas_rows:  # 202029
                x_size = tpas_row[0]
                y_size = tpas_row[1]
                sPDMS_notch = tpas_row[2].upper()
    #######################
    if ((sdev == 'POLARIS-B0A-T14-SG') or (sdev == 'POLARIS-B0A-SG')) and (y_size == 0) :
        x_size = 60
        y_size = 63
    #######################
    ###############################
    # etraveller 
    sql = "SELECT FAMILY_NAME_MES FROM ET_PRODUCTION_TABLE "
    sql = sql + "WHERE LOT_NO = '" + snormal_lot + "' "
    sql = sql + "AND TESTSTAGE = '" + soper + "' "
    sql = sql + "AND PRODUCTION_STATUS = 'ACTIVATED' "
    sql = sql + "AND TEST_PROG_NAME = '" + sprog_name + "' "
    cur_tpas1.execute(sql)
    tpas_rows = cur_tpas1.fetchall()    
    if cur_tpas1.rowcount  >  0 :
        for row in tpas_rows:
            smes_family_name = row[0]

    #--------------------------------
    # temper , test code
    sql = "SELECT TEST_TEMPERATURE , TEST_CODE , DUT_CARD_ID , DELTACHECKREQYN , DELTALIMIT FROM VW_MES_TESTPROGRAM@WSPRD_NEW "
    sql = sql + "WHERE ITMS_DEVICE_NAME = '" + itmsdev + "' "
    #sql = sql + "AND TEST_PROGRAM_NAME = '" + sprog_name + "' "
    cur_tpas1.execute(sql)
    tpas_rows = cur_tpas1.fetchall()    
    if cur_tpas1.rowcount  >  0 :
        for row in tpas_rows:
            stemper =  str(int(row[0]))
            if stemper == "" or stemper == 'None' :
                stemper = ""
                
            stest_code = str(row[1])
            if stest_code == "" or stest_code == 'None' :
                stest_code = ""
            
            sflow_code = stest_code + "@" + stemper
            
            sprobe_card_type = row[2]
            if sprobe_card_type == None :
                sprobe_card_type = " "
            site_to_site_h_cri_flag = row[3]   
            site_to_site_h_cri = row[4]   
            
            if site_to_site_h_cri_flag == 'Y' :
                pass
            else :
                site_to_site_h_cri = " "
            
                
    #---------------------------------------
    
    conn_tpas1.close()
    
    return x_size , y_size, sPDMS_notch, smes_family_name, sflow_code , sprobe_card_type , site_to_site_h_cri ; 

############################
#  bump + stdf map file merge
def get_map_file(slot, swaferid, sbump_id , snotch , x_size , y_size , sfamily_name , soper) :
    
    global mail_text
    
    get_map_file_flag = True
    
    map_data = ""
    
    conn_tpas1 = cx_Oracle.connect('tpasdb' )        
    cur_tpas1 = conn_tpas1.cursor()
    
    conn_mes1 = cx_Oracle.connect('tpasdb')
    cur_mes1 = conn_mes1.cursor()
    # y, x
    
    stdf_array = [[" " for col in range(int(x_size)+1)] for row in range(int(y_size)+1)]
    bump_array = [[" " for col in range(int(x_size)+1)] for row in range(int(y_size)+1)]
    bump_array_convert = [[" " for col in range(int(x_size)+1)] for row in range(int(y_size)+1)]
    map_merge_array = [[" " for col in range(int(x_size)+1)] for row in range(int(y_size)+1)]
    
    sline_1 = ""
    sline_2 = ""
    sline_3 = ""
    
    for k in range(int(x_size)+1) :
        spos1 = k//10         # 정수값
        spos2 = k%10          # 나머지
        sline_1 = sline_1 + "{0:>5}".format(spos1)
        sline_2 = sline_2 + "{0:>5}".format(spos2)
        sline_3 = sline_3 + "{0:>5}".format('-')
        
    
    stdf_sx_max = 0
    stdf_sy_max = 0
    bump_sx_max = 0
    bump_sy_max = 0
    #####################
    
    if sfamily_name.strip().upper() == "SPICAPLUS" or sfamily_name.strip().upper() == "PG4" : 
        bump_flag = False
    else :
        bump_flag = True
        ################        
    try :
        #################
        # stdf map coordinate
        
        sql = "SELECT MAX(TO_NUMBER(X_POS)) , MAX(TO_NUMBER(Y_POS)) FROM TPAS_WAFERSUM_DAT "
        sql = sql + "WHERE LOT_ID = '" + slot + "' "
        sql = sql + "AND WAFER_ID = '" + swaferid + "' " 
        sql = sql + "AND OPER = '" + soper + "' "
        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()    
        if cur_tpas1.rowcount  >  0 :
            for row in tpas_rows:
                stdf_sx_max = row[0]
                stdf_sy_max = row[1]
                
        #----------------------------        
        sql = "SELECT X_POS , Y_POS , SBIN , SBIN_DESC , SITE  FROM TPAS_WAFERSUM_DAT "
        sql = sql + "WHERE LOT_ID = '" + slot + "' "
        sql = sql + "AND WAFER_ID = '" + swaferid + "' "
        sql = sql + "AND OPER = '" + soper + "' "
        sql = sql + "ORDER BY X_POS , Y_POS "
        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()    
        if cur_tpas1.rowcount  >  0 :
            for row in tpas_rows:
                sx_pos = row[0]
                sy_pos = row[1]
                s_bin = row[2]
                s_bin_desc = row[3]
                stdf_array[sy_pos][sx_pos] = s_bin
        #----------------------
        # stdf map
        sbin_all = ""
        for y in range(int(stdf_sy_max)+1) :
                sbin_line = ""
                for x in range(int(stdf_sx_max)+1) :
                    sbin = stdf_array[y][x]
                    sbin_line = sbin_line + "{0:>5}".format(sbin)
                sbin_all = sbin_all + sbin_line + '\n'    
                print(sbin_line)
        ####################            
        # bump map file
        #f = open(source_dir + '/stdf_bump.txt', 'w')
        #f.write(sbin_all)
        #f.close()       
        ######################           
        #------------------------
        # bump map coordinate - notch left
        # spica+ , pg4 는 merge 하면 안되고,  한 wafer 에 다른 device 가 존재하여 wafer sort 에서 다르게 투입됨. bump 안함.
        # 나머지는 merge 
        
        if  (sbump_id != None and bump_flag == True) :
            
            if sbump_id == None :
                msg = 'notch error !! ' + slot + " / " + swaferid + '\n' + 'bump map merge 시 bump id 를 찾을 수 없습니다. !! ' 
                writeLog(msg)
                mail_text = mail_text + msg
                get_map_file_flag = False
                conn_mes1.close()
                conn_tpas1.close()    
                return False 
                
            
            sql = "SELECT MAX(TO_NUMBER(X)) , MAX(TO_NUMBER(Y)) FROM BUMPEAP.WAFERMAP_UNIT_DETAIL@BUMPEAP_BUMPEAP "
            sql = sql + "WHERE ID = '" + sbump_id + "' "
            sql = sql + "ORDER BY X, Y "
            cur_mes1.execute(sql)
            mes_rows = cur_mes1.fetchall()
            
            if cur_mes1.rowcount  >  0 :
                for row in mes_rows :
                    bump_sx_max = row[0]
                    bump_sy_max = row[1]
                    
                    
            sql = "SELECT X, Y, BIN FROM BUMPEAP.WAFERMAP_UNIT_DETAIL@BUMPEAP_BUMPEAP "
            sql = sql + "WHERE ID = '" + sbump_id + "' "
            sql = sql + "ORDER BY X, Y "
            cur_mes1.execute(sql)
            mes_rows = cur_mes1.fetchall()
            
            if cur_mes1.rowcount  >  0 :
                for row in mes_rows :
                    sx_pos = row[0]
                    sy_pos = row[1]
                    s_bin = row[2]
                    bump_array[sy_pos][sx_pos] = s_bin
            #------------------------------------
            sbin_all = ""
            for y in range(int(bump_sy_max)+1) :
                sbin_line = ""
                for x in range(int(bump_sx_max)+1) :
                    sbin = bump_array[y][x]
                    sbin_line = sbin_line + "{0:>5}".format(sbin)
                sbin_all = sbin_all + sbin_line + '\n'    
                print(sbin_line)
            
            print(sbin_all)        
            ####################            
            # bump map file
            f = open(source_dir + '/bump.txt', 'w')
            f.write(sbin_all)
            f.close()       
            ######################        
            # bump 는 모두 left
            # 
            '''
            좌표변환공식						
                            원본 좌표		변환좌표		
            시계방향 90		(x, y)		(y_size - y , x)		
            180		        (x, y)		(x_size - x , y_size - y)		
            270		        (x, y)		(y , x_size - x)		
            '''
            # stdf notch 방향이 down 이면 bump left 를 270도 돌려야함.
            if snotch == "DOWN" or snotch == "BOTTOM" :
                for col in range(int(bump_sx_max)+1) :
                    for row in range(int(bump_sy_max)+1) :
                        bump_array_convert[sy_pos][sx_pos] = bump_array[bump_sx_max - sx_pos][sy_pos]
                
                
            elif snotch == "LEFT" :
                for x in range(int(bump_sx_max)+1) :
                    for y in range(int(bump_sy_max)+1) :
                        bump_array_convert[y][x] = bump_array[y][x]
                
            elif snotch == "RIGHT" :
                for x in range(int(bump_sx_max)+1) :
                    for y in range(int(bump_sy_max)+1) :
                        bump_array_convert[y][x] = bump_array[bump_sy_max - y][bump_sx_max - x]
                
            elif snotch == "UP" or snotch == "TOP" :     
                for col in range(int(bump_sx_max)+1) :
                    for row in range(int(bump_sy_max)+1) :
                        bump_array_convert[sy_pos][sx_pos] = bump_array[sx_pos][bump_sy_max - sy_pos]
                
            else :
                msg = 'notch error !! ' + slot + " / " + swaferid + '\n' + 'bump map notch 변환시 notch 방향이 지정되어 있지 않습니다. !! ' 
                writeLog(msg)
                mail_text = mail_text + msg
                get_map_file_flag = False
                conn_mes1.close()
                conn_tpas1.close()    
                return False 
            
            ############################    
            sbin_all = ""
            for y in range(int(bump_sy_max)+1) :
                sbin_line = ""
                for x in range(int(bump_sx_max)+1) :
                    sbin = bump_array_convert[y][x]
                    sbin_line = sbin_line + "{0:>5}".format(sbin)
                sbin_all = sbin_all + sbin_line + '\n'    
                print(sbin_line)
            
            print(sbin_all)        
            ####################            
            # bump map convert file
            f = open(source_dir + '/bump_map_convert.txt', 'w')
            f.write(sbin_all)
            f.close()       
            ######################           
            # merge map 
            sbin_all = ""
            for y in range(int(bump_sy_max)+1) :
                sy_pos = '{0:02d}'.format(y)
                sbin_line = "{0:>8}".format( '+' + sy_pos) + "{0:>3}".format('|')
                   
                for x in range(int(bump_sx_max)+1) :
                    sbump_bin = bump_array_convert[y][x]
                    stdf_bin = stdf_array[y][x]
                    
                    #--------------------
                    if (sbump_bin == '___') or (sbump_bin == '.') :
                        if stdf_bin.strip() != ""  :
                            msg = 'no die error !! ' + slot + " / " + swaferid + '\n' + 'bump map no die 인데 stdf map 은 die 가 있습니다. ' 
                            writeLog(msg)
                            mail_text = mail_text + msg
                            return False
                    #----------------------
                    # 2022/08/23 진공섭 gj
                    # bump reject 은 
                    # Bump reject 에 대해서는 SBIN222 로 표기 가 되어야 하니 Map/ Sum file 에 반영 될 수 있도록 도움 부탁 드립니다 
                    
                    if stdf_bin.strip() == '' and sbump_bin != '___' and sbump_bin != '.' and sbump_bin != '000' :
                        stdf_bin = '999'  # BUMP REJECT
                    
                    map_merge_array[y][x] = stdf_bin   
                    #--------------------------
                    sbin_line = sbin_line + "{0:>5}".format(stdf_bin)
                
                sbin_all = sbin_all + sbin_line + '\n'    
                print(sbin_line)
            ####################            
            # map merge file
            f = open(source_dir + '/merge.txt', 'w')
            f.write(sbin_all)
            f.close()       
            ######################        
            #bump_array_rotation =
        else :
            ######################           
            # merge map 
            sbin_all = ""
                    
            for y in range(int(stdf_sy_max)+1) :
                sy_pos = '{0:02d}'.format(y)
                sbin_line = "{0:>8}".format( '+' + sy_pos) + "{0:>3}".format('|')
                   
                for x in range(int(stdf_sx_max)+1) :                    
                    stdf_bin = stdf_array[y][x]
                    
                    map_merge_array[y][x] = stdf_bin   
                    #--------------------------
                    sbin_line = sbin_line + "{0:>5}".format(stdf_bin)
                
                sbin_all = sbin_all + sbin_line + '\n'    
                print(sbin_line)
            ####################     
        ################################
        # 여기서 MERGE 함.
        pre_space = "  "
        map_data = pre_space + pre_space + pre_space + pre_space + pre_space + ' ' + sline_1 + '\n'
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + ' ' + sline_2 + '\n'
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + pre_space + '\n'
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + pre_space + '\n'
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + '+' + sline_3 + '  +' + '\n'
        map_data = map_data + sbin_all 
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + '+' + sline_3 + '  +' + '\n'
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + ' ' + sline_1 + '\n'
        map_data = map_data + pre_space + pre_space + pre_space + pre_space + pre_space + ' ' + sline_2 + '\n'
        
        ####################            
        # map merge file
        #f = open(source_dir + '/map.txt', 'w')
        #f.write(map_data)
        #f.close()       
        ######################   
        
        #map_data = stdf_array        
        #-------------------------------
            
    except :
        msg = 'Yield Error !! ' + '\n' + slot + " / " + swaferid 
        writeLog(msg)
        mail_text = mail_text + msg
        conn_mes1.close()
        conn_tpas1.close()  
        return False  
        #conn_mes1.close()
        #conn_tpas1.close()
    
    conn_mes1.close()
    conn_tpas1.close()
    #conn_tpas1.close()
        
    return map_data 

# bump + stdf map file merge end

##################################
############################
# SITE 별 BIN SUMMARY

def get_site_bin_sum(slot, swaferid, stot_yield_limit , soper , site_to_site_h_cri ) :    
    
    global mail_text
    
    get_site_bin_sum_flag = True
    
    dic_site_sum = {}
    dic_site_sum.clear()
    dic_site = {}
    dic_site.clear()
    dic_pass = {}
    dic_pass.clear()
    dic_fail = {}
    dic_fail.clear()
    
    dic_passfail_sum = {}
    dic_passfail_sum.clear()
    
    
    site_sum = ""
    pass_sum = 0
    fail_sum = 0
    passfail_sum = 0
    min_yield = 100.00
    max_yield = 0.00
    
    conn_tpas1 = cx_Oracle.connect('tpasdb' )        
    cur_tpas1 = conn_tpas1.cursor()
    
    
    try :
        sql = "SELECT SITE, DECODE(PASSFAIL,NULL,'SUM',PASSFAIL), COUNT(WAFER_ID) FROM TPAS_WAFERSUM_DAT "
        sql = sql + "WHERE LOT_ID = '" + slot + "' "
        sql = sql + "AND WAFER_ID = '" + swaferid + "' "
        sql = sql + "AND OPER = '" + soper + "' "
        sql = sql + "AND PASSFAIL IN ('PASS', 'FAIL') "
        sql = sql + "GROUP BY ROLLUP(SITE,PASSFAIL) "
        sql = sql + "ORDER BY SITE "
        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()    
        if cur_tpas1.rowcount  >  0 :
            for row in tpas_rows:
                ssite = row[0]
                spass_flag = row[1]
                bin_cnt = row[2]
                #skey = ssite + '~' + spass_flag
                if (str(ssite) == "") or  (ssite == None) :
                    continue
                #--------------------------
                if  spass_flag == 'PASS' :
                    pass_sum = pass_sum + bin_cnt
                    if ssite in dic_pass :
                        del dic_pass[ssite]
                    dic_pass[ssite] = bin_cnt   
                #-----------------------
                if  spass_flag == 'FAIL' :
                    fail_sum = fail_sum + bin_cnt
                    if ssite in dic_fail :
                        del dic_fail[ssite]
                    dic_fail[ssite] = bin_cnt      
                #----------------------------- 
                if  spass_flag == 'SUM' :
                    passfail_sum = passfail_sum + bin_cnt
                    if ssite in dic_passfail_sum :
                        del dic_passfail_sum[ssite]
                    dic_passfail_sum[ssite] = bin_cnt      
                #-----------------------------
                
        #----------------------
        yield_1 = "{0:<12}".format("Test Site")
        yield_2 = "{0:<12}".format("Pass Count")
        yield_3 = "{0:<12}".format("Fail Count")
        yield_4 = "{0:<12}".format("Total Count")
        yield_5 = "{0:<12}".format("Site Yield%")
        #--------------------
        line_str1 = "{0:-<12}".format("'")
        line_str2 = "{0:=<12}".format("'")
        #---------------------
        for k in dic_passfail_sum.keys():
            yield_1 = yield_1 + "{0:>10}".format(k) 
            #---------------------------
            yield_2 = yield_2 + "{0:>10}".format(dic_pass.get(k,' ')) 
            yield_3 = yield_3 + "{0:>10}".format(dic_fail.get(k,' '))        
            yield_4 = yield_4 + "{0:>10}".format(dic_passfail_sum.get(k,' '))  
            #------------------------
            # site 별 yield
            tmp_tot = dic_passfail_sum.get(k,0)
            tmp_pass = dic_pass.get(k,0)
            tmp_yield = (tmp_pass / tmp_tot) * 100
            tmp_yield = str(round(tmp_yield,2))
            
            yield_5 = yield_5 + "{0:>10}".format(tmp_yield + '%')         
            #-------------------------
            line_str1 = line_str1 + "{0:-<10}".format("")
            line_str2 = line_str2 + "{0:=<10}".format("")
            #-------------------------
            # mix yield ,max yield 
                        
            if float(tmp_yield) < min_yield :
                min_yield = float(tmp_yield)
            if float(tmp_yield) > max_yield :
                max_yield = float(tmp_yield)  
        
        yield_1 = yield_1 + "{0:>8}".format("ALL")
        yield_2 = yield_2 + "{0:>8}".format(pass_sum)  
        yield_3 = yield_3 + "{0:>8}".format(fail_sum) 
        yield_4 = yield_4 + "{0:>8}".format(passfail_sum)
        line_len = len(yield_4)
        #------------------------------------
        line_str1 = line_str1 + "{0:-<10}".format("")
        line_str2 = line_str2 + "{0:=<10}".format("")
        #------------------------------------            
        tmp_yield = (pass_sum / passfail_sum) * 100
        tmp_yield = str(round(tmp_yield,2)) + '%'    
        yield_5 = yield_5 + "{0:>8}".format(tmp_yield) 
        #-------------------------------------
        syield_delta = max_yield - min_yield
        yield_6 = "Site-To-Site Delta         : " + str(round(float(syield_delta),2))
        # 수정해야함.
        if site_to_site_h_cri.strip() == "" :
            yield_7 = "Site-To-Site Hold Criteria : "         # <== ?
        else :
            yield_7 = "Site-To-Site Hold Criteria : " +  site_to_site_h_cri        # <== ?
        #------------------        
        yield_8 = "Laser Repair Rate          : "
        yield_9 = "L/R Hold Criteria          : " + str(round(float(stot_yield_limit),2))

        pre_space = "  "
        yield_data = pre_space + pre_space + pre_space + ' ' + yield_1 + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + line_str1 + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_2  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_3  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_4  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + line_str2 + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_5  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + line_str1 + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_6  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_7  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_8  + '\n'
        yield_data = yield_data + pre_space + pre_space + pre_space + ' ' + yield_9  + '\n'
        
        #print(yield_data)
        
    except :
        msg = 'Yield Error !! ' + '\n' + slot + " / " + swaferid 
        writeLog(msg)
        mail_text = mail_text + msg
        conn_tpas1.close()
        get_site_bin_sum_flag = False
        return False
    
    
    conn_tpas1.close()
        
    return yield_data

# [YieldSummaryBegin]  end
##################################
# ;bin summary 
############################
# SITE 별 [BinSummaryBegin]

def get_binsum_yield(slot, swaferid, stot_yield_limit, sDev, dic_hold_criteria , shold_criteria , soper ,sprog_name ) :    
    
    global mail_text
    
    get_binsum_yield_flag = True
        
    dic_binsum_site = {}
    dic_binsum_site.clear()
    
    dic_site_list = {}
    dic_site_list.clear()
    
    dic_bin_list = {}
    dic_bin_list.clear()
    
    site_sum = ""
    pass_sum = 0
    fail_sum = 0
    passfail_sum = 0
    min_yield = 100.00
    max_yield = 0.00
    
    conn_tpas1 = cx_Oracle.connect('tpasdb' )        
    cur_tpas1 = conn_tpas1.cursor()
    try :
        sql = "SELECT DISTINCT SITE FROM TPAS_WAFERSUM_DAT "
        sql = sql + "WHERE LOT_ID = '" + slot + "' "
        sql = sql + "AND WAFER_ID = '" + swaferid + "' "  
        sql = sql + "AND OPER = '" + soper + "' "
        sql = sql + "ORDER BY TO_NUMBER(SITE) "
        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()    
        if cur_tpas1.rowcount  >  0 :
            for row in tpas_rows:            
                ssite = row[0]
                dic_site_list[ssite] = ssite
        #---------------------------------------
        conn_mes1 = cx_Oracle.connect('tpasdb')
        cur_mes1 = conn_mes1.cursor()
        sql = "SELECT KEY2, DATA1 FROM UPTDAT2 "
        sql = sql + "WHERE FACTORY = 'TEST' "
        sql = sql + "AND TABLE_NAME = 'TEST_WAFER_BIN' "
        sql = sql + "AND KEY1 = '" + sDev + "' "
        sql = sql + "AND KEY3 = '" + sprog_name + "' "
        
        sql = sql + "ORDER BY TO_NUMBER(KEY2) "
        cur_mes1.execute(sql)
        mes_rows = cur_mes1.fetchall()    
        if cur_mes1.rowcount  >  0 :
            for row in mes_rows:            
                sbin = row[0]
                sbin_desc = row[1]
                dic_bin_list[sbin] = sbin_desc      
        conn_mes1.close()        
        #--------------------------------------
            
        sql = "SELECT SBIN , DECODE(SITE, NULL, 'SBIN_SUM',SITE) , COUNT(WAFER_ID) FROM TPAS_WAFERSUM_DAT "
        sql = sql + "WHERE LOT_ID = '" + slot + "' "
        sql = sql + "AND WAFER_ID = '" + swaferid + "' "
        sql = sql + "AND OPER = '" + soper + "' "
        sql = sql + "GROUP BY ROLLUP(SBIN, SITE) "        
        sql = sql + "ORDER BY TO_NUMBER(SBIN),SITE "
        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()    
        if cur_tpas1.rowcount  >  0 :
            for row in tpas_rows:
                sbin = row[0]
                ssite = row[1]
                sbin_cnt = row[2]
                #skey = ssite + '~' + spass_flag
                
                if (sbin == None) and (ssite == "SBIN_SUM") :
                    stot_sbin_qty = sbin_cnt
                
                if (sbin == None) or (ssite == None) :
                    continue
                #--------------------------                
                dic_binsum_site[sbin,ssite] = sbin_cnt
                 
        
        line_header = "{0:<4}".format("Bin#") + "{0:>10}".format("Num") + "{0:>8}".format("Yield")
        # '==============================================================================
        # 위 라인 표시
        line_str1 = "{0:=<22}".format("")
        #'--------------------------------------------------------------------------------------------
        # 위 라인표시
        line_str2 = "{0:-<22}".format("")
        ########################
        sitesum_data = []
        dic_sitesum_list = {}
        dic_sitesum_list.clear()
        sitesum_count = [0,1,2,3,4,5,6,7,8]
        ########################    
        for k in dic_site_list.keys() :
            line_str1 = line_str1 + "{0:=<6}".format("")
            line_str2 = line_str2 + "{0:-<6}".format("")
            line_header = line_header + "{0:>6}".format(str(k))
            
        #-------------------
        line_str1 = line_str1 + "{0:=<70}".format("")
        line_str2 = line_str2 + "{0:-<70}".format("")
        line_header = line_header + "     " + "{0:<65}".format("Description")
        line_str1 = line_str1 + "{0:=<42}".format("")
        line_str2 = line_str2 + "{0:-<42}".format("")
        line_header = line_header + "  " + "{0:<40}".format("Hold Criteria")
        ############################
        pre_space = "  "
        bin_data = ""           
        #---------------------
        for k1 in dic_bin_list.keys() : 
            
            bin_data = bin_data + pre_space + pre_space + pre_space 
            
            if (k1, 'SBIN_SUM') in dic_binsum_site.keys() :                  
                sbin_qty = dic_binsum_site[(k1,'SBIN_SUM')]
                syield = sbin_qty / stot_sbin_qty * 100 
                syield = str(round(syield,2)) + '%'            
            else :
                sbin_qty = "0"
                syield = "0.00%" 
            #-----    
            bin_data = bin_data + "{0:<4}".format(str(k1)) + "{0:>10}".format(sbin_qty)                  
            bin_data = bin_data + "{0:>8}".format(syield)  
            #---------------------
            # 초기화
            if int(sbin_qty) > 0 :
                for ss in sitesum_count:
                    dic_sitesum_list[k1,ss] = '0'
            #---------------------
                           
            for k2 in dic_site_list.keys():                
                if (k1, str(k2)) in dic_binsum_site.keys() :                    
                    sbin_qty_site = dic_binsum_site[(k1,str(k2))]                    
                    bin_data = bin_data + "{0:>6}".format(sbin_qty_site)   
                    ##-------------------------
                    # sitesum data db 저장
                    if sbin_qty > 0 :
                        dic_sitesum_list[k1,k2] = sbin_qty_site
                else:
                    bin_data = bin_data + "{0:>6}".format('0')
                    
                #----------------------------------------------
                        
            #-------------------------- 
            if k1 in dic_bin_list.keys():    
                sbin_desc = dic_bin_list[k1]
                bin_data = bin_data + "   " + "/*" + "{0:<65}".format(sbin_desc) + "*/"
            else:
                sbin_desc = "No Desc"
                bin_data = bin_data + "   " + "/*" + "{0:<65}".format(sbin_desc) + "*/"
                msg = 'No SBIN DESC !! UPT - TEST_WAFER_BIN 에 등록해야합니다. ' + '\n' + slot + " / " + swaferid + " / " + sfamily_name
                writeLog(msg)
                mail_text = mail_text + msg
                get_binsum_yield_flag = False
                conn_tpas1.close()
                return False                    
                #---------------------------
            #---------------------------
            # hold criteria
            
            if k1 in dic_hold_criteria.keys() :        
                s = dic_hold_criteria[k1]
                s = shold_criteria + s + '%'
                bin_data = bin_data + "{0:<40}".format(s) + "\n"
            else :
                s = ''
                bin_data = bin_data + "\n"    
            #############################
            # site 정보 db 저장
            if int(sbin_qty) > 0 :
                sbinsum_site_dat = (slot,swaferid,soper,k1,sbin_desc,sbin_qty,syield,dic_sitesum_list[k1,0],dic_sitesum_list[k1,1], \
                            dic_sitesum_list[k1,2], dic_sitesum_list[k1,3], dic_sitesum_list[k1,4], dic_sitesum_list[k1,5], dic_sitesum_list[k1,6], \
                            dic_sitesum_list[k1,7], dic_sitesum_list[k1,8], s )  
                sitesum_data.append(sbinsum_site_dat) 
            #############################
        pre_space = "  "
        data = pre_space + pre_space + " '" + line_str1 + '\n'
        data = data + pre_space + pre_space + pre_space + line_header + '\n'
        data = data + pre_space + pre_space + " '" + line_str2 + '\n'
        data = data + bin_data + '\n'  
        data = data + pre_space + pre_space + " '" + line_str1 + '\n'
                
        print(data)
        #######################################
        # binsummary 를 db 에 저장해야힘.
        # web 에서 조회가능하게
        #######################################
        if len(sitesum_data) > 0:
            
            sql = "DELETE FROM TPAS_WAFERSUM_DAT_SBIN "
            sql = sql + "WHERE LOT_ID = '" + slot + "' "
            sql = sql + "AND WAFER_ID = '" + swaferid + "' "
            sql = sql + "AND OPER = '" + soper + "' "
            cur_tpas1.execute(sql)
            conn_tpas1.commit()
            
            sql = "INSERT INTO TPAS_WAFERSUM_DAT_SBIN (LOT_ID,WAFER_ID ,OPER, SBIN,SBIN_DESC,TOT_QTY ,"
            #                                     1     ,   2     ,  3 ,   4 ,   5     , 6     ,
            sql = sql + " YIELD, SITE_0, SITE_1, SITE_2, SITE_3, SITE_4, SITE_5, SITE_6, SITE_7, SITE_8, HOLD_CRI, TRANS_TIME ) "
            #              7   ,    8  ,   9   ,   10   , 11   ,   12  ,   13  ,   14  ,  15   ,  16   ,  17                
            sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, "
            sql = sql + "  :11, :12, :13, :14, :15, :16, :17, TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS') ) "
            cur_tpas1.executemany(sql,sitesum_data)
            conn_tpas1.commit()
             
            msg = 'TPAS_WAFERSUM_DAT_SBIN Insert complete !! ' + '\n' + " " + swaferid
            print(msg)
            #writeLog(msg)
            #mail_text = mail_text + msg + '\n'
        ###########################
        #data = []
        sitesum_data = []
                
    except :
        msg = 'Yield Error !! ' + '\n' + slot + " / " + swaferid 
        writeLog(msg)
        mail_text = mail_text + msg
        conn_tpas1.close()
        
        return False
    
    conn_tpas1.close()
        
    return data 

# [BinSummaryBegin]  end
##########################
# 2. wafer summary file 의 [SummaryBegin]				
# 'Note : sort by bin number ascending

def get_summary_file_sum(slot, soper, dic_hold_criteria , shold_criteria , sDev , sprog_name) :    
    
    global mail_text
    
    get_summary_file_sum_flag = True
        
    dic_sum_file_sum_bin = {}
    dic_sum_file_sum_bin.clear()
    dic_bin_list = {}
    dic_bin_list.clear()
    dic_wafer_bin_sum = {}
    dic_wafer_bin_sum.clear()
    dic_wafer_bin_cnt = {}
    dic_wafer_bin_cnt.clear()
    dic_wafer_bin_yield = {}
    dic_wafer_bin_yield.clear()
    
    site_sum = ""
    pass_sum = 0
    fail_sum = 0
    passfail_sum = 0
    min_yield = 100.00
    max_yield = 0.00
    
    pre_space = "  "
    line_data = ""
        
    
    conn_tpas1 = cx_Oracle.connect('tpasdb' )        
    cur_tpas1 = conn_tpas1.cursor()
    cur_tpas2 = conn_tpas1.cursor()
    try :
        
        line_str1 = "{0:=<115}".format("'")
        line_str2 = "{0:-<115}".format("'")
        line_header = "{0:<20}".format("WaferID") + "{0:<12}".format("Tester#") + "{0:<37}".format("ProbeCard#") + "{0:<11}".format("Yield") + "{0:<15}".format("RepairRate")  \
                      + "{0:<10}".format("Total") +  "{0:<10}".format("Pass") 
        
        #---------------------------------------
        # header bin name fix 시킴
        conn_mes1 = cx_Oracle.connect('tpasdb')
        cur_mes1 = conn_mes1.cursor()
        sql = "SELECT KEY2, DATA1 FROM UPTDAT2 "
        sql = sql + "WHERE FACTORY = 'TEST' "
        sql = sql + "AND TABLE_NAME = 'TEST_WAFER_BIN' "
        sql = sql + "AND KEY1 = '" + sDev + "' "
        sql = sql + "AND KEY3 = '" + sprog_name + "' "
        sql = sql + "ORDER BY TO_NUMBER(KEY2) "
        cur_mes1.execute(sql)
        mes_rows = cur_mes1.fetchall()    
        if cur_mes1.rowcount  >  0 :
            for row in mes_rows:            
                sbin = row[0]
                line_header = line_header + "{0:<10}".format(str(sbin))
                line_str1 = line_str1 + "{0:=<10}".format('')
                line_str2 = line_str2 + "{0:-<10}".format('')
                sbin_desc = row[1]
                dic_bin_list[sbin] = sbin_desc   
        else:
            msg = 'No SBIN DESC !! UPT - TEST_WAFER_BIN 에 등록해야합니다. ' + '\n' + slot + " / " + sDev
            writeLog(msg)
            mail_text = mail_text + msg
             
            conn_mes1.close() 
            return False        
                       
        conn_mes1.close()        
        #--------------------------------------        
                ###########################
        # # 2. wafer summary file 의 [SummaryBegin]	
        tot_qty = 0
        pass_qty = 0
        sql = "SELECT LOT_ID, WAFER_ID, TESTER_ID , PROBECARD_ID, FINAL_YIELD, TOT_QTY, FINAL_GOOD_QTY FROM TPAS_WAFERSUM_INF "
        #               0         1        2            3               4         5       6
        sql = sql + "WHERE LOT_ID = '" + slot + "' "        
        sql = sql + "AND OPER = '" + soper + "' "
        sql = sql + "ORDER BY LOT_ID, WAFER_ID "
        
        cur_tpas1.execute(sql)
        tpas_rows1 = cur_tpas1.fetchall()    
        if cur_tpas1.rowcount  >  0 :
            for row in tpas_rows1:   
                tot_qty = tot_qty + int(row[5])
                pass_qty = pass_qty + int(row[6])
                swaferid = row[1]
                sfinal_yield = row[4]
                sfinal_yield = "{:.2f}".format(sfinal_yield)
                dic_wafer_bin_cnt = {}
                dic_wafer_bin_cnt.clear()
                #-----------------------
                # wafer 별 header                                    
                line_data = line_data + "{0:<20}".format(row[1]) + "{0:<12}".format(row[2]) + "{0:<37}".format(row[3]) + "{0:<11}".format(sfinal_yield) + "{0:<15}".format("0.00%")  \
                      + "{0:<10}".format(row[5]) +  "{0:<10}".format(row[6]) 
                #------------------------        
                # wafer bin 별 summary
                sql = "SELECT SBIN, COUNT(SBIN) FROM TPAS_WAFERSUM_DAT "
                sql = sql + "WHERE LOT_ID = '" + slot + "' "
                sql = sql + "AND WAFER_ID = '" + swaferid + "' "  
                sql = sql + "AND OPER = '" + soper + "' "
                sql = sql + "GROUP BY SBIN "
                sql = sql + "ORDER BY TO_NUMBER(SBIN)"
                cur_tpas2.execute(sql)
                tpas_rows2 = cur_tpas2.fetchall()    
                if cur_tpas2.rowcount  >  0 :
                    for row2 in tpas_rows2:            
                        sbin = row2[0]
                        sbin_cnt = row2[1]
                        dic_wafer_bin_cnt[sbin] = sbin_cnt
                        
                        if sbin in dic_wafer_bin_sum.keys() : 
                            dic_wafer_bin_sum[sbin] = int(dic_wafer_bin_sum[sbin]) + sbin_cnt
                        else  :
                            dic_wafer_bin_sum[sbin] = sbin_cnt
                
                for k_bin_list in dic_bin_list.keys() :  
                    if k_bin_list in dic_wafer_bin_cnt.keys() :                  
                        sbin_qty = dic_wafer_bin_cnt[k_bin_list]
                    else :
                        sbin_qty = "0"
                            
                    line_data = line_data + "{0:<10}".format(str(sbin_qty))
                
                
                line_data = line_data + '\n'
                
            # 다음 wafer summary 다음 라인에 출력                
        ##########################################
        #2. wafer summary file 의 [SummaryBegin]	
        #--------------------------------------
        line_data = line_data + line_str2 + '\n'
        line_data = line_data + "{0:<20}".format("Total") + "{0:<12}".format(" ") + "{0:<37}".format(" ") + "{0:<11}".format(" ") + "{0:<15}".format(" ") \
                    +  "{0:<10}".format(str(tot_qty)) +  "{0:<10}".format(str(pass_qty)) 
        
        line_tot_yield = "{0:<20}".format("Precentage") + "{0:<12}".format(" ") + "{0:<37}".format(" ") + "{0:<11}".format(" ") + "{0:<15}".format(" ") \
                    +  "{0:<10}".format(str(" ")) +  "{0:<10}".format(" ")             
        
        for k_bin_sum in dic_bin_list.keys() :  
            if k_bin_sum in dic_wafer_bin_sum.keys() :                  
                sbin_qty = dic_wafer_bin_sum[k_bin_sum]
            else :
                sbin_qty = "0"
                            
            line_data = line_data + "{0:<10}".format(str(sbin_qty))
            
            #-------------------------------------------             
            syield = int(sbin_qty) / tot_qty * 100 
            syield = str(round(syield,2)) + '%'          
                
            line_tot_yield = line_tot_yield + "{0:<10}".format(syield)
        #------------------------------
        
        line_data = line_data + '\n'
        line_data = line_data + line_tot_yield + '\n'
        line_data = line_data + line_str1 + '\n'        
        #------------------------------
        data = line_str1 + '\n'
        data = data + line_header + '\n'
        data = data + line_str2 + '\n'
        data = data + line_data 
        data = data + '[SummaryEnd]' + '\n' + '\n'        
        ############################
        #
        line_str1 = "{0:=<100}".format("'")
        line_header = "{0:<10}".format("Bin#") + "{0:<65}".format("Description") 
        line_str2 = "{0:-<100}".format("'")
        
        line_data1 = ""
        #####################################
        for k_bin_list in dic_bin_list.keys() :          
            line_data1 = line_data1 + "{0:<10}".format(' BIN' + str(k_bin_list)) + '  ' + "{0:<65}".format( dic_bin_list[k_bin_list]) + '  ' 
            #---------------------------
            # hold criteria
            if k_bin_list in dic_hold_criteria.keys() :        
                s = dic_hold_criteria[k_bin_list]
                s = shold_criteria + s + '%'
                line_data1 = line_data1 + "{0:<25}".format(s) + "\n"
            else :
                line_data1 = line_data1 + "\n"    
            #############################
            
        ######################        
        data = data + '[BinDefBegin]' + '\n'
        data = data + line_str1 + '\n'
        data = data + line_header + '\n'
        data = data + line_str2 + '\n'
        data = data + line_data1        
        data = data + '[BinDefEnd]' + '\n' + '\n'       
        
        return data    
         
    except:
        msg = str(i) + '\n' + '2. wafer summary report gen Error !! ' + '\n' + slot + " / " + swaferid 
        mail_text = mail_text + '\n' + msg + '\n'
        print(msg)
        writeLog(msg)
        return False

#####################################
# main function
print("== mvl wafer report generation ==")
log_dest = "c:/temp/mvl_wafer_report/log/"

p = Path(log_dest)
p.mkdir(exist_ok=True)

conn_tpas = cx_Oracle.connect('tpasdb' )        
cur_tpas = conn_tpas.cursor()

#################
# table field 순서
sLOT_ID =           0
sWAFER_ID =         1 
sSUB_LOT_ID =       2 
sUSER_ID =          3 
sCUSTOMER =         4 
sLEAD_CNT =         5 
sDEVICE =           6 
sPKG_ID =           7 
sHPSMARTEST_REV =   8 
sTESTER_ID =        9 
sTESTPROG =         10
sTESTFLOW =         11
sUSERPROC =         12
sWAFERTYPE =        13
sAPPLICATION =      14
sFILENAME =         15
sCONFIG =           16
sLEVEL_NAME =       17
sTIMING =           18
sVERTOR =           19
sATTRIB =           20
sSTART_TIME =       21
sEND_TIME =         22
sRETEST_SEQ   =     23
sTOT_QTY =          24
sFIRST_GOOD_QTY =   25
sFINAL_GOOD_QTY =   26
sFIRST_FAIL_QTY =   27
sFINAL_FAIL_QTY =   28
sFIRST_YIELD =      29
sFINAL_YIELD =      30
sNORMAL_LOTID =     31
sREADFLAG =         32
sLOADBOARD_ID =     33
sHANDLER_ID =       34
sPRODUCT_ID =       35
sTESTPROG_REV =     36
sRETEST_CODE =      37
sTESTDESC =         38
sTRANS_FLAG =       39
sOPER =             40
sSBL_FLAG =         41
sPROBECARD_ID =     42
sNOTCH_DIRECTION =  43
sTRANS_TIME =       44
sFAMILY_NAME =      45
sJOB_REV =          46
sPRODUCT_NAME =     47
sBD_FILE_NAME =     48
sFILE_CNT =         49
sBUMP_TOT_QTY =     50
sBUMP_REJ_QTY =     51
sBUMP_MAP_ID  =     52
sTOT_WAFER_QTY =    53
sWAFER_SORT_PROCESS = 54
sWAFER_SORT_TYPE = 55
sTEST_HOUSE = 56
sPROBECARD_TYPE = 57
                    

try:
    
    mes_lot_list = get_mes_lot_list()
     
    for s in mes_lot_list :
    
        sql = "SELECT * FROM TPAS_WAFERSUM_INF "
        sql = sql + "WHERE NORMAL_LOTID = '" + s + "' "
        sql = sql + "AND READFLAG = 'N' "
        sql = sql + "AND CUSTOMER = 'INP' "
        
        # test , 적용시 삭제요망
        #sql = sql + "AND UPPER(FAMILY_NAME) IN ('SPICAPLUS' , 'PG4') "
        #sql = sql + "AND LOT_ID = 'TH6U75.00' "
        
        sql = sql + "ORDER BY LOT_ID, WAFER_ID "
        cur_tpas.execute(sql)
        rows = cur_tpas.fetchall()
        
        if cur_tpas.rowcount <= 0 :
            continue
        i = 0
        data = ""
        pre_space = "  "
        for row in rows:
            i = i + 1
            #data = ""            
            slot = row[sLOT_ID]
            swaferid = row[sWAFER_ID]
            sDev = row[sDEVICE]
            sUserproc = row[sUSERPROC]
            sTemper = row[sTESTDESC]
            snormal_lot = row[sNORMAL_LOTID]
            soper   = row[sOPER]
            sprog_name = row[sTESTPROG]
            swaferid = row[sWAFER_ID]
            suser = row[sUSER_ID]
            sprobe_card = row[sPROBECARD_ID]
            stot_die = row[sBUMP_TOT_QTY]
            if stot_die == 0 :
                stot_die = row[sTOT_QTY]
            
            software_ver = row[sHPSMARTEST_REV]
            sNotch = row[sNOTCH_DIRECTION]
            sbump_id = row[sBUMP_MAP_ID]
            sfamily_name = row[sFAMILY_NAME]
            sfamily_name = sfamily_name.upper()
            
            stot_wafer_qty = row[sTOT_WAFER_QTY]
            if stot_wafer_qty == None :
                stot_wafer_qty = ""
                
            swafer_sort_flow = row[sWAFER_SORT_PROCESS]
            if swafer_sort_flow == None :
                swafer_sort_flow = ""
                
            swafer_sort_type = row[sWAFER_SORT_TYPE]
            if swafer_sort_type == None :
                swafer_sort_type = ""
                
            stest_house = row[sTEST_HOUSE]
            if stest_house == None :
                stest_house = ""
                
            stester_id = row[sTESTER_ID]
            if stester_id == None :
                stester_id = ""
            
            '''    
            sprobe_type = row[sPROBECARD_TYPE]
            if sprobe_type == None : 
                sprobe_type = ""
            '''
            ####################
            start_time = row[sSTART_TIME]
            end_time = row[sEND_TIME] 
            
            start_time_date = datetime.datetime.strptime(start_time, "%Y%m%d%H%M%S")
            end_time_date = datetime.datetime.strptime(end_time, "%Y%m%d%H%M%S")
            start_time_f = start_time_date.strftime('%Y-%m-%d %H:%M:%S')
            end_time_f = end_time_date.strftime('%Y-%m-%d %H:%M:%S')
            diff = end_time_date - start_time_date
            stest_time = round(diff.seconds/60,2)
            
            #####################
            x_size , y_size, sPDMS_notch, smes_family_name, sflow_code , sprobe_type , site_to_site_h_cri = get_pdms_wafer_size(sDev, snormal_lot , soper , sprog_name) 
                          
            ######################
            sbump_map_id = row[sBUMP_MAP_ID]
            
            msg = '\n' + str(i) +  ' ] ' + slot + ' / ' + swaferid + '\n' + 'wafer report generation start' + '\n'
            print(msg)        
            writeLog(msg)
            
            if i == 1 :
                
                cur_line = "[MapVersion, 1.3]" + '\n' + '[LotBegin]' + '\n'
                data = data + cur_line
                cur_line = pre_space + '[LotHeaderBegin]' + '\n'
                data = data + cur_line
                cur_line = pre_space + pre_space + 'Device              : ' + sDev + '\n'
                data = data + cur_line
                cur_line = pre_space + pre_space + 'Lot ID              : ' + slot + '\n'
                data = data + cur_line
                cur_line = pre_space + pre_space + 'Flow Code           : ' + sflow_code + '\n'   # <== ?
                data = data + cur_line
                cur_line = pre_space + pre_space + 'Test Stage          : ' + sUserproc + '\n'
                data = data + cur_line
                
                sort_type = get_sort_type(slot, swaferid)
                cur_line = pre_space + pre_space + 'Sort Type           : ' + sort_type + '\n'  # <== ? 2022/07/06 진공섭 fs 로 fix 
                data = data + cur_line
                
                #--------------------
                if sTemper == "25" :
                    sTemper = "RT"
                elif sTemper < "25" :
                    sTemper = "CT"
                elif sTemper > "25" :    
                    sTemper = "HT"
                #-------------------      
                cur_line = pre_space + pre_space + 'Temperature         : ' + sTemper + '\n'  
                data = data + cur_line
                cur_line = pre_space + pre_space + 'Wafer Qty           : ' + stot_wafer_qty + '\n'     # <== ?
                data = data + cur_line
                
                ##### TEST , 삭제요망
                #smes_family_name = "SPICAPLUS_WS"
                ######################### TEST
                
                if smes_family_name.strip() == "" :
                    msg = 'family name Error !! ' + '\n' + slot + " / " + swaferid 
                    mail_text = mail_text + '\n' + msg + '\n'
                    print(msg)
                    writeLog(msg)
                    
                    continue
                
                if sPDMS_notch.strip() != "" :
                    
                    if sPDMS_notch == "BOTTOM" :
                        sPDMS_notch = "DOWN"
                    if sNotch == "BOTTOM" :
                        sNotch = "DOWN"   
                    
                    #TEST
                    #일단 패스하고 나중에는 BLOCK 해야함.
                    if sPDMS_notch.strip() != sNotch :
                        msg = 'report gen Error !! ' + '\n' + slot + " / " + swaferid + '\n' + 'notch 방향이 pdms 와 맞지 않습니다.' + '\n'
                        msg = msg + 'stdf notch : ' + sNotch + ' / ' + 'pdms notch : ' + sPDMS_notch
                        print(msg)        
                        writeLog(msg)
                        mail_success_flag = False
                        mail_text = mail_text + msg + '\n'  
                        continue              
                        
                #######################
                
                stot_yield_limit = get_yield_limit(soper, smes_family_name)
                #if stot_yield_limit == False :
                if stot_yield_limit == "" :
                    msg = str(i) + '\n' + 'report gen Error !! ' + '\n' + slot + " / " + swaferid + '\n' + 'mes yield limit not found' 
                    mail_text = mail_text + '\n' + msg + '\n'
                    print(msg)
                    writeLog(msg)                    
                    #continue                
                stot_yield_limit = "{:.2f}".format(float(stot_yield_limit))
                ##############################
                dic_hold_criteria , shold_criteria = get_hold_criteria(soper, smes_family_name)
                #if stot_yield_limit == False :
                if shold_criteria == "" :
                    msg = str(i) + '\n' + 'report gen Error !! ' + '\n' + slot + " / " + swaferid + '\n' + 'mes test sbl management data not found' 
                    mail_text = mail_text + '\n' + msg + '\n'
                    print(msg)
                    writeLog(msg)
                    
                    #continue
                ###################
                cur_line = pre_space + pre_space + 'Lot Hold Criteria   : Lot Yield < ' + str(stot_yield_limit) + "%" + '\n'  
                data = data + cur_line
                cur_line = pre_space + pre_space + 'Test House          : ' + stest_house + '\n'     # <== ? Mir.facil_id"
                data = data + cur_line    
                #[LotHeaderEnd]
                cur_line = pre_space + '[LotHeaderEnd]' + '\n' + '\n'   
                data = data + cur_line  
                # wafer sum 생성용
                sLot_end_time , sLot_start_time , sTot_test_time = get_tot_test_time(s, soper)                   
            #######################################
            #[WaferBegin]
            cur_line = pre_space + '[WaferBegin]' + '\n'   
            data = data + cur_line 
            cur_line = pre_space + pre_space + '[WaferHeaderBegin]' + '\n'   
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'Wafer ID          : ' + swaferid + '\n'   
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'Operator#         : ' + str(suser) + '\n'   
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'Tester#           : ' +  stester_id + '\n'   # <== ? "Mir.node_nam"
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'Probe Card#       : ' + sprobe_card + '\n'  
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'Gross Die         : ' + str(stot_die) + '\n'  
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'SortwareVer.      : ' + software_ver + '\n'  
            data = data + cur_line 
            cur_line = pre_space + pre_space + pre_space + 'Program Name      : ' + sprog_name + '\n'  
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'Probe Card Type   : ' + sprobe_type + '\n'  # <== ? "Sdr.card_typ"
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'Total Test Time   : ' +  str(stest_time) + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'End Time          : ' +  str(end_time_f) + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'Start Time        : ' +  str(start_time_f) + '\n' 
            data = data + cur_line
            #####################
            #[WaferHeaderEnd]
            cur_line = pre_space + pre_space + '[WaferHeaderEnd]' + '\n' + '\n'
            data = data + cur_line            
            ##########################
            #[YieldSummaryBegin]
            cur_line = pre_space + pre_space + '[YieldSummaryBegin]' + '\n' 
            data = data + cur_line
            cur_line = get_site_bin_sum(slot, swaferid, stot_yield_limit, soper , site_to_site_h_cri) 
            if cur_line == False :
                continue
            
            data = data + cur_line
            cur_line = pre_space + pre_space + '[YieldSummaryEnd]' + '\n' + '\n'
            data = data + cur_line
            #########################
            # [WaferMapBegin]
            cur_line = pre_space + pre_space + '[WaferMapBegin]' + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'Horizontal  : X' + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'Vertical    : Y' + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'XIncreament : Right' + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'YIncreament : Down' + '\n' 
            data = data + cur_line
            cur_line = pre_space + pre_space + pre_space + 'Notch       : ' + sNotch + '\n' + '\n'
            data = data + cur_line
            ############################
            
            cur_line = get_map_file(slot, swaferid, sbump_id , sNotch , x_size , y_size , sfamily_name , soper) 
            if cur_line == False :
                continue
            
            data = data + cur_line
            
            cur_line = pre_space + pre_space + '[WaferMapEnd]' + '\n' + '\n'
            data = data + cur_line
            #-----------------------------
            
            cur_line = pre_space + pre_space + '[BinSummaryBegin]' + '\n' 
            data = data + cur_line
            ########################
            cur_line = get_binsum_yield(slot, swaferid, stot_yield_limit,sDev, dic_hold_criteria , shold_criteria, soper, sprog_name) 
            if cur_line == False :
                continue
            
            print(data)
            
            data = data + cur_line
            cur_line = pre_space + pre_space + "[BinSummaryEnd]" + '\n'
            data = data + cur_line
            cur_line = pre_space + "[WaferEnd]" + '\n' + '\n'
            data = data + cur_line
                        
            msg = str(i) + '\n' + slot + " / " + swaferid + '\n' + 'MVL wafermap report generation ' + '\n'        
            print(msg)        
            writeLog(msg)
            mail_text = mail_text + '\n' + msg + '\n'                
            # map file end
        ##################################################
        if data.strip() == '' :
            pass
        else :
            
            cur_line = "[LotEnd]" 
            data = data + cur_line
            msg = str(i) + '\n' + slot + '\n' + 'MVL wafermap report generation complete ' + '\n'  + source_dir + '/' + slot + '_' + sDev + '_' + sUserproc + '_map.txt' + '\n'     
            print(msg)        
            writeLog(msg)
            mail_text = mail_text + '\n' + msg + '\n'                
                        
            # bump map file
            f = open(source_dir + '/' + slot + '_' + sDev + '_' + sUserproc + '_map.txt', 'w')
            f.write(data)
            f.close()       
            ######################  
        ###########################################
        # 2. lot  별 summary file 생성
        # wafer map file 생성되면 lot 에 대한 map summary file 생성해야함.
        print(slot + " ] == 2. mvl wafer summary generation start ==")
        sum_data = ""
        cur_line = "[SummaryVersion, 1.3]" + '\n' + '[HeaderBegin]' + '\n'
        sum_data = sum_data + cur_line
        
        cur_line = pre_space + pre_space + 'Device              : ' + sDev + '\n'
        sum_data = sum_data + cur_line
        cur_line = pre_space + pre_space + 'Lot ID              : ' + slot + '\n'
        sum_data = sum_data + cur_line
        cur_line = pre_space + pre_space + 'Flow Code           : ' + sflow_code + '\n'   # <== ?
        sum_data = sum_data + cur_line
        cur_line = pre_space + pre_space + 'Test Stage          : ' + sUserproc + '\n'
        sum_data = sum_data + cur_line        
        cur_line = pre_space + pre_space + 'Sort Type           : ' + sort_type + '\n'  # <== ? 2022/07/06 진공섭 fs 로 fix 
        sum_data = sum_data + cur_line
        #--------------------
        if sTemper == "25" :
            sTemper = "RT"
        elif sTemper < "25" :
            sTemper = "CT"
        elif sTemper > "25" :    
            sTemper = "HT"
        #-------------------   
        cur_line = pre_space + pre_space + 'Temperature         : ' + sTemper + '\n'  
        sum_data = sum_data + cur_line
        cur_line = pre_space + pre_space + 'Wafer Qty           : ' + stot_wafer_qty + '\n'     # <== ?
        sum_data = sum_data + cur_line
        
        cur_line = pre_space + pre_space + 'Lot Hold Criteria   : Lot Yield < ' + str(stot_yield_limit) + "%" + '\n'  
        sum_data = sum_data + cur_line
        
        cur_line = pre_space + pre_space + 'Total Test Time     : ' + str(sTot_test_time) + '\n'      
        sum_data = sum_data + cur_line 
        cur_line = pre_space + pre_space + 'Lot End Time        : ' + str(sLot_end_time) + '\n'     
        sum_data = sum_data + cur_line   
        cur_line = pre_space + pre_space + 'Lot Start Time      : ' + str(sLot_start_time) + '\n'     
        sum_data = sum_data + cur_line    
        cur_line = pre_space + pre_space + 'Program Name        : ' + sprog_name + '\n'  
        sum_data = sum_data + cur_line
            
        cur_line = pre_space + pre_space + 'Test House          : ' + stest_house + '\n'     
        sum_data = sum_data + cur_line   
        cur_line = pre_space + pre_space + 'Notch               : ' + sNotch + '\n' 
        sum_data = sum_data + cur_line
            
        #[LotHeaderEnd]
        cur_line = '[HeaderEnd]' + '\n' + '\n'   
        sum_data = sum_data + cur_line
        #------------------------------------
        #[SummaryBegin]                
        cur_line = '[SummaryBegin]' + '\n' + '\n'   
        sum_data = sum_data + cur_line
        ########################
        cur_line = get_summary_file_sum(slot, soper, dic_hold_criteria, shold_criteria, sDev , sprog_name) 
        if cur_line == False :
            continue
        sum_data = sum_data + cur_line
        ##################################################
        if sum_data.strip() == '' :
            pass
        else :
            
            msg = str(i) + '\n' + slot + '\n' + '2. MVL wafermap summary report generation complete ' + '\n'  + source_dir + '/' + slot + '_' + sDev + '_' + sUserproc + '_sum.txt' + '\n'     
            print(msg)        
            writeLog(msg)
            mail_text = mail_text + '\n' + msg + '\n'                
                        
            # bump map file
            f = open(source_dir + '/' + slot + '_' + sDev + '_' + sUserproc + '_sum.txt', 'w')
            f.write(sum_data)
            f.close()       
            ######################          
        print(slot + " ] == 2. mvl wafer summary generation end ==")
                  
except:
    msg = str(i) + '\n' + 'report gen Error !! ' + '\n' + slot + " / " + swaferid 
    mail_text = mail_text + '\n' + msg + '\n'
    print(msg)
    writeLog(msg)

#################################
# wafer map 통합 ftp 로 map report 전송
ftp_ip = ' '
ftp_id = ' '
ftp_pw = ' '
ftp_path = ' '
#######################
try:
    ############################################
    ftp = ftplib.FTP(ftp_ip)
    ftp.login(ftp_id,ftp_pw)    
    ftp.cwd(ftp_path)
    #############################    
    os.chdir(source_dir)

    msg = ftp_ip + ' ] s2. ftp for map report connection success !! '
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'
    
except:
    #writeLog('3. ftp / ftp연결실패 : 예외사항 ' + ftp_ip)
    msg = ftp_ip + ' ] s2-1. ftp for map report connection fail :  exception '
    mail_text = mail_text + msg + '\n'
    mail_flag = False
    print(msg + ftp_ip)
    writeLog(msg)
###############################
time.sleep(2)
i = 0

now = datetime.datetime.now()
ftp_date = now.strftime('%Y%m')
os.chdir(source_dir)    
for filename in os.listdir(source_dir):
    
    try:
    
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(source_dir)
        full_filename = os.path.join(path, filename)
        
        # 파일만 검색
        if os.path.isfile(full_filename):
            pass
        else:
            continue
        #------------------------------------------        
        if (filename.find('_sum.txt') > -1) or  (filename.find('_map.txt') > -1) :           
            i = i + 1
            msg = str(i) + ' ] s3. map report file backup start : ' + '\n' + " " + full_filename
            ###############################
            # 2. DATE FOLDER            
            try:
                ftp.cwd(ftp_date)
            except:
                ftp.mkd(ftp_date)
                ftp.cwd(ftp_date)      
            #################################
            # backup server upload
            ftp.encoding = 'utf-8'
            
            my_file = open(filename, 'rb')
            #ftp.storbinary('STOR ' + filename , my_file, blocksize=1024)
            #ftp.storbinary('STOR ' + filename , my_file)
            ftpResponse = ftp.storlines('STOR ' + filename , my_file)

            ftp.sendcmd("TYPE i")    # Switch to Binary mode
            
            #if ftp.size(filename) == os.path.getsize(full_filename) :
            if ftpResponse.find('226') > -1 :
                my_file.close()
                
                msg = str(i) + ' ] s3-1. mvl wafer map report trans Success !! ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                
                ####################
                # backup 후 로컬파일삭제
                if os.path.isfile(full_filename):
                    os.remove(full_filename)  # result file delete                
                ########################  
                
            else:
                msg = str(i) + ' ] s3-2. STDF BACKUP error of file size !! : ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                mail_flag = False
                my_file.close()
            #---------------------------------
            
            time.sleep(1)           
            ftp.cwd('../')        
            print(ftp.pwd())
            #----------------
            
            msg = str(i) + ' ] s3. mvl map report backup success !!  ' + '\n' + " " + filename

            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
    except:
        #writeLog('3. ftp / ftp연결실패 : 예외사항 ' + ftp_ip)
        msg = str(i) + ' ] ' + ftp_ip + ' ] s3-3. mvl map report backup exception error !!'
        mail_text = mail_text + msg + '\n'
        mail_flag = False
        print(msg + ftp_ip)
        writeLog(msg)    
# map report 전송완료        
#############################            
        
msg = 'wafer report generation end !!'
#writeLog('wafer report generation end !!')
print(msg)
writeLog(msg)
mail_text = mail_text + '\n' + msg + '\n'

conn_tpas.commit()
conn_tpas.close()

send_mail(mail_text)

#############################33
sys.exit(0)

