from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime, timedelta
import mysql.connector
import json
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

@app.route('/update_counter', methods=['POST'])
def update_counter():
    global counter
    # 如果收到 POST 请求，则增加计数器的值
    if request.method == 'POST':
        try:
            counter += int(request.form['currentDate'])
            print(request.form['currentDate'])
        except Exception as e:
            print("ERR:",e)
    # 重定向到主页
    return redirect('/feeding_calendar')


# 路由，用來顯示每天的餵食魚餌時間和強度
@app.route('/feeding_calendar', methods=['GET','POST'])
def show_feed_schedule():
    subdates=counter
    today = datetime.now().date()
    try: 
        #subdates = int(request.form['currentDate'])
        today += timedelta(days=subdates)
        print(subdates)
    except Exception as e:

        print("ERR:",e)

    end_of_week = today - timedelta(days=7)
    feed_schedule = []

    # 從資料庫中取得一週內的餵食魚餌時間和強度
    while today > end_of_week:
        try:
            query = "SELECT time, voltage FROM feed_alive WHERE voltage>35 and DATE(time) = %s"
            cursor.execute(query, (end_of_week,))
            feedings = cursor.fetchall()
            feed_schedule.append({'name': end_of_week.strftime('%Y-%m-%d') ,'value': 5*len(feedings)/60} ) # 將日期轉換為字串格式並計算餵食次數
            end_of_week += timedelta(days=1)
        except :
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
    return render_template('index.html', data=feed_schedule)



if __name__ == '__main__':
    app.run(debug=True)
    """
    @app.route('/')
def index():
    data=[{'name': 'rose 1', 'value': 40},
        {'name': 'rose 2', 'value': 38},
        {'name': 'rose 3', 'value': 32},
        {'name': 'rose 4', 'value': 30},
        {'name': 'rose 5', 'value': 28},
        {'name': 'rose 6', 'value': 26},
        {'name': 'rose 7', 'value': 22},
        {'name': 'rose 8', 'value': 18}]
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8000)
    
    """