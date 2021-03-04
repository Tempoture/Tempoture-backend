import requests

# Get the Current User's Recently Played Tracks (50)
RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
PLAYLISTS_ENDPOINT =  'https://api.spotify.com/v1/me/playlists'

# https://developer.spotify.com/web-api/web-api-personalization-endpoints/get-recently-played
# Access Token requires scope: user-read-recently-played
def get_recent_tracks(access_token,after=None):
    url = RECENT_TRACKS_ENDPOINT
    if after is not None:
        url += ('&after=' + str(after))
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_current_user_playlists(access_token):
    url = PLAYLISTS_ENDPOINT
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_all_songs_audio(access_token,market_id):
    rjson = get_current_user_playlists(access_token)
    playlists = rjson["items"]
    songs = list()
    song_id = list()
    for playlist in playlists:
        auth_header = {"Authorization": "Bearer {}".format(access_token)}
        req_endpoint = f"https://api.spotify.com/v1/playlists/{playlist['id']}/tracks?market={market_id}"
        try:
            resp =requests.get(req_endpoint, headers=auth_header)
            resp.raise_for_status()
            for track in resp.json()["items"]:
                song_id.append(track['track']['id'])
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
    id_str =  ",".join(song_id)
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
        audio_j = temp_d
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    return audio_j
    

