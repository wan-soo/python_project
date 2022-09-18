import ftplib
import os
import shutil
from pathlib import Path
import time
import gzip
import datetime
from datetime import date, timedelta
import cx_Oracle
#from stdf.stdf_reader import Reader

from time import localtime, strftime
import sys
import glob
##########################
# 메일관련
import email
import smtplib
from email.mime.text import MIMEText

#############
import socket

from stdf.stdf_reader import Reader
from stdf.stdf_writer import Writer
import logging
#from pathlib import Path
#import time
import struct

__author__ = 'Jerry Zhou'

def get_all_records(stdf):
    stdf.read_rec_list = True
    stdf_dic = {}
    i = 0
    for rec_name, position in stdf:    
        if rec_name in ('MIR' , 'MRR','WIR','SDR','WCR','SBR','HBR','PRR','WRR') :
            stdf_dic[str(i) + ' - ' + rec_name] = position
            i += 1
    stdf.read_rec_list = False
    return stdf_dic
#################################
# move 할 폴더생성
# D:\QCT_Datalog
###################################

today = datetime.datetime.now().strftime('%Y%m%d')
tmp_day = date.today() - timedelta(1)
yesterday = tmp_day.strftime('%Y%m%d')
#######################
# 폴더 지정 및 변경
source_dir = "C:/temp/INPHI_MAP/"

org_stdf_dir = "/WAFER/STDF/"

#2021/07/08 inphi 가 mvl 로 변경됨
org_stdf_dir2 = "/STDF/"

target_stdf_ftp = '/STDF/'
tsmc_ftp = '/ws/tsmc_map/'
local_dir = source_dir
###################################
move_dest = source_dir + "CONVERSION_move/"
result_dest = source_dir + "TSMC_MAP/"
complete_dest = source_dir + "COMPLETE_MAP/"

# 압축하고 압축폴더에서 바로 ftp 로 전송
# from_ftp = result_dest
log_dest = source_dir + "mapfile_log/"
###################
new_ftp_ip = 
new_ftp_id = 
new_ftp_pw = 
#######################
new_ftp_ip2 =
new_ftp_id2 =
new_ftp_pw2 =

target_stdf_ftp2 = '/To_Inphi/ws/'

#######################

chk_hour = 0.15
#chk_hour = 0
mail_flag = True
mail_send_flag = False
mail_text = "map conversoin file list " + '\n' + '\n'

print("conersion start ... ")


##################
# ip 구하기
def ipcheck():
    # return socket.gethostbyname(socket.getfqdn())
    return socket.gethostname()


###################################
## log 파일 쓰기 함수
def writeLog(strLog):
    now = datetime.datetime.now()
    logDate = now.strftime('%Y%m%d')
    nowtime = now.strftime('%Y%m%d %H:%M:%S')
    # f = open('./log_' + logDate + '.txt' , 'a')
    f = open(log_dest + "log_" + logDate + ".txt", 'a')

    f.write(nowtime + ' :: ' + strLog + '\n')

    f.close()


################################
def readLog(full_filename):
    # now = datetime.datetime.now()
    # logDate = now.strftime('%Y%m')
    # nowtime = now.strftime('%Y%m%d %H:%M:%S')
    # f = open('./log_' + logDate + '.txt' , 'a')
    # f = open(log_dest + "log_" + logDate + ".txt", 'a')
    with open(full_filename, 'r', encoding='UTF8') as f:
        while True:
            line = f.readline()
            print(line)
    f.close


# email 전송
def send_mail(m_text):
    # "Mrelay.kr.jcetglobal.com"
    print("mail sending")
    smtp = smtplib.SMTP("Mrelay.jkr.jcetglobal.com", 25)
    # smtp = smtplib.SMTP('220.126.190.13', 25)
    # smtp.ehlo()  # say Hello
    # smtp.starttls()  # TLS 사용시 필요
    # smtp.login('sckcim@jcetglobal.com', 'Korea@12')

    # smtp.login('wansoo.kim@jcetglobal.com', 'kasa1010%%')
    m_text = ipcheck() + '\n' + m_text
    # msg = MIMEText(m_text,_charset='ks_c_5601-1987')
    msg = MIMEText(m_text)
    if mail_flag == True:
        msg['Subject'] = 'Inphi map conversion success !! ' + ipcheck()
    else:
        msg['Subject'] = 'Inphi map conversion Error !! ' + ipcheck() + ' - ' + ' check equipment '

    # msg['To'] = 'SCK-IT-CIM-TEST@jcetglobal.com'
    msg['To'] = 'wansoo.kim@jcetglobal.com'
    # smtp.sendmail('sckcim@jcetglobal.com', 'SCK-IT-CIM-TEST@jcetglobal.com', msg.as_string())
    smtp.sendmail('sckcim@jcetglobal.com', 'wansoo.kim@jcetglobal.com', msg.as_string())
    print("mail success !! ")
    # time.sleep(3)
    smtp.quit()

###################################
def get_leadid(sLot):
    conn_mes = cx_Oracle.connect('mesdb')
    cur_mes = conn_mes.cursor()

    lead_id = "XXXX"
    pkg_id = "XXXX"
    swafer_qty = "0"

    sql = "SELECT LEAD_ID,PKG_ID, CUR_WAFER_QTY FROM WIP_LOTINF "
    sql  = sql + " WHERE LOT_ID = '" + sLot.strip().upper() + "' "


    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    for row in rows:  # 202029
        lead_id = row[0]
        pkg_id = row[1]
        swafer_qty = row[2]

    #print(sLot + " mes leadid : " + lead_id)
    #writeLog(sLot + " mes leadid : " + lead_id)

    conn_mes.close()

    return lead_id,pkg_id,swafer_qty  ;
    #return sFile1
###################################
def get_norlot(sLot):
    conn_mes = cx_Oracle.connect('mesdb')
    cur_mes = conn_mes.cursor()

    stmp_lot = ""

    s = sLot.split("-")
    if len(s) == 1 :
        s1_lot = s[0].strip().upper()
        s2_lot = ""
        s3_lot = ""
    elif len(s) == 2 :
        s1_lot = s[0].strip().upper()
        s2_lot = s[1].strip().upper()
        s3_lot = ""
        ####################
        #PP7K55.00-1S (sublot)
        #P65B58.07-1 (dup)
        if len(s2_lot) == 1 :            
            s3_lot = s2_lot
            s2_lot = ""

    elif len(s) == 3 :
        s1_lot = s[0].strip().upper()
        s2_lot = s[1].strip().upper()
        s3_lot = s[2].strip().upper()
    ##########################
    # 왼쪽 13 칸 공백
    #stmp_lot = "{0:<13}".format(s1_lot) + "{0:<3}".format(s2_lot) + "{0:<1}".format(s3_lot)
    stmp_lot = "{0:<20}".format(s1_lot) + "{0:<3}".format(s2_lot) + "{0:<2}".format(s3_lot)
    stmp_lot = stmp_lot.strip()

    sql = "SELECT LOT_ID FROM WIP_LOTINF "
    sql = sql + " WHERE LOT_ID = '" + stmp_lot + "' "

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()

    if rows == None:
        # 13자리
        stmp_lot = "{0:<13}".format(s1_lot) + "{0:<3}".format(s2_lot) + "{0:<1}".format(s3_lot)
        stmp_lot = stmp_lot.strip()

        sql = "SELECT LOT_ID FROM WIP_LOTINF "
        sql = sql + " WHERE LOT_ID = '" + stmp_lot + "' "

        cur_mes.execute(sql)
        rows = cur_mes.fetchall()

        if rows == None:
            stmp_lot = sLot
        

        #stmp_lot = sLot
    
    conn_mes.close()

    return stmp_lot ;
#####################################
# GET WAFER X SIZE , Y SIZE FROM PDMS
def get_pdms_wafer_size(sdev) :

    #-------------------
    x_size = 0
    y_size = 0
    itmsdev = ""
    sPDMS_notch = ""
    sort_type = ""
    #-------------------
    conn_tpas1 = cx_Oracle.connect('etcarddb')    
    cur_tpas1 = conn_tpas1.cursor()

    # 1. get itms device using cust device
    sql = "SELECT DEVICENAME FROM INT_LINKAGE_DEVICES "
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
                sPDMS_notch = tpas_row[2]
        #---------------------------------
        # SORT TYPE
        # . If IS_SAMPLE_SORT is ‘Y’ means sample sort or else full sort.
        # (FF : full sort / SF: Sample sort / PF :Partical sort ) 
        sql = "SELECT IS_SAMPLE_SORT FROM VW_MES_INSERTION@WSPRD_NEW "
        sql = sql + "WHERE SITE_CODE = 'SCK' "
        sql = sql + "AND ITMS_DEVICE_NAME = '" + itmsdev + "' "
        #sql = sql + "AND STATUS = 'ACT' "

        cur_tpas1.execute(sql)
        tpas_rows = cur_tpas1.fetchall()
        if cur_tpas1.rowcount > 0 :            
            for tpas_row in tpas_rows:  # 202029
                sort_type = tpas_row[0]
                if sort_type == 'Y' :
                    sort_type = 'SF'
                else :
                    sort_type = 'FF'
                
    #######################
    if ((sdev == ' ') or (sdev == ' ')) and (y_size == 0) :
        x_size = 60
        y_size = 63
    #######################
    conn_tpas1.close()

    return x_size , y_size, sPDMS_notch , sort_type ; 

###################################
def get_bump_map(slotid, waferid ):

    conn_mes = cx_Oracle.connect('mesdb')
    cur_mes = conn_mes.cursor()
    cust_run_id = ""
    bump_in_qty = 0
    bump_rej_qty = 0
    sMapid = ""

    ###########################
    sql = "SELECT CUST_RUN_ID FROM WIP_RUNINF "
    sql = sql + "WHERE LOT_ID = GET_CPK_RUN_ID( '" + slotid.strip().upper() + "') "
    
    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    if (rows == None) or (len(rows) == 0) :
        pass
    else :
        cust_run_id = rows[0][0]
    #########################
    s = slotid.split("-")

    stemp = s[0].strip().upper()

    sql = "SELECT ID FROM BUMPEAP.WAFERMAP_CUST_FILE@BUMPEAP_BUMPEAP "
    sql = sql + "WHERE FILENAME LIKE '" + waferid + "%" + "' " 
    sql = sql + "AND CUST_LOT_ID LIKE '" + stemp + "%" + "' "
    sql = sql + "AND LATEST = 'Y' " 

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    if ((rows == None) or (len(rows) == 0)) and (cust_run_id != "")  :
        sql = "SELECT ID FROM BUMPEAP.WAFERMAP_CUST_FILE@BUMPEAP_BUMPEAP "
        sql = sql + "WHERE FILENAME LIKE '" + waferid + "%" + "' " 
        sql = sql + "AND CUST_LOT_ID LIKE '" + cust_run_id + "%" + "' "
        sql = sql + "AND LATEST = 'Y' " 

        cur_mes.execute(sql)
        rows = cur_mes.fetchall()
    #################################
    if (rows == None) or (len(rows) == 0) :        
        pass
    else :
        for row in rows:  # 202029
            sMapid = row[0]
            ################################
            # reject qty
            sql = "SELECT COUNT(*) FROM BUMPEAP.WAFERMAP_UNIT_DETAIL@BUMPEAP_BUMPEAP "
            sql = sql + "WHERE ID = " + str(sMapid) 
            sql = sql + "AND WAFER_ID = '" + waferid + "' "
            sql = sql + "AND CUST_BUMP <> '000' "
            sql = sql + "AND CUST_BUMP <> '___' "

            cur_mes.execute(sql)
            rows = cur_mes.fetchall()
            if rows == None:
                pass
            else:
                for row in rows:  # 202029
                    bump_rej_qty = row[0] 
            ##########################################
            # tot qty
            sql = "SELECT COUNT(*) FROM BUMPEAP.WAFERMAP_UNIT_DETAIL@BUMPEAP_BUMPEAP "
            sql = sql + "WHERE ID = " + str(sMapid)
            sql = sql + "AND WAFER_ID = '" + waferid + "' "            
            sql = sql + "AND CUST_BUMP <> '___' "

            cur_mes.execute(sql)
            rows = cur_mes.fetchall()
            if rows == None:
                pass
            else:
                for row in rows:  # 202029
                    bump_in_qty = row[0] 

    conn_mes.close()

    return bump_in_qty , bump_rej_qty , sMapid ;               

