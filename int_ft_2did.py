import ftplib
import os
from re import S
import shutil
from pathlib import Path
import time
import gzip
import datetime
from datetime import date, timedelta
import cx_Oracle
import csv

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
import paramiko
from scp import SCPClient

#################################
# move 할 폴더생성
# D:\QCT_Datalog
###################################
global smail_desc
global last_mail_flag

last_mail_flag = False


today = datetime.datetime.now().strftime('%Y%m%d')
tmp_day = date.today() - timedelta(1)
yesterday = tmp_day.strftime('%Y%m%d')
#######################
# 폴더 지정 및 변경
source_dir = "C:/temp/INT_2DID/"
local_ftp = source_dir

org_stdf_ftp = ' /2DID/'
 
###################################

move_dest = source_dir + "CONVERSION_move/"
#result_dest = source_dir + "TSMC_MAP/"
complete_dest = source_dir + "COMPLETE_MAP/"

# 압축하고 압축폴더에서 바로 ftp 로 전송
#from_ftp = result_dest
log_dest = source_dir + "mapfile_log/"

new_ftp_ip = ' '
new_ftp_id = ' '
new_ftp_pw = ' '
#######################
chk_hour = 0.15
#chk_hour = 0
mail_flag = True
mail_send_flag = False
mail_text = "map conversoin file list " + '\n' + '\n'


smail_desc = ""
print("conersion start ... ")

####################
def stdf_unzip() :
    ssh = paramiko.SSHClient()        
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)        
    ssh.connect("ip", username=" ", password= " ")
    print("ssh connected.")
    #########################
    
    tmp_cmd = 'cd  /INT_ORIGIN_TEMP ; find . -name "*.gz" -mmin +5 -exec gzip -d {}  \; && mv ./*.stdf  /INT_ORIGIN/ '
    stdin, stdout, stderr = ssh.exec_command(tmp_cmd)
    time.sleep(2.0) 
        
    output = stdout.read().decode("utf8")            
    print (output)
    ssh.close()

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
    with open(full_filename, 'r', encoding='UTF8') as f:
        while True:
            line = f.readline()
            print(line)
    f.close

# email 전송
def send_mail(m_text):
    
    global last_mail_flag
    
    # "Mrelay.kr.jcetglobal.com"
    print("mail sending")
    smtp = smtplib.SMTP("mail", 25)
    
    m_text = ipcheck() + '\n' + m_text
    msg = MIMEText(m_text)
    if mail_flag == True:
        msg['Subject'] = 'INT FT 2did datacollection success !! ' + ipcheck()
    else:
        msg['Subject'] = 'INT FT 2DID fuse check Error !! ' + ipcheck() + ' - ' + ' check equipment '

     
    msg['To'] = ' '
    
    if last_mail_flag == False :
        smtp.sendmail(' @jcetglobal.com',  msg['To'].split(',') , msg.as_string())
    else :
        smtp.sendmail(' @jcetglobal.com',   msg.as_string())
        
    print("mail success !! ")
    # time.sleep(3)
    smtp.quit()

###################################
def get_leadid(sLot, sInt_Oper_id):
    conn_mes = cx_Oracle.connect('mesdb')
    cur_mes = conn_mes.cursor()

    stemp_lot = sLot.strip().upper()
    stemp_lot = stemp_lot.replace("-", "%")

    stemp_split = stemp_lot.split("%")
    
    lot_flag = ""
    srun = ""
    sub_lot = ""
    dup_lot = ""
    srun = stemp_split[0]
    if len(stemp_split) == 2 :        
        sub_lot = "{0:<3}".format(stemp_split[1])
        dup_lot = stemp_split[1]
        lot_flag = "2"

    elif len(stemp_split) == 3 :        
        sub_lot = "{0:<3}".format(stemp_split[1])
        dup_lot = stemp_split[2]  
        lot_flag = "3"

    meslot = ""
    lead_id = "XXXX"
    pkg_id = "XXXX"
    
    soper_id = ""
    soper_desc = ""
    
    sql = "SELECT KEY1 FROM UPTDAT2 "
    sql = sql + "WHERE TABLE_NAME = 'INT_OPER_MAPPING' "
    sql = sql + "AND DATA1 = '" + sInt_Oper_id + "' "
    
    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    for row in rows:  # 202029
        soper_id = row[0]
    
    sql = "SELECT DATA1 FROM UPTDAT "
    sql = sql + "WHERE FACTORY = 'TEST' "
    sql = sql + "AND TABLE_NAME = 'QUL_OPER' "
    sql = sql + "AND KEY1 = '" + soper_id + "' "

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    for row in rows:  # 202029
        soper_desc = row[0]
    
    ######################
    sql = "SELECT LOT_ID,CREATE_CMF1,CREATE_CMF3 FROM WIPLTH "
    sql = sql + "WHERE FACTORY = 'TEST' "
    sql = sql + "AND LOT_ID LIKE '" + stemp_lot + "' "

    if lot_flag == "3" :
        sql = sql + "AND SUBSTR(LOT_ID, 14,3) = '" + sub_lot + "'  "
        sql = sql + "AND SUBSTR(LOT_ID, 17,1) = '" + dup_lot + "'  "
    elif lot_flag == "2" :
        sql = sql + "AND ( (LENGTH(LOT_ID) = 17  AND SUBSTR(LOT_ID,17,1) =  '" + dup_lot + "') OR  "
        sql = sql + "      (LENGTH(LOT_ID) <= 16 AND SUBSTR(LOT_ID,14,3) =  '" + sub_lot.strip() + "') ) "        
    else :
        sql = sql + "AND LENGTH(LOT_ID) < 14 "

    sql = sql + "AND CREATE_CMF2 = 'INT' "
    sql = sql + "AND OPER = '" + soper_id + "' "
    sql = sql + "AND HIS_DELETE_FLAG <> 'Y' "
    sql = sql + "AND ROWNUM < 2 "

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    for row in rows:  # 202029
        meslot = row[0]
        pkg_id = row[1]
        lead_id = row[2]
    ######################
    
    conn_mes.close()

    if meslot == "":
        meslot = sLot

    ##################
    # SAMPLE OPER
    #soper_id = "360"
    #soper_desc = "FT1"
    return meslot , lead_id, pkg_id , soper_id, soper_desc ;
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
    stmp_lot = "{0:<13}".format(s1_lot) + "{0:<3}".format(s2_lot) + "{0:<1}".format(s3_lot)
    stmp_lot = stmp_lot.strip()

    sql = "SELECT LOT_ID FROM WIP_LOTINF "
    sql = sql + " WHERE LOT_ID = '" + stmp_lot + "' "

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()

    if rows == None:
        stmp_lot = sLot
    
    conn_mes.close()

    return stmp_lot ;
##############################################
def get_mes_qty(sLot, soper):
    conn_mes = cx_Oracle.connect('mesdb')
    cur_mes = conn_mes.cursor()

    sql = "SELECT QTY1 FROM WIPLTH "
    sql = sql + "WHERE FACTORY = 'TEST' "
    sql = sql + "AND LOT_ID = '" + sLot + "' "
    sql = sql + "AND CREATE_CMF2 = 'INT' "
    sql = sql + "AND OPER = '" +  soper + "' "
    sql = sql + "AND HIS_DELETE_FLAG <> 'Y' "
    sql = sql + "ORDER BY HIST_SEQ DESC "

    cur_mes.execute(sql)
    rows = cur_mes.fetchone()

    if rows == None:
        smes_qty = "0"
    else:
        for row in rows:  # 202029
            smes_qty = row[0]
            break
        
    conn_mes.close()

    return smes_qty ;

