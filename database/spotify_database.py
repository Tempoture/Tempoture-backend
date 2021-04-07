import sys
sys.path.append("..")
from taskrunner import sun_time
from database import ml_database
from datetime import datetime
from spotify_data import genre_ml_classifier


def Insert_Songs_Info(songs):
    '''
    Params:
    Songs- A dictionary of songs which should be given from spotify get all songs table info
    Return:None
    Inserts All songs into the songs table and their top three genres into the song_genres table.
    '''
    for song_id,song_info in songs.items():
        song_in_db = ml_database.Check_Song(song_id)
        if song_in_db is None:

            song_table_info = song_info
            song_table_info['Song_key'] = song_table_info['key'] # In the table we call it Song_key because you can't have key as a column name
            del song_table_info['key']
            song_table_info.update({
                'Song_ID' : song_id
            })

            ml_database.Insert_Song(song_table_info)

            genres = genre_ml_classifier.get_genres(song_info)
            Insert_Genres_Info(set(genres.keys()))
            Insert_Song_Genres_Info(song_id,genres)

def Insert_All_User_Artists_Info(utc_day_id,artists,songs_artists,user_id):
    '''
    Params: 
    utc_day_id -The id of the utc date.
    Artists -  List of tuples in (artist_id,artist_name) format.
    Songs_artists -Dictionary in Artist_Id :List of Songs format.
    User_ID - User Id.
    Inserts Artists into artist table, and user_artist table with corresponding date.
    Inserts all artists songs into artist_songs table.
    Gets top three artist genres.
    '''
    for artist_info in artists:
        
        Insert_Artist_Info(artist_info[0],artist_info[1])
        Insert_User_Artist_Info(artist_info[0],user_id,utc_day_id)

        Insert_Artist_Songs_Info(songs_artists[artist_info[0]],artist_info[0],utc_day_id)

        artist_genres = genre_ml_classifier.get_artist_genre(songs_artists,artist_info[0])
        Insert_Artist_Genres_Info(artist_genres,artist_info[0],utc_day_id)

def Insert_All_User_Playlists_Info(playlists,user_id,utc_day_id,songs_playlists):
    '''
    Params: 
    Playlists- List of tuples of playlists in (playlist_id,playlist_name) format.
    Songs_playlists - dictionary in playlist id : songs format.
    Inserts playlists into Playlist table, and user_playlist table with corresponding date.
    Inserts all playlist songs into playlist song table.
    Gets top three playlist genres.
    '''
    for playlist_info in playlists:
        Insert_Playlist_Info(playlist_info[0],playlist_info[1])
        Insert_User_Playlist_Info(user_id,playlist_info[0],utc_day_id)

        playlist_genres = genre_ml_classifier.get_playlist_genre(songs_playlists,playlist_info[0])
        if 'N/A' in playlist_genres: # This will only happen if the playlist is empty.
            Insert_Genres_Info(['N/A'])

        Insert_Playlist_Genres_Info(utc_day_id,playlist_info[0],playlist_genres)
        if playlist_info[0] in songs_playlists: # In case the playlist is empty.
            Insert_Playlist_Songs_Info(playlist_info[0],songs_playlists[playlist_info[0]],utc_day_id)


def Insert_Time_Data_Info(zipcode,country,location_id,utc_day_id,utc_hour_id):
    '''
    Inserts sun_position , time_period and the timezone into the correct tables.
    '''
    latlng = sun_time.get_long_lat(zipcode,country)
    curr_datetime = datetime.utcnow().strftime("%m/%d/%Y : %H:%M")

    timezone_id = ml_database.Get_TimeZone_ID_From_Location(location_id)

    time_period =  sun_time.getTimePeriod(latlng['lat'], latlng['lng'], curr_datetime)
    time_period_id = Insert_Time_Period_Info(time_period)

    Insert_TimeZone_Hour_Info(timezone_id,utc_hour_id,time_period_id)

    sun_position = sun_time.get_SunPosition(latlng['lat'], latlng['lng'], curr_datetime)
    sun_position_id = Insert_Sun_Position_Info(sun_position)

    Insert_Location_UTC_Day_Hour_Info(location_id,utc_day_id,utc_hour_id,sun_position_id)

def Insert_User_Recent_Songs(recent_tracks,user_id,curr_date):
    '''
    Insert recently listened songs into data_hour_songs table or increments the number of times it was played.
    '''
    for (track_id,track) in recent_tracks.items():
        is_new = ml_database.Check_User_Playlist_Songs(user_id,track_id) is None and ml_database.Check_User_Recent_Songs(user_id,track_id) is None
        curr_hour = datetime.utcnow().strftime("%H:00")
        data_hour_id = ml_database.Get_User_Hour_Data_ID(user_id,curr_hour,curr_date)
        if ml_database.Check_Data_Hour_Songs(user_id,track_id,data_hour_id) is not None:
            ml_database.Increment_Data_Hour_Song_Played(data_hour_id,track_id)
        else:
            Insert_Data_Hour_Song_Info(track_id,data_hour_id,is_new)

