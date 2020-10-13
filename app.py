from flask import Flask, render_template, redirect
from data import spotify
app = Flask(__name__)


@app.route('/')
def hello():
    return "This is our main page"

@app.route('/wip')
def get_user_data():
    # @todo: add authorization to GET request
    # data = spotify.get_recent_tracks(url, auth_header)
    return "This a work in progress!"

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)