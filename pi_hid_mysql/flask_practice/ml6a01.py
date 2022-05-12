import time
from configparser import ConfigParser
import pyodbc
import pymysql
import os


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

db_setting={
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
    global TEXT
    
    if request.method=='POST':
        time_now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        hid = str(request.values.get('hid'))
        name = hid
        

        """ #Search employee Name by hid
        con = pyodbc.connect('DRIVER={SQL Server};SERVER='+SERVER+';DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
        cur = con.cursor()
        try:
            cur.execute(f"select WORKID,NAME FROM {request_table_name} WHERE HIDCARD='{hid}'")
            work_ID,name = cur.fetchone()
        except:
            work_ID = ""
            name = hid
        """
        
        TEXT = f'Hi  {name}, {time_now}'
        
        """ #Insert information to database then disconnect
        cur.execute(f"INSERT INTO {insert_table_name} values ('{hid}','{work_ID}','{name}','{location_number}','{time_now}')")
        con.commit()
        cur.close()
        con.close()
        """
        print(f"{TEXT}\n")
        #print(f"select WORKID,NAME FROM {request_table_name} WHERE HIDCARD='{hid}'")
    return render_template("index.html",text=TEXT)
    

if __name__ == '__main__':
    app.run(port=5001,debug=False)