#############################################
# send_mail('mail test' )
p = Path(move_dest)  # 로컬 다운받은 폴더
p.mkdir(exist_ok=True)
# tsmc map file 생성 폴더
p = Path(result_dest)
p.mkdir(exist_ok=True)
# 로그위치
p = Path(log_dest)
p.mkdir(exist_ok=True)
# tsmc map file 생성후 완료된 맵파일폴더
p = Path(complete_dest)
p.mkdir(exist_ok=True)

# p = Path(log_dest)
# p.mkdir(exist_ok=True)
##############################
print("Conversion main ... ")
# writeLog("FileWatcher main ... ")
# 압축완료되면 전송할 폴더
# move 한 다음 바로 ftp 로 전송하거나, 압축한 다음 바로 전송

# p = Path(from_ftp)
# p.mkdir(exist_ok=True)

# for (path, dir, files) in os.walk("c:/temp/"):
########################
# 1. ftp 의 압축된 gdf.map file 을 다운받는다.
# pc test
###############

org_stdf_ftp_list = []
#######################
#s1
########################
# hp 장비의 map file 과 uflex 장비의 map file 을 구분해서 
# ftp 의 지정된 폴더에 올려야함.
UF_stdf = ['']
HP_stdf = ['']

tot_file_cnt = 0 


# 디버깅시 파일다운 제외
try:
    ############################################
    # cim1 에서 copy 해서 inphi 로 가져온다. inc 파일은제외
     
    i = 0
    for (path, dirs, files) in os.walk(org_stdf_dir):
        #########################
        # 2021/12/24 파일이 없으면 폴더삭제
        if (len(path) > len(org_stdf_dir)) and (len(dirs) == 0) and (len(files) == 0):
            #####################################
            remove_file = os.path.join(path, '')   
            os.rmdir(remove_file)
        #######################################    
        for filename in files:

            ##############################
            if tot_file_cnt > 25 :
                break
            ############################### 
        #             
            full_filename = os.path.join(path, filename)            
            stdf_fnam = filename.split("/")[-1]
            ####################################
            # 2021/09/09 hp map file 저장
            if stdf_fnam.split(".")[-1] == "stdf" :
                HP_stdf.append(stdf_fnam + ".gz")
            elif  stdf_fnam.split(".")[-1] == "gz" :
                HP_stdf.append(stdf_fnam )   
            ####################################
            if (stdf_fnam.find('.stdf') > -1) and (stdf_fnam.upper().find('_CP1_') > -1) \
                and not (stdf_fnam.find('_sum.stdf') > -1) \
                and not (stdf_fnam.find('.stdf_inc') > -1)  :
                #####################
                delta_ago = time.time() - os.path.getmtime(full_filename)
                time_ago = (delta_ago / 60) / 60  # hour
                if time_ago > chk_hour:
                    pass
                else:
                    continue
                ################
                if os.path.isfile(full_filename):
                    pass
                else:
                    continue
                ######################
                msg = "file copy start from network drive to local pc : " + '\n' + " " + stdf_fnam
                writeLog(msg)
                print(msg)
                shutil.copy(full_filename, local_dir)
                
                i = i+ 1
                msg = str(i) + " ] s1 .success : " + '\n' + " [" + str(i) + "] - " + stdf_fnam
                writeLog(msg)
                print(msg)
                time.sleep(1)

                ###############################
                tot_file_cnt = tot_file_cnt + 1
                if tot_file_cnt > 25 :
                    break
                ###############################
    #########################
     
    #for (path, dirs, files) in os.walk(org_stdf_dir2):
    for filename in os.listdir(org_stdf_dir2):

        ##############################
        if tot_file_cnt > 25 :
                break
        ###############################  
        
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(org_stdf_dir2)
        #slocal = os.path.join(path, filename)
        stdf_fnam = filename.split("/")[-1]
        full_filename = os.path.join(path, filename)
        stdf_fnam = filename.split("/")[-1]

        if os.path.isfile(full_filename):
            pass
        else:
            continue
        ########################    
        # 2021/09/09 uflex map file 저장
         
        
        if stdf_fnam.split(".")[-1] == "stdf" :
            UF_stdf.append(stdf_fnam + ".gz")
        elif stdf_fnam.split(".")[-1] == "gz" :
            UF_stdf.append(stdf_fnam)    
        ################################

        if (stdf_fnam.find('.stdf') > -1) and (stdf_fnam.upper().find('_CP1_') > -1) \
            and not (stdf_fnam.find('_sum.stdf') > -1) \
            and not (stdf_fnam.find('.stdf_inc') > -1)  :
            #####################
            delta_ago = time.time() - os.path.getmtime(full_filename)
            time_ago = (delta_ago / 60) / 60  # hour
            if time_ago > chk_hour:
                pass
            else:
                continue
            ################
            if os.path.isfile(full_filename):
                pass
            else:
                continue
            ######################
            msg = "file copy start from network drive to local pc : " + '\n' + " " + stdf_fnam
            writeLog(msg)
            print(msg)
            shutil.copy(full_filename, local_dir)
            i = i+ 1
            msg = str(i) + " ] s1 .success : " + '\n' + " [" + str(i) + "] - " + stdf_fnam
            writeLog(msg)
            print(msg)
            time.sleep(1)
            ###############################
            tot_file_cnt = tot_file_cnt + 1
            if tot_file_cnt > 25 :
                break
            ###############################  
                
    #########################

    # 로컬의  source_dir = "C:/temp/INPHI_MAP/" 파일들중 압축파일은 압축해제
    #i = 0
    for filename in os.listdir(source_dir):
        ################
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(source_dir)
        slocal = os.path.join(path, filename)
        stdf_fnam = filename.split("/")[-1]

        if os.path.isfile(slocal):
            pass
        else:
            continue
        # 1. ftp 의 압축된 gdf.map file 을 다운받는다.        
        
        ###############################
        # 압축풀기
        if (stdf_fnam.find('.stdf.gz') > -1):
            slocal_tmp = slocal.replace(".gz", "")
            with gzip.open(slocal, 'rb') as in_file:
                with open(slocal_tmp, 'wb') as out_file:
                    i = i+ 1
                    shutil.copyfileobj(in_file, out_file)                    
                    smsg = str(i) + ' ] s1-1. decompression success !! : ' + '\n' + " " + stdf_fnam
                    print(smsg)
                    writeLog(smsg)
                    mail_text = mail_text + smsg + '\n'
        ##############################
        
except:
    msg = str(i) + ' ] s1-1. filecopy fail exception from network drive !! : ' + '\n' + " " + filename
    mail_text = mail_text + msg + '\n'
    mail_flag = False
    print(msg)

time.sleep(2)

####################################
# 2. 
# 압축해제된 파일들만 move 폴더로 이동시킴
# 압축파일삭제
i = 0
for filename in os.listdir(source_dir):

    ext = os.path.splitext(filename)[-1]
    path = os.path.abspath(source_dir)
    full_filename = os.path.join(path, filename)

    # 파일만 검색
    if os.path.isfile(full_filename):       
        pass
    else:        
        continue
    #-----------------------
    if (filename.find('.stdf.gz') > -1) :
        os.remove(full_filename)
        time.sleep(1)
        continue
    elif (filename.find('.stdf_inc') > -1) :
        continue
    elif (filename.find('.stdf') > -1) :
        pass        
    else:
        continue
    ###########################
    # 1. stdf, txt, xml 파일 확장자로 지정
    # writeLog("이동시작" + full_filename)
    # ext_dest  가 여러가지일때 하나씩 비교
    ext_flag = False
    if (filename.find('.stdf') > -1):
        ext_flag = True
        ####################
    #if (ext_flag == True) and (time_ago > chk_hour):
    
    if (ext_flag == True):
        mail_text = mail_text + 's2. file select : ' + full_filename + '\n'
        # 1. stdf 파일을 move 하여 move 가능하면 파일완료된 것으로 간주
        # move 는 에러나도 move 됨, rename 해서 에러나면 파일완료안된것으로 간주
        try:
            # 파일이 있으면 걍 넘어감, 덮어쓰기함
            i = i+ 1
            print("stdf file check")
            writeLog("**** stdf file move : " + full_filename)
            
            os.rename(full_filename, full_filename)
            try:
                # 2. source 폴더의 파일 탐색하여 대상 파일 move dest 로 옮김
                ###########################
                mail_send_flag = True
                msg = str(i) + ' ] s2. stdf file move start : ' + '\n' + " " + move_dest + filename
                writeLog(msg)
                print(msg)
                shutil.move(full_filename, move_dest + filename)
                #####################
                msg = str(i) + ' ] s2. file move complete !! : ' + '\n' + " " + move_dest + filename
                print(msg)
                writeLog(msg)
                mail_text = mail_text + msg + '\n'
                ################################
            except:
                msg = str(i) + ' ] s2. file move error !! : ' + '\n' + " " + move_dest + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                mail_flag = False

        except:
            msg = str(i) + ' ] s2. file move exception error !! : ' + '\n' + " " + move_dest + filename
            print(msg)
            mail_text = mail_text + msg + '\n'
            mail_flag = False
            continue
        # move complete 

#################################
# 디버깅시 파일다운 제외
###############################
# 3. file read start
# move 폴더의 stdf 파일을 읽으면서 parsing
time.sleep(3)
#x_y_dic = {}
x_y_dic_final = {}
x_y_dic_first = {}
sbin_desc_dic = {}
#Hbin_desc_dic = {}
#Hbin_pf_dic = {}
sbin_pf_dic = {}
sb_hb_dic = {}

i = 0