def get_temp(sLot, soper):
    conn_tpad = cx_Oracle.connect('tpaduser')  
    cur_tpad = conn_tpad.cursor()

    sTemper = ""
    sql = "SELECT TEMPERATURE FROM DTRACKCIM.TUT_TPAD_INTERFACE "
    sql = sql + "WHERE JOB_NO = '" + sLot + "' "    
    sql = sql + "AND MFG_DEVICE_NAME = '" +  soper + "' "
    sql = sql + "ORDER BY PROGRAM_LOAD_TIME DESC "
    
    cur_tpad.execute(sql)
    rows = cur_tpad.fetchall()

    if rows == None:
        sTemper = ""
    else:
        for row in rows:  # 202029
            sTemper = row[0]
            break
        
    conn_tpad.close()

    if sTemper.strip() == "" :
        sTemper = "NA" 
    elif int(sTemper) > 25 :
        sTemper = "H"
    elif int(sTemper) < 25 :
        sTemper = "C"
    elif int(sTemper) == 25 :
        sTemper = "R" 
    else :
        sTemper = "NA" 
    
    return sTemper ;

###################################
def chk_val(sFilename, slotid, sOper):
    
    global smail_desc
    
    sflag = False
    sdup_msg = ""
    
    smail_flag = False
    smail_desc = ""
    sfuse = ""
    sunit = ""
    sfuse_val_flag = False
        
    conn_tpas1 = cx_Oracle.connect('tpaddb')
    cur_tpas1 = conn_tpas1.cursor()
    cur_tpas2 = conn_tpas1.cursor()
    
    smail_desc =  "LotID :" + slotid + " Oper :" + sOper + "\n" + " filename : " + sFilename + "\n" 
    
    #####################################
    # 1. 차수별로 구분하여 FUSE 중복이면 ALARM MAIL
    #Compare CLASSTAG within all units (rejects & Bin1) test summary/sequence
    #1A, 1B, 1C, 2A, 3A, etc..) STDF
    # SINGLE STDF FILE
    sql = "SELECT FUSE FROM TPAS_2DID_DAT "        
    sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
    sql = sql + "AND OPER = '" + sOper + "' "    
    sql = sql + "AND FUSE <> 'N/A' "
    sql = sql + "AND FUSE <> ' ' "
    sql = sql + "AND FUSE <> 'NA' "
    # invalid fuse 는 제외 0000C000_00000003_000003 _ 로 SPLIT 했을 때 두번째 문자열이 000 으로 시작하면 INVALID FUSE
    sql = sql + "AND ((INSTR(FUSE,'_') > 0 AND NOT REGEXP_SUBSTR(FUSE, '[^_]+', 1, 2) LIKE  '000%') OR (INSTR(FUSE,'_') = 0 ) ) "
    # HBIN 23 은 INVALID CASE 로 체크로직에서 제외
    sql = sql + "AND NOT HBIN = '23' "
    
    sql = sql + "AND LENGTH(FUSE) > 5 "
    #sql = sql + "GROUP BY FUSE, RETEST_SEQ "
    sql = sql + "GROUP BY FUSE, FILENAME "
    sql = sql + "HAVING COUNT(FUSE) > 1 "
    
    cur_tpas1.execute(sql)
    tpas_row = cur_tpas1.fetchall()
    if cur_tpas1.rowcount > 0 :
        for row in tpas_row:
            #sunit = row[0]
            sfuse = row[0]
            sunit = ""
            
            sql = "SELECT UNIT_2DID FROM TPAS_2DID_DAT "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND OPER = '" + sOper + "' "
            sql = sql + "AND FUSE = '" + sfuse + "' "
            # INVALID FUSE CODE 는 제외
            sql = sql + "AND ((INSTR(FUSE,'_') > 0 AND NOT REGEXP_SUBSTR(FUSE, '[^_]+', 1, 2) LIKE  '000%') OR (INSTR(FUSE,'_') = 0 ) ) "
            sql = sql + "GROUP BY UNIT_2DID "
            cur_tpas2.execute(sql)
            tpas_row2 = cur_tpas2.fetchall()
            
            if cur_tpas2.rowcount > 1 :
                for row2 in tpas_row2:
                    sunit = sunit + row2[0] + ", "
                    
                #if scnt > 1:
                sflag = True
                sfuse_val_flag = True
                #serr_code = "FUSE_CHK_ERROR"
                sdup_msg = sdup_msg + "[" + sunit + " / " + sfuse + "] " + "\n"
        
        
    #--------------------
    if sflag == True :        
        
        smail_desc = smail_desc + "\n" + "[ 1. CLASSTAG_RULE1_ERROR : " + sdup_msg 
        
        msg = str(i) + ' ] fuse check error insert :  <==============' + '\n' + slotid +  " / " + sOper + '\n'
        writeLog(msg)        
        print(msg)

        sql = "SELECT LOT_ID FROM MES_BLOCK "
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND OPER = '" + sOper + "' "
        sql = sql + "AND ERR_CODE = 'CLASSTAG_RULE1_ERROR' " 
        
        cur_tpas2.execute(sql)
        tpas_row2 = cur_tpas2.fetchall()
        
        if cur_tpas2.rowcount > 0 :
            sql = "DELETE FROM MES_BLOCK "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND OPER = '" + sOper + "' "
            sql = sql + "AND ERR_CODE = 'CLASSTAG_RULE1_ERROR' " 
            
            cur_tpas2.execute(sql)
            conn_tpas1.commit()
        ################################
        # BLOCK TABLE        
        sql = "INSERT INTO MES_BLOCK (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'CLASSTAG_RULE1_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
        
        #################################
        # HISTORY TABLE 
        sql = "INSERT INTO MES_BLOCK_HIS (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'CLASSTAG_RULE1_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        #################################
        
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
    ####################################     
    ######################################
    # 2. SUM 기준으로 FUSE 중복 + 2DID 다를 때 BLOCK
    #Compare CLASSTAG between ‘Bin1 vs Bin1 only’ across other test
    #summary/sequence (1A, 2A, 3A) STDF
    # ALL STDF FILE , BIN1
    sdup_msg = ""
    sflag = False
    sunit_cnt = 0
    
    sql = "SELECT FUSE FROM TPAS_2DID_DAT "        
    sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
    sql = sql + "AND OPER = '" + sOper + "' "  
    sql = sql + "AND HBIN = '1' "  
    sql = sql + "AND FUSE <> 'N/A' "
    sql = sql + "AND FUSE <> ' ' "
    sql = sql + "AND FUSE <> 'NA' "
    # invalid fuse 는 제외 0000C000_00000003_000003 _ 로 SPLIT 했을 때 두번째 문자열이 000 으로 시작하면 INVALID FUSE
    sql = sql + "AND ((INSTR(FUSE,'_') > 0 AND NOT REGEXP_SUBSTR(FUSE, '[^_]+', 1, 2) LIKE  '000%') OR (INSTR(FUSE,'_') = 0 ) ) "
    # HBIN 23 은 INVALID CASE 로 체크로직에서 제외
    sql = sql + "AND NOT HBIN = '23' "
    
    sql = sql + "AND LENGTH(FUSE) > 5 "
    sql = sql + "GROUP BY FUSE "
    sql = sql + "HAVING COUNT(FUSE) > 1 "
    
    cur_tpas1.execute(sql)
    tpas_row = cur_tpas1.fetchall()
    
    if cur_tpas1.rowcount > 0 :
                    
        for row in tpas_row:
            #sunit = row[0]
            sfuse = row[0]
            sunit = ""
            
            sql = "SELECT UNIT_2DID FROM TPAS_2DID_DAT "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND OPER = '" + sOper + "' "
            sql = sql + "AND FUSE = '" + sfuse + "' "
            # INVALID FUSE CODE 는 제외
            sql = sql + "AND ((INSTR(FUSE,'_') > 0 AND NOT REGEXP_SUBSTR(FUSE, '[^_]+', 1, 2) LIKE  '000%') OR (INSTR(FUSE,'_') = 0 ) ) "
            sql = sql + "GROUP BY UNIT_2DID "
            cur_tpas2.execute(sql)
            tpas_row2 = cur_tpas2.fetchall()
            
            if cur_tpas2.rowcount > 1 :
                for row2 in tpas_row2:
                    sunit = sunit + row2[0] + ", "
                    sunit_cnt = sunit_cnt + 1
                    
                #if scnt > 1:
                
                #serr_code = "FUSE_CHK_ERROR"
                sdup_msg = sdup_msg + "[" + sunit + " / " + sfuse + "] " + "\n"
        
        if sunit_cnt > 3 :
            sflag = True
            sfuse_val_flag = True
                
    ##############################    
    if sflag == True :
        
        smail_desc = smail_desc + "\n" + "[ 2. CLASSTAG_RULE2_ERROR : " + sdup_msg
        
        msg = str(i) + ' ] fuse check error insert :  <==============' + '\n' + slotid +  " / " + sOper + '\n'
        writeLog(msg)        
        print(msg)

        sql = "SELECT LOT_ID FROM MES_BLOCK "
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND OPER = '" + sOper + "' "
        sql = sql + "AND ERR_CODE = 'CLASSTAG_RULE2_ERROR' " 
        
        cur_tpas2.execute(sql)
        tpas_row2 = cur_tpas2.fetchall()
        
        if cur_tpas2.rowcount > 0 :
            sql = "DELETE FROM MES_BLOCK "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND OPER = '" + sOper + "' "
            sql = sql + "AND ERR_CODE = 'CLASSTAG_RULE2_ERROR' " 
            
            cur_tpas2.execute(sql)
            conn_tpas1.commit()
        ################################
        # BLOCK TABLE        
        sql = "INSERT INTO MES_BLOCK (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'CLASSTAG_RULE2_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
        
        #################################
        # HISTORY TABLE 
        sql = "INSERT INTO MES_BLOCK_HIS (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'CLASSTAG_RULE2_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        #################################
        
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
    ####################################
    # 2did yield check 0.05% 
    sflag = False
    sdup_msg = ""
    
    sql = "SELECT UNIT_YIELD FROM TPAS_2DIDSUM_INF "
    sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
    sql = sql + "AND OPER = '" + sOper + "' "
        
    cur_tpas2.execute(sql)
    tpas_row2 = cur_tpas2.fetchall()
    for row2 in tpas_row2:
        unit_yield = row2[0]
        #if int(unit_yield) <= 99.95 :
        if float(unit_yield) <= 99.95 :
            sflag = True
            sfuse_val_flag = True
            sdup_msg = "2DID UNIT YIELD (Unit Reject rate is more than 0.05%) : " + str(unit_yield)  
    
            smail_desc = smail_desc + "\n" + sdup_msg
            
    ################################
    if sflag == True :   
        sql = "SELECT LOT_ID FROM MES_BLOCK "
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND OPER = '" + sOper + "' "
        sql = sql + "AND ERR_CODE = '2DID_UNIT_YIELD_ERROR' " 
        
        cur_tpas2.execute(sql)
        tpas_row2 = cur_tpas2.fetchall()
        
        if cur_tpas2.rowcount > 0 :
            sql = "DELETE FROM MES_BLOCK "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND OPER = '" + sOper + "' "
            sql = sql + "AND ERR_CODE = '2DID_UNIT_YIELD_ERROR' " 
            
            cur_tpas2.execute(sql)
            conn_tpas1.commit()
        ################################
        
        # BLOCK TABLE        
        sql = "INSERT INTO MES_BLOCK (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'2DID_UNIT_YIELD_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
        
        #################################
        # HISTORY TABLE 
        sql = "INSERT INTO MES_BLOCK_HIS (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'2DID_UNIT_YIELD_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        #################################
        
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
    ####################################        
    ## MIX CHECK
    ######################################    
    sdup_msg = ""
    sflag = False
    
    sql = "SELECT B.UNIT_2DID, B.INT_RETEST, B.USERPROC FROM "        
    sql = sql + "( SELECT UNIT_2DID, INT_RETEST , OPER FROM TPAS_2DID_DAT "
    sql = sql + "  WHERE  LOT_ID = '" + slotid + "' "
    sql = sql + "  AND OPER = '" + sOper + "' "
    sql = sql + "  GROUP BY UNIT_2DID, INT_RETEST , OPER "
    sql = sql + "  MINUS "
    sql = sql + "  SELECT UNIT_2DID , INT_RETEST , OPER  FROM TPAS_2DIDSUM_DAT "
    sql = sql + "  WHERE  LOT_ID = '" + slotid + "' "
    sql = sql + "  AND OPER = '" + sOper + "' "
    sql = sql + "  AND HBIN = '1' "
    sql = sql + "  GROUP BY UNIT_2DID, INT_RETEST , OPER "
    sql = sql + " ) A , TPAS_2DID_DAT B "
    sql = sql + " WHERE A.UNIT_2DID = B.UNIT_2DID "
    sql = sql + " AND A.INT_RETEST = B.INT_RETEST "
    sql = sql + " AND A.OPER = B.OPER "
    sql = sql + " AND B.HBIN = '1' "
    sql = sql + " ORDER BY A.UNIT_2DID "
    
    cur_tpas1.execute(sql)
    tpas_row = cur_tpas1.fetchall()
    
    if cur_tpas1.rowcount > 0 :
        
        for row in tpas_row:
            sunit = row[0] 
            sretest = row[1]
            suser_proc = row[2]
            sflag = True
            sdup_msg = sdup_msg + "[" + sunit + " / " + sretest + " / " + suser_proc + "] BIN1 MIXING " + "\n"
        
        smail_desc = smail_desc + "\n" + sdup_msg 
    ##############################
    
    
    if sflag == True :        
        
        msg = str(i) + ' ] fuse check error insert :  <==============' + '\n' + slotid +  " / " + sOper + '\n'
        writeLog(msg)        
        print(msg)

        sql = "SELECT LOT_ID FROM MES_BLOCK "
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND OPER = '" + sOper + "' "
        sql = sql + "AND ERR_CODE = 'FUSE_MIX_CHK_ERROR' " 
        
        cur_tpas2.execute(sql)
        tpas_row2 = cur_tpas2.fetchall()
        
        if cur_tpas2.rowcount > 0 :
            sql = "DELETE FROM MES_BLOCK "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND OPER = '" + sOper + "' "
            sql = sql + "AND ERR_CODE = 'FUSE_MIX_CHK_ERROR' " 
            
            cur_tpas2.execute(sql)
            conn_tpas1.commit()
        ##############################
        # ##
        # BLOCK TABLE        
        sql = "INSERT INTO MES_BLOCK (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'FUSE_MIX_CHK_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
        
        #################################
        # HISTORY TABLE 
        sql = "INSERT INTO MES_BLOCK_HIS (LOT_ID, OPER, ERR_CODE, BLOCK_FLAG, BLOCK_DATE, ERR_DESC, ACT_USER ) "        
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid       
        sql = sql + "'" + sOper + "' , "  # 2. customer
        sql = sql + "'FUSE_CHK_ERROR' , "  # 3. pkg
        sql = sql + "'Y' , "  # 4. lead        
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sdup_msg[0:499] + "' ,  "    # PARTID
        sql = sql + "'CIM_2DID_DATA_COL'  "    # int retest   
        sql = sql + ") "
        #################################
        
        cur_tpas2.execute(sql)
        conn_tpas1.commit()
    ####################################
        
    conn_tpas1.close()                
    
    return sfuse_val_flag ,sdup_msg, smail_flag , smail_desc ;


