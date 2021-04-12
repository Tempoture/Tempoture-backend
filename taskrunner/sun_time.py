from datetime import datetime, timedelta,timezone
from timezonefinder import TimezoneFinder
from astral import LocationInfo
from astral.sun import sun
import pytz
import os
import requests
from dotenv import load_dotenv

GOOGLE_MAP_KEY = ''
try:
    GOOGLE_MAP_KEY = os.environ['GOOGLE_MAP_KEY']
except Exception:
    load_dotenv()
    GOOGLE_MAP_KEY = os.getenv('GOOGLE_MAP_KEY')

'''
Added Dependencies:
Pytz,TimeZoneFinder,astral
TODO: If we can let's attempt to see if we can find timezone and sunposition without these added dependencies.
'''
#TODO:Unit test this method
def get_SunPosition(latitude, longitude, curr_time):
    tf = TimezoneFinder()
    utc = pytz.UTC
    time_zone = tf.timezone_at(lng=longitude, lat=latitude)
    location = LocationInfo()
    location.name = 'name'
    location.region = 'region'
    location.latitude = latitude
    location.longitude = longitude
    location.timezone = time_zone
    location.elevation = 0
    curr_datetime = utc.localize(
        datetime.strptime(curr_time, "%m/%d/%Y : %H:%M"))
    s = sun(location.observer, curr_datetime)
    if curr_datetime >= s["dawn"] and curr_datetime < s["sunrise"]:
        return "Dawn"
    elif curr_datetime >= s["sunrise"] and curr_datetime < s["noon"]:
        return "Sunrise"
    elif curr_datetime >= s["noon"] and curr_datetime < s["sunset"]:
        return "Noon"
    elif curr_datetime >= s["sunset"] and curr_datetime < s["dusk"]:
        return "Sunset"
    else:
        return "Dusk"

#TODO:Unit test this method
def getTimePeriod(latitude,longitude, curr_time):
    converted_time = getConvertedTime(curr_time,getTimeZone(latitude, longitude))
    if converted_time.hour == 12:
        return "Noon"
    elif converted_time.hour < 12 and converted_time.hour >= 5:
        return "Morning"
    elif converted_time.hour > 12 and converted_time.hour < 18:
        return "Afternoon"
    elif converted_time.hour > 18:
        return "Evening"
    elif converted_time.hour == 0:
        return "Midnight"
    else:
        return "Night"

#TODO:Unit test this method
def get_long_lat(zipcode, country):
    maps_query = f'https://maps.google.com/maps/api/geocode/json?components=country:{country}|postal_code:{zipcode}&sensor=false&key={GOOGLE_MAP_KEY}'
    try:
        resp = requests.get(maps_query)
        resp.raise_for_status()
        if resp.json()['status'] == 'ZERO_RESULTS': # Google Maps can not decode private zipcodes+ country combinations.
            location = dict()
        else:
            location = resp.json()['results'][0]['geometry']['location']
        return location
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))
        return dict()


def getTimeZone(latitude, longitude):
    obj = TimezoneFinder()
    return obj.timezone_at(lng=longitude, lat=latitude)

def getConvertedTime(curr_date,given_timezone):
    curr_datetime = datetime.strptime(curr_date, "%m/%d/%Y : %H:%M")
    local_tz = pytz.timezone(given_timezone)
    return curr_datetime.replace(tzinfo=timezone.utc).astimezone(local_tz)