#ptr_flag = False
# s3
for filename in os.listdir(move_dest):
    # x,y 좌표초기화
    # 만약 동일 좌표일 경우 나중 data 로 덮어쓰기해야함.
    #x_y_dic.clear()
    x_y_dic_first.clear()
    x_y_dic_final.clear()
    sbin_desc_dic.clear()
    sb_hb_dic.clear()
    #Hbin_desc_dic.clear()
    #Hbin_pf_dic.clear()
    
    sbin_pf_dic.clear()
    #######################
    x_y_dic_first_good = 0
    x_y_dic_first_reject = 0
    ########################    
    x_y_dic_final_good = 0
    x_y_dic_final_reject = 0
    #######################
    sINP_Test_prog = ""
    sTest_prog = ""

    ext = os.path.splitext(filename)[-1]
    path = os.path.abspath(move_dest)
    full_filename = os.path.join(path, filename)
    #stdf 파일에 대해서만 conversion
    if os.path.isfile(full_filename):
        if ext == ".stdf":
            pass
        elif ext == ".gz":
            os.remove(full_filename)
            time.sleep(2)
            continue
        else:
            continue
    else:
        continue

    i = i + 1
    msg = str(i) + ' ] s3. stdf file read start !! : ' + '\n' + " " + move_dest + filename
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'

    try:
        temp = filename.upper()
        #temp = temp.split('_')
        #temp1 = temp[3].split('-')
        #waferno = temp1[1]
        #tsmc_file_name = temp[1] + '-' + '1' + '-' + waferno
        # 3. file read start
        #tsmc_file = open(result_dest + tsmc_file_name, 'w')
        line_temp = ''
        line_header = ''
        sData_count = 0
        header_flag = False
        bin_data_flag = ''
        #####################################
        sTart_time = ''
        x_y_bin_data_first = ''
        x_y_bin_data_final = ''
        ######################
        sWafertype = "SCK3-S"
        sApp = " "
        sConfig = " "
        sLevelname = " "
        sTiming = " "
        sVentor = " "
        sAttribe = " "
        sPkg_id = " "
        sReadflag = "N"
        sHandler = " "
        sRetest_code = " "
        sTransflag = "N"
        sSBL_flag = "N"
        sNotch_direction = ''
        sNotch = ''
        ###################################
        # loadboard id 12
        # 12 자리 공란으로
        sLoadbd = "            "
        # bin defnition file 20
        # BIN_FILE: TMJR29_SCK_1_1 = > default
        sBD_file = ""
        
        ####################################
        # sorter id 1자리
        sSorter = "1"
        # test site 8자리
        sTest_site = "SCK"
        sTest_site = "{0:<8}".format(sTest_site)
        # fd file name 20자리
        sFD_file = "                    "
        x_y_bin_data = ""
        #################################
        slotid = ""
        sWaferid = ""
        sSlotid = ""
        sFamily = ""
        sDev = ""
        sProd_name = ""
        sTester_id = ""
        sOper_id = ""
        sTest_prog_rev = ""
        sHPSMARTEST_rev = ""
        sUser_proc = ""
        sTemper = ""
        sRetestseq = ""
        sJob_rev = ""
        sEnd_time = ""
        sProber_card = ""
        sbin_num = ""
        sbin_desc = ""
        Hbin_num = ""
        Hbin_desc = "NoDesc"
        #Hbin_pf = ""
        sbin_pf = ""
        sX = ""
        sY = ""
        sSoft_bin = ""
        sHard_bin = ""
        sTest_time = ""
        sPart_flag = ""

        snor_lotid = ""
        spkg_type = ""
        sort_type = ""
        sfacil_id = ""
        sProber_card_type = ""

        ##################################
        # writeLog('    conversion complete !! ' + result_dest + tsmc_file_name)

        #####################################
        # stdf file reader

        stdf = Reader()
        stdf.load_stdf_file(stdf_file=full_filename)
        stdf_dic = get_all_records(stdf)
        if stdf_dic:
            for item in stdf_dic:
                positon = stdf_dic[item]
                stdf.STDF_IO.seek(positon)
                rec_name, header, body = stdf.read_record()
                
                #for r in rec_name:
                if rec_name == 'MIR':
                    slotid = body['LOT_ID'].decode('utf-8')
                    slotid = slotid.upper().strip()
                    #print('    lot_id find' + slotid)
                    
                    ##---------------------------
                    sSlotid = body['SBLOT_ID'].decode('utf-8')
                    sSlotid = sSlotid.upper().strip()
                    #print('    SBLOT_ID find' + sSlotid)
                    ##-------------------------------
                    #FAMLY_ID - POLARIS
                    if body['FAMLY_ID'] == '' :
                        sFamily = ' '
                    else:    
                        sFamily = body['FAMLY_ID'].decode('utf-8')  # POLARIS
                    #device PART_TYP
                    sDev = body['PART_TYP'].decode('utf-8')
                    #sProd_name = sDev
                    ############################
                    # eng'r 자재
                    if (sDev == "ZSPCIAPLUS-A0" or sDev == "1"):
                        break
                    ############################
                    # tester id
                    sTester_id = body['NODE_NAM'].decode('utf-8')
                    
                    #oper id
                    sOper_id = body['OPER_NAM'].decode('utf-8')
                    
                    #test program name - JOB_NAM
                    sTest_prog_rev = body['JOB_NAM'].decode('utf-8')
                    
                    #START T
                    sTart_time = body['START_T']
                    
                    ## HPSmarTest_revision: handler rev
                    sHPSMARTEST_rev = body['EXEC_VER'].decode('utf-8')
                    
                    ## loc desc , loc code
                    sUser_proc = body['TEST_COD'].decode('utf-8')
                    sLoc = "340"
                    # temperature
                    if body['TST_TEMP'] == '':
                        sTemper = ' '
                    else:    
                        sTemper = body['TST_TEMP'].decode('utf-8')
                    #retest code
                    sRetestseq = body['RTST_COD'].decode('utf-8')
                    #test
                    sRetestseq = '0'
                    
                    if body['JOB_REV'] == '':
                        sJob_rev = ' '
                    else:    
                        sJob_rev = body['JOB_REV'].decode('utf-8')
                    ###################
                    # WAFER_SORT_PROCESS TESTFLOW FOR WAFER SORT
                    if body['PKG_TYP'] == '' :
                        spkg_type = ' '
                    else :    
                        spkg_type = body['PKG_TYP'].decode('utf-8', errors="")
                    #Sort Type     : FS      
                    #if body['CMOD_COD'] == '' :
                    #    scmod_code = ' '
                    #else :    
                    #    scmod_code = body['CMOD_COD'].decode('utf-8', errors="")
                    #sfacil_id Test House   : ARDENTEC
                    if body['FACIL_ID'] == '' :
                        sfacil_id = ' '
                    else :
                        sfacil_id = body['FACIL_ID'].decode('utf-8', errors="")
                    
                    # Mir.rom_cod   = SORT TYPE
                    #if body['ROM_COD'] == '' :
                    #    sfacil_id = ' '
                    #else :
                    #    sfacil_id = body['FACIL_ID'].decode('utf-8', errors="")
                        

                if rec_name == 'MRR':
                    # finish time
                    sEnd_time = body['FINISH_T']

                if rec_name == 'WIR':
                    sWaferid = body['WAFER_ID'].decode('utf-8')

                if rec_name == 'WRR':
                    if sWaferid == '':
                        sWaferid = body['WAFER_ID'].decode('utf-8')    
                    
                    ############################
                if rec_name == 'SDR':
                    sProber_card = body['CARD_ID'].decode('utf-8')
                    if body['CARD_TYP'] == '' :
                        sProber_card_type = ' '
                    else :    
                        sProber_card_type = body['CARD_TYP'].decode('utf-8')
                        
                    
                if rec_name == 'WCR':
                    sNotch = body['WF_FLAT'].decode('utf-8')
                    #pos_x = body['POS_X'].decode('ascii')
                    #pos_y = body['POS_Y'].decode('ascii')
                    

                if rec_name == 'SBR':
                    sbin_num = body['SBIN_NUM']
                    ######################
                    if (body['SBIN_NAM'] == 'N/A') or (body['SBIN_NAM'] == '') :
                        sbin_desc = 'N/A'
                    else :    
                        sbin_desc = body['SBIN_NAM'].decode('utf-8')
                    ####################    
                    sbin_desc_dic[sbin_num] = sbin_desc

                    ######################
                    if body['SBIN_PF'] == 'N/A' :
                        sbin_pf = 'F'
                    else :    
                        sbin_pf = body['SBIN_PF'].decode('utf-8', errors="")
                    ########################    
                    # CANOPUS-A2A-T15-B 의 경우 bin1, bin2 가 good 이나
                    # 고객 test program 문제로 bin1 만 good 으로 지정되어 있어서
                    # mes 와 수량불일치 발생
                    # 고객 test program 수정을 안해줘서 여기서 강제로 bin2 도 pass 로 수정함.
                    # bin2 가 hbin code라서 여기서는 안되고 dic 부분에수정      
                    # 2022/08/16 device 추가 
                    # IN0299-A1A-T15-B , ZIN0299-A1A-T15-B              
                    # 2022/0824 IN0295-A0A-T15-B device 추가
                    if (sDev == "CANOPUS-A2A-T15-B" and int(sb_hb_dic[sbin_num]) == 2) :
                        sbin_pf_dic[sbin_num] = "P"
                    
                    elif (sDev == "IN0299-A1A-T15-B" and int(sb_hb_dic[sbin_num]) == 2) :
                        sbin_pf_dic[sbin_num] = "P"
                    elif (sDev == "ZIN0299-A1A-T15-B" and int(sb_hb_dic[sbin_num]) == 2) :
                        sbin_pf_dic[sbin_num] = "P"    
                    
                    elif (sDev == "ZIN0295-A0A-T15-B" and int(sb_hb_dic[sbin_num]) == 2) :
                        sbin_pf_dic[sbin_num] = "P"    
                    elif (sDev == "IN0295-A0A-T15-B" and int(sb_hb_dic[sbin_num]) == 2) :
                        sbin_pf_dic[sbin_num] = "P"            
                    
                    else :        
                        sbin_pf_dic[sbin_num] = sbin_pf
                    ####################################################
                    # part_typ
                    #Hbin_desc = "NoDesc"
                #if rec_name == 'HBR':
                #    Hbin_num = body['HBIN_NUM']
                #    Hbin_desc = "NoDesc"
                    #if body['HBIN_NAM'] == 0:
                    #    Hbin_desc = "NoDesc"
                    #else:
                    #    Hbin_desc = body['HBIN_NAM'].decode('utf-8', errors="NoDesc")


                    #Hbin_pf = body['HBIN_PF'].decode('utf-8', errors="")
                    #Hbin_desc_dic[Hbin_num] = Hbin_desc
                    #Hbin_pf_dic[Hbin_num] = Hbin_pf
                ##########################
                # X, Y, SOFTBIN , HARDBIN
                if rec_name == 'PRR':
                    sX = body['X_COORD']
                    sY = body['Y_COORD']
                    sSoft_bin = body['SOFT_BIN']
                    #sSoft_bin_desc = sbin_desc_dic[sSoft_bin]

                    sHard_bin = body['HARD_BIN']
                    sSite = body['SITE_NUM']
                    sTest_time = body['TEST_T']
                    sPart_flag = body['PART_FLG']

                    ##################################
                    # softbin , hardbin code match
                    sb_hb_dic[sSoft_bin] = sHard_bin
                    ##################################
                    ########################    
                    # CANOPUS-A2A-T15-B 의 경우 bin1, bin2 가 good 이나
                    # 고객 test program 문제로 bin1 만 good 으로 지정되어 있어서
                    # mes 와 수량불일치 발생
                    # 고객 test program 수정을 안해줘서 여기서 강제로 bin2 도 pass 로 수정함.
                    # bin2 가 hbin code라서 여기서는 안되고 dic 부분에수정     
                    # 2022/08/16 IN0299-A1A-T15-B ,  ZIN0299-A1A-T15-B    
                    # 2022/0824 IN0295-A0A-T15-B device 추가
                              
                    if (sDev == "CANOPUS-A2A-T15-B" and int(sHard_bin) == 2) :
                        sbin_pf_dic[sSoft_bin] = "P"   
                    elif (sDev == "IN0299-A1A-T15-B" and int(sHard_bin) == 2) :
                        sbin_pf_dic[sSoft_bin] = "P"
                    elif (sDev == "ZIN0299-A1A-T15-B" and int(sHard_bin) == 2) :
                        sbin_pf_dic[sSoft_bin] = "P"   
                        
                    elif (sDev == "ZIN0295-A0A-T15-B" and int(sHard_bin) == 2) :
                        sbin_pf_dic[sSoft_bin] = "P"   
                    elif (sDev == "IN0295-A0A-T15-B" and int(sHard_bin) == 2) :
                        sbin_pf_dic[sSoft_bin] = "P"   
                    ####################################################
                    
                    ##################################
                    x_y = "{0:>4}".format(sX) + "{0:>4}".format(sY)
                    # tsmc format use hardbin , tpas_wafer_dat use softbin + hardbin
                    bin_data = "{0:>4}".format(sSoft_bin) + "{0:>4}".format("0") + "*" + str(sX) + "/" + str(sY) + "/" + \
                                str(sSoft_bin) + "/" + str(sHard_bin) + "/" + str(sSite) + "/" + str(sTest_time) + "/" + str(sPart_flag)
                    #line_die =  x_y + bin_data
                    ######################################
                    # 신규좌표만 count - retest 는 무시하고 pass
                    if x_y in x_y_dic_first:
                        pass
                    else:
                        x_y_dic_first[x_y] = bin_data
                    ##################################
                    # final yield 용 - retest 의 경우는 기존꺼 지우고 덮어쓰기함
                    if x_y in x_y_dic_final:
                        del x_y_dic_final[x_y]
                    x_y_dic_final[x_y] = bin_data
                    ##################################
            #if rec_name == 'PTR':
            #    print('    PTR' + str(body['TEST_NUM']))
            #    ptr_flag = True
        ##################################
        #del stdf
        #del stdf_dic 
        del stdf_dic               
        ############################
        # eng'r 자재
        if (sDev == "ZSPCIAPLUS-A0" or sDev == "1"):
            continue
        ############################
        
        slotid_tsmc = "{0:<12}".format(slotid.upper())  # 왼쪽12칸 공백정렬
        slotid_tsmc = "{0:<12}".format(slotid_tsmc[0:9])
        
        sTester_id = sTester_id.upper()
        sTester_id_tsmc = "{0:<8}".format(sTester_id)  # 왼쪽8칸 공백정렬

        if sOper_id.strip() == "" :
            sOper_id = "testuser"

        sOper_id_tsmc = "{0:<8}".format(sOper_id)  # 왼쪽8칸 공백정렬
        sTest_prog_rev_tsmc =  "{0:<30}".format(sTest_prog_rev[0:30])   # 왼쪽8칸 공백정렬
        org_time = sTart_time
        #sTart_time = time.localtime(sTart_time)
        sTart_time = time.gmtime(sTart_time)
        time_format = '%Y%m%d%H%M%S'
        sTart_time = strftime(time_format, sTart_time)

        sTart_time_tsmc = sTart_time[0:4] + '-' + sTart_time[4:6] + '-' + sTart_time[6:8] + ' ' \
                            + sTart_time[8:10] + ':' + sTart_time[10:12] + ':' + sTart_time[12:14]
        sTart_time_tsmc = "{0:<19}".format(sTart_time_tsmc)  # 왼쪽19칸 공백정렬
        sHPSMARTEST_rev = sHPSMARTEST_rev.split(",")[0]
        sHPSMARTEST_rev = sHPSMARTEST_rev.split("(")[0]
        sHPSMARTEST_rev = sHPSMARTEST_rev.replace("s/w rev.","")
        sHPSMARTEST_rev = sHPSMARTEST_rev.replace("(T)", "")
        sHPSMARTEST_rev = sHPSMARTEST_rev.strip()
        if (sRetestseq == "FT" or sRetestseq == "N" or sRetestseq == "0"):
            sRetestseq = "0"
        elif (sRetestseq == "1" or sRetestseq == "RT1" or sRetestseq == "Y"):
            sRetestseq = "1"
        elif (sRetestseq == "2" or sRetestseq == "RT2"):
            sRetestseq = "2"
        elif (sRetestseq == "3" or sRetestseq == "RT3"):
            sRetestseq = "3" 
        else :
            msg = str(i) + ' ] s3. stdf file fail exception !! ' + '\n' + " " + move_dest + filename + '\n' 
            msg = msg + '\n' + 'retest seq 값을 가져올 수 없습니다.'
            writeLog(msg)
            print(msg)
            mail_text = mail_text + msg + '\n'

            sRetestseq = "9" 


        sWaferid = sWaferid.upper().strip()
        sWaferno = sWaferid.split('-')
        sWaferno = sWaferno[1]
        sWaferno = sWaferno[0:2]
        sWaferno = sWaferno.strip()
        sWaferno_tsmc = "{0:<2}".format(sWaferno)  # 왼쪽2칸 공백정렬
        ###########################
        sJob_rev = sJob_rev[0:30]

        ########################################
        x_size, y_size, sPDMS_notch , sort_type = get_pdms_wafer_size(sDev)

        if (y_size == "" or y_size == None or y_size == 0) :
            
            msg = str(i) + ' ] s3. tsmc map creation fail exception !! ' + '\n' + " " + move_dest + filename + '\n' 
            msg = msg + '\n' + 'pdms site 에서 y max 값을 가져올 수 없습니다.'
            writeLog(msg)
            print(msg)
            mail_text = mail_text + msg + '\n'
            continue
        
        #########################################

        if sNotch == "" :
            sNotch = sPDMS_notch.upper()
            sNotch = sNotch[0]
        ##########################
        if (sNotch == 'U') or (sNotch == 'T') :
            sNotch_direction = "UP"
        elif ((sNotch == 'D') or (sNotch == 'B')) :
            sNotch_direction = "DOWN"
        elif sNotch == 'L':
            sNotch_direction = "LEFT"
        elif sNotch == 'R':
            sNotch_direction = "RIGHT"
        else:
            sNotch_direction = sNotch

        if  sNotch_direction == "" :
            sNotch_direction = "NA"
        
        # sEnd_time = time.localtime(sEnd_time)
        sEnd_time = time.gmtime(sEnd_time)
        time_format = '%Y%m%d%H%M%S'
        sEnd_time = strftime(time_format, sEnd_time)

        sEnd_time_tsmc = sEnd_time[0:4] + '-' + sEnd_time[4:6] + '-' + sEnd_time[6:8] + ' ' \
                         + sEnd_time[8:10] + ':' + sEnd_time[10:12] + ':' + sEnd_time[12:14]
        sEnd_time_tsmc = "{0:<19}".format(sEnd_time_tsmc)  # 왼쪽19칸 공백정렬

                
        if sFamily.upper().find("POLARIS") > -1  :
            sBD_file = "TMJR29_SCK_1_1"
            sProd_name = "TMJR29"
            sProd_code = "TMJR29"
        elif sFamily.upper().find("CANOPUS") > -1 :
            #2021/10/18 진공섭gj 수정
            #sBD_file = "TMLN87G_SCK_1_1"
            sBD_file = "TMLN87_SCK_1_1"
            sProd_name = "TMLN87"
            sProd_code = "TMLN87"
        elif sFamily.upper().find("CARINA") > -1 :
            sBD_file = "TMNI76_SCK_1_1"
            sProd_name = "TMNI76"
            sProd_code = "TMNI76" 
        elif sFamily.upper().find("PORRIMA DR") > -1 :
            sBD_file = "TMLD34_SCK_1_1"
            sProd_name = "TMLD34"
            sProd_code = "TMLD34" 
        elif sFamily.upper().find("PORRIMADR") > -1 :
            sBD_file = "TMLD34_SCK_1_1"
            sProd_name = "TMLD34"
            sProd_code = "TMLD34"     
        elif sFamily.upper().find("ALCOR") > -1 :
            sBD_file = "TMNC80_SCK_1_1"
            sProd_name = "TMNC80"
            sProd_code = "TMNC80" 
        
        elif sFamily.upper().find("SPICAPLUS") > -1 :
            #2021/10/18 진공섭gj 수정
            #sBD_file = "TMPI95A-EAZT_SCK_1_1"
            sBD_file = "TMPI95_SCK_1_1"
            sProd_name = "TMPI95"
            sProd_code = "TMPI95" 
            ###########################
            # 2021/11/30 진공섭 책임님 확인 - spicaplus & pg4 notch down fix
            sNotch_direction = "DOWN"
            sNotch = 'D'
            ###########################
        
        elif sDev.upper().find("SPICAPLUS") > -1 :
            #2021/10/18 진공섭gj 수정
            #sBD_file = "TMPI95A-EAZT_SCK_1_1"
            sBD_file = "TMPI95_SCK_1_1"
            sProd_name = "TMPI95"
            sProd_code = "TMPI95" 
            ###########################
            # 2021/11/30 진공섭 책임님 확인 - spicaplus & pg4 notch down fix
            sNotch_direction = "DOWN"
            sNotch = 'D'
            ###########################    
           
                
        elif sFamily.upper().find("SPICA") > -1 :
            #2021/10/18 진공섭gj 수정
            #sBD_file = "TMMP53A-EAZT_SCK_1_1"
            sBD_file = "TMMP53_SCK_1_1"
            sProd_name = "TMMP53"
            sProd_code = "TMMP53" 
        
        elif sFamily.upper().find("PG4") > -1 :
            #2021/10/18 진공섭gj 수정
            #sBD_file = "TMPI95A-EAZT_SCK_1_1"
            sBD_file = "TMPI95_SCK_2_1"
            sProd_name = "TMPI95"
            sProd_code = "TMPI95" 
            sSorter = "2" 
            ###########################
            # 2021/11/30 진공섭 책임님 확인 - spicaplus & pg4 notch down fix
            sNotch_direction = "DOWN"
            sNotch = 'D'
            ###########################

        elif sFamily.upper().find("DENEB") > -1 :
            # 2021/10/01 gs 수정요청
            #2021/10/18 진공섭gj 수정
            # sBD_file = "TMNR16B-EAZT_SCK_1_1"
            #sBD_file = "TMNR16_SCK_1_1"
            sBD_file = "TMNR16_SCK_1_1"
            sProd_name = "TMNR16"
            sProd_code = "TMNR16" 

        else:
            # tsmc 맵에만 문제되는데 바로 확인안되서 파일 백업으로 안넘어가서 에러없앰

            #msg = str(i) + '  ERROR ] s3. Family not defined ==> prod_name , prod_code error !! ' + '\n' + " " + move_dest + filename
            #writeLog(msg)
            #print(msg)
            #mail_send_flag = True
            #mail_text = mail_text + msg + '\n'
            #mail_flag = False
            
            sBD_file = " "
            sProd_name = " "
            sProd_code = " " 

            
        sBD_file = "{0:<20}".format(sBD_file)  # 왼쪽20칸 공백정렬        
        sProd_name_tsmc = "{0:<32}".format(sProd_name)  # 왼쪽32칸 공백정렬
        sProd_code_tsmc = "{0:<6}".format(sProd_code)  # 왼쪽6칸 공백정렬

        # mpw code 4자리 스페이스
        sMPW_code = "0000"
        sMPW_code_tsmc = "{0:<4}".format(sMPW_code)  # 왼쪽4칸 공백정렬
        
        
        sINP_Test_prog = sTest_prog_rev_tsmc.strip()
        sProber_card_tsmc = "{0:<12}".format(sProber_card)  # 왼쪽19칸 공백정렬

        line_header = slotid_tsmc + sWaferno_tsmc + sProd_name_tsmc + sMPW_code_tsmc + sProd_code_tsmc + sTester_id_tsmc + sOper_id_tsmc \
                      + sTest_prog_rev_tsmc + sTart_time_tsmc + sEnd_time_tsmc + sProber_card_tsmc + sLoadbd + sBD_file \
                      + sNotch + sSorter + sTest_site + sFD_file
        #################
        
        snor_lotid = get_norlot(slotid)
        sLead, sPkg , swafer_qty = get_leadid(snor_lotid)
        
        #print(ptr_flag)
        ###############################
        # first yield용 - good , reject count
        for k in x_y_dic_first.keys():
            x_y = k
            # bin_data = x_y_dic_first.get(x_y)
            bin_data = x_y_dic_first.get(x_y)
            bin_data = bin_data.split("*")
            tmp_xy = bin_data[1]
            sx = tmp_xy.split('/')[0]
            sy = tmp_xy.split('/')[1]
            #sH = tmp_xy.split('/')[3]
            sS = tmp_xy.split('/')[2]
            bin_data = bin_data[0]
            x_y_bin_data_first = x_y_bin_data_first + x_y + bin_data + '\n'
            ######################
            # final 에 good bin , reject bin count 함
            #if Hbin_pf_dic.get(int(sH)) == "P":
            if sbin_pf_dic.get(int(sS)) == "P":
                x_y_dic_first_good = x_y_dic_first_good + 1
            else:
                x_y_dic_first_reject = x_y_dic_first_reject + 1
        ########################################
        x_y_dic_first = {}
        x_y_dic_first.clear()
        ##############
        
        print(filename + " ] x_y_dic_first complete")
        writeLog(filename + ' : x_y_dic_first success !!  '  )
        # final
        ##################################
        tsmc_body = ''
        tsmc_x = ''
        tsmc_y = ''

        for k in x_y_dic_final.keys():
            
            #####################
            if tsmc_body == '' :
                pass
            else:
                tsmc_body = tsmc_body + '\n'
            ###################
            
            x_y = k
            bin_data = x_y_dic_final.get(x_y)
            bin_data = bin_data.split("*")
            tmp_xy = bin_data[1]
            tsmc_x = tmp_xy.split('/')[0]
            tsmc_y = tmp_xy.split('/')[1]
            #########################
            # tsmc map format 의 x,y 영점이 상단 0 --> 하단 0 으로 변경
            if (y_size == "" or y_size == None or y_size == 0) :
                pass
            else :
                tsmc_y = str(int(y_size) - int(tsmc_y))
            ################################
            #sH = tmp_xy.split('/')[3]
            sS = tmp_xy.split('/')[2]

            bin_data = bin_data[0]
            #x_y_bin_data_final = x_y_bin_data_final + x_y + bin_data + '\n'
            ######################
            # final 에 good bin , reject bin count 함
            if sbin_pf_dic.get(int(sS)) == "P":
                x_y_dic_final_good = x_y_dic_final_good + 1
            else:
                x_y_dic_final_reject = x_y_dic_final_reject + 1

            #####################
            # tsmc y coordination bottom --> top change
            #tsmc_body = tsmc_body + "{0:>4}".format(tsmc_x) + "{0:>4}".format(tsmc_y) + bin_data + '\n'
            tsmc_body = tsmc_body + "{0:>4}".format(tsmc_x) + "{0:>4}".format(tsmc_y) + bin_data
            ######################################
             
        ######################################
        print(filename + " ] x_y_dic_final complete")
        writeLog(filename + ' : x_y_dic_final success !!  ')

        # tsmc_file_name = slotid  + '-' + '1' + '-' + sWaferno
        #tsmc_file_name = slotid_tsmc.strip()  + '-' + '1' + '-' + sWaferno
        tsmc_file_name = slotid_tsmc.strip()  + '-' + sSorter + '-' + sWaferno
        tsmc_file = open(result_dest + tsmc_file_name, 'w')
        tsmc_file.write(line_header + '\n')
        #tsmc_file.write(x_y_bin_data_final + '\n')
        #tsmc_file.write(tsmc_body + '\n')
        tsmc_file.write(tsmc_body)
        

        tsmc_file.close()
        msg = str(i) + ' ] s3. tsmc map creation success : ' + '\n' + " " + tsmc_file_name
        writeLog(msg)
        print(msg)
        ##############################
        # conversion 이 완료되면 test result file 을 complete 폴더로 옮김
        if line_header == '':
            mail_send_flag = True
            msg = str(i) + ' ] s3. Error ] no End_data ' +  '\n' + " " + tsmc_file_name

            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
            mail_flag = False

        #else:
            #os.remove(full_filename)
        #    shutil.move(full_filename, complete_dest + filename)

        cfilename = filename
        msg = str(i) + ' ] s3. complete file move !! ' + '\n' + " " + result_dest + cfilename
        print(msg)
        mail_text = mail_text + msg + '\n'
        writeLog(msg)


    except:
        #tsmc_file.close()
        msg = str(i) + ' ] s3. tsmc map creation fail exception !! ' + '\n' + " " + move_dest + filename + '\n' 
        msg = msg + '\n' + ' ** rec_name : ' + str(rec_name) + '  ** header : ' +  str(header) + '  ** body : ' + str(body) 
        writeLog(msg)
        print(msg)

        
        mail_send_flag = True
        mail_text = mail_text + msg + '\n'
        mail_flag = False
        continue

    #######################################
    # db insert
    # tpas_wafer_inf
    ########################
    sFirst_tot_qty = x_y_dic_first_good + x_y_dic_first_reject
    sFinal_tot_qty = x_y_dic_final_good + x_y_dic_final_reject

    sFirst_yield = (x_y_dic_first_good / sFirst_tot_qty) * 100
    sFinal_yield = (x_y_dic_final_good / sFinal_tot_qty) * 100
    sLoadbd = " "

    try:
        msg = str(i) + ' ] s4. tpas summary start :  ' + '\n' + " " + full_filename
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        print(msg)
        ################################
        conn_tpas = cx_Oracle.connect('tpasdb')
         
        cur_tpas = conn_tpas.cursor()

        sql = "SELECT * FROM TPAS_WAFER_INF "
        sql = sql + "WHERE FILENAME = '" + filename + "' "
        cur_tpas.execute(sql)
        tpas_row = cur_tpas.fetchone()
        if tpas_row == None:
            True
        else:
            #####################################
            #동일파일명은 wafer_inf ,wafer_dat 삭제
            sql = "DELETE FROM TPAS_WAFER_DAT "
            sql = sql + "WHERE FILENAME = '" + filename + "' "
            cur_tpas.execute(sql)
            conn_tpas.commit()
            ###################################
            sql = "DELETE FROM TPAS_WAFER_INF "
            sql = sql + "WHERE FILENAME = '" + filename + "' "
            cur_tpas.execute(sql)
            conn_tpas.commit()
            ########################
        try:
            # TPAS_WAFER_INF
            sql = "INSERT INTO TPAS_WAFER_INF (LOT_ID,WAFER_ID , SUB_LOT_ID, USER_ID , CUSTOMER,LEAD_CNT,DEVICE, "
            #                                     1  ,   2     ,   3       ,    4    ,   5     ,    6   ,  7
            sql = sql + " PKG_ID,HPSMARTEST_REV,TESTER_ID,TESTPROG,TESTFLOW,USERPROC, "
            #                8  ,     9        ,    10    ,   11    ,  12    ,   13
            sql = sql + " WAFERTYPE,APPLICATION,FILENAME,CONFIG,LEVEL_NAME,TIMING, "
            #                14    ,     15     ,   16   ,  17 ,  18,        19
            sql = sql + " VERTOR,ATTRIB,START_TIME,END_TIME,RETEST_SEQ,TOT_QTY,FIRST_GOOD_QTY, "
            #               20  ,  21  ,   22     ,   23   ,   24     ,  25   ,       26
            sql = sql + " FINAL_GOOD_QTY, FIRST_FAIL_QTY, FINAL_FAIL_QTY, FIRST_YIELD, FINAL_YIELD, "
            #                   27      ,  28           ,   29          ,   30       ,   31
            sql = sql + " NORMAL_LOTID,READFLAG, LOADBOARD_ID,HANDLER_ID,PRODUCT_ID, "
            #               32        ,   33   ,    34       ,    35    ,     36
            sql = sql + " TESTPROG_REV,RETEST_CODE,TESTDESC,TRANS_FLAG , OPER, SBL_FLAG , "
            #                 37      ,     38    ,   39   ,  40       ,  41 ,    42
            sql = sql + " PROBECARD_ID,NOTCH_DIRECTION, TRANS_TIME , FAMILY_NAME , JOB_REV , PRODUCT_NAME , BD_FILE_NAME ) "  # 필드추가함.
            #               43        ,       44      ,    45      ,    46       ,  47     ,     48       ,   49
            sql = sql + "VALUES ( "
            sql = sql + "'" + slotid + "' , "  # 1. lotid
            sql = sql + "'" + sWaferid + "' , "  # 2. WAFER_ID
            sql = sql + "'" + sSlotid + "' , "  # 3. sublot
            sql = sql + "'" + sOper_id  + "' , "  # 4. operator
            sql = sql + "'INP' , "  # 5. cust
            sql = sql + "'" + sLead  + "' , "  # 6. lead
            sql = sql + "'" + sDev  + "' , "  # 7. device
            sql = sql + "'" + sPkg_id  + "' , "  # 8. PKG_ID
            sql = sql + "'" + sHPSMARTEST_rev  + "' , "  # 9. handler rev etcard data
            sql = sql + "'" + sTester_id  + "' , "  # 10, test id

            sql = sql + "'" + sTest_prog_rev  + "' , "  # 11. test program name

            sql = sql + "' ' , "  # 12. test flow
            sql = sql + "'" + sUser_proc  + "' , "  # 13. user proc sUser_proc = "CP1" fix
            sql = sql + "'" + sWafertype  + "' , "  # 14 fix sck-s
            sql = sql + "'" + sApp + "' , "  # 15. app 공백
            sql = sql + "'" + filename + "' , "  # 16. filename
            sql = sql + "'" + sConfig + "' , "  # 17. config
            sql = sql + "'" + sLevelname + "' , "  # 18. level name
            sql = sql + "'" + sTiming + "' , "  # 19. timing
            sql = sql + "'" + sVentor + "' , "  # 20. ventor
            sql = sql + "'" + sAttribe + "' , "  # 21. attribe
            sql = sql + "'" + sTart_time + "' , "  # 22. start time
            sql = sql + "'" + sEnd_time + "' , "  # 23. end time
            sql = sql + "'" + sRetestseq + "' , "  # 24. retest seq
            sql = sql + "'" + str(sFinal_tot_qty) + "' , "  # 25. tot qty
            sql = sql + "'" + str(x_y_dic_first_good) + "' , "  # 26. first good qty
            sql = sql + "'" + str(x_y_dic_final_good) + "' , "  # 27. final good qty
            sql = sql + "'" + str(x_y_dic_first_reject) + "' , "  # 28. first fail qty
            sql = sql + "'" + str(x_y_dic_final_reject) + "' , "  # 29. final fail qty

            sql = sql + "'" + str(round(sFirst_yield,2)) + "' , "  # 30. first yield
            sql = sql + "'" + str(round(sFinal_yield,2)) + "' , "  # 31. final yield

            #sql = sql + "'" + slotid + "' , "  # 32. normal lot id
            #snor_lotid
            sql = sql + "'" + snor_lotid + "' , "  # 32. normal lot id
            sql = sql + "'" + sReadflag + "' , "  # 33. read flag
            sql = sql + "'" + sLoadbd + "' , "  # 34. LOADBOARD_ID
            sql = sql + "'" + sHandler + "' , "  # 35. handler
            sql = sql + "'" + sProd_code + "' , "  # 36. PRODUCT ID , prod code
            #sql = sql + "'" + sTest_prog_rev + "' , "  # 37. TESTPROG_REV
            #sINP_Test_prog
            sql = sql + "'" + sINP_Test_prog + "' , "  # 37. TESTPROG_REV

            sql = sql + "'" + str(sRetest_code) + "' , "  # 38. RETEST_CODE
            sql = sql + "'" + sTemper + "' , "  # 39. sTesttemp 온도 testdesc
            sql = sql + "'" + sTransflag + "' , "  # 40 trans flag
            sql = sql + "'" + sLoc + "' , "  #  41 oper
            sql = sql + "'" + sSBL_flag + "' , "  # 42 sbl flag
            sql = sql + "'" + sProber_card.strip() + "' , "  # 43 prober card id
            
            sql = sql + "'" + sNotch_direction.strip() + "' , "  # 44 notch
            sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')  , "  # 45 trans time
            sql = sql + "'" + sFamily + "' , "  # 46.family name
            sql = sql + "'" + sJob_rev + "' , "  # 47.JOB_REV
            sql = sql + "'" + sProd_name + "' , "   # 48. prod name
            sql = sql + "'" + sBD_file.strip() + "'  "   # 49. BD FILE
            sql = sql + ") "
            cur_tpas.execute(sql)
            conn_tpas.commit()
            conn_tpas.close()

            msg = str(i) + ' ] s4. TPAS_WAFER_INF Insert complete !! ' + '\n' + " " + full_filename

            print(msg)
            writeLog(msg + '\n' + sql)
            mail_text = mail_text + msg + '\n'

            ###################################
            # TPAS_WAFER_DAT
            #sDie_inf = x , y ,  sSoft_bin + "," + sHard_bin + "," + temp1[3].strip() + \
            #           "," + temp1[4].strip() + temp1[5].strip() + \
            #           "," + temp1[8].strip() + temp1[9].strip()

            conn_tpas = cx_Oracle.connect('tpasdb')
             
            cur_tpas = conn_tpas.cursor()
            data = []
            die_test_time =  int(org_time)*1000
            k_cnt = 0

            for k in x_y_dic_final.keys():
                x_y = k
                k_cnt = k_cnt + 1

                #if k_cnt == 3005 :
                #    print(str(3005))

                temp = x_y_dic_final.get(x_y)
                temp = temp.split('*')
                bin_data = temp[1]
                bin_data = bin_data.split('/')
                sX_pos = bin_data[0]
                sY_pos = bin_data[1]
                sSB = bin_data[2]
                sHB = bin_data[3]
                ########################
                #if sbin_pf_dic.get(int(sHB)) == "P":
                if sbin_pf_dic.get(int(sSB)) == "P":
                    sPass_flag = "PASS"
                else:
                    sPass_flag = "FAIL"
                ########################
                sSite = bin_data[4]
                sTest_time = bin_data[5]
                sPart_flag = bin_data[6]
                #############################
                die_test_time = die_test_time + int(sTest_time)
                ##################
                sDie_time = time.gmtime(die_test_time/1000.0)
                time_format = '%Y%m%d%H%M%S.{}'.format(die_test_time%1000)
                sDie_time = strftime(time_format, sDie_time)
                #sDie_time = sDie_time
                ##########################
                now = datetime.datetime.now()
                nowtime = now.strftime('%Y%m%d%H%M%S')
                #################################
                sBin_desc = ''
                HBin_desc = ''
                sBin_desc = sbin_desc_dic.get(int(sSB))
                ###
                if sBin_desc == None:
                   sBin_desc = "NoDesc" 
                ####   
                HBin_desc = "NoDesc"
                #HBin_desc = Hbin_desc_dic[int(sHB)]
                #HBin_desc = Hbin_desc_dic[int(sHB)]
                #################################
                # list , tuple use
                add_data = (slotid,sWaferid,sSlotid,str(sX_pos),str(sY_pos), str(sSB), \
                         sBin_desc, str(sHB), HBin_desc, sPass_flag, str(sDie_time) ,str(sSite), str(sUser_proc), str(sLoc), \
                         sNotch_direction.strip(), str(nowtime), filename, str(sRetestseq), str(sTart_time), str(sEnd_time) )
                data.append(add_data)
                #print(str(k_cnt))
            ######################
                
            #########    

            if len(data) > 0:
                sql = "INSERT INTO TPAS_WAFER_DAT (LOT_ID,WAFER_ID , SUB_LOT_ID, X_POS,Y_POS,SBIN,SBIN_DESC, "
                #                                     1  ,   2     ,   3       ,   4  ,   5  , 6 ,  7
                sql = sql + " HBIN,HBIN_DESC,PASSFAIL,TEST_TIME,SITE,USERPROC, "
                #              8  ,   9     ,   10   ,   11    , 12 ,   13
                sql = sql + " OPER,NOTCH_DIRECTION,TRANS_TIME, FILENAME, RETEST_SEQ , START_TIME , END_TIME ) "
                #              14 ,       15      ,   16     ,  17     ,    18      ,   19       ,  20
                sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, "
                sql = sql + "  :11, :12, :13, :14, :15, :16, :17, :18, :19, :20 ) "
                cur_tpas.executemany(sql,data)
                conn_tpas.commit()
                conn_tpas.close()

                msg = str(i) + ' ] s5. TPAS_WAFER_DAT Insert complete !! ' + '\n' + " " + full_filename
                print(msg)
                writeLog(msg)
                mail_text = mail_text + msg + '\n'

            ###########################
            data = []
            #######################
            #conn_tpas.commit()
            #conn_tpas.close()
            ###########################
            msg = str(i) + ' ] s5. TPAS_WAFERSUM TABLE Insert START !! ' + '\n' + " " + filename
            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
            
            # ==============>>>> tpas wafersum table insert  <<<<=====================
            conn_tpas = cx_Oracle.connect('tpaddb')
            
            cur_tpas = conn_tpas.cursor()
            #####################################
            #######################
            # HBIN 별 PASS OR FAIL 을 TPAS_WAFER_DAT 에 저장된 DATA 로 매칭시킴
            #sql = "SELECT DISTINCT HBIN,PASSFAIL FROM TPAS_WAFER_DAT "            
            sql = "SELECT DISTINCT SBIN,PASSFAIL FROM TPAS_WAFER_DAT "            
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "
            sql = sql + "AND  WAFER_ID = '" + sWaferid + "' "
            sql = sql + "AND OPER = '" + sLoc + "' "            
            cur_tpas.execute(sql)
            tpas_row = cur_tpas.fetchall()
            if tpas_row == None:
                mail_send_flag = True        
                msg = str(i) + ' ] ERROR !! SBIN DESC ERROR !! ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                mail_flag = False
                conn_tpas.close()
                continue
            else:
                #### ==>> row data 찾아서 sum 에 insert
                sbin_pf_dic = {}
                sbin_pf_dic.clear()
                for row in tpas_row:
                    #Hbin_num = row[0]
                    #Hbin_pf = row[1]
                    #Hbin_pf_dic[int(Hbin_num)] = Hbin_pf[0]
                    sbin_num = row[0]
                    sbin_pf = row[1]
                    sbin_pf_dic[int(sbin_num)] = sbin_pf[0]
            ##########################            
            
            # LOT_ID, WAFER_ID,OPER 로 TPAS_WAFERSUM_DAT 조회하여 삭제
            sql = "DELETE FROM TPAS_WAFERSUM_DAT "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "
            sql = sql + "AND  WAFER_ID = '" + sWaferid + "' "
            sql = sql + "AND OPER = '" + sLoc + "' "
            cur_tpas.execute(sql)
            conn_tpas.commit()
            ###################################
            #LOT_ID, WAFER_ID, OPER로  TPAS_WAFERSUM_INF 조회하여  삭제
            sql = "DELETE FROM TPAS_WAFERSUM_INF "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "
            sql = sql + "AND  WAFER_ID = '" + sWaferid + "' "
            sql = sql + "AND OPER = '" + sLoc + "' "
            cur_tpas.execute(sql)
            conn_tpas.commit()
            ########################
            #==============>>>>> TPAS_WAFERSUM_DATA INSERT START
            # ROW DATA SEARCH --> SUM TABLE INSERT
            # lot,wafer,oper data all sum
            data = []
            x_y_dic_final = {}
            x_y_dic_final.clear()

            x_y_dic_final_good = 0
            x_y_dic_final_reject = 0

            #TPAS_WAFER_DAT
            sql = "SELECT LOT_ID,WAFER_ID , SUB_LOT_ID, X_POS,Y_POS,SBIN,SBIN_DESC, "
            #              0    ,   1     ,      2    ,   3  ,   4 ,  5  ,   6
            sql = sql + " HBIN,HBIN_DESC,PASSFAIL,TEST_TIME,SITE,USERPROC, "
            #              7  ,      8  ,   9    ,   10    , 11 , 12
            sql = sql + " OPER,NOTCH_DIRECTION,TRANS_TIME, FILENAME, RETEST_SEQ FROM TPAS_WAFER_DAT "
            #              13 ,       14      ,     15   ,   16    ,    17
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "
            sql = sql + "AND  WAFER_ID = '" + sWaferid + "' "
            sql = sql + "AND OPER = '" + sLoc + "' "
            sql = sql + "ORDER BY LOT_ID, WAFER_ID, OPER , RETEST_SEQ, START_TIME , TEST_TIME "
            cur_tpas.execute(sql)
            tpas_row = cur_tpas.fetchall()
            if tpas_row == None:
                True
            else:
                #### ==>> row data 찾아서 sum 에 insert
                for row in tpas_row:
                    sX_pos = row[3]
                    sY_pos = row[4]
                    x_y = "{0:>4}".format(sX_pos) + "{0:>4}".format(sY_pos)

                    sSB = row[5]
                    sBin_desc = row[6]
                    sHB = row[7]
                    HBin_desc = row[8]
                    sPass_flag = row[9]
                    sDie_time = row[10]
                    sSite = row[11]
                    sUser_proc = row[12]
                    sLoc = row[13]
                    sNotch_direction = row[14]
                    now = datetime.datetime.now()
                    nowtime = now.strftime('%Y%m%d%H%M%S')
                    sfilename = row[16]
                    sRetestseq = row[17]

                    add_data = (slotid, sWaferid, sSlotid, \
                                str(sX_pos), str(sY_pos), sSB, sBin_desc, sHB, HBin_desc, sPass_flag, \
                                sDie_time, str(sSite), sUser_proc, sLoc, sNotch_direction.strip(),  str(nowtime), \
                                sfilename, str(sRetestseq))
                    ####################
                    # for tpas_wafersum_dat
                    if x_y in x_y_dic_final:
                        del x_y_dic_final[x_y]
                    x_y_dic_final[x_y] = add_data
                    #########################

            for k in x_y_dic_final.keys():
                x_y = k
                bin_data = x_y_dic_final.get(x_y)
                #sH = bin_data[7].strip()
                sS = bin_data[5].strip()

                #if Hbin_pf_dic.get(int(sH)) == "P":
                if sbin_pf_dic.get(int(sS)) == "P":
                    ######################
                    # final 에 good bin , reject bin count 함
                    x_y_dic_final_good = x_y_dic_final_good + 1
                else:
                    x_y_dic_final_reject = x_y_dic_final_reject + 1

                data.append(bin_data)

            if len(data) > 0:
                sql = "INSERT INTO TPAS_WAFERSUM_DAT (LOT_ID,WAFER_ID , SUB_LOT_ID, X_POS,Y_POS,SBIN,SBIN_DESC, "
                #                                     1     ,   2     ,   3       ,   4  ,   5  , 6 ,  7
                sql = sql + " HBIN,HBIN_DESC,PASSFAIL,TEST_TIME,SITE,USERPROC, "
                #              8  ,   9     ,   10   ,   11    , 12 ,   13
                sql = sql + " OPER,NOTCH_DIRECTION,TRANS_TIME, FILENAME, RETEST_SEQ   ) "
                #              14 ,       15      ,   16     ,  17     ,    18
                sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, "
                sql = sql + "  :11, :12, :13, :14, :15, :16, :17, :18 ) "
                cur_tpas.executemany(sql,data)
                conn_tpas.commit()
                conn_tpas.close()

                msg = str(i) + ' ] s5. TPAS_WAFERSUM_DAT Insert complete !! ' + '\n' + " " + sWaferid

                print(msg)
                writeLog(msg)
                mail_text = mail_text + msg + '\n'
            ###########################
            data = []
            sbin_pf_dic = {}
            sbin_pf_dic.clear()
            ###########
            # bump map qty
            
            ##############################    
            bump_in_qty, bump_rej_qty, bump_map_id = get_bump_map(slotid, sWaferid)
            #sConfig = str(bump_rej_qty)
            #sLevelname = str(bump_in_qty) 
            if sFamily.strip().upper() == "SPICAPLUS" or sFamily.strip().upper() == "PG4" : 
                # mult bin 이라 bump 와 merge 안됨
                bump_map_id = " "
                
            ###########################################################
            sFinal_tot_qty = x_y_dic_final_good + x_y_dic_final_reject
            sFinal_yield = (x_y_dic_final_good / sFinal_tot_qty) * 100
            #########################################################
            ###############===> save on tpas_wafersum_inf
            ### final db insert
            conn_tpas = cx_Oracle.connect('tpasdb')
            
            cur_tpas = conn_tpas.cursor()

            file_cnt = '0'

            sql = "SELECT TOT_QTY, FIRST_GOOD_QTY , FIRST_FAIL_QTY , FIRST_YIELD "
            sql = sql + " FROM TPAS_WAFER_INF "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "
            sql = sql + "AND  WAFER_ID = '" + sWaferid + "' "
            sql = sql + "AND OPER = '" + sLoc + "' "
            sql = sql + "ORDER BY LOT_ID, WAFER_ID, OPER , RETEST_SEQ  , START_TIME   "
            cur_tpas.execute(sql)
            tpas_row = cur_tpas.fetchall()
            if tpas_row == None:
                True
            else:
                ###########################
                file_cnt = str(cur_tpas.rowcount)

                # TPAS_WAFER_INF - FIRST DATA SEARCH
                for row in tpas_row:
                    #sFirst_tot_qty = row[0]
                    x_y_dic_first_good = row[1]
                    x_y_dic_first_reject = row[2]
                    sFirst_yield = row[3]
                    break

                ############################
                # EXCEPT FIRST DATA, THE OTHER DATA IS GENERATED BASE ON CURRENT data
                sSBL_flag = "Y"
                if spkg_type.strip() != '' :
                    spkg_type = spkg_type + '@' + sTemper
                
                
                sql = "INSERT INTO TPAS_WAFERSUM_INF (LOT_ID,WAFER_ID , SUB_LOT_ID, USER_ID , CUSTOMER,LEAD_CNT,DEVICE, "
                #                                     1  ,   2     ,   3       ,    4    ,   5     ,    6   ,  7
                sql = sql + " PKG_ID,HPSMARTEST_REV,TESTER_ID,TESTPROG,TESTFLOW,USERPROC, "
                #                8  ,     9        ,    10    ,   11    ,  12    ,   13
                sql = sql + " WAFERTYPE,APPLICATION,FILENAME,CONFIG,LEVEL_NAME,TIMING, "
                #                14    ,     15     ,   16   ,  17 ,  18,        19
                sql = sql + " VERTOR,ATTRIB,START_TIME,END_TIME,RETEST_SEQ,TOT_QTY,FIRST_GOOD_QTY, "
                #               20  ,  21  ,   22     ,   23   ,   24     ,  25   ,       26
                sql = sql + " FINAL_GOOD_QTY, FIRST_FAIL_QTY, FINAL_FAIL_QTY, FIRST_YIELD, FINAL_YIELD, "
                #                   27      ,  28           ,   29          ,   30       ,   31
                sql = sql + " NORMAL_LOTID,READFLAG, LOADBOARD_ID,HANDLER_ID,PRODUCT_ID, "
                #               32        ,   33   ,    34       ,    35    ,     36
                sql = sql + " TESTPROG_REV,RETEST_CODE,TESTDESC,TRANS_FLAG , OPER, SBL_FLAG , "
                #                 37      ,     38    ,   39   ,  40       ,  41 ,    42
                sql = sql + " PROBECARD_ID,NOTCH_DIRECTION, TRANS_TIME , FAMILY_NAME , JOB_REV , PRODUCT_NAME , BD_FILE_NAME , FILE_CNT , "
                #               43        ,       44      ,    45      ,    46       ,  47     ,    48       ,      49       ,     50    
                sql = sql + " BUMP_TOT_QTY , BUMP_REJ_QTY , BUMP_MAP_ID , TOT_WAFER_QTY , WAFER_SORT_PROCESS , WAFER_SORT_TYPE , TEST_HOUSE , "  # 필드추가함."        
                #                  51     ,     52              53            54                 55                  56              57
                sql = sql + " PROBECARD_TYPE ) "
                #                   58
                sql = sql + "VALUES ( "
                sql = sql + "'" + slotid + "' , "  # 1. lotid
                sql = sql + "'" + sWaferid + "' , "  # 2. WAFER_ID
                sql = sql + "'" + sSlotid + "' , "  # 3. sublot
                sql = sql + "'" + sOper_id + "' , "  # 4. operator
                sql = sql + "'INP' , "  # 5. cust
                sql = sql + "'" + sLead + "' , "  # 6. lead
                sql = sql + "'" + sDev + "' , "  # 7. device
                sql = sql + "'" + sPkg_id + "' , "  # 8. PKG_ID
                sql = sql + "'" + sHPSMARTEST_rev + "' , "  # 9. handler rev etcard data
                sql = sql + "'" + sTester_id + "' , "  # 10, test id

                sql = sql + "'" + sTest_prog_rev + "' , "  # 11. test program name

                sql = sql + "' ' , "  # 12. test flow
                sql = sql + "'" + sUser_proc + "' , "  # 13. user proc sUser_proc = "CP1" fix
                sql = sql + "'" + sWafertype + "' , "  # 14 fix sck-s
                sql = sql + "'" + sApp + "' , "  # 15. app 공백
                sql = sql + "'" + filename + "' , "  # 16. filename
                sql = sql + "'" + sConfig + "' , "  # 17. config
                sql = sql + "'" + sLevelname + "' , "  # 18. level name
                sql = sql + "'" + sTiming + "' , "  # 19. timing
                sql = sql + "'" + sVentor + "' , "  # 20. ventor
                sql = sql + "'" + sAttribe + "' , "  # 21. attribe
                sql = sql + "'" + sTart_time + "' , "  # 22. start time
                sql = sql + "'" + sEnd_time + "' , "  # 23. end time
                sql = sql + "'" + str(sRetestseq) + "' , "  # 24. retest seq
                sql = sql + "'" + str(sFinal_tot_qty) + "' , "  # 25. tot qty
                sql = sql + "'" + str(x_y_dic_first_good) + "' , "  # 26. first good qty
                sql = sql + "'" + str(x_y_dic_final_good) + "' , "  # 27. final good qty
                sql = sql + "'" + str(x_y_dic_first_reject) + "' , "  # 28. first fail qty
                sql = sql + "'" + str(x_y_dic_final_reject) + "' , "  # 29. final fail qty

                sql = sql + "'" + str(round(sFirst_yield, 2)) + "' , "  # 30. first yield
                sql = sql + "'" + str(round(sFinal_yield, 2)) + "' , "  # 31. final yield

                #sql = sql + "'" + slotid + "' , "  # 32. normal lot id
                #snor_lotid
                sql = sql + "'" + snor_lotid + "' , "  # 32. normal lot id

                sql = sql + "'" + sReadflag + "' , "  # 33. read flag
                sql = sql + "'" + sLoadbd + "' , "  # 34. LOADBOARD_ID
                sql = sql + "'" + sHandler + "' , "  # 35. handler
                sql = sql + "'" + sProd_name + "' , "  # 36. PRODUCT ID
                # sql = sql + "'" + sTest_prog_rev + "' , "  # 37. TESTPROG_REV
                # sINP_Test_prog
                sql = sql + "'" + sINP_Test_prog + "' , "  # 37. TESTPROG_REV

                sql = sql + "'" + sRetest_code + "' , "  # 38. RETEST_CODE
                sql = sql + "'" + sTemper + "' , "  # 39. sTesttemp 온도 testdesc
                sql = sql + "'" + sTransflag + "' , "  # 40 trans flag
                sql = sql + "'" + sLoc + "' , "  # 41 oper
                sql = sql + "'" + sSBL_flag + "' , "  # 42 sbl flag
                sql = sql + "'" + sProber_card.strip() + "' , "  # 43 prober card id
                sql = sql + "'" + sNotch_direction.strip() + "' , "  # 44 notch
                sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS')  , "  # 45 trans time
                sql = sql + "'" + sFamily + "' , "  # 46.family name                
                sql = sql + "'" + sJob_rev + "' , "  # 47.JOB_REV
                sql = sql + "'" + sProd_name + "' , "   # 48. prod name
                sql = sql + "'" + sBD_file.strip() + "',  "   # 49. BD FILE
                sql = sql + "'" + file_cnt + "'  "  + " , " # 50. file count
                ####################
                # BUMP 수량 추가
                sql = sql + str(bump_in_qty) + " , "
                sql = sql + str(bump_rej_qty) + " , "
                sql = sql + "'" + str(bump_map_id) + "' , "
                sql = sql + "'" + str(swafer_qty) + "' , "
                sql = sql + "'" + str(spkg_type) + "' , "   # WAFER_SORT_PROCESS
                #sql = sql + "'" + str(scmod_code) + "' , "   # WAFER_SORT_TYPE
                sql = sql + "'" + str(sort_type) + "' , "   # WAFER_SORT_TYPE
                sql = sql + "'" + str(sfacil_id) + "' , "   # TEST HOUSE
                # sProber_card_type
                sql = sql + "'" + str(sProber_card_type) + "' "   # 2.	Probe Card Type   : 4S_2x2
                sql = sql + ") "
                cur_tpas.execute(sql)
                conn_tpas.commit()
                conn_tpas.close()
                msg = str(i) + ' ] s5. TPAS_WAFERSUM_INF Insert complete !! ' + '\n' + " " + sWaferid

                print(msg)
                writeLog(msg + '\n' + sql)
                mail_text = mail_text + msg + '\n'

                ###################################
                # success filename save
                #org_stdf_ftp_list.append(filename)
                #complete_dest = source_dir + "COMPLETE_MAP/"
                shutil.move(full_filename, complete_dest + filename)
                time.sleep(1)

        except:
            mail_send_flag = True
            conn_tpas.rollback()
            conn_tpas.close()
            msg = str(i) + ' ] S4,S5,S6 tpas summary insert error  !! ' + '\n' + " " + result_dest + filename
            print(msg)
            mail_text = mail_text + msg + '\n'
            writeLog(msg)
            mail_flag = False
            continue

    except:
        mail_send_flag = True
        conn_tpas.rollback()
        conn_tpas.close()
        msg = str(i) + ' ] S4,S5,S6 tpas summary insert error exception  !! ' + '\n' + " " + result_dest + filename
        print(msg)
        mail_text = mail_text + msg + '\n'
        writeLog(msg)
        mail_flag = False
        continue
    #############################FF
    # MVL REPORT 생성할 LOTID, WAFERID 저장
        
    ###################
    x_y_dic_final = {}
    x_y_dic_first = {}
    sbin_desc_dic = {}
    sbin_pf_dic = {}
    x_y_dic_first.clear()
    x_y_dic_final.clear()
    sbin_desc_dic.clear()    
    sbin_pf_dic.clear()