#############################################
# send_mail('mail test' )
p = Path(move_dest)  # 로컬 다운받은 폴더
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
#print("/ STDF/INT_ORIGIN stdf.gz file unzip ... ")
#stdf_unzip()
print("INT FT 2DID data collection main ... ")

org_stdf_ftp_list = []
i = 0
#######################

try:
    ############################################
    #org_stdf_ftp = ' /2DID/'
    ftp = ftplib.FTP(new_ftp_ip)
    ftp.login(new_ftp_id, new_ftp_pw)
    #
    ftp.cwd(org_stdf_ftp)
    os.chdir(local_ftp)
    
    files = ftp.nlst()

    #########################
    # if map file no exist , exit
    if len(files) == 0:
        print('    ==> no map file ')
        ftp.close()
        quit()

    for filename in files:

        writeLog("==> file down start : " + filename)
        print("==> file down start : " + filename)

        stdf_fnam = filename.split("/")[-1]

        #if (stdf_fnam.find('.stdf.data') > -1) and  (stdf_fnam.find('Golden.2did.') == -1)  and  (stdf_fnam.find('eng_rmbnew') == -1)  :
        if (stdf_fnam.upper().find('.STDF_') > -1) and  (stdf_fnam.upper().find('_2DID') > -1)  :

          
            stdf_mtim = ftp.voidcmd("MDTM " + filename)[4:].strip()
            stdf_mtim_ts = time.mktime(datetime.datetime.strptime(stdf_mtim, '%Y%m%d%H%M%S').timetuple())
            #####################
            delta_ago = time.time() - stdf_mtim_ts
            time_ago = (delta_ago / 60) / 60  # hour
            if time_ago > chk_hour:
                pass
            else:
                continue
            ################
            slocal = os.path.join(source_dir, stdf_fnam)
            msg = "file down start : " + '\n' + " " + stdf_fnam
            writeLog(msg)
            print(msg)
            # 1. ftp 의 압축된 gdf.map file 을 다운받는다.
            sfile = open(slocal, 'wb')
            ftp.retrbinary('RETR ' + filename, sfile.write)
            sfile.close()

            #if ftp.size(filename) == os.path.getsize(local_filename):
            i = i+ 1
            smsg = str(i) + ' ] s1. ftp download Success !! : ' + '\n' + " " + stdf_fnam
            print(smsg)
            writeLog(smsg)
            mail_text = mail_text + smsg + '\n'
            ###############################
            # 압축풀기
            if (stdf_fnam.find('.gz') > -1):
                slocal_tmp = slocal.replace(".gz", "")
                with gzip.open(slocal, 'rb') as in_file:
                    with open(slocal_tmp, 'wb') as out_file:
                        shutil.copyfileobj(in_file, out_file)

    ftp.close()

