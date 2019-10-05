from flask import g
import sqlite3

def connect_db():
    return sqlite3.connect('weather.db')

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