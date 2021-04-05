import sys
sys.path.append("..")
from database import ml_database
from joblib import load
from Genre_preprocessor import get_prediction,DropTransformer

def get_genres(song_info):
    song_genre_dict = song_info
    song_genre_dict['key'] = song_genre_dict['Song_key'] # In the table we call it Song_key because you can't have key as a column name
    del song_genre_dict['Song_key']
    del song_genre_dict['Song_ID']
    return get_prediction(song_genre_dict)

def get_playlist_genre(songs_playlists,playlist):
    genre_occur = dict()
    if playlist in songs_playlists: # This is a check if there are no songs in that playlist.
        for song_id in songs_playlists[playlist]:
            genre_info = ml_database.Get_Song_Genre_Query(song_id)
            for genre,confidence in genre_info.items():
                if genre in genre_occur:
                    genre_occur[genre]+= confidence
                else:
                    genre_occur[genre] = confidence
        return dict(sorted(genre_occur.items(), key=lambda x: x[1], reverse=True)[:3])
    else:
        genre_occur = {
            'N/A' : 1.00
        }
        return genre_occur

def get_artist_genre(songs_artists,artist):
    genre_occur = dict()
    for song_id in songs_artists[artist]:
        genre_info = ml_database.Get_Song_Genre_Query(song_id)
        for genre,confidence in genre_info.items():
            if genre in genre_occur:
                genre_occur[genre]+= confidence
            else:
                genre_occur[genre] = confidence
    return dict(sorted(genre_occur.items(), key=lambda x: x[1], reverse=True)[:3])