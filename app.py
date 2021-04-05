from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from spotify_data import spotify,genre_ml_classifier
import requests
from weather_data import weather
import json
from taskrunner import sun_time
from database import ml_database
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
    keys = ['refresh_token','access_token','last_refresh','display_name','zipcode','country','user_id']
    if all(key in request.form for key in keys): 
        refresh_token = request.form['refresh_token']
        access_token = request.form['access_token']
        name = request.form['display_name']
        country = request.form['country']
        user_id = request.form['user_id']
        zipcode = request.form['zipcode']
        last_refresh = int(request.form['last_refresh'])
        query = ml_database.Check_User_Query(user_id)
        status = 200
        success = True
        if query is None:
            spotify_info = spotify.get_all_songs_table_info(access_token,country)
            utc_day = datetime.utcnow().strftime("%m/%d/%Y")
            ml_database.Insert_UTC_Day_Query(utc_day)
            utc_day_id = ml_database.Get_UTC_Day_ID_Query(utc_day)
            ml_database.Insert_Location_Query(zipcode,country)
            Location_ID = ml_database.Get_Location_ID_Query(zipcode,country)
            songs = spotify_info['Songs']
            user_table = {
                'Display_name' : name,
                'Last_Known_Location_ID' : Location_ID,
                'Home_Location_ID' : Location_ID,
                'numRuns'  : 0,
                'numSongs' : len(songs),
                'numHours' : 0,
                'access_token'   : access_token,
                'refresh_token'  : refresh_token,
                'last_refreshed' : last_refresh,
                'User_ID' : user_id
            }
            ml_database.Insert_User_Query(user_table)
            for song_id,song_info in songs.items():
                song_query = ml_database.Check_Song_Query(song_id)
                if song_query is None:
                    song_table_info = song_info
                    song_table_info['Song_key'] = song_table_info['key'] # In the table we call it Song_key because you can't have key as a column name
                    del song_table_info['key']
                    song_table_info.update({
                        'Song_ID' : song_id
                    })
                    ml_database.Insert_Song_Query(song_table_info)
                    genres = genre_ml_classifier.get_genres(song_info)
                    for genre in set(genres.keys()):
                        ml_database.Insert_Genre_Query(genre)
                    for genre,confidence in genres.items():
                        genre_id = ml_database.Get_Genre_ID_Query(genre)
                        song_genre_info = {
                            'Song_ID'  : song_id,
                            'Genre_ID' : genre_id,
                            'Confidence' : confidence
                        }
                        ml_database.Insert_Song_Genre_Query(song_genre_info)
            recently_played_songs = spotify_info['Recently_Played_Songs']
            for song in recently_played_songs:
                recently_played_songs_user_table = {
                    'Song_ID' : song,
                    'User_ID' : user_id,
                    'UTC_Day_ID' : utc_day_id
                }
                ml_database.Insert_Recently_Played_Songs_User_Query(recently_played_songs_user_table)
            artists = spotify_info['Artists']
            songs_artists = spotify_info['Songs_Artists']
            for artist_info in artists:
                artist_table = {
                    'Artist_ID' : artist_info[0],
                    'Artist_name' : artist_info[1]
                }
                user_artist_table = {
                    'User_ID' : user_id,
                    'Artist_ID' : artist_info[0],
                    'UTC_Day_ID' : utc_day_id
                }
                ml_database.Insert_Artist_Query(artist_table)
                ml_database.Insert_Users_Artists_Query(user_artist_table)
                genres_artists = genre_ml_classifier.get_artist_genre(songs_artists,artist_info[0])
                for genre,confidence in genres_artists.items():
                    genre_id = ml_database.Get_Genre_ID_Query(genre)
                    genre_artist_table = {
                        'Genre_ID' : genre_id,
                        'Artist_ID' : artist_info[0],
                        'Confidence' : confidence
                    }
                    ml_database.Insert_Genre_Artist_Query(genre_artist_table)
                for song in songs_artists[artist_info[0]]:
                    song_artist_table = {
                        'Song_ID' : song,
                        'Artist_ID' : artist_info[0],
                        'UTC_Day_ID' : utc_day_id
                    }
                    ml_database.Insert_Song_Artist_Query(song_artist_table)
            playlists = spotify_info['Playlists']
            songs_playlists = spotify_info['Songs_Playlists']
            for playlist_info in playlists:
                playlist_table = {
                    'Playlist_ID' : playlist_info[0],
                    'Playlist_name' : playlist_info[1]
                }
                user_playlist_table = {
                    'User_ID' : user_id,
                    'Playlist_ID' : playlist_info[0],
                    'UTC_Day_ID' : utc_day_id
                }
                ml_database.Insert_Playlist_Query(playlist_table)
                ml_database.Insert_Users_Playlists_Query(user_playlist_table)
                genres_playlists = genre_ml_classifier.get_playlist_genre(songs_playlists,playlist_info[0])
                if 'N/A' in genres_playlists: # This will only happen if the playlist is empty.
                    ml_database.Insert_Genre_Query('N/A')
                for genre,confidence in genres_playlists.items():
                    genre_id = ml_database.Get_Genre_ID_Query(genre)
                    genre_playlist_table = {
                        'Genre_ID' : genre_id,
                        'Playlist_ID' : playlist_info[0],
                        'Confidence' : confidence
                    }
                    ml_database.Insert_Genre_Playlist_Query(genre_playlist_table)
                if playlist_info[0] in songs_playlists:
                    for song in songs_playlists[playlist_info[0]]:
                        song_playlist_table = {
                            'Song_ID' : song,
                            'Playlist_ID' : playlist_info[0],
                            'UTC_Day_ID' : utc_day_id
                        }
                        ml_database.Insert_Songs_Playlist_Query(song_playlist_table)
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
    global curr_date
    utc_day_id = ml_database.Get_UTC_Day_ID_Query(curr_date)
    locations = ml_database.Get_Day_Locations(utc_day_id)
    for location_id in locations:
        zipcode,country =  ml_database.Get_Location_Data(location_id)
        longlat = sun_time.get_long_lat(zipcode, country)
        prev_weather_data = weather.get_prev_day_data(longlat['lat'],longlat['lng'])
        for hour_data in prev_weather_data:
            date = datetime.utcfromtimestamp(hour_data["dt"])
            utc_hour = date.strftime("%H:00")
            utc_day =  date.strftime("%m/%d/%Y")
            utc_day_id = ml_database.Get_UTC_Day_ID_Query(utc_day)
            utc_hour_id = ml_database.Get_UTC_Hour_ID_Query(utc_hour)
            weather_info = {
                'UTC_Day_ID'  : 1,
                'UTC_Hour_ID' : 1,
                'Temperature' : hour_data['temp'],
                'Feels_like'  : hour_data['feels_like'],
                'pressure'    : hour_data['pressure'],
                'humidity'    : 100.00 / float(hour_data['humidity']),
                'dew_point'   : hour_data['dew_point'],
                'cloudiness'  : 100.00 / float(hour_data['clouds']),
                'visibility'  : hour_data['visibility'],
                'wind_speed'  : hour_data['wind_speed'],
                'wind_gust'   : hour_data['wind_gust'] if 'wind_gust' in hour_data else None,
                'rain'        : hour_data['rain']['1h'] if 'rain' in hour_data else None,
                'snow'        : hour_data['snow']['1h'] if 'snow' in hour_data else None,
                'conditions_id' :hour_data['weather'][0]['id'],
                'conditions'  : hour_data['weather'][0]['description']
            }
            ml_database.Insert_Weather_Info(weather_info)
            weather_id =  ml_database.Get_Weather_ID(location_id,utc_day_id,utc_hour_id)
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
    status = 404
    success = False
    message = "Fields are incorrect"
    keys = ['user_id','zipcode','country']
    if all(key in request.form for key in keys): 
        user_id = request.form['user_id']
        zipcode = request.form['zipcode']
        country =  request.form['country']
        ml_database.Insert_Location_Query(zipcode,country)
        Location_ID =  ml_database.Get_Location_ID_Query(zipcode,country)
        ml_database.Update_User_Last_Location(Location_ID,user_id)
        user_location = ml_database.Get_User_Home_Location(user_id)
        if user_location[0] is 'ZipCode N/A':
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
    global curr_date
    users =  ml_database.Get_Users()
    for user_id in users:
        # if bool(ml_database.Get_User_NumRuns(user_id)) or (datetime.utcnow().minute == 15 and datetime.utcnow().hour == 0): # The first run per user must start at 0:00 UTC
        curr_time = int((time.time() * 1000))
        access_info = ml_database.Get_Access_Information(user_id)
        (new_access_token,new_last_refresh) = refresh_token.check_new_token(access_info['access_token'],access_info['refresh_token'],access_info['last_refreshed'])
        ml_database.Update_Access_information(user_id,new_access_token,new_last_refresh)
        recent_tracks = spotify.get_recent_tracks(new_access_token,after=curr_time-900000,id_only=True)# Did you FINISH any songs in the last 15 minutes.
        numHours = ml_database.Get_User_NumHours(user_id)
        numRuns = ml_database.Get_User_NumRuns(user_id)
        if numRuns == 0:
            ml_database.Insert_UTC_Day_Query(curr_date)
            utc_day_id =  ml_database.Get_UTC_Day_ID_Query(curr_date)
            data_per_date = {
                'UTC_Day_ID' : utc_day_id,
                'User_ID'    : user_id
            }
            ml_database.Insert_Day_Data(data_per_date)
        if numRuns % 4 == 0 and numRuns % 96 != 0: # Every hour move to a new Dict, we start on the first hour so we don't need to increment.
            numHours+= 1
            ml_database.Increment_NumHours(user_id)
        curr_hour = datetime.utcnow().strftime("%H:00")
        if ml_database.Check_DataCollectedPerHour(user_id,curr_date,curr_hour) is None: # We need to know the hour it was listened too so we can convert it to weather at the end.
            ml_database.Insert_UTC_Hour_Query(curr_hour)
            utc_hour_id = ml_database.Get_UTC_Hour_ID_Query(curr_hour)
            location_id = ml_database.Get_User_Last_Location_ID(user_id)
            utc_day_id =  ml_database.Get_UTC_Day_ID_Query(curr_date)
            data_date_id = ml_database.Get_User_Day_Data_ID(user_id,curr_date)
            zipcode,country = ml_database.Get_User_Last_Location(user_id)
            latlng = sun_time.get_long_lat(zipcode,country)
            curr_datetime = datetime.utcnow().strftime("%m/%d/%Y : %H:%M")
            timezone_id = ml_database.Get_TimeZone_ID_From_Location_Query(location_id)
            sun_position = sun_time.get_SunPosition(latlng['lat'], latlng['lng'], curr_datetime)
            time_period =  sun_time.getTimePeriod(latlng['lat'], latlng['lng'], curr_datetime)
            time_period_table = {
                'Time_Period' : time_period
            }
            ml_database.Insert_Time_Period(time_period_table)
            time_period_id = ml_database.Get_Time_Period_ID(time_period)
            timezone_hour_table = {
                'TimeZone_ID' : timezone_id,
                'UTC_Hour_ID' : utc_hour_id,
                'Time_Period_ID' : time_period_id
            }
            ml_database.Insert_TimeZone_Hour(timezone_hour_table)
            sun_position_table = {
                'Sun_Position' : sun_position
            }
            ml_database.Insert_Sun_Position(sun_position_table)
            sun_position_id = ml_database.Get_Sun_Position_ID(sun_position)
            data_hour_table = {
                'User_ID'  : user_id,
                'Location_ID' : location_id,
                'UTC_Hour_ID' : utc_hour_id,
                'UTC_Day_ID'  : utc_day_id,
                'SunPosition_ID' : sun_position_id,
                'DataCollectedPerDate_ID' : data_date_id,
                'Weather_Characteristics_ID' : None
            }
            ml_database.Insert_Hour_Data(data_hour_table)
        if bool(recent_tracks):
            for (track_id,track) in recent_tracks.items():
                is_new = ml_database.Check_User_Playlist_Songs(user_id,track_id) is None and ml_database.Check_User_Recent_Songs(user_id,track_id) is None
                curr_hour = datetime.utcnow().strftime("%H:00")
                data_hour_id = ml_database.Get_User_Hour_Data_ID(user_id,curr_hour,curr_date)
                if ml_database.Check_Data_Hour_Songs(user_id,track_id,data_hour_id) is not None:
                    ml_database.Increment_Data_Hour_Song_Played(data_hour_id,track_id)
                else:
                    data_hour_songs_table = {
                        'DataCollectedPerHour_ID' : data_hour_id,
                        'Song_ID' :track_id,
                        'numPlayed' : 1,
                        'isNew' : int(is_new)
                    }
                    ml_database.Insert_Data_Hour_Song(data_hour_songs_table)
                # We're only storing the songs we heard, the other songs the user in the user's playlist will be recorded as 0.
        numRuns += 1
        ml_database.Increment_NumRuns(user_id)
        if numRuns % 96 == 0 and numRuns != 0: # Every 15 minutes a day it incruments so in theory this should create a new date every day
            curr_date = datetime.utcnow().strftime("%m/%d/%Y")
            ml_database.Insert_UTC_Day_Query(curr_date)
            utc_day_id =  ml_database.Get_UTC_Day_ID_Query(curr_date)
            data_per_date = {
                'UTC_Day_ID' : utc_day_id,
                'User_ID'    : user_id
            }
            ml_database.Insert_Day_Data(data_per_date)
            ml_database.Set0_NumHours(user_id)
            try:
                resp = requests.get("http://localhost:5000/fill_weather")
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
    zipcode = weather.get_zipcode()
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
    app.run(use_reloader=True, debug=True, threaded=True,port=5000)
