
import os
import shutil
from pathlib import Path
import time

import datetime
from datetime import date, timedelta

import cx_Oracle
import csv

import sys
#############
import pandas as pd
from io import StringIO
#################################
# move 할 폴더생성
# D:\QCT_Datalog
###################################

today = datetime.datetime.now().strftime('%Y%m%d')
tmp_day = date.today() - timedelta(1)
yesterday = tmp_day.strftime('%Y%m%d')
#######################
# 폴더 지정 및 변경
#######################
# 폴더 지정 및 변경
source_dir = "C:/temp/SIP_PARA/"
local_ftp = source_dir
###################################
org_csv = source_dir + "ORIGIN_CSV/"
complete_csv = source_dir + "COMPLETE_CSV/"
####################################
# 압축하고 압축폴더에서 바로 ftp 로 전송
#from_ftp = result_dest
log_dest = source_dir + "log/"

# send_mail('mail test' )
p = Path(source_dir)  # 로컬 다운받은 폴더
p.mkdir(exist_ok=True)

p = Path(org_csv)  # 로컬 다운받은 폴더
p.mkdir(exist_ok=True)
# 로그위치
p = Path(log_dest)
p.mkdir(exist_ok=True)
# tsmc map file 생성후 완료된 맵파일폴더
p = Path(complete_csv)
p.mkdir(exist_ok=True)
####################################

new_ftp_ip = ''
new_ftp_id = ''
new_ftp_pw = ''
#######################

#chk_hour = 24*15
chk_hour = 0.25
mail_flag = True
mail_send_flag = False
mail_text = "eagle parametric report " + '\n' + '\n'

global dic_target_para



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

def get_userproc(soper):
    conn_mes = cx_Oracle.connect('mesdb')
    cur_mes = conn_mes.cursor()
    sql = "SELECT DATA1 FROM UPTDAT "
    sql = sql + "WHERE FACTORY = 'TEST' "
    sql = sql + "AND TABLE_NAME = 'QUL_OPER' "
    sql = sql + "AND KEY1 = '" + str(soper) + "' "

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    for row in rows:  # 202029
        userproc = row[0]
    conn_mes.close()
    return userproc;

###################################
def get_leadid(sLot, sOper_desc):
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

    soper = ""
    sql = "SELECT KEY1 FROM UPTDAT "
    sql = sql + "WHERE FACTORY = 'TEST' "
    sql = sql + "AND TABLE_NAME = 'QUL_OPER' "
    sql = sql + "AND DATA1 = '" + sOper_desc.strip().upper() + "' "

    cur_mes.execute(sql)
    rows = cur_mes.fetchall()
    for row in rows:  # 202029
        soper = row[0]
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

    sql = sql + "AND CREATE_CMF2 = 'RMB' "
    sql = sql + "AND OPER = '" +  soper + "' "
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

    return meslot , lead_id,pkg_id , soper ;
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
    
###################################
def get_para_name(sproject):
    
    global dic_target_para
    
    dic_target_para = {}
    dic_target_para.clear()
    
    sip_conn1 = cx_Oracle.connect('sipdb')
    sip_cur1 = sip_conn1.cursor()

    sql = "SELECT PARA_NAME, UPPER_LIMIT, LOWER_LIMIT FROM SIP_PARA_LIMIT "
    sql = sql + " WHERE PROJECT = '" + sproject + "' "
    
    sip_cur1.execute(sql)
    rows = sip_cur1.fetchall()

    if sip_cur1.rowcount > 0 :
        for row in rows :
            spara_name = row[0]
            supper = row[1]
            slower = row[2]            
            dic_target_para[spara_name] =  spara_name + '~' + supper + '~' + slower
    
    sip_conn1.close()

#############################################
project_list = []
gubun_list = []

i = 0
#######################
# 3. file read start
time.sleep(3)
#x_y_dic = {}
unit_dic = {}

i = 0
tot_file_cnt = 0

msg =  "sip para data analysis datacollection start"

print(msg)
writeLog(msg)

sinput_pass_fail = ""
while sinput_pass_fail.upper() != 'PASS' and  sinput_pass_fail.upper != 'ALL' and  sinput_pass_fail.upper != 'FAIL' and sinput_pass_fail.upper != 'C' :
    msg = "Please input 'PASS' or 'FAIL' or 'ALL'   or C (cancel) : "
    sinput_pass_fail = input(msg)
    sinput_pass_fail = sinput_pass_fail.upper()
    if sinput_pass_fail == 'PASS' or  sinput_pass_fail == 'ALL' or  sinput_pass_fail == 'FAIL' :
        break
    if sinput_pass_fail == 'C' :
        sys.exit(0)

