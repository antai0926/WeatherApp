#!/usr/local/bin/python3

from flask import Flask, render_template, request, g, make_response
import requests
import sqlite3

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('weather.db')

def format_response(city):
    weather_key = "bd45fc9db8849cb46d00a451483ccd44"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"APPID": weather_key, "q": city, "units": "Metric"}
    response = requests.get(url, params=params)
    weather = response.json()
    dic_weather_info = {}
    try:
        if weather.get('message') == "city not found":
            dic_weather_info.update({"not_found": "Cannot find this city!"})
        else:
            city = weather['name']
            descript = weather['weather'][0]['description']
            temp = weather['main']['temp']
            dic_weather_info.update({"info": {"city":city,"temp":temp,"descript":descript}})
            insert_weather(city, temp, descript)
    except:
        dic_weather_info.update({"error":"There was a problem"})
    return dic_weather_info

def get_all_weather():
    cursor = g.db.execute('SELECT city, temp, descript FROM weather;')
    weathers =   [dict(city=row[0],temp=row[1],descript=row[2])for row in cursor.fetchall()]
    return weathers

def insert_weather(city, temp, descript):
    sql_query = """
                insert into weather ("city", "temp", "descript") VALUES (:city, :temp, :descript);
            """
    g.db.execute(sql_query, {
        'city': city,
        'temp': temp,
        'descript': descript,
    })
    g.db.commit()

def set_recent_five_cookie(request,resp, city, temp, descript):
    dic_cookie = request.cookies
    if "count" not in dic_cookie or dic_cookie.get("count") is None:
        resp.set_cookie("count", str(0))
        count=0
    else:
        count = int(dic_cookie["count"])
        count += 1
        if count == 5:
            count = 0
    resp.set_cookie("count", str(count))
    resp.set_cookie(f"city{count}", str(city))
    resp.set_cookie(f"temp{count}", str(temp))
    resp.set_cookie(f"descript{count}", str(descript))

def read_recent_five_cookie(request):
    dic_cookie = request.cookies
    list_weathers = []
    for i in range(5):
        city = dic_cookie.get(f"city{i}")
        temp = dic_cookie.get(f"temp{i}")
        descript = dic_cookie.get(f"descript{i}")
        if city is not None and city != "":
            list_weathers.append({"city":city, "temp": temp, "descript": descript})
    return list_weathers

@app.before_request
def before_request():
    g.db = connect_db()

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

    if request.method == 'POST':
        city = request.form['city']
        weather_dic = format_response(city)
        if "not_found" in weather_dic:
            weather_str = weather_dic["not_found"]
        elif "error" in weather_dic:
            weather_str = weather_dic["error"]
        else:
            city = weather_dic['info']['city']
            temp = weather_dic['info']['temp']
            descript = weather_dic['info']['descript']
            weather_str = f"{city} is {temp}°C and {descript}"
            resp = make_response(render_template('home.html', data=weather_str))
            set_recent_five_cookie(request, resp, city, temp, descript)
            return resp
    return render_template('home.html', data=weather_str)

@app.route('/history', methods=['GET'])
def show_history():
    list_weather = get_all_weather()
    return render_template('history.html', weathers=list_weather)

@app.route('/recent', methods=['GET'])
def show_recent():
    list_weathers = read_recent_five_cookie(request)
    return render_template('recent.html', weathers=list_weathers)

if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)