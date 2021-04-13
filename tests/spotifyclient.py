import requests
import json
import base64

# GOAL: Create a cleaner SpotifyClient class to call from main app


RECENT_TRACKS_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played?limit=5'
PLAYLISTS_ENDPOINT =  'https://api.spotify.com/v1/me/playlists'
CREATE_PLAYLISTS_ENDPOINT = 'https://api.spotify.com/v1/users/{}/playlists'
MODIFY_TRACKS_PLAYLISTS_ENDPOINT = 'https://api.spotify.com/v1/playlists/{}/tracks'
CHANGE_PLAYLIST_COVER_ENDPOINT = 'https://api.spotify.com/v1/playlists/{}/images'
DEFAULT_PLAYLIST_COVER = 'logo.jpeg'
DEFAULT_PLAYLIST_NAME = 'Your Tempoture Playlist'
DEFAULT_PLAYLIST_DESC = 'A custom-made playlist made by Tempoture for you!'



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
        """
        :param after (int): optional timestamp in milliseconds
        
        Output: 
        trackURIs = list of Spotify track URIs from user's recently played  
        """

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
        """
        :param name (str): = optional argument for custom name of new playlist, will default to hardcoded string if none
        :param desc (str): = optional argument for custom description of new playlist, will default to hardcoded string if none

        Output: 
        playlist_id (int): id of the newly created playlist  

        """

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
        playlist_id = -1
        try:
            playlist_id = resp_json["id"]
        except Exception:
            print("Status " + str(resp_json["error"]["status"]) + ": " + resp_json["error"]["message"])
        return playlist_id

    def change_playlist_cover(self, playlist_id, cover=None):
        """
        Input:
        :param playlist_id (int): Spotify playlist id
        :param cover (str): optional argument for custom album cover photo, will default to hardcoded encoded string if none
    
        @todo: 
        Output: 
        a bool which determines if cover change went through successfully
    
        """
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
        return True

    def add_playlist_tracks(self, playlist_id, track_uri_data):
        """
        Input:
        :param playlist_id (int): id of Spotify playlist being modified
        :param track_uri_data (list): a list of Spotify track URI's , ex. ['spotify:track:xxxxxx', 'spotify:track:yyyyyyy']
    
        Output: 
        snapshot_id = updated snapshot_id of the modified playlist (-1 if error occurred)
    
        """
        data = json.dumps(track_uri_data)
        url = MODIFY_TRACKS_PLAYLISTS_ENDPOINT.format(playlist_id)
        response = self.post_api_request(url, data)
        resp_json = response.json()
        snapshot_id = -1
        try:
            snapshot_id = resp_json["snapshot_id"]
        except Exception:
            print("Status " + str(resp_json["error"]["status"]) + ": " + resp_json["error"]["message"])

        return snapshot_id

    def remove_playlist_tracks(self, playlist_id, track_uri_data, snapshot_id):
        """
        Input:
        :param playlist_id (int): id of Spotify playlist being modified
        :param track_uri_data (list): a list of Spotify track URIs to remove. Formatted ex: { "tracks": [{ "uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh" },{ "uri": "spotify:track:1301WleyT98MSxVHPZCA6M" }] }
        :param snapshot_id (int): (optional) playlist’s snapshot ID against which you want to make the changes

        @todo: 
        Output: 
        snapshot_id = updated snapshot_id of the modified playlist (-1 if error occurred)
    
        """
        data = json.dumps(track_uri_data)
        url = MODIFY_TRACKS_PLAYLISTS_ENDPOINT.format(playlist_id)
        response = self.delete_api_request(url, data)
        resp_json = response.json()
        snapshot_id = -1
        try:
            snapshot_id = resp_json["snapshot_id"]
        except Exception:
            print("Status " + str(resp_json["error"]["status"]) + ": " + resp_json["error"]["message"])

        print(resp_json)
        return snapshot_id

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

    def delete_api_request(self, url, data):
        response = requests.delete(
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
        """
        :param name (str): = optional argument for custom name of new playlist, will default to hardcoded string if none
        :param desc (str): = optional argument for custom description of new playlist, will default to hardcoded string if none

        Output: 
        snapshot_id (int): a Spotify snapshot id which represents the specific playlist version

        """

        playlist_id = self.create_playlist(name, desc)
        self.change_playlist_cover(playlist_id)
        url = MODIFY_TRACKS_PLAYLISTS_ENDPOINT.format(playlist_id)
        track_uri_data =  self.get_recent_tracks()
        data = json.dumps(track_uri_data)
        response = self.post_api_request(url, data)
        resp_json = response.json()
        snapshot_id = resp_json["snapshot_id"]
        return snapshot_id


   # Create a new demo playlist and populate with your 5 most recent songs 
    def create_tempoture_playlist(self, track_uri_data, name=None, desc=None, cover=None):
        """
        Input:
        :param track_uri_data (list): a list of Spotify track URI's , ex. ['spotify:track:xxxxxx', 'spotify:track:yyyyyyy']
        :param name (str): optional argument for custom name of new playlist, will default to hardcoded string if none
        :param desc (str): optional argument for custom description of new playlist, will default to hardcoded string if none
        :param cover (str): optional argument for custom album cover photo, will default to hardcoded encoded string if none
        
        Output: 
        playlist_id (int): id of newly created custom Spotify playlist

        """
        if name is None:
            name = DEFAULT_PLAYLIST_NAME
        if desc is None:
            desc = DEFAULT_PLAYLIST_DESC
        if cover is None:
            cover = DEFAULT_PLAYLIST_COVER

        playlist_id = self.create_playlist(name, desc)

        if playlist_id == -1:
            raise Exception("Could not create playlist.")
        
        if self.change_playlist_cover(playlist_id) == False:
            raise Exception("Could not change playlist cover.")

        snapshot_id = self.add_playlist_tracks(playlist_id, track_uri_data)

        if  snapshot_id == -1:
            raise Exception("Could not add tracks to playlist.")

        return playlist_id

