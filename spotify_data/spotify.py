# Get the Current User's Recently Played Tracks (50)
RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'

# https://developer.spotify.com/web-api/web-api-personalization-endpoints/get-recently-played
# Access Token requires scope: user-read-recently-played
def get_recent_tracks(access_token):
    url = RECENT_TRACKS_ENDPOINT
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    resp = requests.get(url, headers=auth_header)
    return resp.json()
