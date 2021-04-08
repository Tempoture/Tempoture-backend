import pyodbc
import os
from dotenv import load_dotenv
import pandas as pd
import sys
sys.path.append("..")
from taskrunner import sun_time
import requests

server = '<server>.database.windows.net'
database = '<database>'
username = '<username>'
password = '<password>'   
driver= '{ODBC Driver 17 for SQL Server}'
GOOGLE_MAP_KEY = ''
try: 
    server = os.environ['ML_DATABASE_SERVER']
    database = os.environ['ML_DATABASE_NAME']
    username = os.environ['ML_DATABASE_USER_ID']
    password = os.environ['ML_DATABASE_PASSWORD']
    GOOGLE_MAP_KEY = os.environ['GOOGLE_MAP_KEY']
except Exception: 
    load_dotenv()
    server = os.getenv('ML_DATABASE_SERVER')
    database = os.getenv('ML_DATABASE_NAME')
    username = os.getenv('ML_DATABASE_USER_ID')
    password = os.getenv('ML_DATABASE_PASSWORD')
    GOOGLE_MAP_KEY = os.getenv('GOOGLE_MAP_KEY')


# TODO: Potentially use an ORM Like SQL Alchemy  to turn this into an object structure instead.
# TODO: UNIT TEST insert methods on tables with no foreign keys
# TODO: Integration tests for all the other methods.
with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password,autocommit=True) as conn:
    
    def Update_Data_Hour_Per_Location_Weather(Location_ID,UTC_Day_ID,UTC_Hour_ID,Weather_Characteristics_ID):
        query_string = f"UPDATE DataCollectedPerHour SET Weather_Characteristics_ID = {Weather_Characteristics_ID} WHERE UTC_Day_ID = {UTC_Day_ID} AND UTC_Hour_ID = {UTC_Hour_ID} AND Location_ID = {Location_ID}"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Update_User_Last_Location(Location_ID,User_ID):
        query_string = f"UPDATE Users SET Last_Known_Location_ID = {Location_ID} WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Update_User_Num_Songs(numSongs,User_ID):
        query_string = f"UPDATE Users SET numSongs = {numSongs} WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)

    
    def Update_Access_information(User_ID,access_token,last_refreshed):
        query_string =  f"UPDATE Users SET access_token = '{access_token}',last_refreshed = {last_refreshed} WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)

        
    def Update_User_Home_Location(Location_ID,User_ID):
        query_string = f"UPDATE Users SET Home_Location_ID = {Location_ID} WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Set0_NumHours(User_ID):
        query_string =  f"UPDATE Users SET numHours= 0 WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Complete_Task(Task_ID):
        query_string = f"UPDATE Tasks SET Complete = 1 WHERE Task_ID = '{Task_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Increment_NumHours(User_ID):
        query_string =  f"UPDATE Users SET numHours=numHours + 1 WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Increment_NumRuns(User_ID):
        query_string =  f"UPDATE Users SET numRuns=numRuns + 1 WHERE User_ID = '{User_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    def Increment_Data_Hour_Song_Played(DataCollectedPerHour_ID,Song_ID):
        query_string = f"UPDATE DataCollectedPerHour_Songs SET numPlayed = numPlayed + 1 WHERE DataCollectedPerHour_ID = {DataCollectedPerHour_ID} AND Song_ID = '{Song_ID}'; "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
    
    
    def Check_User(user):
        query_string = f"SELECT User_ID FROM Users WHERE User_ID = '{user}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row
    
    def Check_Song(song):
        query_string = f"SELECT Song_ID FROM Songs WHERE Song_ID = '{song}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row
    
    def Check_DataCollectedPerHour(User_ID,date,hour):
        query_string = f"SELECT *  FROM DataCollectedPerHour A inner join UTC_Day B on A.UTC_Day_ID = B.UTC_Day_ID inner join UTC_Hour C on A.UTC_Hour_ID = C.UTC_Hour_ID WHERE C.UTC_Hour = '{hour}' AND B.UTC_Day = '{date}' AND A.User_ID = '{User_ID}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row
    
    def Check_User_Playlist_Songs(User_ID,Song_ID):
        query_string = f"SELECT B.Song_ID FROM Users_Playlists A inner join  Songs_Playlists B on A.Playlist_ID = B.Playlist_ID WHERE A.User_ID = '{User_ID}' AND B.Song_ID ='{Song_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row

    def Check_User_Recent_Songs(User_ID,Song_ID):
        query_string = f"SELECT Song_ID FROM RecentlyPlayedSongs_User WHERE User_ID = '{User_ID}' AND Song_ID = '{Song_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row
    
    def Check_Data_Hour_Songs(User_ID,Song_ID,DataCollectedPerHour_ID):
        query_string = f"SELECT Song_ID FROM DataCollectedPerHour_Songs WHERE DataCollectedPerHour_ID = {DataCollectedPerHour_ID} AND Song_ID = '{Song_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row

    def Get_User_Playlist_Songs(User_ID):
        query_string = f"SELECT B.Song_ID FROM Users_Playlists A inner join  Songs_Playlists B on A.Playlist_ID = B.Playlist_ID WHERE A.User_ID = '{User_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            playlist_songs = [row[0] for row in cursor.fetchall()]
            return playlist_songs

    def Get_Users():
        query_string = f"SELECT USER_ID FROM Users;"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            users = [row[0] for row in cursor.fetchall()]
            return users

    def Get_Location_Data(Location_ID):
        location_query_string = f"SELECT Zipcode,Country FROM Location WHERE Location_ID = {Location_ID}"
        with conn.cursor() as cursor:
            cursor.execute(location_query_string)
            row = cursor.fetchone()
            return row
    
    def Get_User_NumRuns(User_ID):
        query_string = f"SELECT numRuns FROM Users WHERE User_ID='{User_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]

    def Get_User_NumHours(User_ID):
        query_string = f"SELECT numHours FROM Users WHERE User_ID='{User_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_Access_Information(User_ID):
        query_string = f"SELECT access_token,refresh_token,last_refreshed FROM Users WHERE User_ID='{User_ID}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            access_info = {
                'access_token'  : row[0],
                'refresh_token' : row[1],
                'last_refreshed': row[2]
            }
            return access_info
    
    def Get_Day_Locations(UTC_Day_ID):
        query_string = f"SELECT DISTINCT Location_ID FROM DataCollectedPerHour WHERE UTC_DAY_ID = {UTC_Day_ID}"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            locations = [row[0] for row in cursor.fetchall()]
            return locations
    
    def Get_Song_Genre(song_id):
        query_string = f"SELECT A.Song_ID,B.Genre,A.Confidence FROM Song_Genres A inner join Genres B on A.Genre_ID = B.Genre_ID WHERE Song_ID='{song_id}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            genre_dict = {row[1]:float(row[2]) for row in cursor.fetchall()}
            return genre_dict
    
    def Get_User_Home_Location(User_ID):
        query_string = f"SELECT Home_Location_ID FROM Users WHERE User_ID = '{User_ID}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            location_id = cursor.fetchone()
            location_query_string = f"SELECT Zipcode,Country FROM Location WHERE Location_ID = {location_id[0]}"
            cursor.execute(location_query_string)
            location_data = cursor.fetchone()
            return location_data
    
    def Get_User_Last_Location(User_ID):
        query_string = f"SELECT Last_Known_Location_ID FROM Users WHERE User_ID = '{User_ID}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            location_id = cursor.fetchone()
            location_query_string = f"SELECT Zipcode,Country FROM Location WHERE Location_ID = {location_id[0]}"
            cursor.execute(location_query_string)
            location_data = cursor.fetchone()
            return location_data
        
    def Get_TimeZone_ID(timezone_name):
        query_string = f"SELECT TimeZone_ID FROM TimeZone WHERE TimeZone_name = '{timezone_name}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_TimeZone_ID_From_Location(location_id):
        query_string = f'SELECT TimeZone_ID FROM Location WHERE Location_ID = {location_id};'
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_User_Day_Data_ID(User_ID,date_id):
        query_string = f"SELECT DataCollectedPerDate_ID FROM DataCollectedPerDate WHERE User_ID = '{User_ID}' AND UTC_Day_ID = '{date_id}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_User_Hour_Data_ID(User_ID,hour_id,date_id):
        query_string = f"SELECT DataCollectedPerHour_ID FROM DataCollectedPerHour WHERE User_ID = '{User_ID}' AND UTC_Hour_ID = '{hour_id}' AND UTC_Day_ID = '{date_id}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_User_Last_Location_ID(User_ID):
        query_string = f"SELECT Last_Known_Location_ID FROM Users WHERE User_ID = '{User_ID}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            location_id = cursor.fetchone()
            return location_id[0]

    
    def Get_Location_ID(zipcode,country):
        query_string = f"SELECT Location_ID FROM Location WHERE zipcode = '{zipcode}' AND country = '{country}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_UTC_Day_ID(utc_day):
        query_string = f"SELECT UTC_Day_ID FROM UTC_Day WHERE UTC_Day = '{utc_day}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_UTC_Hour_ID(utc_hour):
        query_string = f"SELECT UTC_Hour_ID FROM UTC_Hour WHERE UTC_Hour = '{utc_hour}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_Genre_ID(genre):
        query_string = f"SELECT Genre_ID FROM Genres WHERE Genre = '{genre}'"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_Time_Period_ID(time_period):
        query_string = f"SELECT Time_Period_ID FROM Time_Period WHERE Time_Period = '{time_period}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_Sun_Position_ID(sun_position):
        query_string = f"SELECT Sun_Position_ID FROM Sun_Position WHERE Sun_Position = '{sun_position}';"
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Get_Weather_ID(Location_ID,UTC_Day_ID,UTC_Hour_ID):
        query_string = f"SELECT Weather_Characteristics_ID FROM Weather_Characteristics WHERE Location_ID = {Location_ID} AND UTC_Day_ID  = {UTC_Day_ID} AND UTC_Hour_ID = {UTC_Hour_ID} "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]

    def Get_Task_Type_ID(task_type):
        query_string = f"SELECT Task_Type_ID FROM Task_Type WHERE Task_Type = '{task_type}' "
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            row = cursor.fetchone()
            return row[0]
    
    def Insert_Task(task_info):
        columns = ', '.join(task_info.keys())
        placeholders = ', '.join('?' * len(task_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in task_info.values()]
        query_string = f"INSERT INTO Tasks ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_Task_Type(task_type_info):
        columns = ', '.join(task_type_info.keys())
        placeholders = ', '.join('?' * len(task_type_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in task_type_info.values()]
        query_string = f"INSERT INTO Task_Type ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
            
    def Insert_Location(location_info):
        columns = ', '.join(location_info.keys())
        placeholders = ', '.join('?' * len(location_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in location_info.values()]
        query_string = f"INSERT INTO Location ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_TimeZone(timezone_info):
        columns = ', '.join(timezone_info.keys())
        placeholders = ', '.join('?' * len(timezone_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in timezone_info.values()]
        query_string = f"INSERT INTO TimeZone ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_UTC_Day(utc_day_info):
        columns = ', '.join(utc_day_info.keys())
        placeholders = ', '.join('?' * len(utc_day_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in utc_day_info.values()]
        query_string = f"INSERT INTO UTC_Day ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_UTC_Hour(utc_hour_info):
        columns = ', '.join(utc_hour_info.keys())
        placeholders = ', '.join('?' * len(utc_hour_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in utc_hour_info.values()]
        query_string = f"INSERT INTO UTC_Hour ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Genre(genre_info):
        columns = ', '.join(genre_info.keys())
        placeholders = ', '.join('?' * len(genre_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in genre_info.values()]
        query_string = f"INSERT INTO Genres ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Weather(weather_info):
        columns = ', '.join(weather_info.keys())
        placeholders = ', '.join('?' * len(weather_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in weather_info.values()]
        query_string = f"INSERT INTO Weather_Characteristics ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Data_Hour_Song(data_hour_songs_info):
        columns = ', '.join(data_hour_songs_info.keys())
        placeholders = ', '.join('?' * len(data_hour_songs_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in data_hour_songs_info.values()]
        query_string = f"INSERT INTO DataCollectedPerHour_Songs ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_TimeZone_Hour(timezone_hour_info):
        columns = ', '.join(timezone_hour_info.keys())
        placeholders = ', '.join('?' * len(timezone_hour_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in timezone_hour_info.values()]
        query_string = f"INSERT INTO TimeZone_UTC_Hour ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_Sun_Position(sun_position_info):
        columns = ', '.join(sun_position_info.keys())
        placeholders = ', '.join('?' * len(sun_position_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in sun_position_info.values()]
        query_string = f"INSERT INTO Sun_Position ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_Location_UTC_Day_Hour(location_day_hour_info):
        columns = ', '.join(location_day_hour_info.keys())
        placeholders = ', '.join('?' * len(location_day_hour_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in location_day_hour_info.values()]
        query_string = f"INSERT INTO Location_UTC_Day_Hour ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Time_Period(time_period_info):
        columns = ', '.join(time_period_info.keys())
        placeholders = ', '.join('?' * len(time_period_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in time_period_info.values()]
        query_string = f"INSERT INTO Time_Period ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Day_Data(day_info):
        columns = ', '.join(day_info.keys())
        placeholders = ', '.join('?' * len(day_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in day_info.values()]
        query_string = f"INSERT INTO DataCollectedPerDate ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_Hour_Data(hour_info):
        columns = ', '.join(hour_info.keys())
        placeholders = ', '.join('?' * len(hour_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in hour_info.values()]
        query_string = f"INSERT INTO DataCollectedPerHour ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_User(user_information):
        columns = ', '.join(user_information.keys())
        placeholders = ', '.join('?' * len(user_information.keys()))
        columns = columns.replace("'","")
        values = [x for x in user_information.values()]
        query_string = f"INSERT INTO Users ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Song(song_info):
        columns = ', '.join(song_info.keys())
        placeholders = ', '.join('?' * len(song_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in song_info.values()]
        query_string = f"INSERT INTO Songs ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Song_Genre(song_genre_info):
        columns = ', '.join(song_genre_info.keys())
        placeholders = ', '.join('?' * len(song_genre_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in song_genre_info.values()]
        query_string = f"INSERT INTO Song_Genres ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Song_Artist(song_artist_info):
        columns = ', '.join(song_artist_info.keys())
        placeholders = ', '.join('?' * len(song_artist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in song_artist_info.values()]
        query_string = f"INSERT INTO Songs_Artists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Songs_Playlist(song_playlist_info):
        columns = ', '.join(song_playlist_info.keys())
        placeholders = ', '.join('?' * len(song_playlist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in song_playlist_info.values()]
        query_string = f"INSERT INTO Songs_Playlists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Artist(artist_info):
        columns = ', '.join(artist_info.keys())
        placeholders = ', '.join('?' * len(artist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in artist_info.values()]
        query_string = f"INSERT INTO Artists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Genre_Artist(genre_artist_info):
        columns = ', '.join(genre_artist_info.keys())
        placeholders = ', '.join('?' * len(genre_artist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in genre_artist_info.values()]
        query_string = f"INSERT INTO Genres_Artists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Playlist(playlist_info):
        columns = ', '.join(playlist_info.keys())
        placeholders = ', '.join('?' * len(playlist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in playlist_info.values()]
        query_string = f"INSERT INTO Playlists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Genre_Playlist(genre_playlist_info):
        columns = ', '.join(genre_playlist_info.keys())
        placeholders = ', '.join('?' * len(genre_playlist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in genre_playlist_info.values()]
        query_string = f"INSERT INTO Genres_Playlists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)
    
    def Insert_Recently_Played_Songs_User(recently_played_info):
        columns = ', '.join(recently_played_info.keys())
        placeholders = ', '.join('?' * len(recently_played_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in recently_played_info.values()]
        query_string = f"INSERT INTO RecentlyPlayedSongs_User ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Users_Artists(user_artist_info):
        columns = ', '.join(user_artist_info.keys())
        placeholders = ', '.join('?' * len(user_artist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in user_artist_info.values()]
        query_string = f"INSERT INTO Users_Artists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_Users_Playlists(user_playlist_info):
        columns = ', '.join(user_playlist_info.keys())
        placeholders = ', '.join('?' * len(user_playlist_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in user_playlist_info.values()]
        query_string = f"INSERT INTO Users_Playlists ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)

    def Insert_User_Genres(user_genre_info):
        columns = ', '.join(user_genre_info.keys())
        placeholders = ', '.join('?' * len(user_genre_info.keys()))
        columns = columns.replace("'","")
        values = [x for x in user_genre_info.values()]
        query_string = f"INSERT INTO Users_Genres ({columns}) VALUES ({placeholders});"
        with conn.cursor() as cursor:
            cursor.execute(query_string,values)