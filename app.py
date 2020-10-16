from flask import Flask, render_template, redirect,request
from data import spotify
import requests as apirequest
app = Flask(__name__)


geokey=''
weatherkey=''
def getweather():
    ip = request.remote_addr
    r=apirequest.get('https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}&fields=geo'.format(geokey,ip))
    thedict=r.json()
    try:
        zipcode=thedict['zipcode']
        countrycode=thedict['country_code2']
        wr=apirequest.get('http://api.openweathermap.org/data/2.5/weather?zip={0},{1}&appid={2}'.format(zipcode,countrycode,weatherkey))
        weatherdict=wr.json()
    except Exception:
        return dict()
    return weatherdict



@app.route('/')
def hello():
    weatherdict=getweather()
    return "This is our main page"

@app.route('/wip')
def get_user_data():
    # @todo: add authorization to GET request
    # data = spotify.get_recent_tracks(url, auth_header)
    return "This a work in progress!"



if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)