#############################
# data collection 은 완료
# ==> ftp 로 파일전송 ,  tsmc map 부터  stdf 파일까지 차례대로 전송
# 7. comp_dest 파일을 ftp 로 전송 for tsmc map file
# 7. ftp 연결
# 진공섭 GJ 
# 2022/03/12 TSMC MAP BACKUP 요청
# Backup server :  
# Backup Directory : /qct_nfs04/INPHI_DATA/TSMC_MAP 

try:
    ############################################
    ftp = ftplib.FTP(new_ftp_ip)
    ftp.login(new_ftp_id,new_ftp_pw)
    target_tsmc_ftp = '/qct_nfs04/INPHI_DATA/TSMC_MAP/'
    ftp.cwd(target_tsmc_ftp)
    #############################
    # result 는 c 드라이브
    result_dest = source_dir + "TSMC_MAP/"
    os.chdir(result_dest)

    msg = str(i) +  ' ] ' + new_ftp_ip + ' ] s7. ftp for tsmc map file connection success !! '
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'

except:
    #writeLog('3. ftp / ftp연결실패 : 예외사항 ' + ftp_ip)
    msg = str(i) + ' ] ' + new_ftp_ip + ' ] s7. ftp for tsmc map file connection fail :  exception '
    mail_text = mail_text + msg + '\n'
    mail_flag = False
    print(msg + new_ftp_ip)
    writeLog(msg)
    #send_mail('[3.ftp error : ' + ftp_ip + ']' )