def Insert_User_Genres_Info(user_id,user_genres,utc_day_id):
    '''
    Inserts user's top three genres and the corresponding confidence levels.
    '''
    for genre,confidence in user_genres.items():
        genre_id = ml_database.Get_Genre_ID(genre)
        user_genre_table = {
            'User_ID'  : user_id,
            'Genre_ID' : genre_id,
            'UTC_Day_ID' : utc_day_id,
            'Confidence' : confidence
        }
        ml_database.Insert_User_Genres(user_genre_table)

def Insert_User_Recently_Played_Songs_Info(utc_day_id,user_id,recently_played_songs):
    for song in recently_played_songs:
        recently_played_songs_user_table = {
            'Song_ID' : song,
            'User_ID' : user_id,
            'UTC_Day_ID' : utc_day_id
        }
        ml_database.Insert_Recently_Played_Songs_User(recently_played_songs_user_table)

def Insert_Genres_Info(genres):
    for genre in genres:
        genre_table = {
            'Genre' : genre
        }
        ml_database.Insert_Genre(genre_table)

def Insert_Song_Genres_Info(song_id,genres):
    for genre,confidence in genres.items():
        genre_id = ml_database.Get_Genre_ID(genre)
        song_genre_table = {
            'Song_ID'  : song_id,
            'Genre_ID' : genre_id,
            'Confidence' : confidence
        }
        ml_database.Insert_Song_Genre(song_genre_table)

def Insert_Artist_Genres_Info(genres_artists,artist_id,utc_day_id):
    for genre,confidence in genres_artists.items():
        genre_id = ml_database.Get_Genre_ID(genre)
        genre_artist_table = {
            'Genre_ID' : genre_id,
            'Artist_ID' : artist_id,
            'UTC_Day_ID' : utc_day_id,
            'Confidence' : confidence
        }
        ml_database.Insert_Genre_Artist(genre_artist_table)

def Insert_Artist_Songs_Info(songs_artists,artist_id,utc_day_id):
    for song in songs_artists:
        song_artist_table = {
            'Song_ID' : song,
            'Artist_ID' : artist_id,
            'UTC_Day_ID' : utc_day_id
        }
        ml_database.Insert_Song_Artist(song_artist_table)

def Insert_Playlist_Songs_Info(playlist_id,songs_playlists,utc_day_id):
    for song in songs_playlists:
        song_playlist_table = {
            'Song_ID' : song,
            'Playlist_ID' : playlist_id,
            'UTC_Day_ID' : utc_day_id
        }
        ml_database.Insert_Songs_Playlist(song_playlist_table)

def Insert_Playlist_Genres_Info(utc_day_id,playlist_id,genres_playlists):
    for genre,confidence in genres_playlists.items():
        genre_id = ml_database.Get_Genre_ID(genre)
        genre_playlist_table = {
            'Genre_ID' : genre_id,
            'Playlist_ID' : playlist_id,
            'UTC_Day_ID' : utc_day_id,
            'Confidence' : confidence
        }
        ml_database.Insert_Genre_Playlist(genre_playlist_table)


def Insert_Playlist_Info(playlist_name,playlist_id):
    playlist_table = {
        'Playlist_ID' : playlist_name,
        'Playlist_name' : playlist_id
    }
    ml_database.Insert_Playlist(playlist_table)

def Insert_User_Playlist_Info(user_id,playlist_id,utc_day_id):
    user_playlist_table = {
        'User_ID' : user_id,
        'Playlist_ID' : playlist_id,
        'UTC_Day_ID' : utc_day_id
    }
    ml_database.Insert_Users_Playlists(user_playlist_table)

def Insert_Artist_Info(artist_id,artist_name):
    artist_table = {
        'Artist_ID' : artist_id,
        'Artist_name' : artist_name
    }
    ml_database.Insert_Artist(artist_table)

def Insert_User_Artist_Info(artist_id,user_id,utc_day_id):
    user_artist_table = {
        'User_ID' : user_id,
        'Artist_ID' : artist_id,
        'UTC_Day_ID' : utc_day_id
    }
    ml_database.Insert_Users_Artists(user_artist_table)

def Insert_TimeZone_Info(timezone_name):
    timezone_table = {
        'TimeZone_name' : timezone_name
    }
    ml_database.Insert_TimeZone(timezone_table)
    timezone_id = ml_database.Get_TimeZone_ID(timezone_name)
    return timezone_id

def Insert_Location_Info(zipcode,country):
    location_table = {
        'TimeZone_ID' : None,
        'Zipcode' : zipcode,
        'Country' : country
    }
    if zipcode != 'ZipCode N/A':
        latlong = sun_time.get_long_lat(zipcode, country)
        timezone_name = sun_time.getTimeZone(latlong['lat'],latlong['lng'])
        location_table['TimeZone_ID'] = Insert_TimeZone_Info(timezone_name)
    ml_database.Insert_Location(location_table)
    location_id = ml_database.Get_Location_ID(zipcode,country)
    return location_id

def Insert_UTC_Day_Info(utc_day):
    utc_day_table = {
        'UTC_Day' : utc_day
    }
    ml_database.Insert_UTC_Day(utc_day_table)
    utc_day_id = ml_database.Get_UTC_Day_ID(utc_day)
    return utc_day_id

