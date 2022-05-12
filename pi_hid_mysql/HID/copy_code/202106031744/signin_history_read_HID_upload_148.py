#!/usr/bin/python3

import time
from configparser import ConfigParser
#import pyodbc
import pymysql
import os
import pandas as pd

TEXT = "請刷卡" # 網頁預設文字


# DATABASE Information
dbconfig = ConfigParser()
dbconfig.read("config.ini")
SERVER = dbconfig["DATABASE"]["SERVER"]
DATABASE = dbconfig["DATABASE"]["DATABASE"]
PORT = dbconfig["DATABASE"]["PORT"]
USERNAME = dbconfig["DATABASE"]["USERNAME"]
PASSWORD = dbconfig["DATABASE"]["PASSWORD"]
request_table_name = dbconfig["DATABASE"]["request_table_name"]
insert_table_name = dbconfig["DATABASE"]["insert_table_name"]
location_number = dbconfig["SETTING"]["location_number"]
sharefloder = dbconfig["SETTING"]["sharefloder"]

db_settings={
    "host":SERVER,
    "port":int(PORT),
    "user":USERNAME,
    "password":PASSWORD,
    "db":DATABASE,
    "charset":"utf8"
    }

def get_file_list(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        dir_list = sorted(dir_list, key = lambda x:os.path.getmtime(os.path.join(file_path,x)))
        return dir_list

list_record = get_file_list (file_path = sharefloder)
for record in list_record:
    df_record = pd.read_csv(sharefloder+'/'+ record, converters = {u'hid':str,u'location_number':str})
    hid = df_record.iloc[0].hid
    time_now = df_record.iloc[0].time_now

    """ ###Search employee Name by hid
    con = pymysql.connect(**db_settings)
    cur = con.cursor()
    try:
        cur.execute(f"select WORKID,NAME FROM {request_table_name} WHERE HIDCARD='{hid}'")
        work_ID,name = cur.fetchone()
    except:
        work_ID = ""
        name = hid
    """ 
    
    #TEXT = f'Hi  {name}, {time_now}'
    
    """ #Insert information to database then disconnect
    cur.execute(f"INSERT INTO {insert_table_name} values ('{hid}','{work_ID}','{name}','{location_number}','{time_now}')")
    con.commit()
    cur.close()
    con.close()
    
    os.remove(sharefloder+'/'+record)
    """
