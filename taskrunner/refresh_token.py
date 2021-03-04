import os
import requests
import time
from dotenv import load_dotenv
import urllib.parse

CLIENT_ID = ""
CLIENT_SECRET = ""

try: 
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
except Exception: 
    load_dotenv()
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def check_new_token(token,refresh_token,last_refresh):
    d = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    auth_header = {
            "Content-Type": "application/x-www-form-urlencoded"
    }
    access_token = token
    curr =  int(time.time()) * 1000 # TIME IN MILLISECONDS
    if curr - int(last_refresh) >= 3600000:
        try:
            resp = requests.post('https://accounts.spotify.com/api/token',params=urllib.parse.urlencode(d),headers=auth_header)
            resp.raise_for_status()
            access_token = resp.json()['access_token']
            curr = int(time.time())
        except requests.exceptions.HTTPError as err:
            print("ERR:" + str(err))
    return (access_token,curr)
        