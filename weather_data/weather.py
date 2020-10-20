import requests
from flask import Flask, request, jsonify, redirect

def get_current_weather_json():
    CLIENT_IP = request.remote_addr
    GEO_KEY = "Api Key Goes Here"
    WEATHER_KEY = 'Api Key Goes Here'
    CURRENT_GEO_ENDPOINT = 'https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}&fields=geo'.format(GEO_KEY,CLIENT_IP)    
    r = requests.get(CURRENT_GEO_ENDPOINT)
    thedict=r.json()
    try:
        zipcode=thedict['zipcode']
        countrycode=thedict['country_code2']
        wr = requests.get('http://api.openweathermap.org/data/2.5/weather?zip={0},{1}&appid={2}'.format(zipcode,countrycode,WEATHER_KEY))
        weatherdict=wr.json()
    except Exception:
        return dict()
    return weatherdict

def get_current_weather():
    if bool(get_current_weather_json()):
        if get_current_weather_json()['cod'] == 200:
            return get_current_weather_json()['weather'][0]
    return dict()