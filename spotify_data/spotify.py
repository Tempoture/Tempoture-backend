# Get the Current User's Recently Played Tracks (50)
RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'

# To do:
# - User Authroization

# https://developer.spotify.com/web-api/web-api-personalization-endpoints/get-recently-played/
def get_recent_tracks(auth_header):
    url = RECENT_TRACKS_ENDPOINT
    # @todo: use authorization from frontend
    # resp = requests.get(url, headers=auth_header)
    # return resp.json()
