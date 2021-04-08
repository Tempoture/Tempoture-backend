import requests
import sys
from rq import get_current_job
import time
from taskrunner import refresh_token
from datetime import datetime
sys.path.append("..")
from spotify_data import spotify,genre_ml_classifier
from database import spotify_database,ml_database

def store():
    try:
        local = f"https://backendtempoture.herokuapp.com/store_tracks"
        resp = requests.get(local)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))

def store_user_info(user_id,access_token,country):
    '''
    This takes a while to complete so it will be executed in the redis rq server background.

    '''
    job = get_current_job()

    spotify_info = spotify.get_all_songs_table_info(access_token,country)

    utc_day = datetime.utcnow().strftime("%m/%d/%Y")
    utc_day_id = spotify_database.Insert_UTC_Day_Info(utc_day)

    songs = spotify_info['Songs']
    spotify_database.Insert_Songs_Info(songs)

    ml_database.Update_User_Num_Songs(len(songs),user_id)

    user_genres = genre_ml_classifier.get_user_genre(songs)
    spotify_database.Insert_User_Genres_Info(user_id,user_genres,utc_day_id)

    recently_played_songs = spotify_info['Recently_Played_Songs']
    spotify_database.Insert_User_Recently_Played_Songs_Info(utc_day_id,user_id,recently_played_songs)

    artists = spotify_info['Artists']
    songs_artists = spotify_info['Songs_Artists']
    spotify_database.Insert_All_User_Artists_Info(utc_day_id,artists,songs_artists,user_id)
    playlists = spotify_info['Playlists']
    songs_playlists = spotify_info['Songs_Playlists']
    spotify_database.Insert_All_User_Playlists_Info(playlists,user_id,utc_day_id,songs_playlists)
    
    ml_database.Complete_Task(job.get_id())

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
    # TODO: Change this code to with NumHours initialized to -1.
    users =  ml_database.Get_Users()
    fill_prev_weather = False
    prev_date_id = -1
    for user_id in users:
        # if ml_database.Get_User_NumRuns(user_id) % 96 != 0 or (datetime.utcnow().minute == 15 and datetime.utcnow().hour == 0): # The first run per user must start at 0:00 UTC
        curr_time = int((time.time() * 1000))

        access_info = ml_database.Get_Access_Information(user_id)
        (new_access_token,new_last_refresh) = refresh_token.check_new_token(access_info['access_token'],access_info['refresh_token'],access_info['last_refreshed'])
        ml_database.Update_Access_information(user_id,new_access_token,new_last_refresh)

        recent_tracks = spotify.get_recent_tracks(new_access_token,after=curr_time-900000,id_only=True)# Did you FINISH any songs in the last 15 minutes.

        numHours = ml_database.Get_User_NumHours(user_id)
        numRuns = ml_database.Get_User_NumRuns(user_id)
        
        if numRuns == 0:
            utc_day_id = spotify_database.Insert_UTC_Day_Info(datetime.utcnow().strftime("%m/%d/%Y"))
            ml_database.Update_User_Curr_Data_Date_ID(utc_day_id,user_id)
            spotify_database.Insert_Data_Date_Info(utc_day_id,user_id)

        if numRuns % 4 == 0 and numRuns % 96 != 0: # Every hour move to a new Dict, we start on the first hour so we don't need to increment.
            numHours+= 1
            ml_database.Increment_NumHours(user_id)
            
        curr_date_id = ml_database.Get_User_Curr_Data_Date_ID(user_id)
        curr_hour_id = ml_database.Get_User_Curr_Data_Hour_ID(user_id)
        
        if numRuns % 4 == 0: # We need to know the hour it was listened too so we can convert it to weather at the end.
            curr_hour_id = spotify_database.Insert_UTC_Hour_Info(datetime.utcnow().strftime("%H:00"))
            ml_database.Update_User_Curr_Data_Hour_ID(curr_hour_id,user_id)
            location_id = ml_database.Get_User_Last_Location_ID(user_id)
            data_date_id = ml_database.Get_User_Day_Data_ID(user_id,curr_date_id)
            zipcode,country = ml_database.Get_User_Last_Location(user_id)

            spotify_database.Insert_Data_Hour_Info(user_id,location_id,curr_hour_id,data_date_id,curr_date_id)

            if zipcode != 'ZipCode N/A':
                spotify_database.Insert_Time_Data_Info(zipcode,country,location_id,curr_date_id,curr_hour_id)

        if bool(recent_tracks):
            spotify_database.Insert_User_Recent_Songs(recent_tracks,user_id,curr_date_id,curr_hour_id)
        numRuns += 1
        ml_database.Increment_NumRuns(user_id)
        if numRuns % 96 == 0 and numRuns != 0: # Every 15 minutes a day it incruments so in theory this should create a new date every day
            fill_prev_weather = True
            prev_date_id = curr_date_id
            utc_day_id = spotify_database.Insert_UTC_Day_Info(datetime.utcnow().strftime("%m/%d/%Y"))
            ml_database.Update_User_Curr_Data_Date_ID(utc_day_id,user_id)
            spotify_database.Insert_Data_Date_Info(utc_day_id,user_id)
            ml_database.Set0_NumHours(user_id)
            numHours = 0
    if fill_prev_weather:
        fill_weather(prev_date_id)

def fill_weather(prev_date_id):
    '''
    This will be called once per day after all the user's track information.
    Gets information for the previous day and fills in the weather for each hour.
    This is done BY ZIPCODE not by user to avoid too many calls to the weather API.
    '''
    locations = ml_database.Get_Day_Locations(prev_date_id)
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