import time
from configparser import ConfigParser
#import pyodbc
import pymysql
import os
#import MySQLdb
import pandas as pd
import paho.mqtt.client as mqtt

HOST = "localhost"
PORT = 1883
mqtt_topic = "V5F_green" #TOPIC name

#client = mqtt.Client()
#client.connect(HOST, PORT, 600)
#client.publish(mqtt_topic, "Hello")




TEXT = "請刷卡" # 網頁預設文字
### DATABASE Information
dbconfig = ConfigParser()
dbconfig.read("config.ini")
SERVER = dbconfig["DATABASE"]["SERVER"]
DATABASE = dbconfig["DATABASE"]["DATABASE"]
PORT = dbconfig["DATABASE"]["PORT"]
USERNAME = dbconfig["DATABASE"]["USERNAME"]
PASSWORD = dbconfig["DATABASE"]["PASSWORD"]
request_table_name = dbconfig["DATABASE"]["request_table_name"]
insert_table_name = dbconfig["DATABASE"]["insert_table_name"]
insert_table_name_summary_record = dbconfig["DATABASE"]["insert_table_name_summary_record"]
location_number = dbconfig["SETTING"]["location_number"]
color = dbconfig["SETTING"]["color"]

db_settings={
    "host":SERVER,
    "port":int(PORT),
    "user":USERNAME,
    "password":PASSWORD,
    "db":DATABASE,
    "charset":"utf8"
    }


     
from flask import Flask,render_template,request
app = Flask(__name__)


@app.route("/", methods=['GET','POST'])
def submit():
    global TEXT, HOST, PORT, mqtt_topic
    j = "False"
    alarm_msg = " "    
    if request.method=='POST':
        time_now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        hid = str(request.values.get('hid'))
        client = mqtt.Client()
        client.connect(HOST, PORT, 65535)
        client.publish(mqtt_topic, hid)
        client.disconnect()
        
        ### insert hid_record
        con = pymysql.connect(**db_settings)
        #con = pymysql.connect("localhost","hid_record","hid_record$dss0","hid_record_db")
        #con = pymysql.connect(SERVER,USERNAME,PASSWORD,DATABASE)
        #con = pymysql.connect('172.20.10.13',USERNAME,PASSWORD,DATABASE)

        cur = con.cursor()      
        cur.execute(f"INSERT INTO {insert_table_name} values ('{hid}','{location_number}','{time_now}')")
        con.commit()
        cur.close()
        con.close()       
        '''
        #con = pymysql.connect(SERVER,USERNAME,PASSWORD,DATABASE)
        con = pymysql.connect(**db_settings)
        cur = con.cursor()  
        try:
            cur.execute(f"select user_hid,entry_time,location_number FROM {insert_table_name}")
            get_userhid,get_entry_time,get_location_number = cur.fetchone()
            print(get_userhid,get_entry_time,get_location_number )
        except:
            print('NG')
        cur.close()
        con.close()              
        '''

        ### query whitelist
        con_query_whitelist  = pymysql.connect(**db_settings )
        cur_query_whitelist  = con_query_whitelist.cursor()
        try:
            sql_query_whitelist  = """SELECT t.WORKID FROM whitelist t"""
            cur_query_whitelist.execute(sql_query_whitelist )
            heads = cur_query_whitelist.description
            df_query_whitelist  = pd.read_sql(sql_query_whitelist , con_query_whitelist )
            list_whitelist = [i for i in df_query_whitelist.WORKID]
        except:
            print("whitelist_NG")

        con_query_whitelist.close()
        con_query_whitelist.close 
        
        
         ###Search employee Name by hid
        con = pymysql.connect(**db_settings)
        cur = con.cursor()
        
        try:
            cur.execute(f"select * FROM {request_table_name} WHERE HIDCARD='{hid}'")
            DEPARTMENT,WORKID,NAME,HIDCARD,ABGROUP,COLOR = cur.fetchone()
            if COLOR == color:
                judge = 'OK'
                TEXT = f'{WORKID} {NAME}  is key in, {time_now}'
            elif WORKID in list_whitelist:  ### whitelist
                judge = 'OK'  ### whitelist
                TEXT = f'Whitelist {WORKID} {NAME}  is key in, {time_now}'  ### whitelist
            else:
                judge = 'NG'
                TEXT = f'No entry !! {WORKID} {NAME}  is key in, {time_now}'
                j = 'True'
                alarm_msg = '顏色組別錯誤,無進入權限'				 
        except:
            DEPARTMENT = ""
            WORKID = ""
            NAME = hid
            HIDCARD = hid
            ABGROUP = ""
            COLOR = ""
            TEXT = f'No entry !! {hid} is key in, {time_now}'
            alarm_msg = 'HID卡號無對應工號,無進入權限' 
                           
        
        
  
        #print('###Insert information to database then disconnect')
         ###Insert information to database then disconnect
        #print(f"INSERT INTO {insert_table_name_summary_record} (user_hid,location_number,entry_time,DEPARTMENT,WORKERID,NAME,HIDCARD,ABGROUP,COLOR) values ('{hid}','{location_number}','{time_now}','{DEPARTMENT}','{WORKID}','{NAME}','{HIDCARD}','{ABGROUP}','{COLOR}')")
        cur.execute(f"INSERT INTO {insert_table_name_summary_record } (user_hid,location_number,entry_time,DEPARTMENT,WORKERID,NAME,HIDCARD,ABGROUP,COLOR) values ('{hid}','{location_number}','{time_now}','{DEPARTMENT}','{WORKID}','{NAME}','{HIDCARD}','{ABGROUP}','{COLOR}')")
        con.commit()
        cur.close()
        con.close()
        
        print(f"{TEXT}\n")
        #print(f"select WORKID,NAME FROM {request_table_name} WHERE HIDCARD='{hid}'")
    return render_template("HID.html",text=TEXT, j = j, alarm_msg=alarm_msg)
    

if __name__ == '__main__':
    app.run(port=5000,debug=False)
    
    
    
 # https://stackoverflow.com/questions/61190321/calling-invoking-a-javascript-function-from-python-a-flask-function-within-html