sip_conn = cx_Oracle.connect('sipdb')
sip_cur = sip_conn.cursor()

sql = "DELETE FROM SIP_PARA_DAT "            
sip_cur.execute(sql)
sip_conn.commit()
sql = "DELETE FROM SIP_PARASUM_DAT "            
sip_cur.execute(sql)
sip_conn.commit()
           

for (path, dir, files) in os.walk(org_csv):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        path = os.path.abspath(path)
        full_filename = os.path.join(path, filename)
        ####################
        # csv 파일 찾음, 하위폴더까지
        # 어제와 오늘로 조회해서 year, ww 조회 ==> y2020ww28

        if (ext == '.csv') :
            print("csv file name : " + filename)
            #############
            # 로그 남기기
            writeLog(filename + ' : 파일선택')
            #############################33
            ## 해당 파일의 db data 는 일괄삭제한다.
            '''
            sql = "SELECT FILENAME FROM SIP_PARA_DAT "
            sql = sql + "WHERE FILENAME = '" + filename + "'"
            sip_cur.execute(sql)
            row = sip_cur.fetchall()

            if sip_cur.rowcount > 0 :

                #print(filename +  " ] Delete old data")
                sql = "DELETE FROM SIP_PARA_DAT "
                sql = sql + "WHERE FILENAME = '" + filename + "'"
                sip_cur.execute(sql)
                sip_conn.commit()
                #print(filename + " ] Delete old data complete ")
            '''
            ########################
            sgubun = path.split('\\')[-1]
            sgubun = sgubun.upper()
            sproject = path.split('\\')[-2]
            sproject = sproject.upper() 
            
            get_para_name(sproject)
                       
            ###########################
            #with open(full_filename, 'r') as f:
            with open(full_filename, 'r' ) as f:
                
                ##################################
                # 로그 남기기
                writeLog(filename + ' : 파싱시작')
                #############################
                sVer = next(f)  # 첫번째라인 version
                
                stemp = f.read()
                data = stemp.replace('\x00','?')
                csv_read = csv.DictReader(StringIO(data))
                
                #csv_read = csv.DictReader(f)
                header = csv_read
                
                data = []
                dic_para = {}
                dic_para.clear()
                line_cnt = 0
                try :
                    for line in csv_read:
                    
                    # 0: Package , 1:Start Date  2: Start Time  3:End Date  4: End Time
                    # 5: machin  6: lot
                        #print(line)
                        #print('file reading : ' + filename)
                        line_cnt = line_cnt + 1
                        
                        sFile = filename
                        sPath = full_filename
                        sunit = line['SerialNumber']
                        
                        ##################
                        if sunit.upper().find('UPPER') > -1 or sunit.upper().find('LOWER') > -1 or sunit.upper().find('UNIT') > -1 or sunit.strip() == '' :
                            continue
                        
                        start_time = line['startTime']
                        stop_time = line['stopTime']
                        sDev = line['DeviceName']
                        #sDev = line['Device_Name']
                        sLot = line['LotID']
                        sOper = line['ProcessID']
                        sretest = line['RetestCode']
                        sPass = line['TestResult']
                        
                        for k in dic_target_para :
                            stemp = dic_target_para[k]
                            stemp = stemp.split('~')
                            spara = stemp[0]                        
                            #spara = 'RF_RX_MMWAVE_B24A_24300P0_S2_GAIN'
                            if (spara in header.fieldnames) == True:
                                spara_val = line[spara]
                                ######################
                                now = datetime.datetime.now()
                                nowtime = now.strftime('%Y%m%d%H%M%S')                        
                                add_data = (sproject, sgubun,sLot,sunit, sOper,spara,spara_val,start_time,stop_time,sretest,filename,nowtime, sPass)                        
                                skey = sproject + '~' + sgubun+ '~' + sLot + '~' + sunit + '~' +sOper + '~' + spara                                        
                                if skey in dic_para :
                                    del dic_para[skey]
                                dic_para[skey] = add_data 
                                #########################
                        '''
                        spara = 'RF_RX_MMWAVE_B28B_28000P0_S10_GAIN'
                        spara_val = line[spara]
                        ######################
                        now = datetime.datetime.now()
                        nowtime = now.strftime('%Y%m%d%H%M%S')                        
                        add_data = (sproject, sgubun,sLot,sunit, sOper,spara,spara_val,start_time,stop_time,sretest,filename,nowtime)                        
                        skey = sproject + '~' + sgubun+ '~' + sLot + '~' + sunit + '~' +sOper + '~' + spara                                        
                        if skey in dic_para :
                            del dic_para[skey]
                        dic_para[skey] = add_data                         
                        #########################
                        '''
                    # 최종 data 정리하여 TPAS_2DIDSUM_DAT 저장준비                    
                    for k in dic_para.keys():                                                    
                        line_temp = dic_para.get(k)
                        
                        data.append(line_temp)                    
                    ###########################        
                    if len(data) > 0:    

                        sql = "INSERT INTO SIP_PARA_DAT (PROJECT, GUBUN, LOT_ID, UNIT, OPER, PARA_NAME, PARA_VAL,START_TIME, END_TIME, "
                        #                                   1  ,    2   ,  3   ,  4  , 5   ,  6      ,  7      ,     8     ,    9
                        sql = sql + "RETEST_SEQ,FILENAME, TRANS_TIME , PASS_FAIL ) "
                        #                 10   ,   11   ,  12  
                        sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8, :9 , :10, :11, :12, :13 ) "
                        
                        sip_cur.executemany(sql,data)            
                        sip_conn.commit()
                            
                        
                        msg = str(i) + ' ] s5. SIP_PARA_DAT Insert complete !! ' + '\n' + " " + full_filename
                        print(msg)
                        writeLog(msg)
                        mail_text = mail_text + msg + '\n'
                         #############################    
                    ####################################
                    # summary insert
                    data = []
                    dic_para = {}
                    dic_para.clear()
                    
                    sql = "SELECT LOT_ID FROM SIP_PARASUM_DAT "
                    sql = sql + "WHERE PROJECT = '" + sproject + "' "
                    sql = sql + "AND GUBUN = '" + sgubun + "' " 
                    sql = sql + "AND LOT_ID = '" + sLot + "' "            
                    sql = sql + "AND OPER = '" + sOper + "' "                    
                    sql = sql + "AND ROWNUM < 2 "

                    sip_cur.execute(sql)
                    rows = sip_cur.fetchall()
                    if  sip_cur.rowcount > 0 :
                        sql = "DELETE SIP_PARASUM_DAT "
                        sql = sql + "WHERE PROJECT = '" + sproject + "' "
                        sql = sql + "AND GUBUN = '" + sgubun + "' " 
                        sql = sql + "AND LOT_ID = '" + sLot + "' "            
                        sql = sql + "AND OPER = '" + sOper + "' "                    
                        
                        sip_cur.execute(sql)
                        sip_conn.commit()
                    #######################
                    sql = "SELECT PROJECT, GUBUN, LOT_ID, UNIT, OPER, PARA_NAME, PARA_VAL, PASS_FAIL FROM SIP_PARA_DAT "                    
                    sql = sql + "WHERE PROJECT = '" + sproject + "' "
                    sql = sql + "AND GUBUN = '" + sgubun + "' " 
                    sql = sql + "AND LOT_ID = '" + sLot + "' "            
                    sql = sql + "AND OPER = '" + sOper + "' "     
                    sql = sql + "ORDER BY LOT_ID, OPER , RETEST_SEQ, START_TIME, TRANS_TIME  "
                    sip_cur.execute(sql)
                    rows = sip_cur.fetchall()
                    
                    if sip_cur.rowcount > 0 :
                        for row in rows:
                            
                            skey = row[0] + '~' + row[1] + '~' + row[2] + '~' + row[3] + '~' + row[4] + '~' + row[5]                
                            
                            if skey in dic_para :
                                del dic_para[skey]
                            dic_para[skey] = row 
                        #########################
                        # 최종 data 정리하여 TPAS_2DIDSUM_DAT 저장준비
                        
                        for k in dic_para.keys():
                            
                            line_temp = dic_para.get(k)
                            now = datetime.datetime.now()
                            nowtime = now.strftime('%Y%m%d%H%M%S')
                            snowtime = (nowtime,)
                            
                            line_temp1 = line_temp + tuple(snowtime) 
                            data.append(line_temp1)
                        #################
                        ###########################        
                        if len(data) > 0:    

                            sql = "INSERT INTO SIP_PARASUM_DAT (PROJECT, GUBUN, LOT_ID, UNIT, OPER, PARA_NAME, PARA_VAL , PASS_FAIL , TRANS_TIME ) "
                            #                                        1  ,  2  ,    3  ,  4   , 5  ,   6      ,   7      ,     8  
                            
                            sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8 , :9) "
                            
                            sip_cur.executemany(sql,data)            
                            sip_conn.commit()
                                
                            
                            msg = str(i) + ' ] s5. SIP_PARASUM_DAT Insert complete !! ' + '\n' + " " + full_filename
                            print(msg)
                            writeLog(msg)
                            mail_text = mail_text + msg + '\n'
                            #---------------------
                            if sproject in project_list :
                                pass
                            else:
                                project_list.append(sproject)  
                            #-----------------------
                            if sgubun in gubun_list :
                                pass
                            else:
                                gubun_list.append(sgubun)  
                                                               
                         #############################    
                    
                except Exception as e:  # 예외가 발생했을 때 실행됨                     
                    writeLog(filename + ' : Insert Error !!' +  e)
                    continue
                     
            f.close()
            #############
            # 로그 남기기
            writeLog(filename + ' : DB 저장완료')
            print(filename + ' : DB 저장완료')
