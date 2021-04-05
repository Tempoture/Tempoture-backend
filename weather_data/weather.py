import requests
import xmltodict
import os
import json
from datetime import datetime,timedelta
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv
import time
import socket

GEO_KEY = ""
WEATHER_KEY = ""

try: 
    GEO_KEY = os.environ['GEO_API_KEY']
    WEATHER_KEY = os.environ['WEATHER_API_KEY']
except Exception: 
    load_dotenv()
    GEO_KEY = os.getenv('GEO_API_KEY')
    WEATHER_KEY = os.getenv('WEATHER_API_KEY')

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
    weather_dict = {}
    try:
        CLIENT_IP = request.remote_addr
        CURRENT_GEO_ENDPOINT = 'https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}&fields=geo'.format(GEO_KEY,CLIENT_IP)    
        r = requests.get(CURRENT_GEO_ENDPOINT)
        r.raise_for_status()
        thedict=r.json()
        zipcode=thedict['zipcode']
        countrycode=thedict['country_code2']
        units_type = 'imperial'
        wr = requests.get('http://api.openweathermap.org/data/2.5/weather?zip={0},{1}&mode=xml&appid={2}&units={3}'.format(zipcode,countrycode,WEATHER_KEY,units_type))
        wr.raise_for_status()
        weather_dict = xmltodict.parse(wr.content)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(f'ERROR:{str(e)}')
        weather_dict = {"ERROR" : str(e)}
    return weather_dict

def get_prev_day_data(lat,lng):
    try:
        prev_day = datetime.utcnow() - timedelta(days = 1)
        wr =  requests.get(f"http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lng}&dt={int(prev_day.timestamp())}&appid={WEATHER_KEY}")
        wr.raise_for_status()
        return wr.json()['hourly']
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(f'ERROR:{str(e)}')
        return dict()

# Note from OpenWeather API:
# If you do not see some of the parameters in your API response it means that these weather 
# phenomena are just not happened for the time of measurement for the city or location chosen. 
# Only really measured or calculated data is displayed in API response.
def get_weather_from_zipcode(zipcode,country_code):
    try:
        units_type = 'imperial'
        wr = requests.get('http://api.openweathermap.org/data/2.5/weather?zip={0},{1}&mode=xml&appid={2}&units={3}'.format(zipcode,country_code,WEATHER_KEY,units_type))
        weatherdict = xmltodict.parse(wr.content)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERR:" + str(err))
    return weatherdict

def get_weather_from_latlong(latitude,longitude):
    try:
        units_type = 'imperial'
        wr = requests.get('http://api.openweathermap.org/data/2.5/weather?lat={0}&long={1}&mode=xml&appid={2}&units={3}'.format(latitude,longitude,WEATHER_KEY,units_type))
        weatherdict = xmltodict.parse(wr.content)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERR:" + str(err))
    return weatherdict


def get_historical_weather_latlong(latitude,longitude,date):#Date: Unix timestamp
    try:
        units_type = 'imperial'
        wr = requests.get('https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={time}&appid={key}&units={units}'.format(latitude,longitude,date,WEATHER_KEY,units_type))
        weatherdict = xmltodict.parse(wr.content)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERR:" + str(err))
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

get_prev_day_data(40.178098,-74.241539)