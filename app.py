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
from taskrunner import refresh_token,background_task_app
import os 

app = Flask(__name__)
CORS(app)
curr_date = datetime.utcnow().strftime("%m/%d/%Y")
REDIS_URL = os.environ.get('REDISTOGO_URL') or 'redis://'
app.redis = Redis.from_url(REDIS_URL)
app.task_queue = rq.Queue('microblog-tasks', connection=app.redis,default_timeout=3600)


scheduler = BackgroundScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.start()
scheduler.add_job(func=background_task_app.store,trigger='cron',id='Store',minute='0-59/15')


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

@app.route('/fill_weather',methods =['GET'])
def fill_weather():
    '''
    This will be called once per day after all the user's track information.
    Gets information for the previous day and fills in the weather for each hour.
    This is done BY ZIPCODE not by user to avoid too many calls to the weather API.
    '''
    global curr_date
    utc_day_id = ml_database.Get_UTC_Day_ID(curr_date)
    locations = ml_database.Get_Day_Locations(utc_day_id)
    for location_id in locations:
        zipcode,country =  ml_database.Get_Location_Data(location_id)
        if zipcode != 'ZipCode N/A': # We don't collect weather data if you don't have a zipcode
            longlat = sun_time.get_long_lat(zipcode, country)
            prev_weather_data = weather.get_prev_day_data(longlat['lat'],longlat['lng'])
            for hour_data in prev_weather_data:
                date = datetime.utcfromtimestamp(hour_data["dt"]) 
                utc_hour = date.strftime("%H:00")
                utc_day =  date.strftime("%m/%d/%Y")
                utc_day_id = ml_database.Get_UTC_Day_ID(utc_day)
                utc_hour_id = ml_database.Get_UTC_Hour_ID(utc_hour)

                weather_id = spotify_database.Insert_Weather_Info(hour_data,utc_day_id,utc_hour_id,location_id)
                ml_database.Update_Data_Hour_Per_Location_Weather(location_id,utc_day_id,utc_hour_id,weather_id)

    response = app.response_class(
        response=json.dumps({'success':True}),
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
            

@app.route('/store_tracks', methods = ['GET'])
def store_tracks():
    '''
    Stores users 
    -Track information
    -Location
    on a 15 minute interval called by the taskrunner into a single data collected per hour row.

    Creates new row in data collected per hour every hour.
    Creates new row in data collected per day per day.

    Gets weather information at the end of the UTC Day.
    '''
    global curr_date
    users =  ml_database.Get_Users()
    for user_id in users:
        if bool(ml_database.Get_User_NumRuns(user_id)) or (datetime.utcnow().minute == 15 and datetime.utcnow().hour == 0): # The first run per user must start at 0:00 UTC
            curr_time = int((time.time() * 1000))

            access_info = ml_database.Get_Access_Information(user_id)
            (new_access_token,new_last_refresh) = refresh_token.check_new_token(access_info['access_token'],access_info['refresh_token'],access_info['last_refreshed'])
            ml_database.Update_Access_information(user_id,new_access_token,new_last_refresh)

            recent_tracks = spotify.get_recent_tracks(new_access_token,after=curr_time-900000,id_only=True)# Did you FINISH any songs in the last 15 minutes.

            numHours = ml_database.Get_User_NumHours(user_id)
            numRuns = ml_database.Get_User_NumRuns(user_id)
            
            if numRuns == 0:
                utc_day_id = spotify_database.Insert_UTC_Day_Info(curr_date)
                spotify_database.Insert_Data_Date_Info(utc_day_id,user_id)

            if numRuns % 4 == 0 and numRuns % 96 != 0: # Every hour move to a new Dict, we start on the first hour so we don't need to increment.
                numHours+= 1
                ml_database.Increment_NumHours(user_id)
            curr_hour = datetime.utcnow().strftime("%H:00")
            if ml_database.Check_DataCollectedPerHour(user_id,curr_date,curr_hour) is None: # We need to know the hour it was listened too so we can convert it to weather at the end.
                utc_hour_id = spotify_database.Insert_UTC_Hour_Info(curr_hour)

                location_id = ml_database.Get_User_Last_Location_ID(user_id)
                utc_day_id =  spotify_database.Insert_UTC_Day_Info(curr_date)
                data_date_id = ml_database.Get_User_Day_Data_ID(user_id,utc_day_id)
                zipcode,country = ml_database.Get_User_Last_Location(user_id)

                spotify_database.Insert_Data_Hour_Info(user_id,location_id,utc_hour_id,data_date_id,utc_day_id)

                if zipcode != 'ZipCode N/A':
                    spotify_database.Insert_Time_Data_Info(zipcode,country,location_id,utc_day_id,utc_hour_id)
            if bool(recent_tracks):
                spotify_database.Insert_User_Recent_Songs(recent_tracks,user_id,curr_date)
            numRuns += 1
            ml_database.Increment_NumRuns(user_id)
            if numRuns % 96 == 0 and numRuns != 0: # Every 15 minutes a day it incruments so in theory this should create a new date every day
                curr_date = datetime.utcnow().strftime("%m/%d/%Y")
                utc_day_id = spotify_database.Insert_UTC_Day_Info(curr_date)
                spotify_database.Insert_Data_Date_Info(utc_day_id,user_id)

                ml_database.Set0_NumHours(user_id)
                try: # We only get the weather at the end of the day as we can get all of the days weather in a single call which is important to keep under the rate limit.
                    resp = requests.get("https://backendtempoture.herokuapp.com/fill_weather")
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print("ERR:" + str(err))
                numHours = 0
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
