from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from spotify_data import spotify,genre_ml_classifier
import requests
from weather_data import weather
import json
from apscheduler.schedulers.background import BackgroundScheduler
from taskrunner import sun_time
from database import ml_database,spotify_database
import requests
from datetime import datetime
import time
from redis import Redis
import rq
from taskrunner import background_task_app
import os 

app = Flask(__name__)
CORS(app)
curr_date = datetime.utcnow().strftime("%m/%d/%Y")
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
app.redis = Redis.from_url(REDIS_URL)
app.task_queue = rq.Queue('microblog-tasks', connection=app.redis,default_timeout=3600)


scheduler = BackgroundScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.start()
scheduler.add_job(func=background_task_app.store_tracks,trigger='cron',id='Store',minute='0-59/15')

def launch_task(name, description, **kwargs):
    rq_job = app.task_queue.enqueue('taskrunner.background_task_app.' + name,kwargs=kwargs)
    if 'user_id' in kwargs:
        spotify_database.Insert_Full_Task_Info(task_id = rq_job.get_id(),task_type = name,description = description,user_id=kwargs['user_id'])
    else:
        spotify_database.Insert_Full_Task_Info(task_id = rq_job.get_id(),task_type = name,description = description)
    return rq_job
    
#TODO: We need to add in a method that recollects the users data every week.


@app.route('/store_user', methods = ['POST'])
def store_user():
    '''
    Stores Users:
    -Location
    -TimeZone
    -Artists
    -Recently Played Songs
    -Playlists
    -Liked Genres
    '''
    status = 404
    success = False
    message = "Fields are incorrect"
    keys = ['refresh_token','access_token','last_refresh','display_name','zipcode','country','user_id']
    if all(key in request.form for key in keys): 
        refresh_token = request.form['refresh_token']
        access_token = request.form['access_token']
        name = request.form['display_name']
        country = request.form['country']
        user_id = request.form['user_id']
        zipcode = request.form['zipcode']
        last_refresh = int(request.form['last_refresh'])
        query = ml_database.Check_User(user_id)
        status = 200
        success = True
        if query is None:
            location_id = spotify_database.Insert_Location_Info(zipcode,country)
            spotify_database.Insert_User_Info(user_id,access_token,refresh_token,last_refresh,name,location_id,-1)

            launch_task(name='store_user_info',description='Storing Spotify and location info for user.',user_id = user_id, \
            access_token = access_token, country = country)
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
    '''
    Used to update user's Last_Known_Location and updates home location if unknown.
    '''
    status = 404
    success = False
    message = "Fields are incorrect"
    keys = ['user_id','zipcode','country']
    if all(key in request.form for key in keys): 
        user_id = request.form['user_id']
        zipcode = request.form['zipcode']
        country =  request.form['country']

        location_id = spotify_database.Insert_Location_Info(zipcode,country)

        ml_database.Update_User_Last_Location(location_id,user_id)

        user_location = ml_database.Get_User_Home_Location(user_id)

        if user_location[0] == 'ZipCode N/A': # This is 
            ml_database.Update_User_Home_Location(Location_ID,user_id)
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

# @app.route('/weather')
# def get_weather():
#     zipcode = '07305'
#     data = weather.get_current_weather()
#     if "ERROR" not in data:
#         avg_temp = weather.get_avg_temp(data)
#         pressure = weather.get_pressure(data)
#         humidity = weather.get_humidity(data)
#         weather_id = weather.get_weather_id(data)
#         wind_speed = weather.get_wind_speed(data)
#         wind_direction = weather.get_wind_direction(data)
#         cloudiness = weather.get_cloudiness(data)
#         precipitation = weather.get_precipitation(data)
#         last_updated = weather.get_last_updated(data)
#         response = app.response_class(
#             response=json.dumps(data),
#             status=200,
#             mimetype='application/json'
#         )
#         return response
#     else:
#         response = app.response_class(
#             response=json.dumps({"ERROR": "Refer to console for more information"}),
#             status=406,
#             mimetype='application/json'
#         )
#         return response


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, threaded=True,port=5000)
