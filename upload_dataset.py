import pymysql
import datetime
from configparser import ConfigParser

dbconfig = ConfigParser()
dbconfig.read("config.ini")
SERVER = dbconfig["DATABASE"]["SERVER"]
DATABASE = dbconfig["DATABASE"]["DATABASE"]
PORT = dbconfig["DATABASE"]["PORT"]
USERNAME = dbconfig["DATABASE"]["USERNAME"]
PASSWORD = dbconfig["DATABASE"]["PASSWORD"]
location_number = dbconfig["SETTING"]["location_number"]
insert_table_name = "hid_record_count"

db_settings={
    "host":SERVER,
    "port":int(PORT),
    "user":USERNAME,
    "password":PASSWORD,
    "db":DATABASE,
    "charset":"utf8"
    }

def dataset_upload(today=None, location=None, OK_count=None, NG_count=None):
    con = pymysql.connect(**db_settings)
    cur = con.cursor()      
    cur.execute(f"INSERT INTO {insert_table_name} values ('{today}','{location}','{OK_count}','{NG_count}')")
    con.commit()
    cur.close()
    con.close()

today = datetime.date.today()
NG_count = 100
OK_count = 50
dataset_upload(today, location_number, OK_count, NG_count)
