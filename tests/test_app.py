import os
from spotifyclient import SpotifyClient


def main():
    SpotifyObj = SpotifyClient(os.getenv("SPOTIFY_ACCESS_TOKEN"),
                                   os.getenv("SPOTIFY_USER_ID"))
    SpotifyObj.create_tempoture_playlist(SpotifyObj.get_recent_tracks())
    #print(SpotifyObj.test_create_and_populate("Tempoture", "Cool New Playlist"))
    #print(SpotifyObj.create_playlist("Tempoture", "Tempoture's Cool Custom Playlist For You!"))


if __name__ == "__main__":
    main()