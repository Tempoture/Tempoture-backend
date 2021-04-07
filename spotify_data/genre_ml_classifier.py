import sys
sys.path.append("..")
from database import ml_database
from joblib import load
from Genre_preprocessor import get_prediction,DropTransformer

def get_genres(song_info):
    '''
    Params:
    Song_info - A dictionary form of the song_table in the database.

    Returns:
    A dictionary of the top three genres in the form 
    Genre(str) : Confidence(float)
    Ex: 'Anime': 0.30

    '''
    song_genre_dict = song_info
    song_genre_dict['key'] = song_genre_dict['Song_key'] # In the table we call it Song_key because you can't have key as a column name
    del song_genre_dict['Song_key']
    del song_genre_dict['Song_ID']
    return get_prediction(song_genre_dict)


def get_playlist_genre(songs_playlists,playlist):
    '''
    Returns:
    A dictionary of the top three playlist genres in Genre confidence format or N/A is empty playlist.
    '''
    genre_occur = dict()
    if playlist in songs_playlists: # This is a check if there are no songs in that playlist.
        for song_id in songs_playlists[playlist]:
            genre_info = ml_database.Get_Song_Genre(song_id)
            for genre,confidence in genre_info.items():
                if genre in genre_occur:
                    genre_occur[genre]+= confidence
                else:
                    genre_occur[genre] = confidence
            normalized_genre = {genre: confidence / len(songs_playlists[playlist]) for genre, confidence in genre_occur.items()}
        return dict(sorted(normalized_genre.items(), key=lambda x: x[1], reverse=True)[:3]) # We get the top 3 genres for any playlist.
    else:# If there are no songs in the playlist return N/A
        genre_occur = {
            'N/A' : 1.00
        }
        return genre_occur


def get_artist_genre(songs_artists,artist):
    '''
    Returns:
    Top three artist genres in genre: confidence format.
    '''
    genre_occur = dict()
    for song_id in songs_artists[artist]:
        genre_info = ml_database.Get_Song_Genre(song_id)
        for genre,confidence in genre_info.items():
            if genre in genre_occur:
                genre_occur[genre]+= confidence
            else:
                genre_occur[genre] = confidence
    normalized_genre = {genre: confidence / len(songs_artists[artist]) for genre, confidence in genre_occur.items()}
    return dict(sorted(normalized_genre.items(), key=lambda x: x[1], reverse=True)[:3])


def get_user_genre(songs):
    '''
    Returns:
    Get the the users top 3 genres in genre: confidence format.
    '''
    genre_list = ['Classical', 'Comedy', 'R&B', 'Blues', 'Children’s Music', 'Rap',
       'Soul', 'Alternative', 'Soundtrack', 'Rock', 'Hip-Hop', 'Dance',
       'Electronic', 'World', 'Country', 'Anime', 'Pop', 'Reggaeton',
       'Reggae', 'Movie', 'Jazz', 'Folk', 'Opera', 'Ska']
    genre_dict = {genre: 0.0 for genre in genre_list}
    for song_id in songs:
        genre_info = ml_database.Get_Song_Genre(song_id)
        for genre,confidence in genre_info.items():
            if genre in genre_dict:
                genre_dict[genre]+= confidence
            else:
                genre_dict[genre] = confidence
    normalized_genre = {genre: confidence / len(songs) for genre, confidence in genre_dict.items()}
    return dict(sorted(normalized_genre.items(), key=lambda x: x[1], reverse=True)[:3])