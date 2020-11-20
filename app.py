import requests
from flask import Flask, request, jsonify, redirect
from spotify_data import spotify
from weather_data import weather
import psycopg2
import urllib.parse as urlparse
import os

url = urlparse.urlparse(os.environ['DATABASE_URL'])
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)

connection = psycopg2.connect(db)
cur = connection.cursor()

app = Flask(__name__)

def weather_json():
    data = weather.get_current_weather()
    return data

@app.route('/', methods=['GET'])
def spotify_user_songs():
    access_token = request.args.get('access_token')
    data = spotify.get_recent_tracks(access_token)
    return data

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
