import pymysql
import json

def query(dev_serial, radon, temp, hum, d1_0, d2_5, d10_0):
    try:
        with open("/home/pi/dbinfo.json") as json_file:
            json_data = json.load(json_file)
            host = json_data["host"]
            port = int(json_data["port"])
            user = json_data["user"]
            password = json_data["password"]
            database = json_data["database"]
        conn = pymysql.connect(host=host, port=port ,user=user,password=password,database=database)
        cursor = conn.cursor()
        query_str = "INSERT INTO Monitor (dev_serial, radon, temperature, humidity, dust_1, dust_2_5, dust_10) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query_str , (dev_serial, radon, temp, hum, d1_0, d2_5, d10_0)) 
        conn.commit()
        print("saved")
        conn.close()
    except Exception as e:
        print("method of save error")
        print(e)
        print("save is failed")


