from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from spotify_data import spotify
import requests
from weather_data import weather
import json
import requests
from datetime import datetime
import time
from taskrunner import refresh_token

app = Flask(__name__)
CORS(app)
numRuns  = 0
curr_date = datetime.now().strftime("%d/%m/%Y")

@app.route('/api', methods=['GET'])
def api():
    return {
        'userID': 1,
        'title': 'Flask and React Application.',
        'completed': False
    }
#Route Testing Data transfer from front end to Back end
@app.route('/data', methods = ['POST','GET'])
def data():

    if 'zipcode' not in request.form or 'authKey' not in request.form or 'country' not in request.form :
        response = app.response_class(
            response=json.dumps({'success':False}),
            status=404,
            mimetype='application/json'
        )
        return response
    
    zipcode = request.form['zipcode']
    country_code = request.form['country']
    authKey = request.form['authKey']

    responseD = {
        'zipcode' : zipcode,
        'authKey' : authKey,
        'country' : country_code
    }

    response = app.response_class(
        response=json.dumps(responseD),
        status=200,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/store_user', methods = ['POST'])
def store_user():
    status = 404
    success = False
    message = "Fields are incorrect"
    if 'refresh_token' in request.form and 'access_token' in request.form and 'last_refresh' in request.form and 'display_name' in request.form and 'zip_code' in request.form and 'country' in request.form:
        refresh_token = request.form['refresh_token']
        access_token = request.form['access_token']
        zip_code = request.form['zip_code']
        name = request.form['display_name']
        country = request.form['country']
        last_refresh = request.form['last_refresh']
        with open('data.json','r') as f:
                data = json.load(f)
                status = 200
                success = True
                if name not in data:
                    audio_j = spotify.get_all_songs_audio(access_token,country)
                    data_name ={
                        name:{
                            'access_token'  : access_token,
                            'refresh_token' : refresh_token,
                            'country' : country,
                            'zip_code' : zip_code,
                            'last_refresh' : last_refresh,
                            'last_country' : country,
                            'last_zip_code' : zip_code,
                            'songs' : audio_j,
                            'dates' : dict()
                        }
                    }
                    with open('data.json','w') as w:
                        json.dump(data_name,w,  indent = 4)
                        message = "User inserted"
                else:
                    message = "User already inserted"
    response = app.response_class(
        response=json.dumps({'success':success,'message' : message}),
        status=status,
        mimetype='application/json'
    )
    return response

@app.route('/update_location', methods = ['POST'])
def update_location():
    status = 404
    success = False
    message = "Fields are incorrect"
    if 'display_name' in request.form and 'zip_code' in request.form and 'country' in request.form:
        with open('data.json','r') as f:
            data = json.load(f)
            new_write = dict()
            name = request.form['display_name']
            zip_code = request.form['zip_code']
            country = request.form['country']
            data[name]['last_zip_code'] = zip_code
            data[name]['last_country'] = country
            if data[name]['zip_code'] is 'ZipCode N/A':
                data[name]['zip_code'] = zip_code
                data[name]['country'] = country
            new_write = data
            with open('data.json','w') as w:
                json.dump(new_write,w, indent = 4)
            success = True
            status = 200
            message = "Updated Location"
    response = app.response_class(
        response=json.dumps({'success':success,'message' : message}),
        status=status,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
            

@app.route('/store_tracks', methods = ['GET'])
def store_tracks():
    with open('data.json','r') as f:
            global numRuns
            global curr_date
            data = json.load(f)
            new_write = dict()
            for (name,user) in data.items():
                curr_time = int(round(time.time() * 1000))
                (user['access_token'],user['last_refresh']) = refresh_token.check_new_token(user['access_token'],user['refresh_token'],user['last_refresh'])
                print(curr_time-30000)
                recent_tracks = spotify.get_recent_tracks(user['access_token'],curr_time-30000)
                if not bool(user['dates']):
                    user['dates'][curr_date] = list()
                user['dates'][curr_date].append(recent_tracks['items'])
                if numRuns % 96 == 0:
                    curr_date = datetime.now().strftime("%d/%m/%Y")
                    user['dates'][curr_date]=list()
                new_write[name] = user
                with open('data.json','w') as w:
                    json.dump(new_write,w, indent = 4)
            numRuns+=1
    response = app.response_class(
        response=json.dumps({'success':True}),
        status=200,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
#Route Testing Data transfer from front end to Back end
@app.route('/get_weather', methods = ['POST','GET'])
def get_zip_weather():
    if 'zipcode' not in request.form or 'authKey' not in request.form or 'country' not in request.form :
        response = app.response_class(
            response=json.dumps({'success':False}),
            status=404,
            mimetype='application/json'
        )
        return response
    
    zipcode = request.form['zipcode']
    country_code = request.form['country']
    authKey = request.form['authKey']
    response = app.response_class(
        response=json.dumps(weather.get_weather_from_zipcode(zipcode,country_code)),
        status=200,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
@app.route('/songs', methods=['GET'])
def spotify_user_songs():
    access_token = request.args.get('access_token')
    data = spotify.get_recent_tracks(access_token)
    return data

@app.route('/playlist', methods=['GET'])
def spotify_user_playlists():
    access_token = request.args.get('access_token')
    data = spotify.get_current_user_playlists(access_token)
    return data

# '''
# Related Playlist
# '''
# @app.route('/relatedplaylist', methods=['GET'])
# def spotify_user_playlists():
#     access_token = request.args.get('access_token')
#     data = spotify.get_current_user_playlists(access_token)
#     return data

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
    return data


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, threaded=True)