# 7. comp_dest 파일을 ftp 로 전송
# 7. 단계마다 잠시 delay
time.sleep(3)
i = 0
#####################
# 여기서는 tsmc 맵파일 전송
# 2022/03/12 TSMC MAP BACKUP 요청
# Backup server :  
# Backup Directory : /qct_nfs04/INPHI_DATA/TSMC_MAP 
#result_dest = source_dir + "TSMC_MAP/"
for filename in os.listdir(result_dest):
    
    ext = os.path.splitext(filename)[-1]
    path = os.path.abspath(result_dest)
    full_filename = os.path.join(path, filename)

    ################################
    # ftp 폴더에  lotno 로 폴더생성하여 전송
    tsmc_fnam = filename.split("/")[-1]
    
    sfile_lot = tsmc_fnam.split("-")[0]
    sfile_lot = sfile_lot.upper()
    ######################################
            
    # 파일만 검색
    if os.path.isfile(full_filename):
        pass
    else:
        continue

    msg = str(i) + ' ] s8. tsmc map upload start : ' + '\n' + " " + full_filename
    ###############################
    # 2. DATE FOLDER
    try:
        ftp.cwd(sfile_lot)
    except:
        ftp.mkd(sfile_lot)
        ftp.cwd(sfile_lot)      
    #################################
                
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'

    try:
        ############################################
         
        
        i = i + 1
        mail_send_flag = True
        my_file = open(filename, 'rb')
        ftp.storbinary('STOR ' + filename , my_file, blocksize=1024)

        if ftp.size(filename) == os.path.getsize(filename) :
            my_file.close()
            
            msg = str(i) + ' ] ' + new_ftp_ip + ' ] s8. ftp for tsmc map file upload Success !! ' + '\n' + " " + full_filename

            print(msg)
            mail_text = mail_text + msg + '\n'
            writeLog(msg)
        else:
            msg = str(i) + ' ] ' + new_ftp_ip + ' ] s8. ftp for tsmc map file upload error exception !! : ' + '\n' + " " + full_filename
            print(msg)
            mail_text = mail_text + msg + '\n'
            writeLog(msg)
            mail_flag = False
            my_file.close()
        #######################
        # lotno 폴더에 백업후 다시 lotno 폴더를 나온다.
        time.sleep(1)           
        ftp.cwd('../')
        print(ftp.pwd())
        ##########################    
            
        my_file.close()
    except:
        msg = str(i) +  ' ] ' + new_ftp_ip + ' ] s8. ftp error exception !! tsmc map file :  ' + '\n' + " " + full_filename
        print(msg)
        mail_flag = False
        my_file.close()
        mail_text = mail_text + msg + '\n'
        writeLog(msg)
        continue
        #####################
     
        
