from datetime import datetime, timedelta
from pyzipcode import ZipCodeDatabase
from timezonefinder import TimezoneFinder
from astral import LocationInfo
from astral.sun import sun
import pytz

def get_SunPosition(latitude,longitude,curr_time):
    tf = TimezoneFinder()
    utc=pytz.UTC
    time_zone = tf.timezone_at(lng=longitude, lat=latitude)
    location = LocationInfo()
    location.name = 'name'
    location.region = 'region'
    location.latitude = latitude
    location.longitude = longitude
    location.timezone = time_zone
    location.elevation = 0
    curr_datetime = utc.localize(datetime.strptime(curr_time,"%m/%d/%Y : %H:%M"))
    s = sun(location.observer,curr_datetime)
    if curr_datetime >= s["dawn"] and curr_datetime < s["sunrise"] :
        return "Dawn"
    elif curr_datetime >= s["sunrise"] and curr_datetime < s["noon"]:
        return "Sunrise"
    elif curr_datetime >= s["noon"] and curr_datetime < s["sunset"]:
        return "Noon"
    elif curr_datetime >= s["sunset"] and curr_datetime < s["dusk"]:
        return "Sunset"
    else:
        return "Dusk"


def getTimePeriod(zipcode,curr_time):
    curr_datetime = datetime.strptime(curr_time,"%m/%d/%Y : %H:%M")
    zip_id = int(zipcode.lstrip('0'))
    zcdb = ZipCodeDatabase()
    converted_time = curr_datetime + timedelta(hours=zcdb[zip_id].timezone)
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

def getConvertedTime(zipcode,curr_time):
    curr_datetime = datetime.strptime(curr_time,"%m/%d/%Y : %H:%M")
    zip_id = int(zipcode.lstrip('0'))
    zcdb = ZipCodeDatabase()
    converted_time = curr_datetime + timedelta(hours=zcdb[zip_id].timezone)
    return converted_time.strftime("%m/%d/%Y : %H:%M")
