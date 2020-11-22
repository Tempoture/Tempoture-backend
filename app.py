import requests
from flask import Flask, request, jsonify, redirect
from spotify_data import spotify
from weather_data import weather

app = Flask(__name__)

def weather_json():
    data = weather.get_current_weather()
    return data

@app.route('/', methods=['GET'])
def api():
    return {
        'userID': 1,
        'title': 'Flask and React Application.',
        'completed': False
    }

@app.route('/songs', methods=['GET'])
def spotify_user_songs():
    access_token = request.args.get('access_token')
    data = spotify.get_recent_tracks(access_token)
    return data

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
