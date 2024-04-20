
from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime, timedelta
import mysql.connector
import json

app = Flask(__name__)

timetable = {}


def convert_to_timetable(data):
    timetable = {}    
    for key, value in data.items():
                        
        hour, minute, second = value['start']
        start_time = int(hour)*3600 +60 * int(minute) +int(second)
        hour, minute, second = value['end']
        end_time = int(hour)*3600 +60 * int(minute)+ int(second)
                        
        if (end_time - start_time)/ 60 > 40:
            timetable[value['start'][0]+':00'] = "O"
        else:
            timetable[value['start'][0]+':00'] = "O"
            timetable[value['end'][0]+':00'] ="O"
            

    #補上空白的時間
    for hour in range(0, 24):
        time_key = f"{hour:02d}:00"
        if time_key not in timetable:
            timetable[time_key]='-'
    
    return timetable
# 假設這是你的課表資料

app = Flask(__name__)

# 連接到 MySQL 資料庫
db = mysql.connector.connect(
    host="34.81.183.159",
    user="lab403",
    password="66386638",
    database="fishDB"
)
counter = 0

cursor = db.cursor()

#按下按鈕計算當前天數後路由到feeding_calendar
@app.route('/update_counter', methods=['POST'])
def update_counter():
    global counter
    # 如果收到POST,計數器增加
    if request.method == 'POST':
        try:
            counter += int(request.form['currentDate'])
            print(request.form['currentDate'])
        except Exception as e:
            print("ERR:",e)
    # 重定向到主页
    return redirect('/feeding_calendar')

# 路由,用來顯示每天的餵食魚餌時間和強度
@app.route('/feeding_calendar', methods=['GET','POST'])
def show_feed_schedule():
    
    subdates=counter
    today = datetime.now().date()
    today += timedelta(days=subdates)

    end_of_week = today - timedelta(days=6)
    feed_schedule = []
    feed_calendar={}
    hourly_data={}

    # 從資料庫中取得一週內的餵食魚餌時間和強度
    while today >= end_of_week:
        try:
            query = "SELECT time, voltage FROM feed_alive WHERE voltage>35 and DATE(time) = %s"
            cursor.execute(query, (end_of_week,))
            feedings = cursor.fetchall()
            feed_schedule.append({'name': end_of_week.strftime('%Y-%m-%d') ,'value': 5*len(feedings)/60} ) # 將日期轉換為字串格式並計算餵食次數

###################### 
            #取出每小時的開始與結束
            hourly_data={}
            for feeding in feedings:
                feed_time = str(feeding[0].time()).split(":")
                hour,minute,second=feed_time
                if feed_time[0] not in hourly_data:
                    hourly_data[hour] = {"start": feed_time, "end": feed_time}
                else:
                     hourly_data[hour]["end"] = feed_time

            feed_calendar[end_of_week.strftime('%Y-%m-%d')]=convert_to_timetable(hourly_data)
            print("hgfhgfh")


#####################

        except Exception as e:
            print("ERR:",e)
            try:
                db = mysql.connector.connect(
                    host="34.81.183.159",
                    user="lab403",
                    password="66386638",
                    database="fishDB"
                )
                cursor = db.cursor()
            except Exception as e:    
                print("ERR:",e)
                continue
        end_of_week += timedelta(days=1)
    return render_template('feeding_calendar.html', data=feed_schedule,timetable=feed_calendar)



if __name__ == '__main__':
    app.run(debug=True)
