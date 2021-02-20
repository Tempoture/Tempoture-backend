import requests
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from spotify_data import spotify
from weather_data import weather

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['GET'])
def api():
    return {
        'userID': 1,
        'title': 'Flask and React Application.',
        'completed': False
    }

#Route Testing Data transfer from front end to Back end
@app.route('/data', methods = ['POST'])
def data():

    data_json = request.get_json()

    if not data_json:
        return "Json Request Failed" #data not found/error 404 etc

    data = data_json.get('authKey')

    return data #Show data on screen
    

@app.route('/songs', methods=['GET'])
def spotify_user_songs():
    access_token = request.args.get('access_token')
    data = spotify.get_recent_tracks(access_token)
    return data

@app.route('/weather')
def get_weather():
    zipcode = weather.get_zip_code()
    data = weather.get_current_weather()
    avg_temp = weather.get_avg_temp(data)
    pressure = weather.get_pressure(data)
    humidity = weather.get_humidity(data)
    weather_id = weather.get_weather_id(data)
    wind_speed = weather.get_wind_speed(data)
    wind_direction = weather.get_wind_direction(data)
    cloudiness = weather.get_cloudiness(data)
    precipitation = weather.get_precipitation(data)
    last_updated = weather.get_last_updated(data)

    # print(zipcode)
    # print(avg_temp)
    # print(pressure)
    # print(humidity)
    # print(weather_id)
    # print(wind_speed)
    # print(wind_direction)
    # print(cloudiness)
    # print(precipitation)
    # print(last_updated)

    return data


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, threaded=True)