ftp.close()

##########################################
# 2021/12/23 TSMC MAP FILE 도 새로운 FTP 서버로 전송
# NEW FTP 서버로 전송시작

# 7-1. comp_dest 파일을 ftp 로 전송 for tsmc map file
# 7-1. ftp 연결
try:
    target_stdf_ftp2 = ' '
    ############################################
    
    ftp = ftplib.FTP(new_ftp_ip2)
    ftp.login(new_ftp_id2,new_ftp_pw2)
    ftp.cwd(target_stdf_ftp2)
    #############################
    result_dest = source_dir + " MAP/"
    os.chdir(result_dest)

    msg = str(i) + ' ] ' +  new_ftp_ip2 +  ' ] s7-1. ftp for tsmc map file connection success !! '
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'

except:
    #writeLog('3. ftp / ftp연결실패 : 예외사항 ' + ftp_ip)
    msg = str(i) +  + ' ] ' +  new_ftp_ip2 + ' ] s7-1. ftp for tsmc map file connection fail :  exception '
    mail_text = mail_text + msg + '\n'
    mail_flag = False
    print(msg + new_ftp_ip2)
    writeLog(msg)
    #send_mail('[3.ftp error : ' + ftp_ip + ']' )

# 7-1. tsmc 파일을 ftp 로 전송
# 7-1. 단계마다 잠시 delay
time.sleep(3)
i = 0
#####################
#result_dest = source_dir + " MAP/"
for filename in os.listdir(result_dest):
    
    ext = os.path.splitext(filename)[-1]
    path = os.path.abspath(result_dest)
    full_filename = os.path.join(path, filename)

    # 파일만 검색
    if os.path.isfile(full_filename):
        pass
    else:
        continue

    msg = str(i) + ' ] ' +  new_ftp_ip2 + ' ] s8-1. tsmc map upload start : ' + '\n' + " " + full_filename

    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'

    try:
        ############################################
         
        i = i + 1
        mail_send_flag = True
        my_file = open(filename, 'rb')
        ftp.storbinary('STOR ' + filename , my_file, blocksize=1024)

        if ftp.size(filename) == os.path.getsize(filename) :
            my_file.close()
            
            msg = str(i) + ' ] ' +  new_ftp_ip2 +  ' ] s8-1. ftp for tsmc map file upload Success !! ' + '\n' + " " + full_filename

            print(msg)
            mail_text = mail_text + msg + '\n'
            writeLog(msg)

            ###############################
            # ftp 전송후 move 파일 삭제
            from_path = os.path.abspath(result_dest)
            # filename was added .gz, split filename after delete gz
            #from_filename = os.path.splitext(filename)[0]
            from_full_filename = os.path.join(from_path, filename)
            if os.path.isfile(from_full_filename):
                # move 파일삭제
                time.sleep(2)
                os.remove(from_full_filename)  # result file delete
                ##################
                msg = str(i) + ' ] ' +  new_ftp_ip2 + ' ] s8-1. ftp transfer and tsmc file delete ' + '\n' + " " + from_full_filename

                mail_text = mail_text + msg + '\n'
                print(msg)
                writeLog(msg)
            ##################################
            #writeLog('3. ftp / ftp 전송성공 !!  ' + comp_dest + filename)
        else:
            msg = str(i) + ' ] ' +  new_ftp_ip2 + ' ] s8-1. ftp for tsmc map file upload error exception !! : ' + '\n' + " " + full_filename
            print(msg)
            mail_text = mail_text + msg + '\n'
            writeLog(msg)
            mail_flag = False
            my_file.close()

        my_file.close()
    except:
        msg = str(i) + ' ] ' +  new_ftp_ip2 + ' ] s8-1. ftp error exception !! tsmc map file :  ' + '\n' + " " + full_filename
        print(msg)
        mail_flag = False
        my_file.close()
        mail_text = mail_text + msg + '\n'
        writeLog(msg)
        continue
        #####################
