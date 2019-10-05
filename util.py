import requests
import model

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
            model.insert_weather(city, temp, descript)
    except:
        dic_weather_info.update({"error":"There was a problem"})
    return dic_weather_info



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