except:
    msg = str(i) + ' ] s1. ftp download fail exception !! : ' + '\n' + " " + stdf_fnam
    mail_text = mail_text + msg + '\n'
    mail_flag = False
    print(msg)

time.sleep(3)
# test
######################

# 2. source 폴더의 파일 탐색하여 대상 파일 move dest 로 옮김

#source_dir = "C:/temp/INT_2DID/"

for filename in os.listdir(source_dir):

    ext = os.path.splitext(filename)[-1]
    path = os.path.abspath(source_dir)
    full_filename = os.path.join(path, filename)

    # 파일만 검색
    if os.path.isfile(full_filename):
        # print(" : " + full_filename)
        # writeLog("파일 : " + full_filename)
        #pass
        if os.path.getsize(full_filename) > 0 :
            pass
        else:
            continue

    else:
        # print("파일아님 : " + full_filename)
        # writeLog("파일아님 : " + full_filename)
        continue
    ext_flag = False
    if (filename.upper().find('.STDF_2DID') > -1) :
        ext_flag = True
        pass
    else:
        continue
    ###########################
    # 1. stdf, txt, xml 파일 확장자로 지정
    # writeLog("이동시작" + full_filename)
    # ext_dest  가 여러가지일때 하나씩 비교
    #if (ext_flag == True) and (time_ago > chk_hour):
    if (ext_flag == True):
        mail_text = mail_text + '1. file select : ' + full_filename + '\n'
        # 1. stdf 파일을 move 하여 move 가능하면 파일완료된 것으로 간주
        # move 는 에러나도 move 됨, rename 해서 에러나면 파일완료안된것으로 간주
        try:
            # 파일이 있으면 걍 넘어감, 덮어쓰기함
            print("**** 2did file check : " + full_filename)
            writeLog("**** 2did file check : " + full_filename)
            
            #os.rename(full_filename, full_filename + '_')
            os.rename(full_filename, full_filename)
            try:
                # 2. source 폴더의 파일 탐색하여 대상 파일 move dest 로 옮김
                ###########################
                #mail_send_flag = True
                msg = str(i) + ' ] s2. 2did stdf_2DID move start : ' + '\n' + " " + move_dest + filename
                writeLog(msg)
                print(msg)
                shutil.move(full_filename, move_dest + filename)
                #####################
                msg = str(i) + ' ] s2. 2did stdf_2DID move complete !! : ' + '\n' + " " + move_dest + filename
                print(msg)
                writeLog(msg)
                mail_text = mail_text + msg + '\n'
                ################################
            except:
                msg = str(i) + ' ] s2. 2did stdf_2DID move error !! : ' + '\n' + " " + move_dest + filename
                print(msg)
                mail_text = mail_text + msg + '\n'
                mail_flag = False

        except:
            msg = str(i) + ' ] s2. 2did stdf_2DID move exception error !! : ' + '\n' + " " + move_dest + filename
            print(msg)
            mail_text = mail_text + msg + '\n'
            mail_flag = False
            continue
        # move complete
#################################

# 3. file read start
time.sleep(3)
#x_y_dic = {}
unit_dic = {}

i = 0

