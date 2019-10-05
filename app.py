#!/usr/local/bin/python3

from flask import Flask, render_template, request, g, make_response
import os
import model
import util

app = Flask(__name__)

@app.before_request
def before_request():
    g.db = model.connect_db()

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

    if request.method == 'POST':
        city = request.form['city']
        weather_dic = util.format_response(city)
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
            util.set_recent_five_cookie(request, resp, city, temp, descript)
            return resp
    return render_template('home.html', data=weather_str)

@app.route('/history', methods=['GET'])
def show_history():
    list_weather = model.get_all_weather()
    return render_template('history.html', weathers=list_weather)

@app.route('/recent', methods=['GET'])
def show_recent():
    list_weathers = util.read_recent_five_cookie(request)
    return render_template('recent.html', weathers=list_weathers)

if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)