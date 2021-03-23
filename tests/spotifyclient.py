import requests
import json
import base64

# GOAL: Create a cleaner SpotifyClient class to call from main app


RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played?limit=5'
PLAYLISTS_ENDPOINT =  'https://api.spotify.com/v1/me/playlists'
CREATE_PLAYLISTS_ENDPOINT = 'https://api.spotify.com/v1/users/{}/playlists'
ADD_TRACKS_PLAYLISTS_ENDPOINT = 'https://api.spotify.com/v1/playlists/{}/tracks'
CHANGE_PLAYLIST_COVER_ENDPOINT = 'https://api.spotify.com/v1/playlists/{}/images'
DEFAULT_PLAYLIST_COVER = 'logo.jpeg'

class SpotifyClient:
    def __init__(self, access_token, user_id):
        """ 
        :param access_token (str): needed to fetch or push data from Spotify API
        :param user_id (str): needed for playlist updates on user's account

        """
        self.access_token = access_token
        self.user_id = user_id
    
    # https://developer.spotify.com/web-api/web-api-personalization-endpoints/get-recently-played
    # Access Token requires scope: user-read-recently-played
    def get_recent_tracks(self, after=None):
    #  Input:
    #  after = optional timestamp in milliseconds (int)
    #  
    #  Output: 
    #  trackURIs = list of Spotify track URIs from user's recently played  
    #
        url = RECENT_TRACKS_ENDPOINT
        if after is not None:
            url += ('&after=' + str(after))
        response = self.get_api_request(url)
        trackNames = [track["track"]["name"] for track in response.json()["items"]]
        trackURIs = [track["track"]["uri"] for track in response.json()["items"]]
        return trackURIs

    def get_current_user_playlists(self):
        url = PLAYLISTS_ENDPOINT
        response = self.get_api_request(self, url)
        return response.json()
    
    # https://developer.spotify.com/documentation/web-api/reference/#endpoint-create-playlist
    # Scopes needed: playlist-modify-public & playlist-modify-private
    def create_playlist(self, name=None, desc=None):
    #  Input:
    #  name = optional argument for custom name of new playlist, will default to hardcoded string if none (str)
    #  desc = optional argument for custom description of new playlist, will default to hardcoded string if none (str)  
    #
    #  Output: 
    #  playlist_id = id of the newly created playlist  
    #

        url = CREATE_PLAYLISTS_ENDPOINT.format(self.user_id)
        if name is None:
            name = "Custom Tempoture Playlist"

        # Allow empty descriptions?

        data = json.dumps({
            "name": name,
            "public": True,
            "collaborative": False,
            "description": desc
        })
        response = self.post_api_request(url, data)
        resp_json = response.json()
        playlist_id = resp_json["id"]
        return playlist_id

    def change_playlist_cover(self, playlist_id, cover=None):
    #  Input:
    #  playlist_id = Spotify playlist id (int)
    #  cover = optional argument for custom album cover photo, will default to hardcoded encoded string if none (str)  
    #
    #  @todo: 
    #  Output: 
    #  a bool which determines if cover change went through successfully
    #    
    #
        url = CHANGE_PLAYLIST_COVER_ENDPOINT.format(playlist_id)
        if (cover is None):
            cover = DEFAULT_PLAYLIST_COVER
        encoded_string = ""
        with open(cover, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            file = encoded_string
        response = requests.put(
        url,
        headers={
            "Content-Type": "image/jpeg",
            "Authorization": f"Bearer {self.access_token}"
        },
        data = encoded_string
        )

    def get_api_request(self, url):
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        return response

    def post_api_request(self, url, data):
        response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        return response


    # Create a new demo playlist and populate with your 5 most recent songs 
    def test_create_and_populate(self, name=None, desc=None):
    #  Input:
    #  name = optional argument for custom name of new playlist, will default to hardcoded string if none (str)
    #  desc = optional argument for custom description of new playlist, will default to hardcoded string if none (str)  
    #
    #  Output: 
    #  snapshot_id = a Spotify snapshot id which represents the specific playlist version  (int)
    #    
    #
        playlist_id = self.create_playlist(name, desc)
        self.change_playlist_cover(playlist_id)
        url = ADD_TRACKS_PLAYLISTS_ENDPOINT.format(playlist_id)
        track_uri_data =  self.get_recent_tracks()
        data = json.dumps(track_uri_data)
        response = self.post_api_request(url, data)
        resp_json = response.json()
        snapshot_id = resp_json["snapshot_id"]
        return snapshot_id