for filename in os.listdir(move_dest):
    # x,y 좌표초기화
    # 만약 동일 좌표일 경우 나중 data 로 덮어쓰기해야함.
    #x_y_dic.clear()
    unit_dic.clear()
    #######################
    unit_good = 0
    unit_fail = 0
    ########################    
    bin_good = 0
    bin_fail = 0
    #######################
    tot_qty = 0    
    ########################    
    unit_yield = 0
    bin_yield = 0
    #################
    
    ext = os.path.splitext(filename)[-1]
    path = os.path.abspath(move_dest)
    full_filename = os.path.join(path, filename)
    #stdf 파일에 대해서만 conversion
    if os.path.isfile(full_filename):
        if ext.upper() == ".STDF_2DID":
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
    msg = str(i) + ' ] s3. 2did stdf_2DID file read start !! : ' + '\n' + " " + move_dest + filename
    print(msg)
    writeLog(msg)
    mail_text = mail_text + msg + '\n'
    try:
        
        slotid = ""        
        sDev = ""        
        sTester_id = ""
        sTest_prog = ""
        sOper_id = ""
        sOper_desc = ""
        sRetestseq = ""
        sStart_time = ""
        sEnd_time = " "
        sX = ""
        sY = ""
        sSoft_bin = ""
        sHard_bin = ""
        unit = ""
        snor_lotid = ""
        sWaferno = ""
        sPass_flag = ""
        sFuse = ""
        sPart_id = ""
        #########################
        #temp = filename.upper()
        temp = filename
        temp = temp.upper().replace(".STDF_2DID", "")
        temp = temp.split('_')
        # 1. lotid
        slotid = temp[0] 
        slotid = slotid.upper()
        # 2. intel oper
        #sOper_desc = temp[1]
        sInt_Oper_id = temp[1]
        # 3. intel retest code
        sInt_retest = temp[2]
        # 4. subcon retest or X
        # 5. intel lotid
        sInt_lot = temp[4]
        # 6. part id
        sPart_id = temp[5]
        # 7. MMID - change device
        sDev = temp[6]
        # 8. tester id
        sTester_id = temp[7]
        sTester_id = sTester_id.upper()
        # 9. date
        sStart_time = temp[8]
        
        
        sCust = "INT"
        #sTest_prog = temp[5] + '.' + temp[6]
        #sTester_id = temp[7]
        #sTester_id = sTester_id.upper()
        
        #sOper_desc = temp[10]
        #sStart_time = temp[9]
        
        tmp_retest = sInt_retest[0]
        sRetestseq = str(int(tmp_retest)-1)
        
        ##########################
        line_temp = ''
        line_cnt = 0
        with open(full_filename, 'r', encoding='UTF8') as unit_file:

            lines = unit_file.readlines()
            for line in lines:             
                
                line_cnt = line_cnt + 1
                line = line.upper()
                
                if not line:
                    break
                # S206JN30	6124	1	S206JN3019947	S206JN30_02120512_021963	100	1	P	4705	77405	1B
                #################################
                
                line_temp = line.split("\t")
                line_item_sort = []
                
                for line_data in line_temp :
                    if line_data.strip() == '' :
                        line_data = 'N/A'        
                    if line_data.strip() != '' :
                        line_item_sort.append(line_data.strip())    

                ################################        
                sseq = line_cnt
                unit = line_item_sort[3].strip()

                ######################
                #  error die 구분해서 count 해야함
                if unit == "ERROR" or unit == "N/A" or unit == "NA" or unit.find('BARCODE') > -1 or unit.find('N/A') > -1 \
                    or unit.find('NOT_') > -1 : 
                    unit = unit + "_" + str(sseq) + "_" + sInt_retest
                
                x_y = unit
                ######################################
                # 신규좌표만 count - retest 는 무시하고 pass                
                # unit 별로 data 저장
                unit_dic[x_y] = line

                ##################################
        #################
        snor_lotid , sLead, sPkg, sOper_id, sOper_desc = get_leadid(slotid, sInt_Oper_id)
        sTemper = get_temp(slotid, sOper_id)
        if (sTemper != "H") and (sTemper != "R") and (sTemper != "C") :
            msg = str(i) + ' ] Temperature Error !! ' + '\n' + " " + slotid + " / " + sOper_id
            writeLog(msg)
            print(msg)
            mail_send_flag = True
            mail_text = mail_text + msg + '\n'
            mail_flag = False
            
        #snor_lotid = get_norlot(slotid)
        #print(ptr_flag)
        ###############################
        # first yield용 - good , reject count
        line_cnt = 0
        for k in unit_dic.keys():
            
            #line_temp = unit_dic.get(k)
            line_cnt = line_cnt + 1
            ##################
            line = unit_dic.get(k)

            #################################
            line_temp = ''            
            ####################        
            line_temp = line.split("\t")
            line_item_sort = []
                
            for line_data in line_temp :
                if line_data.strip() == '' :
                        line_data = 'N/A'   
                if line_data.strip() != '' :
                    line_item_sort.append(line_data.strip())            
            ####################              
            #slot = line_item_sort[0].strip()
            #soper = line_item_sort[1].strip()            
            sSite = line_item_sort[2].strip()   
            sunit = line_item_sort[3].strip()
            sfuse = line_item_sort[4].strip()   
            sSoft_bin = line_item_sort[5].strip()
            sHard_bin = line_item_sort[6].strip()               
            #####################################            
            sPass_flag = line_item_sort[7].strip()
            #######################################
            # 2022/07/04 김홍수선임 INT 2DID UNIT FAIL 아니면서 HBIN 1 이면 PASS 로 인식하도록 수정
            if sunit == "ERROR" or sunit == "N/A" or sunit == "NA" or \
               sunit.find('BARCODE') > -1  or sunit.find('N/A') > -1 or sunit.find('NOT_') > -1 : 
                pass
            else :
                if (sHard_bin == "1" and sfuse == "N/A") :
                    sPass_flag = "P"            
            ###############################
            
            ###############################
            sTest_time = line_item_sort[8].strip()
            sUnit_seq  = line_item_sort[9].strip()
            #sint_retest = line_item_sort[9].strip()
            #sRetestseq
            ######################
            if sPass_flag == "GOOD" or sPass_flag == "P" :
                bin_good = bin_good + 1
            #elif sPass_flag == "BAD":
            else:
                bin_fail = bin_fail + 1   
            ######################
            #  error die 구분해서 count 해야함
            if sunit == "ERROR" or sunit == "N/A" or sunit == "NA" or sunit.find('BARCODE') > -1  or sunit.find('N/A') > -1 \
                    or sunit.find('NOT_') > -1 : 
                unit_fail = unit_fail + 1
                #unit = unit + "_" + str(sRetestseq) + "_"  + str(sseq)
            else  :
                unit_good = unit_good + 1   
        ######################        
        tot_qty = bin_good + bin_fail
        bin_yield = (bin_good / tot_qty) * 100
        unit_yield = (unit_good / tot_qty) * 100

        cfilename = filename
        msg = str(i) + ' ] s3. file parsing complete !! ' + '\n' + " " + cfilename
        print(msg)
        mail_text = mail_text + msg + '\n'
        writeLog(msg)

    except:
        #tsmc_file.close()
        msg = str(i) + ' ] s3. file parsing fail exception !! ' + '\n' + " " + move_dest + filename
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
    try:

        msg = str(i) + ' ] s4. TPAS_2DID_INF start :  ' + '\n' + " " + full_filename
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        print(msg)
        ################################
         
        conn_tpas1 = cx_Oracle.connect('tpasdb')
        cur_tpas1 = conn_tpas1.cursor()
        #####################################
        #동일파일명은 wafer_inf ,wafer_dat 삭제
        sql = "SELECT * FROM TPAS_2DID_INF "
        sql = sql + "WHERE FILENAME = '" + filename + "' "
        cur_tpas1.execute(sql)
        tpas_row = cur_tpas1.fetchone()
        if tpas_row == None:
            pass
        else:
            msg = str(i) + ' ] s4. TPAS_2DID_INF delete :  ' + '\n' + " " + full_filename
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
            print(msg)
            
            sql = "DELETE FROM TPAS_2DID_INF "
            sql = sql + "WHERE FILENAME = '" + filename + "' "
            cur_tpas1.execute(sql)
            conn_tpas1.commit()
            ###################################
            sql = "DELETE FROM TPAS_2DID_DAT "
            sql = sql + "WHERE FILENAME = '" + filename + "' "
            cur_tpas1.execute(sql)
            conn_tpas1.commit()
        ########################        
        cur_tpas1.close()
        
        conn_tpas1 = cx_Oracle.connect('tpaddb')
        cur_tpas1 = conn_tpas1.cursor()
        # TPAS_WAFER_INF
        msg = str(i) + ' ] s4. TPAS_2DID_INF insert :  ' + '\n' + " " + full_filename
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        print(msg)

        sql = "INSERT INTO TPAS_2DID_INF (LOT_ID, CUSTOMER, PKG_ID, LEAD_ID, DEVICE, TESTER_ID , TESTPROG , "
        #                                     1  ,   2    ,   3   ,    4   ,   5   ,    6   
        sql = sql + " USERPROC, FILENAME, START_TIME, END_TIME, RETEST_SEQ, TOT_QTY, "
        #                7    ,     8    ,     9    ,    10   ,    11     ,    12   ,  13
        sql = sql + " BIN_GOOD_QTY, UNIT_GOOD_QTY , BIN_FAIL_QTY, UNIT_FAIL_QTY, BIN_YIELD, UNIT_YIELD,  "
        #              14         ,     15      ,      16      ,     17    ,     18       ,     19
        sql = sql + " NORMAL_LOTID , READFLAG, OPER,SBL_FLAG, NOTCH_DIRECTION, TRANS_TIME, PART_ID, INT_RETEST, "
        sql = sql + " OPER_DESC, INT_LOT_ID , TEMPER ) "
        #                     20   ,  21  ,   22  ,      23        ,   24      ,  25     ,   26
        sql = sql + "VALUES ( "
        sql = sql + "'" + slotid + "' , "  # 1. lotid
        #sql = sql + "'RMB' , "  # 2. customer
        sql = sql + "'" + sCust + "' , "  # 2. customer
        sql = sql + "'" + sPkg + "' , "  # 3. pkg
        sql = sql + "'" + str(sLead)  + "' , "  # 4. lead
        sql = sql + "'" + sDev  + "' , "  # 5. device
        sql = sql + "'" + sTester_id  + "' , "  # 6. tester id
        sql = sql + "' ' , "  # 
        sql = sql + "'" + sInt_Oper_id  + "' , "  # 8. INT OPER  USERPROC
        sql = sql + "'" + filename  + "' , "  # 9. filename
        sql = sql + "'" + str(sStart_time)  + "' , "  # 10.START_TIME
        sql = sql + "'" + str(sEnd_time)  + "' , "  # 11, end time
        sql = sql + "'" + str(sRetestseq)  + "' , "  # 12. RETEST_SEQ
        sql = sql + "'" + str(tot_qty)  + "' , "  # 13. tot qty
        sql = sql + "'" + str(bin_good)  + "' , "  # 14 BIN_GOOD_QTY
        sql = sql + "'" + str(unit_good)  + "' , "  # 15 UNIT_GOOD_QTY
        sql = sql + "'" + str(bin_fail) + "' , "  # 16. BIN_FAIL_QTY
        sql = sql + "'" + str(unit_fail) + "' , "  # 17. UNIT_FAIL_QTY
        sql = sql + "'" + str(round(bin_yield,2)) + "' , "  # 18. BIN_YIELD
        sql = sql + "'" + str(round(unit_yield,2)) + "' , "  # 19. UNIT_YIELD
        sql = sql + "'" + snor_lotid + "' , "  # 20. normal_lotid
        sql = sql + "'N' , "  # 21. READFLAG
        sql = sql + "'" + str(sOper_id) + "' , "  # 22. OPER
        sql = sql + "'N' , "  # 23. SBL_FLAG 
        sql = sql + "'NA' , "  # 24. NOTCH_DIRECTION
        sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') , "  # 25. TRANS_TIME 
        sql = sql + "'" + sPart_id + "' ,  "    # PARTID
        sql = sql + "'" + sInt_retest + "' , "    # int retest   
        sql = sql + "'" + sOper_desc + "' , "    #  SCK OPER DESC
        sql = sql + "'" + sInt_lot + "' , "
        sql = sql + "'" + sTemper + "' "
        sql = sql + ") "
        
        cur_tpas1.execute(sql)
        conn_tpas1.commit()
        conn_tpas1.close()

        msg = str(i) + ' ] s4. TPAS_2DID_INF Insert complete !! ' + '\n' + " " + full_filename

        print(msg)
        writeLog(msg + '\n' + sql)
        mail_text = mail_text + msg + '\n'

         
        conn_tpas1 = cx_Oracle.connect('tpasdb')
        cur_tpas1 = conn_tpas1.cursor()
        data = []
        #die_test_time =  int(org_time)*1000
        for k in unit_dic.keys():
            line = unit_dic.get(k)
            
            #################################
            line_temp = ''
            #unit_temp = line[7:22].strip()
            #if unit_temp.strip() == '':
            #    line[7:9].replace("  " , "NA")
            ########################        
            line_temp = line.split("\t")
            line_item_sort = []
                
            for line_data in line_temp :
                if line_data.strip() == '' :
                    line_data = 'N/A'   
                if line_data.strip() != '' :
                    line_item_sort.append(line_data.strip())    
            #if unit_temp.strip() == '':
            #        line_item_sort.insert(1, "NA")
            ############################        
            #sseq = line[0:7].strip()
            #unit = line[7:22].strip()
            #sseq = line_item_sort[0].strip()
            #unit = line_item_sort[3].strip()
            unit = k

            ####
            #if unit == "ERROR" or unit == "N/A" or unit == "NA" or unit.find('BARCODE') > -1  \
            #        or unit.find('NOT_') > -1 :  
            #    unit = k + "_" + str(sRetestseq)
            ####
            
            sX = 0
            sY = 0
            sWaferno = " "
            
            sSite = line_item_sort[2].strip()   
            #sunit = line_item_sort[3].strip()
            sunit = unit
            sfuse = line_item_sort[4].strip()   
            sSoft_bin = line_item_sort[5].strip()
            sHard_bin = line_item_sort[6].strip()               
            sPass_flag = line_item_sort[7].strip()
            #######################################
            # 2022/07/04 김홍수선임 INT 2DID UNIT FAIL 아니면서 HBIN 1 이면 PASS 로 인식하도록 수정
            if sunit.strip() == "ERROR" or sunit.strip() == "N/A" or sunit.strip() == "NA" \
                or sunit.strip().find('BARCODE') > -1  or sunit.strip().find('N/A') > -1 or sunit.strip().find('NOT_') > -1 : 
                pass
            else :
                if (sHard_bin == "1" and sfuse == "N/A") :
                    sPass_flag = "P"            
            ###############################
            
            sTest_time = line_item_sort[8].strip()
            sUnit_seq  = line_item_sort[9].strip()
            
            ##########################
            now = datetime.datetime.now()
            nowtime = now.strftime('%Y%m%d%H%M%S')
            #################################
            # list , tuple use
            add_data = (slotid,sunit, str(sX),str(sY), str(sWaferno), \
                        str(sSoft_bin), str(sHard_bin), sPass_flag, sInt_Oper_id, str(sOper_id) , \
                        sStart_time,sEnd_time , 'NA' , str(nowtime), filename, str(sRetestseq),sfuse,sInt_retest, sOper_desc, str(sSite), str(sUnit_seq), str(sTest_time))
            data.append(add_data)
            ##################

        msg = str(i) + ' ] s4. TPAS_2DID_DAT start :  ' + '\n' + " " + full_filename
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        print(msg)

        if len(data) > 0:        
            sql = "INSERT INTO TPAS_2DID_DAT (LOT_ID,UNIT_2DID,X_POS, Y_POS, WAFER_NO, "
            #                                     1  ,   2      ,   3 ,   4 ,   5  ,   
            sql = sql + " SBIN,HBIN,PASSFAIL,USERPROC,OPER,START_TIME, "
            #               6    7 ,  8 ,   9    ,     10     , 11 
            sql = sql + " END_TIME,NOTCH_DIRECTION,TRANS_TIME,FILENAME,RETEST_SEQ,FUSE,INT_RETEST,OPER_DESC,SITE_ID,UNIT_SEQ,TEST_TIME ) "
            #              12    ,       13      ,   14         ,   15     ,   16  ,   17      ,  18, 19       ,  20      , 21     ,   22    
            sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, "
            sql = sql + "  :11, :12, :13, :14, :15, :16, :17, :18, :19, :20 , :21 , :22 ) "
            cur_tpas1.executemany(sql,data)
            conn_tpas1.commit()
            conn_tpas1.close() 
            msg = str(i) + ' ] s5. TPAS_2DID_DAT Insert complete !! ' + '\n' + " " + full_filename
            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
        ############
        data = []        
        unit_dic = {}
        unit_dic.clear()
        # ==============>>>> tpas sum table insert  <<<<=====================
        
        msg = str(i) + ' ] s5. TPAS_2DID_SUMDAT TABLE Insert START !! ' + '\n' + " " + filename
        print(msg)
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        
         
        conn_tpas1 = cx_Oracle.connect('tpasdb')
        cur_tpas1 = conn_tpas1.cursor()
        #####################################
        # tot qty 를 normal test 파일의 tot qty 로 한다.
        nor_test_qty = 0

        sql = "SELECT COUNT(DISTINCT UNIT_2DID) FROM TPAS_2DID_DAT "    
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND USERPROC = '" + sInt_Oper_id + "' "
        sql = sql + "AND  RETEST_SEQ = 0 "
        cur_tpas1.execute(sql)
        tpas_row = cur_tpas1.fetchone()
        if tpas_row == None:
            pass
        else:            
            nor_test_qty = tpas_row[0] 
            if nor_test_qty == None :
                nor_test_qty = 0
                               
        #########################################
        sql = "SELECT LOT_ID FROM TPAS_2DIDSUM_INF "    
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND USERPROC = '" + sInt_Oper_id + "' "
        cur_tpas1.execute(sql)
        tpas_row = cur_tpas1.fetchone()
        if tpas_row == None:
            pass
        else:
            sql = "DELETE FROM TPAS_2DIDSUM_INF "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND USERPROC = '" + sInt_Oper_id + "' "
            cur_tpas1.execute(sql)
            conn_tpas1.commit()

        conn_tpas1.close()
        
        conn_tpas1 = cx_Oracle.connect('tpasdb')
        cur_tpas1 = conn_tpas1.cursor()

        sql = "SELECT LOT_ID FROM TPAS_2DIDSUM_DAT "
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND USERPROC = '" + sInt_Oper_id + "' "
        sql = sql + "AND ROWNUM < 2 "

        cur_tpas1.execute(sql)
        tpas_row = cur_tpas1.fetchone()
        if tpas_row == None:
            pass
        else:    
            sql = "DELETE FROM TPAS_2DIDSUM_DAT "
            sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
            sql = sql + "AND USERPROC = '" + sInt_Oper_id + "' "
            cur_tpas1.execute(sql)
            conn_tpas1.commit()
        ###################################        
        #####################################            
        # LOT_ID, WAFER_ID,OPER 로 TPAS_WAFERSUM_DAT 조회하여 삭제
        msg = str(i) + ' ] s4. TPAS_2DIDSUM delete :  ' + '\n' + " " + full_filename
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        print(msg)

        #LOT_ID, WAFER_ID, OPER로  TPAS_WAFERSUM_INF 조회하여  삭제
        
        ########################
        conn_tpas1.close()
         
        conn_tpas1 = cx_Oracle.connect('tpasdb')
        cur_tpas1 = conn_tpas1.cursor()
        #==============>>>>> TPAS_WAFERSUM_DATA INSERT START
        # ROW DATA SEARCH --> SUM TABLE INSERT
        # lot,wafer,oper data all sum
        data = []
        unit_dic = {}
        unit_dic.clear()
        ###############    
        unit_good = 0
        unit_fail = 0
        ###############
        bin_good = 0
        bin_fail = 0
        ###############
        tot_qty = 0    
        ###############
        unit_yield = 0
        bin_yield = 0
        ###############
        tmp_line = ""
        #FOR TPAS_2DIDSUM_DAT 
        #sql = "SELECT LOT_ID,UNIT_2DID ,X_POS,Y_POS,WAFER_NO, "
        #sql = "SELECT LOT_ID,UNIT_2DID,SITE_ID, FUSE "
        sql = "SELECT LOT_ID,UNIT_2DID ,X_POS,Y_POS,WAFER_NO, "
        #                0  ,   1     ,  2    ,  3 , 4
        sql = sql + " SBIN,HBIN,PASSFAIL,USERPROC,OPER,START_TIME, "
        #              5  , 6  ,  7     ,  8     , 9  , 10 
        sql = sql + " END_TIME,NOTCH_DIRECTION,TRANS_TIME,FILENAME,RETEST_SEQ, "
        #              11     ,   12          ,  13    ,   14    ,   15 
        sql = sql + " FUSE, INT_RETEST, OPER_DESC, SITE_ID, UNIT_SEQ, TEST_TIME "
        #               16,   17     ,    18     ,   19   ,   20  ,     21
        sql = sql + " FROM TPAS_2DID_DAT "
        sql = sql + "WHERE LOT_ID = '" + slotid + "' "            
        sql = sql + "AND USERPROC = '" + sInt_Oper_id + "' "
        sql = sql + "ORDER BY LOT_ID, USERPROC , RETEST_SEQ, INT_RETEST, START_TIME, TRANS_TIME  "
        cur_tpas1.execute(sql)
        tpas_row = cur_tpas1.fetchall()
        if tpas_row == None:
            pass
        else:
            #### ==>> row data 찾아서 sum 에 insert
            for row in tpas_row:
                
                unit = row[1]                
                x_y =unit                
                if x_y in unit_dic :
                    del unit_dic[x_y]
                unit_dic[x_y] = row
            #########################
            # 최종 data 정리하여 TPAS_2DIDSUM_DAT 저장준비
            for k in unit_dic.keys():
                
                line_temp = unit_dic.get(k)
                data.append(line_temp)
                ##################                
                unit = line_temp[1].strip()                                
                sPass_flag = line_temp[7].strip()
                sFuse = line_temp[16].strip()
                #######################################
                # 2022/07/04 김홍수선임 INT 2DID UNIT FAIL 아니면서 HBIN 1 이면 PASS 로 인식하도록 수정
                if sunit.strip() == "ERROR" or sunit.strip() == "N/A" or sunit.strip() == "NA" \
                    or sunit.strip().find('BARCODE') > -1  or sunit.strip().find('N/A') > -1 or sunit.strip().find('NOT_') > -1 : 
                    pass
                else :
                    if (sHard_bin == "1" and sfuse == "N/A") :
                        sPass_flag = "P"            
                ###############################
                ######################
                if sPass_flag == "GOOD" or sPass_flag == "P" :
                    bin_good = bin_good + 1
                #elif sPass_flag == "BAD":
                else:
                    bin_fail = bin_fail + 1   
                ######################
                # error die 구분해서 count 해야함
                #if unit == "ERROR" or unit == "N/A" or unit == "NA" :
                if unit.find("ERROR_") > -1 or unit.find("N/A_") > -1 or unit.find("NA_") > -1 or \
                   unit.find('BARCODE') > -1 or unit.find('NOT_') > -1 :
                    unit_fail = unit_fail + 1
                    
                else  :
                    unit_good = unit_good + 1   

            ######################
            # normal test  파일의 tot_qty 을 사용
            if nor_test_qty > 0 : 
                tot_qty = nor_test_qty
            else :    
                tot_qty = bin_good + bin_fail
            ###########################    
            bin_yield = (bin_good / tot_qty) * 100
            unit_yield = (unit_good / tot_qty) * 100
            #############
            unit_dic = {}
            unit_dic.clear()
            msg = str(i) + ' ] s4. TPAS_2DIDSUM_DAT insert start :  ' + '\n' + " " + full_filename
            writeLog(msg)
            mail_text = mail_text + msg + '\n'
            print(msg)

            conn_tpas1.close()
             
            conn_tpas1 = cx_Oracle.connect('tpasdb')
            cur_tpas1 = conn_tpas1.cursor()
        
            ########################
            if len(data) > 0:
                sql = "INSERT INTO TPAS_2DIDSUM_DAT (LOT_ID, UNIT_2DID, X_POS, Y_POS, WAFER_NO, "
                #                                     1  ,   2      ,   3 ,   4 ,   5 
                sql = sql + " SBIN,HBIN,PASSFAIL,USERPROC,OPER,START_TIME, "
                #              6  ,  7 ,  8     ,   9    , 10 ,   11 
                sql = sql + " END_TIME,NOTCH_DIRECTION,TRANS_TIME,FILENAME,RETEST_SEQ , "                
                #              12     ,  13           ,   14     ,   15   ,   16  
                sql = sql + " FUSE, INT_RETEST, OPER_DESC, SITE_ID, UNIT_SEQ, TEST_TIME) "
                #              17      17           19       20       21        22
                sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, "
                sql = sql + "  :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22 ) "
                cur_tpas1.executemany(sql,data)
                conn_tpas1.commit()
                                
                msg = str(i) + ' ] s5. TPAS_2DIDSUM_DAT Insert complete !! ' + '\n' + " " + full_filename

                print(msg)
                writeLog(msg)
                mail_text = mail_text + msg + '\n'
            ###########################
            msg = str(i) + ' ] s5. TPAS_2DIDSUM_INF TABLE Insert START !! ' + '\n' + " " + filename
            print(msg)
            writeLog(msg)
            mail_text = mail_text + msg + '\n'

            data = []
            unit_dic = {}
            unit_dic.clear()
            
            sSBL_flag = "Y"
            
            conn_tpas1.close()
             
            conn_tpas1 = cx_Oracle.connect('tpasdb')
            cur_tpas1 = conn_tpas1.cursor()
            
            # TPAS_WAFER_INF
            sql = "INSERT INTO TPAS_2DIDSUM_INF (LOT_ID, CUSTOMER, PKG_ID, LEAD_ID, DEVICE, TESTER_ID , "
            #                                     1  ,   2    ,   3   ,    4   ,   5   ,    6   
            sql = sql + " TESTPROG , USERPROC, FILENAME, START_TIME, END_TIME,RETEST_SEQ, TOT_QTY, "
            #                7    ,     8    ,     9    ,    10   ,    11     ,    12   ,  13
            sql = sql + " BIN_GOOD_QTY, UNIT_GOOD_QTY , BIN_FAIL_QTY, UNIT_FAIL_QTY, BIN_YIELD, UNIT_YIELD,  "
            #              14         ,     15      ,      16      ,     17    ,     18       ,     19
            sql = sql + " NORMAL_LOTID , READFLAG, OPER,SBL_FLAG, NOTCH_DIRECTION, TRANS_TIME, PART_ID , "
            #                     20   ,  21     , 22  ,  23    ,   24            ,  25      ,   26
            sql = sql + " INT_RETEST, OPER_DESC, INT_LOT_ID , TEMPER) "
            
            sql = sql + "VALUES ( "
            sql = sql + "'" + slotid + "' , "  # 1. lotid
            #sql = sql + "'RMB' , "  # 2. customer
            sql = sql + "'" + sCust + "' , "  # 2. customer
            sql = sql + "'" + sPkg + "' , "  # 3. pkg
            sql = sql + "'" + str(sLead)  + "' , "  # 4. lead
            sql = sql + "'" + sDev  + "' , "  # 5. device
            sql = sql + "'" + sTester_id  + "' , "  # 6. tester id
            sql = sql + "'" + sTest_prog  + "' , "  # 7. testprog
            sql = sql + "'" + sInt_Oper_id  + "' , "  # 8. USERPROC
            sql = sql + "'" + filename  + "' , "  # 9. filename
            sql = sql + "'" + str(sStart_time)  + "' , "  # 10.START_TIME
            sql = sql + "'" + str(sEnd_time)  + "' , "  # 11, end time
            sql = sql + "'" + str(sRetestseq)  + "' , "  # 12. RETEST_SEQ
            sql = sql + "'" + str(tot_qty)  + "' , "  # 13. tot qty
            sql = sql + "'" + str(bin_good)  + "' , "  # 14 BIN_GOOD_QTY
            sql = sql + "'" + str(unit_good)  + "' , "  # 15 UNIT_GOOD_QTY
            sql = sql + "'" + str(bin_fail) + "' , "  # 16. BIN_FAIL_QTY
            sql = sql + "'" + str(unit_fail) + "' , "  # 17. UNIT_FAIL_QTY
            sql = sql + "'" + str(round(bin_yield,2)) + "' , "  # 18. BIN_YIELD
            sql = sql + "'" + str(round(unit_yield,2)) + "' , "  # 19. UNIT_YIELD
            sql = sql + "'" + snor_lotid + "' , "  # 20. normal_lotid
            sql = sql + "'Y' , "  # 21. READFLAG
            sql = sql + "'" + str(sOper_id) + "' , "  # 22. OPER
            sql = sql + "'" + sSBL_flag + "' , "  # 23. SBL_FLAG 
            sql = sql + "' ' , "  # 24. NOTCH_DIRECTION
            sql = sql + " TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') ,  "  # 25. TRANS_TIME            
            sql = sql + "'" + sPart_id + "' , "    # PARTID
            sql = sql + "'" + sInt_retest + "' ,  "    # int retest   
            sql = sql + "'" + sOper_desc + "' , "    #  SCK OPER DESC
            sql = sql + "'" + sInt_lot + "' , "
            sql = sql + "'" + sTemper + "'  "            
            sql = sql + ") "
            cur_tpas1.execute(sql)
            conn_tpas1.commit()
            conn_tpas1.close()

            msg = str(i) + ' ] s6. TPAS_2DIDSUM_INF Insert complete !! ' + '\n' + " " + filename

            print(msg)
            writeLog(msg + '\n' + sql)
            mail_text = mail_text + msg + '\n'

            ###################################
            # success filename save
            org_stdf_ftp_list.append(filename)
            os.remove(full_filename)
            ########################################
            fuse_error_flag,sdup_msg, fuse_mail_flag, fuse_mail_desc = chk_val(filename, slotid, str(sOper_id))
            
            if (fuse_error_flag == True) or (fuse_mail_flag == True):
                msg = str(i) + ' Int fuse check error !!! ]  <==================== ' + slotid + " / " + str(sOper_id) + '\n' + " " + filename + '\n' + fuse_mail_desc
                
                writeLog(msg)
                print(msg)
                mail_send_flag = True
                mail_text = mail_text + msg + '\n'
                mail_flag = False
                send_mail(msg + "\n End message !!")
            
    except:
        #tsmc_file.close()
        msg = str(i) + ' DB error !!! ] s6. tpas DB exception Error !! <================ !!!!!!!!!!!!!! ' + '\n' + " " + filename
        writeLog(msg)
        print(msg)
        mail_send_flag = True
        mail_text = mail_text + msg + '\n'
        mail_flag = False
        continue

