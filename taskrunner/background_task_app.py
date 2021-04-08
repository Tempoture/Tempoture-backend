import requests
import sys
from rq import get_current_job
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

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        if progress >= 100:
            task.complete = True
        db.session.commit()

def store_user_info(user_id,access_token,country):
    job = get_current_job()

    spotify_info = spotify.get_all_songs_table_info(access_token,country)
    print("SONGS RECEIVED")
    utc_day = datetime.utcnow().strftime("%m/%d/%Y")
    utc_day_id = spotify_database.Insert_UTC_Day_Info(utc_day)

    songs = spotify_info['Songs']
    spotify_database.Insert_Songs_Info(songs)
    print("SONGS STORED")

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
    print("Completed")
