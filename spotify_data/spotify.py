RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played'

# To do:
# - User Authroization

# https://developer.spotify.com/web-api/web-api-personalization-endpoints/get-recently-played/
def get_recent_tracks(auth_header):
    url = RECENT_TRACKS_ENDPOINT
    # @todo: add authorization to GET request
    # resp = requests.get(url, auth_header)
    # return resp.json()