##########################################
# 9. final step start
# 9-1 base on complete map file, delete local file ,
# 9-2 move ftp file to backup folder
if len(org_stdf_ftp_list) > 0 :

    try:
        #############################
        
        ftp = ftplib.FTP(new_ftp_ip)
        ftp.login(new_ftp_id, new_ftp_pw)
        ftp.cwd(org_stdf_ftp)
        backup_org_path = ftp.pwd()
        backup_org_path = backup_org_path + "/"
        files = ftp.nlst()
        ########################
        msg = str(i) + ' ] s7. ftp file backup start !!  '
        print(msg)
        writeLog(msg)
        mail_text = mail_text + msg + '\n' + '\n'

        time.sleep(2)
        i = 0
        #####################
        # target file name : save in org_stdf_ftp_list
        for filename in files:

            stdf_filename = filename.split("/")[-1]
            
            if (stdf_filename.upper().find('.STDF_2DID') > -1):
                #l_file : .stdf  server file : .stdf or .stdf.gz
                for l_file in org_stdf_ftp_list:
                    if (stdf_filename.upper().find(l_file.upper()) > -1):
                        
                        temp = stdf_filename.upper()
                        temp = temp.split('_')                    
                        #sfile_lot = temp[0] + '.' + temp[1]
                        sfile_lot = temp[0] 
                        # 1.backup folder
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
                        backup_target_path = backup_org_path + "BACKUP/"
                        success = ftp.rename(backup_org_path + stdf_filename , \
                                            backup_target_path + sfile_lot + '/'+ stdf_filename)

                        time.sleep(2)

                        i = i + 1

                        if success.find('success') > -1:
                            print('ftp backup success !!')
                        ftp.cwd('../')
                        ftp.cwd('../')
                        print(ftp.pwd())

                        msg = str(i) + ' ] s7. ftp file backup progress !!  ' + '\n' + " " + stdf_filename

                        print(msg)
                        writeLog(msg)
                        mail_text = mail_text + msg + '\n'

        #################
        msg = str(i) + ' ] s7. ftp file backup complete !!  '
        print(msg)
        writeLog(msg)
        mail_text = mail_text + msg + '\n' + '\n'
        ##################
    except:
        #writeLog('3. ftp / ftp연결실패 : 예외사항 ' + ftp_ip)
        msg = str(i) + ' ] s7. ftp file backup fail :  exception  '

        mail_text = mail_text + msg + '\n'
        mail_flag = False
        print(msg + new_ftp_ip)
        writeLog(msg)

    ftp.close()
##########################
msg = str(i) + ' ==> int 2did insert end !! '
print(msg)
mail_text = mail_text + '\n' + msg + '\n'

if (mail_send_flag == False) and (mail_flag == True):
    pass
else:
    # mail send when file exist only
    last_mail_flag = True
    send_mail(mail_text)

sys.exit(0)