# 원본 csv 파일 upload 완료
##################################
# 결과 csv 파일 생성
#header_list = ['PROJECT','LOT_ID' , 'UNIT' , 'OPER' , 'PARA_NAME' ]
header_list = ['PROJECT', 'UNIT' , 'PARA_NAME' ]
##############################
sql = "DELETE SIP_PARASUM_FINAL "        
sip_cur.execute(sql)
sip_conn.commit()
######################        
for sproject in project_list :
    
    msg = ' ==> csv summary file generation start '
    print(msg)
        
    df1 = pd.DataFrame([])   
    df2 = pd.DataFrame([])   
    result_filename = os.path.join(complete_csv, sproject + '_complete.csv')
    sql = "SELECT PROJECT , GUBUN, LOT_ID, UNIT, OPER , PARA_NAME , PARA_VAL, PASS_FAIL , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') FROM SIP_PARASUM_DAT "
    #sql = "SELECT PROJECT , LOT_ID, UNIT, OPER , PARA_NAME , PARA_VAL FROM SIP_PARASUM_DAT "
    sql = sql + "WHERE PROJECT = '" + sproject + "' "
    sql = sql + "AND GUBUN = 'T0' " 
    sql = sql + "AND UNIT IN ( "
    sql = sql + "SELECT DISTINCT UNIT FROM SIP_PARASUM_DAT "
    sql = sql + "WHERE PROJECT = '" + sproject + "' "
    sql = sql + "AND PARA_VAL IS NOT NULL "
    sql = sql + "AND GUBUN <> 'T0' " 
    sql = sql + " ) "
    if sinput_pass_fail == 'ALL' :
        pass
    else :
        sql = sql + "AND PASS_FAIL = '" + sinput_pass_fail + "' "
        
    #sql = sql + "ORDER BY GUBUN , LOT_ID , UNIT , OPER, PARA_NAME "
    sql = sql + "ORDER BY GUBUN , LOT_ID , PARA_NAME "
    
    sip_cur.execute(sql)
    rows = sip_cur.fetchall()
    if  sip_cur.rowcount > 0 :
        
        data = rows
        ###########################
        # FINAL DB 에 INSERT
        sql = "INSERT INTO SIP_PARASUM_FINAL (PROJECT, GUBUN, LOT_ID, UNIT, OPER, PARA_NAME, PARA_VAL , PASS_FAIL , TRANS_TIME ) "
        #                                        1  ,  2  ,    3  ,  4   , 5  ,   6      ,   7      ,     8          
        sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8 , :9) "        
        sip_cur.executemany(sql,data)            
        sip_conn.commit()
        ##############################           
        
        df1 = pd.DataFrame(rows) 
        df1.drop(1, axis=1, inplace=True)
        df1.drop(2, axis=1, inplace=True)
        df1.drop(4, axis=1, inplace=True)
        df1.drop(7, axis=1, inplace=True)
        df1.drop(8, axis=1, inplace=True)
        

        header_list.append('T0') 
        
        
        msg = str(i) + ' ] s5. SIP_PARASUM_FINAL Insert complete !! ' + '\n' + " " + full_filename
        print(msg)
        writeLog(msg)
        mail_text = mail_text + msg + '\n'
        
              
    
    #sql = "SELECT PROJECT , GUBUN, LOT_ID, UNIT, OPER , PARA_NAME , PARA_VAL FROM SIP_PARASUM_DAT "
    sgubun_cnt = 0
    sgubun_str = ''
    gubun_list.sort()
    
    for sgubun in gubun_list :
        
        sql = "SELECT PROJECT , GUBUN, LOT_ID, UNIT, OPER , PARA_NAME , PARA_VAL, PASS_FAIL , TO_CHAR(SYSDATE,'YYYYMMDDHH24MISS') FROM SIP_PARASUM_DAT "
        #sql = "SELECT PROJECT , LOT_ID, UNIT, OPER , PARA_NAME , PARA_VAL FROM SIP_PARASUM_DAT "
        sql = sql + "WHERE PROJECT = '" + sproject + "' "
        sql = sql + "AND GUBUN = '" + sgubun + "' "        
        sql = sql + "AND GUBUN <> 'T0' " 
        if sinput_pass_fail == 'ALL' :
            pass
        else :
            sql = sql + "AND PASS_FAIL = '" + sinput_pass_fail + "' "
            
        sql = sql + "AND PARA_VAL IS NOT NULL "    
        sql = sql + "ORDER BY GUBUN , LOT_ID , PARA_NAME "
        
        sip_cur.execute(sql)
        rows = sip_cur.fetchall()
        if  sip_cur.rowcount > 0 :
            data = rows
            ###########################
            # FINAL DB 에 INSERT
            sql = "INSERT INTO SIP_PARASUM_FINAL (PROJECT, GUBUN, LOT_ID, UNIT, OPER, PARA_NAME, PARA_VAL , PASS_FAIL , TRANS_TIME ) "
            #                                        1  ,  2  ,    3  ,  4   , 5  ,   6      ,   7      ,     8          
            sql = sql + "VALUES ( :1, :2, :3, :4, :5, :6, :7, :8 , :9) "        
            sip_cur.executemany(sql,data)            
            sip_conn.commit()
            ##############################           
        
            
            df2 = pd.DataFrame(rows) 
        
            df2.drop(1, axis=1, inplace=True)
            df2.drop(2, axis=1, inplace=True)            
            df2.drop(4, axis=1, inplace=True)
            df2.drop(7, axis=1, inplace=True)
            df2.drop(8, axis=1, inplace=True)
            
            
            sgubun_cnt = sgubun_cnt + 1 
            header_list.append(sgubun)             
            #--------------------------------------
            if sgubun_cnt == 1  :
                if df1.empty == True :
                    #df_result = pd.merge(df1, df2, how="outer", on=[0,1,2,3,4])
                    df_result = df2
                #df_result = df1.merge(df2, left_on =[0,1,2,3,4], right_on = [0,1,2,3,4] )
                else :
                    #df_result = pd.merge(df1, df2, how="outer", on=[0,1,2,3,4])
                    df_result = pd.merge(df1, df2, how="outer", on=[0,5,3])
            else :
                #df_result = df_result.merge(df2, how="outer", left_on =[0,1,2,3,4], right_on = [0,1,2,3,4] )
                #df_result = pd.merge(df_result, df2, how="outer", on=[0,1,2,3,4])
                df_result = pd.merge(df_result, df2, how="outer", on=[0,5,3])
                
            #-------------------------------
            
    #sgubun_str = sgubun_str[:-1]            
    #df_result.to_csv(result_filename, header=['PROJECT','LOT_ID' , 'UNIT' , 'OPER' , 'PARA_NAME' , 'T0' , 'TC200' , 'TC500' ] ,index=False)
    df_result.to_csv(result_filename, header= header_list ,index=False)

    msg = sproject + ' ]  ==> csv summary file generation complete !! '
    print(msg)
    
sip_conn.close()     
 #############################33
msg = sproject + ' Eagle parametric data generation complete !! '
print(msg)
writeLog(msg)

time.sleep(3)
