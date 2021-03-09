from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from spotify_data import spotify
import requests
from weather_data import weather
import json
from taskrunner import sun_time
import requests
from datetime import datetime
import time
from taskrunner import refresh_token

app = Flask(__name__)
CORS(app)
curr_date = datetime.utcnow().strftime("%m/%d/%Y")

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

    if 'latitude' not in request.form or 'authKey' not in request.form or 'longitude' not in request.form :
        response = app.response_class(
            response=json.dumps({'success':False}),
            status=404,
            mimetype='application/json'
        )
        return response
    
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    authKey = request.form['authKey']

    responseD = {
        'latitude' : latitude,
        'authKey' : authKey,
        'longitude' : longitude
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
    keys = ['refresh_token','access_token','last_refresh','display_name','latitude','longitude','zipcode','country']
    if all(key in request.form for key in keys): 
        refresh_token = request.form['refresh_token']
        access_token = request.form['access_token']
        latitude = float(request.form['latitude'])
        name = request.form['display_name']
        longitude = float(request.form['longitude'])
        country = request.form['country']
        zip_code = request.form['zipcode']
        last_refresh = int(request.form['last_refresh'])
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
                            'longitude' : longitude,
                            'latitude' : latitude,
                            'zipcode' : zip_code,
                            'country' : country,
                            'last_refresh' : last_refresh,
                            'last_longitude' : longitude,
                            'last_latitude' : latitude,
                            'last_zipcode' : zip_code,
                            'last_country' : country,
                            'numSongs' : len(audio_j),
                            'songs' : audio_j,
                            'dates' : dict()
                        }
                    }
                    with open('data.json','w') as w: # TEST
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

@app.route('/get_data', methods = ['GET'])
def get_data():
    with open('data.json','r') as f:
        data = json.load(f)
    response = app.response_class(
        response=json.dumps({'JSON':data},indent=4),
        status=200,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/update_location', methods = ['POST'])
def update_location():
    status = 404
    success = False
    message = "Fields are incorrect"
    keys = ['display_name','latitude','longitude','zipcode','country']
    if all(key in request.form for key in keys): 
        with open('data.json','r') as f:
            data = json.load(f)
            new_write = dict()
            name = request.form['display_name']
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            zip_code = request.form['zipcode']
            country =  request.form['country']
            data[name]['last_latitude'] = latitude
            data[name]['last_longitude'] = longitude
            data[name]['last_zipcode'] = zip_code
            data[name]['last_country'] = country
            if data[name]['zipcode'] is 'ZipCode N/A':
                data[name]['latitude'] = latitude
                data[name]['longitude'] = longitude
                data[name]['zipcode'] = zip_code
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
        global curr_date
        data = json.load(f)
        new_write = dict()
        for (name,user) in data.items():
            if bool(user['dates']) or (datetime.utcnow().minute == 15 and datetime.utcnow().hour == 0): # The first run per user must start at 0:00 UTC
                curr_time = int((time.time() * 1000))
                (user['access_token'],user['last_refresh']) = refresh_token.check_new_token(user['access_token'],user['refresh_token'],user['last_refresh'])
                recent_tracks = spotify.get_recent_tracks(user['access_token'],after=curr_time-900000,id_only=True)# Did you FINISH any songs in the last 15 minutes.
                if not bool(user['dates']):
                    user['dates']['numRuns'] = 0 # This is done versus a global var so if a new user joins in later we can keep track of their start point
                    user['dates']['numHours'] = 0
                    user['dates'][curr_date] = dict()
                    for i in range(24):
                        user['dates'][curr_date][str(i)] = dict()
                numHours = user['dates']['numHours']
                numRuns  = user['dates']['numRuns']
                print(f"NumRuns:{numRuns}\nNumHours:{numHours}")
                if numRuns % 4 == 0 and numRuns % 96 != 0: # Every hour move to a new Dict, we start on the first hour so we don't need to increment.
                    numHours+= 1
                if not bool(user['dates'][curr_date][str(numHours)]): # We need to know the hour it was listened too so we can convert it to weather at the end.
                    user['dates'][curr_date][str(numHours)] = {
                        'UTC TIME' : datetime.utcnow().strftime("%m/%d/%Y : %H:00"),
                        'Converted Time' : sun_time.getConvertedTime(user['last_zipcode'],datetime.utcnow().strftime("%m/%d/%Y : %H:00")),
                        'Location' : {
                            'Zipcode' : user['last_zipcode'],
                            'Country' : user['last_country']
                        },
                        'Sun Position' : sun_time.get_SunPosition(float(user['last_latitude']),float(user['last_longitude']),datetime.utcnow().strftime("%m/%d/%Y : %H:%M")),
                        'Time Period' : sun_time.getTimePeriod(user['last_zipcode'],datetime.utcnow().strftime("%m/%d/%Y : %H:00")),
                        'Songs' : {}
                    }
                if bool(recent_tracks):
                    for (track_id,track) in recent_tracks.items():
                        if track_id in user['songs'].keys(): # We only want to log the songs we recorded
                            if track_id in user['dates'][curr_date][str(numHours)]['Songs']:
                                user['dates'][curr_date][str(numHours)]['Songs'][track_id]['numPlayed'] += 1
                            else:
                                user['dates'][curr_date][str(numHours)]['Songs'][track_id] = {
                                    'numPlayed' : 1,
                                    'name' :track['name']
                                }
                            # We're only storing the songs we heard, the other songs the user in the user's playlist will be recorded as 0.
                numRuns += 1
                if numRuns % 96 == 0 and numRuns != 0: # Every 15 minutes a day it incruments so in theory this should create a new date every day
                    curr_date = datetime.utcnow().strftime("%m/%d/%Y")
                    user['dates'][curr_date] = dict()
                    for i in range(24):
                        user['dates'][curr_date][str(i)] = list()
                    numHours = 0
                user['dates']['numRuns'] = numRuns
                user['dates']['numHours'] = numHours
                new_write[name] = user
                with open('data.json','w') as w:
                    json.dump(new_write,w, indent = 4)
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
    if 'latitude' not in request.form or 'authKey' not in request.form or 'longitude' not in request.form :
        response = app.response_class(
            response=json.dumps({'success':False}),
            status=404,
            mimetype='application/json'
        )
        return response
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    authKey = request.form['authKey']
    response = app.response_class(
        response=json.dumps(weather.get_weather_from_latitude(latitude,longitude)),
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
    if "ERROR" not in data:
        avg_temp = weather.get_avg_temp(data)
        pressure = weather.get_pressure(data)
        humidity = weather.get_humidity(data)
        weather_id = weather.get_weather_id(data)
        wind_speed = weather.get_wind_speed(data)
        wind_direction = weather.get_wind_direction(data)
        cloudiness = weather.get_cloudiness(data)
        precipitation = weather.get_precipitation(data)
        last_updated = weather.get_last_updated(data)
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        response = app.response_class(
            response=json.dumps({"ERROR": "Refer to console for more information"}),
            status=406,
            mimetype='application/json'
        )
        return response


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, threaded=True)
