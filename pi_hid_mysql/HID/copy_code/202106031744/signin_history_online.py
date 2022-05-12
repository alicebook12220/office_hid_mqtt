import time
from configparser import ConfigParser
#import pyodbc
import pymysql
import os
#import MySQLdb

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
location_number = dbconfig["SETTING"]["location_number"]

db_settings={
    "host":SERVER,
    #"port":int(PORT),
    "user":USERNAME,
    "password":PASSWORD,
    "db":DATABASE,
    "charset":"utf8"
    }


     
from flask import Flask,render_template,request
app = Flask(__name__)


@app.route("/", methods=['GET','POST'])
def submit():
    global TEXT
    
    if request.method=='POST':
        time_now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        hid = str(request.values.get('hid'))
        
        print(hid)
        
        ### insert hid_record
        #con = pymysql.connect(db_settings)
        #con = MySQLdb.connect(db_settings)
        con = pymysql.connect("localhost","hid_record","hid_record$dss0","hid_record_db")

        cur = con.cursor()      
        cur.execute(f"INSERT INTO {insert_table_name} values ('{hid}','{location_number}','{time_now}')")
        con.commit()
        cur.close()
        con.close()       
        
        """
        con = pymysql.connect("localhost","root","ml6a01","hid_record_db")
        cur = con.cursor()  
        try:
            cur.execute(f"select user_hid,entry_time,location_number FROM {insert_table_name} '")
            get_userhid,get_entry_time,get_location_number = cur.fetchone()
            print(get_userhid,get_entry_time,get_location_number )
        except:
            print('NG')
        cur.close()
        con.close()              
        
        """    
        
        """ ###Search employee Name by hid
        con = pymysql.connect(db_settings)
        cur = con.cursor()
        try:
            cur.execute(f"select WORKID,NAME FROM {request_table_name} WHERE HIDCARD='{hid}'")
            work_ID,name = cur.fetchone()
        except:
            work_ID = ""
            name = hid
        """
        
        TEXT = f'{hid} is key in, {time_now}'
        
        """ ###Insert information to database then disconnect
        cur.execute(f"INSERT INTO {insert_table_name} values ('{hid}','{work_ID}','{name}','{location_number}','{time_now}')")
        con.commit()
        cur.close()
        con.close()
        """
        print(f"{TEXT}\n")
        #print(f"select WORKID,NAME FROM {request_table_name} WHERE HIDCARD='{hid}'")
    return render_template("HID.html",text=TEXT)
    

if __name__ == '__main__':
    app.run(port=5000,debug=False)