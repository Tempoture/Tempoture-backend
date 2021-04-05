import requests
import json
from datetime import datetime

# Get the Current User's Recently Played Tracks (50)
RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
PLAYLISTS_ENDPOINT =  'https://api.spotify.com/v1/me/playlists'

# https://developer.spotify.com/web-api/web-api-personalization-endpoints/get-recently-played
# Access Token requires scope: user-read-recently-played
def get_recent_tracks(access_token,after=None,limit=None,id_only=False):
    url = RECENT_TRACKS_ENDPOINT
    if after is not None:
        url += ('&after=' + str(after))
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    resp = requests.get(url, headers=auth_header)
    resp.raise_for_status()
    if id_only:
        song_id = dict()
        for track in resp.json()["items"]:
            song_id[track['track']['id']] = {'name' : track['track']['name'],'Finished_at' : track['played_at']}
        return song_id
    return resp.json()

def get_current_user_playlists(access_token):
    url = PLAYLISTS_ENDPOINT
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def chunks(lst, n): # We have to split our playlist requests in chunks of 50
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def validate_full(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_month(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m')
        return True
    except ValueError:
        return False

def get_songs_audio_features(access_token,song_id,extra_info):
    song_id_req = list(chunks(list(song_id),50)) # In case they have more than 50 songs which is likely we need to split requests up into batches of 50.
    audio_dict = dict()
    for req in song_id_req:
        id_str =  ",".join(req)
        req_endpoint = f'https://api.spotify.com/v1/audio-features/?ids={id_str}'
        auth_header = {"Authorization": "Bearer {}".format(access_token)}
        audio_j = ""
        try:
            resp =requests.get(req_endpoint, headers=auth_header)
            resp.raise_for_status()
            audio_j = resp.json()
            temp_d = {}
            for a in audio_j['audio_features']:
                temp_d[a['id']] = a
                temp_d[a['id']].pop('type', None)
                temp_d[a['id']].pop('uri', None)
                temp_d[a['id']].pop('analysis_url', None)
                temp_d[a['id']].pop('track_href', None)
                temp_d[a['id']]['Song_name'] = extra_info[a['id']]['name']
                temp_d[a['id']]['popularity'] = extra_info[a['id']]['popularity']
                release_year = datetime.now().year
                if validate_full(extra_info[a['id']]['release_date']):
                    release_year =  datetime.strptime(extra_info[a['id']]['release_date'],"%Y-%m-%d").year
                elif validate_month(extra_info[a['id']]['release_date']):
                    release_year =  datetime.strptime(extra_info[a['id']]['release_date'],"%Y-%m").year
                elif extra_info[a['id']]['release_date'] != '0000':
                    release_year =  datetime.strptime(extra_info[a['id']]['release_date'],"%Y").year
                temp_d[a['id']]['release_year'] = release_year
                temp_d[a['id']]['is_explicit'] = int(extra_info[a['id']]['is_explicit'])
                temp_d[a['id']].pop('id', None)
            audio_dict.update(temp_d)
        except requests.exceptions.HTTPError as err:
            print("ERR:" + str(err))
    return audio_dict

def get_all_songs_table_info(access_token,market_id):
    songs_playlists = dict()
    songs = set() # Avoid duplicates between songs
    extra_info = dict()
    artist_songs = dict()
    playlists = list()
    artists = set()
    rjson = get_current_user_playlists(access_token)
    playlists_resp = rjson["items"]

    # Getting Playlists table info and the corresponding artists info.
    for playlist in playlists_resp:  
        auth_header = {"Authorization": "Bearer {}".format(access_token)}
        req_endpoint = f"https://api.spotify.com/v1/playlists/{playlist['id']}/tracks?market={market_id}"
        playlists.append((playlist['id'],playlist['name']))
        try:
            resp =requests.get(req_endpoint, headers=auth_header)
            resp.raise_for_status()
            for track in resp.json()['items']:
                songs.add(track['track']['id'])
                for artist in track['track']['artists']:
                    artists.add((artist['id'],artist['name']))
                    if artist['id'] not in artist_songs:
                        artist_songs[artist['id']] = list()                        
                    artist_songs[artist['id']].append(track['track']['id'])
                if playlist['id'] not in songs_playlists:
                    songs_playlists[playlist['id']] = list()
                songs_playlists[playlist['id']].append(track['track']['id'])
                extra_info[track['track']['id']] = {
                    'name' : track['track']['name'],
                    'is_explicit' : track['track']['explicit'],
                    'popularity' : track['track']['popularity'],
                    'release_date' : track['track']['album']['release_date']
                }
        except requests.exceptions.HTTPError as err:
            print("ERR:" + str(err))
    recently_played_songs = list()
    try:
        resp = get_recent_tracks(access_token)
        for track in resp["items"]:
            songs.add(track['track']['id'])
            if track['track']['id'] not in songs_playlists:
                for artist in track['track']['artists']:
                    artists.add((artist['id'],artist['name']))
                    if artist['id'] not in artist_songs:
                        artist_songs[artist['id']] = list()                        
                    artist_songs[artist['id']].append(track['track']['id'])
                recently_played_songs.append(track['track']['id'])
                extra_info[track['track']['id']] = {
                    'name' : track['track']['name'],
                    'is_explicit' : track['track']['explicit'],
                    'popularity' : track['track']['popularity'],
                    'release_date' : track['track']['album']['release_date']
                }
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))
    songs_features = get_songs_audio_features(access_token,songs,extra_info)
    return_dict = {
        'Recently_Played_Songs' : recently_played_songs,
        'Playlists' : playlists,
        'Songs_Playlists' :songs_playlists,
        'Songs' : songs_features,
        'Artists' : list(artists),
        'Songs_Artists' : artist_songs
    }
    return return_dict