ftp.close()

# 2021/12/23 새로운 FTP 전송끝 
# 
##########################################
# 9. final step start
# 9-1 base on complete map file, delete local file ,
# 9-2 move ftp file to backup folder
 
try:
    #######################    
    i = 0
    for filename in os.listdir(complete_dest):
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(complete_dest)
        slocal = os.path.join(path, filename)
        stdf_fnam = filename.split("/")[-1]

        if os.path.isfile(slocal):
            pass
        else:
            continue

        i = i+ 1
        smsg = str(i) + ' ] s9-1. stdf file compression start : ' + '\n' + " " + stdf_fnam
        print(smsg)
        writeLog(smsg)
        mail_text = mail_text + smsg + '\n'
        ###############################
        # 압축하기
        if (stdf_fnam.find('.stdf.gz') == -1) and (stdf_fnam.find('.stdf') > -1):            
            slocal_tmp = slocal + ".gz"
            with open(slocal, 'rb') as in_file:
                with gzip.open(slocal_tmp, 'wb') as out_file:    
                    shutil.copyfileobj(in_file, out_file)                    
                    smsg = str(i) + ' ] s9-1. compression success !! : ' + '\n' + " " + stdf_fnam
                    print(smsg)
                    writeLog(smsg)
                    mail_text = mail_text + smsg + '\n'
    #############################
     
    ftp = ftplib.FTP(new_ftp_ip)
    ftp.login(new_ftp_id, new_ftp_pw)
    ftp.cwd(target_stdf_ftp)
    os.chdir(complete_dest)
    backup_org_path = ftp.pwd()
    backup_org_path = backup_org_path + "/"
    files = ftp.nlst()
    ########################
    msg = str(i) + ' ] s9-2. ftp file backup start !!  '
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n' + '\n'

    time.sleep(1)
    i = 0    
    #######################    
    for filename in os.listdir(complete_dest):
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(complete_dest)
        slocal = os.path.join(path, filename)
        stdf_fnam = filename.split("/")[-1]        

        if os.path.isfile(slocal):
            pass
        else:
            continue
        ############################### 
        if (stdf_fnam.find('.stdf.gz') > -1):
            i = i + 1
            # 31번서버의 STDF_DONE 폴더에도 복사하여 
            
            # 날짜복사 copy2     
            #shutil.copy2(slocal, cust_stdf_dir + stdf_fnam)
            # 파일날짜를 복사한날로 변경
            #shutil.copy(slocal, cust_stdf_dir + stdf_fnam)
                        

            
            #if stdf_fnam in UF_stdf :
            #    shutil.copy(slocal, cust_stdf_dir3 + stdf_fnam)
            #else :
            #    shutil.copy(slocal, cust_stdf_dir2 + stdf_fnam)
                        
            sfile_lot = stdf_fnam.split("_")[1]
            sfile_lot = sfile_lot.upper()
            # 1.backup folder
            # uflex map file 은 backup_uf 에 저장하고
            # hp map file 은 그대로 backup 에 저장한다.
            if stdf_fnam in UF_stdf :
                try:
                    ftp.cwd('BACKUP_UF')
                except:
                    ftp.mkd('BACKUP_UF')
                    ftp.cwd('BACKUP_UF')
            else :
                try:
                    ftp.cwd('BACKUP')
                except:
                    ftp.mkd('BACKUP')
                    ftp.cwd('BACKUP')

            ###############
            # 2. DATE FOLDER
            try:
                ftp.cwd(sfile_lot)
            except:
                ftp.mkd(sfile_lot)
                ftp.cwd(sfile_lot)
            ##################
            #backup_target_path = backup_org_path + "BACKUP/"
            #success = ftp.rename(backup_org_path + stdf_filename , \
            #                        backup_target_path + sfile_lot + '/'+ stdf_fnam)
            ####################
            #FTP UPLOAD
            my_file = open(filename, 'rb')
            ftp.storbinary('STOR ' + filename , my_file, blocksize=1024)

            if ftp.size(filename) == os.path.getsize(slocal) :
                my_file.close()
                
                msg = str(i) + ' ] s9-2. BACKUP Success !! ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                org_stdf_ftp_list.append(stdf_fnam)
                org_stdf_ftp_list.append(stdf_fnam.replace('.stdf.gz', '.stdf'))
                ####################
                # backup 후 로컬파일삭제
                # 2021/12/22 new ftp setup 에 따라 여기서는 old ftp 에 올리고 종료
                #os.remove(slocal)  # result file delete
                #os.remove(slocal.replace('.stdf.gz', '.stdf'))  # result file delete

            else:
                msg = str(i) + ' ] s9-2. BACKUP error exception !! : ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                mail_flag = False
                my_file.close()

            #my_file.close()
            time.sleep(1)           
            ftp.cwd('../')
            ftp.cwd('../')
            print(ftp.pwd())

            msg = str(i) + ' ] s9-2. ftp file backup progress !!  ' + '\n' + " " + filename

            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
    
    ftp.close()
    # stdf 파일 백업 36번서버 끝
    ##################################################################
    # stdf 파일 
    # 8번 2021/12/22 추가
    # 김효근 gj 파일전송 # 2021/12/22 new ftp 서버 구성 시작
    # stdf 파일을 고객계정으로 전송
    ###  
    
    target_stdf_ftp2 = ' '
    
    
    
    ftp = ftplib.FTP(new_ftp_ip2)
    ftp.login(new_ftp_id2, new_ftp_pw2)
    ftp. cwd(target_stdf_ftp2)
    os.chdir(complete_dest)
    backup_org_path = ftp.pwd()
    backup_org_path = backup_org_path + "/"
    files = ftp.nlst()
    ########################
    msg = str(i) + ' ] s10-2. ftp file backup start !!  '
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n' + '\n'

    time.sleep(1)
    i = 0    
    #######################    
    for filename in os.listdir(complete_dest):
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(complete_dest)
        slocal = os.path.join(path, filename)
        stdf_fnam = filename.split("/")[-1]        

        if os.path.isfile(slocal):
            pass
        else:
            continue
        ############################### 
        if (stdf_fnam.find('.stdf.gz') > -1):
            i = i + 1
            # 31번서버의 STDF_DONE 폴더에도 복사하여 
             
            # 날짜복사 copy2     
            #shutil.copy2(slocal, cust_stdf_dir + stdf_fnam)
            # 파일날짜를 복사한날로 변경
            #shutil.copy(slocal, cust_stdf_dir + stdf_fnam)
            # 2021/12/22 새로운 ftp 서버 (.24 서버 )생성으로 여기서는 
            # .5 ftp 에 올리는 것을 중단하고 새로운 서버에 올린다.
            #if stdf_fnam in UF_stdf :
            #    shutil.copy(slocal, cust_stdf_dir3 + stdf_fnam)
            #else :
            #    shutil.copy(slocal, cust_stdf_dir2 + stdf_fnam)
                        
            sfile_lot = stdf_fnam.split("_")[1]
            sfile_lot = sfile_lot.upper()
            # 1.backup folder
            # uflex map file 은 backup_uf 에 저장하고
            # hp map file 은 그대로 backup 에 저장한다.
            # 2021/12/22 ws 폴더에서 stdf 폴더로 이동
            if stdf_fnam in UF_stdf :
                try:
                    ftp.cwd('stdf_uf')
                except:
                    ftp.mkd('stdf_uf')
                    ftp.cwd('stdf_uf')
            else :
                try:
                    ftp.cwd('stdf')
                except:
                    ftp.mkd('stdf')
                    ftp.cwd('stdf')
            #################################
            # 2. DATE FOLDER
            #
            #try:
            #    ftp.cwd(sfile_lot)
            #except:
            #    ftp.mkd(sfile_lot)
            #    ftp.cwd(sfile_lot)
            #'''
            ##################
            #backup_target_path = backup_org_path + "BACKUP/"
            #success = ftp.rename(backup_org_path + stdf_filename , \
            #                        backup_target_path + sfile_lot + '/'+ stdf_fnam)
            ####################
            #FTP UPLOAD
            my_file = open(filename, 'rb')
            ftp.storbinary('STOR ' + filename , my_file, blocksize=1024)

            if ftp.size(filename) == os.path.getsize(slocal) :
                my_file.close()
                
                msg = str(i) + ' ] s10-2. BACKUP Success !! ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                org_stdf_ftp_list.append(stdf_fnam)
                org_stdf_ftp_list.append(stdf_fnam.replace('.stdf.gz', '.stdf'))
                ####################
                # backup 후 로컬파일삭제
                if os.path.isfile(slocal):
                    os.remove(slocal)  # result file delete
                if os.path.isfile(slocal.replace('.stdf.gz', '.stdf')):    
                    os.remove(slocal.replace('.stdf.gz', '.stdf'))  # result file delete

            else:
                msg = str(i) + ' ] s10-2. BACKUP error exception !! : ' + '\n' + " " + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                writeLog(msg)
                mail_flag = False
                my_file.close()

            #my_file.close()
            time.sleep(1)           
            # stdf 에 upload 후에 다시 ws 폴더로 나가서
            ftp.cwd('../')
            #ftp.cwd('../')
            print(ftp.pwd())

            msg = str(i) + ' ] s10-2. ftp file backup progress !!  ' + '\n' + " " + filename

            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
    
    ftp.close()
    # 2021/12/22 new ftp 서버 구성 끝    
    ################################
    # 백업후 cim1 서버의 파일은 삭제
    org_stdf_dir = " /STDF/"
     

    #2021/07/08 inphi 가 mvl 로 변경됨
    org_stdf_dir2 = " /STDF/"


    for (path, dirs, files) in os.walk(org_stdf_dir):
        for filename in files:
            full_filename = os.path.join(path, filename)            
            stdf_fnam = filename.split("/")[-1]

            if stdf_fnam in org_stdf_ftp_list :
                os.remove(full_filename)  # result file delete
                time.sleep(1)
    ####################################
    # 백업후 cim1 서버의 파일은 삭제
    for (path, dirs, files) in os.walk(org_stdf_dir2):
        for filename in files:
            full_filename = os.path.join(path, filename)            
            stdf_fnam = filename.split("/")[-1]

            if stdf_fnam in org_stdf_ftp_list :
                os.remove(full_filename)  # result file delete
                time.sleep(1)            
    ############################################
    msg = str(i) + ' ] s9. ftp file backup complete !!  '
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n' + '\n'
    ##################
except Exception as ex:
    #writeLog('3. ftp / ftp연결실패 : 예외사항 ' + ftp_ip)
    msg = str(i) + ' ] s9. ftp file backup fail :  exception  ' + ex
    mail_text = mail_text + msg + '\n'
    mail_flag = False
    print(msg + ftp.host)
    writeLog(msg)    

ftp.close()

######################################################
msg = str(i) + ' ==> Inphi map conversion end !! '
print(msg)
writeLog(msg)
mail_text = mail_text + '\n' + msg + '\n'

if (mail_send_flag == False) and (mail_flag == True):
    pass
else:
    # mail send when file exist only
    send_mail(mail_text)

sys.exit(0)
