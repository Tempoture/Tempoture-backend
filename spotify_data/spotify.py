import requests
import json

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

def get_all_songs_audio(access_token,market_id):
    song_id = set()
    name_id = dict()
    try:
        resp = get_recent_tracks(access_token)
        for track in resp["items"]:
            song_id.add(track['track']['id'])
            name_id[track['track']['id']] = track['track']['name']
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))
    rjson = get_current_user_playlists(access_token)
    playlists = rjson["items"]
    for playlist in playlists:
        auth_header = {"Authorization": "Bearer {}".format(access_token)}
        req_endpoint = f"https://api.spotify.com/v1/playlists/{playlist['id']}/tracks?market={market_id}"
        try:
            resp =requests.get(req_endpoint, headers=auth_header)
            resp.raise_for_status()
            for track in resp.json()["items"]:
                song_id.add(track['track']['id'])
                name_id[track['track']['id']] = track['track']['name']
        except requests.exceptions.HTTPError as err:
            print("ERR:" + str(err))
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
                temp_d[a['id']]['name'] = name_id[a['id']]
                temp_d[a['id']].pop('id', None)
            audio_dict.update(temp_d)
        except requests.exceptions.HTTPError as err:
            print("ERR:" + str(err))
    return audio_dict
    