def Insert_UTC_Hour_Info(utc_hour):
    utc_hour_table = {
        'UTC_Hour' : utc_hour
    }
    ml_database.Insert_UTC_Hour(utc_hour_table)
    utc_hour_id = ml_database.Get_UTC_Hour_ID(utc_hour)
    return utc_hour_id

def Insert_User_Info(user_id,access_token,refresh_token,last_refresh,display_name,location_id,numSongs):
    user_table = {
                'Display_name' : display_name,
                'Last_Known_Location_ID' : location_id,
                'Home_Location_ID' : location_id,
                'numRuns'  : 0,
                'numSongs' : numSongs,
                'numHours' : 0,
                'access_token'   : access_token,
                'refresh_token'  : refresh_token,
                'last_refreshed' : last_refresh,
                'User_ID' : user_id
            }
    ml_database.Insert_User(user_table)

def Insert_Weather_Info(hour_data,utc_day_id,utc_hour_id,location_id):
    weather_info = {
        'UTC_Day_ID'  : utc_day_id,
        'UTC_Hour_ID' : utc_hour_id,
        'Location_ID' : location_id,
        'Temperature' : hour_data['temp'],
        'Feels_like'  : hour_data['feels_like'],
        'pressure'    : hour_data['pressure'],
        'humidity'    : 100.00 / float(hour_data['humidity']), # This is given in a percentage so we have to conver it.
        'dew_point'   : hour_data['dew_point'],
        'cloudiness'  : 100.00 / float(hour_data['clouds']), # Same as above.
        'visibility'  : hour_data['visibility'],
        'wind_speed'  : hour_data['wind_speed'],
        'wind_gust'   : hour_data['wind_gust'] if 'wind_gust' in hour_data else None,
        'wind_deg'    : hour_data['wind_deg'],
        'rain'        : hour_data['rain']['1h'] if 'rain' in hour_data else None,
        'snow'        : hour_data['snow']['1h'] if 'snow' in hour_data else None,
        'conditions_id' :hour_data['weather'][0]['id'],
        'conditions'  : hour_data['weather'][0]['description']
    }
    ml_database.Insert_Weather(weather_info)
    weather_id =  ml_database.Get_Weather_ID(location_id,utc_day_id,utc_hour_id)
    return weather_id

def Insert_Sun_Position_Info(sun_position):
    sun_position_table = {
        'Sun_Position' : sun_position
    }
    ml_database.Insert_Sun_Position(sun_position_table)
    sun_position_id = ml_database.Get_Sun_Position_ID(sun_position)
    return sun_position_id

def Insert_Time_Period_Info(time_period):
    time_period_table = {
        'Time_Period' : time_period
    }
    ml_database.Insert_Time_Period(time_period_table)
    time_period_id = ml_database.Get_Time_Period_ID(time_period)
    return time_period_id

def Insert_TimeZone_Hour_Info(timezone_id,utc_hour_id,time_period_id):
    timezone_hour_table = {
        'TimeZone_ID' : timezone_id,
        'UTC_Hour_ID' : utc_hour_id,
        'Time_Period_ID' : time_period_id
    }
    ml_database.Insert_TimeZone_Hour(timezone_hour_table)

def Insert_Location_UTC_Day_Hour_Info(location_id,utc_day_id,utc_hour_id,sun_position_id):
    location_day_hour_table = {
        'Location_ID' : location_id,
        'UTC_Hour_ID' : utc_hour_id,
        'UTC_Day_ID'  : utc_day_id,
        'Sun_Position_ID' : sun_position_id
    }
    ml_database.Insert_Location_UTC_Day_Hour(location_day_hour_table)

def Insert_Data_Date_Info(utc_day_id,user_id):
    data_per_date = {
        'UTC_Day_ID' : utc_day_id,
        'User_ID'    : user_id
    }
    ml_database.Insert_Day_Data(data_per_date)
    data_date_id = ml_database.Get_User_Day_Data_ID(user_id,utc_day_id)
    return data_date_id

def Insert_Data_Hour_Info(user_id,location_id,utc_hour_id,data_date_id,utc_day_id):
    data_hour_table = {
        'User_ID'  : user_id,
        'Location_ID' : location_id,
        'UTC_Hour_ID' : utc_hour_id,
        'UTC_Day_ID'  : utc_day_id,
        'DataCollectedPerDate_ID' : data_date_id,
        'Weather_Characteristics_ID' : None
    }
    ml_database.Insert_Hour_Data(data_hour_table)
    data_hour_id = ml_database.Get_User_Hour_Data_ID(user_id,utc_hour_id,utc_day_id)
    return data_hour_id

def Insert_Data_Hour_Song_Info(track_id,data_hour_id,is_new):
    data_hour_songs_table = {
        'DataCollectedPerHour_ID' : data_hour_id,
        'Song_ID' :track_id,
        'numPlayed' : 1,
        'isNew' : int(is_new)
    }
    ml_database.Insert_Data_Hour_Song(data_hour_songs_table)
