import requests
from flask import Flask, request, jsonify, redirect
from spotify_data import spotify
from weather_data import weather
app = Flask(__name__)

@app.route('/')
def main():
    data = weather.get_current_weather()
    print(data)
    return "Hello World!"

@app.route('/wip')
def get_user_data():
    # @todo: add authorization to GET request
    # data = spotify.get_recent_tracks(url, auth_header)
    return "This a work in progress!"

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)