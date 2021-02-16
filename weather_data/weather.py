import requests
import xmltodict
import os
from flask import Flask, request, jsonify, redirect

# API KEYS
try: 
    GEO_KEY = os.environ['GEO_API_KEY']
    WEATHER_KEY = os.environ['WEATHER_API_KEY']
except Exception: 
    print("No API Key Supplied")


# Return user's zip code
def get_zip_code():
    CLIENT_IP = request.remote_addr
    CURRENT_GEO_ENDPOINT = 'https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}&fields=geo'.format(GEO_KEY,CLIENT_IP)    
    r = requests.get(CURRENT_GEO_ENDPOINT)
    thedict=r.json()
    try:
        zipcode=thedict['zipcode']
    except Exception:
        return '00000'
    return zipcode

# Note from OpenWeather API:
# If you do not see some of the parameters in your API response it means that these weather 
# phenomena are just not happened for the time of measurement for the city or location chosen. 
# Only really measured or calculated data is displayed in API response.
def get_current_weather():
    CLIENT_IP = request.remote_addr
    CURRENT_GEO_ENDPOINT = 'https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}&fields=geo'.format(GEO_KEY,CLIENT_IP)    
    r = requests.get(CURRENT_GEO_ENDPOINT)
    thedict=r.json()
    try:
        zipcode=thedict['zipcode']
        countrycode=thedict['country_code2']
        units_type = 'imperial'
        wr = requests.get('http://api.openweathermap.org/data/2.5/weather?zip={0},{1}&mode=xml&appid={2}&units={3}'.format(zipcode,countrycode,WEATHER_KEY,units_type))
        weatherdict = xmltodict.parse(wr.content)
    except Exception:
        return dict()
    return weatherdict


# Weather Data for User
# Table includes:
#   - daily_forecast_id
#   - date
#   - average_temp
#   - pressure
#   - humidity
#   - weather_id
#   - wind_speed
#   - wind_direction
#   - cloudiness
#   - precipitation_volume
#   - snow_volume ?
#   - precipitation_probability ?
#   - updated_at

# in fahrenheit
def get_avg_temp(data):
    try:
        return data['current']['temperature']['@value']
    except Exception:
        return -1

# in hPa
def get_pressure(data):
    try:
        return data['current']['pressure']['@value']
    except Exception:
        return -1

# in %
def get_humidity(data):
    try:
        return data['current']['humidity']['@value']
    except Exception:
        return -1

# weather code
def get_weather_id(data):
    try:
        return data['current']['weather']['@number']
    except Exception:
        return -1

# in mph
def get_wind_speed(data):
    try:
        return data['current']['wind']['speed']['@value']
    except Exception:
        return -1

# in degrees
def get_wind_direction(data):
    try:
        return data['current']['wind']['direction']['@value']
    except Exception:
        return -1

# in %  , 0 - 1
def get_cloudiness(data):
    try:
        return data['current']['clouds']['@value']
    except Exception:
        return -1

# in mm
def get_precipitation(data):
    try:
        return data['current']['precipitation']['@value']
    except Exception:
        return 0

# ex. "2020-11-24T20:36:00"
def get_last_updated(data):
    try:
        return data['current']['lastupdate']['@value']
    except Exception:
        return -1
