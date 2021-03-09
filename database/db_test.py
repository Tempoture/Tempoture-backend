# File name: db_test.py
# Description: Connect to database and test its functionality
#              Using sqlalchemy seems not able to connect to the database successfully.
#              Instead, we use psycopg2 to implement the functionality.

import psycopg2
import random
import datetime
# from sqlalchemy import create_engine
# from sqlalchemy.sql import text

# connect to the database
conn = psycopg2.connect(
    """
    dbname = "FILL IN LATER"
    host = ec2-54-85-13-135.compute-1.amazonaws.com
    user = "FILL IN LATER"
    password = "FILL IN LATER"
    port = 5432
    """
)

# set to autocommit so that each query will be committed automatically after execution
conn.set_session(autocommit = True)

#------------------------------ below are the select queries for the tempoture database ------------------------------#

def Select_Countries_Query(country):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        select_query = "SELECT * FROM countries WHERE country_name=\'{}\'".format(country)
        cursor.execute(select_query)
        countries = cursor.fetchall()
    return countries

def Select_States_Query(state):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        select_query = "SELECT * FROM states WHERE state_name=\'{}\'".format(state)
        cursor.execute(select_query)
        states = cursor.fetchall()
    return states

def Select_Cities_Query(city):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        select_query = "SELECT * FROM cities WHERE city_name=\'{}\'".format(city)
        cursor.execute(select_query)
        cities = cursor.fetchall()
    return cities

def Select_User_Query(email, password):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        select_query = "SELECT * FROM users WHERE email=\'{}\' AND password = \'{}\'".format(email, password)
        cursor.execute(select_query)
        users = cursor.fetchall()

    return users

def Select_Daily_Forecasts_Query(city_id):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        select_query = "SELECT * FROM daily_forecasts WHERE city_id={}".format(city_id)
        cursor.execute(select_query)
        daily_forcasts = cursor.fetchall()

    return daily_forcasts

#------------------------------ below are the insert queries for the tempoture database ------------------------------#

def Insert_Countries_Query(country_name):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        insert_query = "INSERT INTO countries (country_id, country_name) \
                        VALUES(DEFALUT, \'{}\')".format(country_name) 
        cursor.execute(insert_query)
        
    return insert_query

def Insert_States_Query(state_name, country_id):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        insert_query = "INSERT INTO countries (state_id, state_name, country_id) \
                        VALUES(DEFALUT, \'{}\', {})".format(state_name, country_id) 
        cursor.execute(insert_query)
        
    return insert_query

def Insert_Cities_Query(city_name, state_id):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        insert_query = "INSERT INTO cities (city_id, city_name, state_id) \
                        VALUES(DEFALUT, \'{}\', {})".format(city_name, state_id) 
        cursor.execute(insert_query)
        
    return insert_query

def Insert_User_Query(email, password, spotify_id, date_created, time_updated, city_id):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        insert_query = "INSERT INTO users (user_id, email, password, spotify_id, date_created, time_updated, city_id) \
                        VALUES(DEFALUT, \'{}\', \'{}\', \'{}\', \'{}\', TIMESTAMP \'{}\', {})".format(
                            email, password, spotify_id, date_created, time_updated, city_id) 
        cursor.execute(insert_query)
        
    return insert_query


def Insert_Daily_Forecasts_Query(daily_forecast_id, weather_date, average_temp, pressure, humidity, wind_speed, wind_direction, cloudiness, 
                            precipitation_volume, snow_volume, precipitation_probability, time_updated, city_id):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        insert_query = "INSERT INTO daily_forecasts(daily_forecast_id, weather_date, average_temp, pressure, humidity, wind_speed, wind_direction, \
                                                        cloudiness, precipitation_volume, snow_volume, precipitation_probability, time_updated, city_id) \
                        VALUES({}, \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', TIMESTAMP \'{}\', {})".format(
                            daily_forecast_id, weather_date, average_temp, pressure, humidity, wind_speed, wind_direction, cloudiness, 
                            precipitation_volume, snow_volume, precipitation_probability, time_updated, city_id) 
        cursor.execute(insert_query)
        
    return insert_query

#------------------------------ below are the delete queries for the tempoture database ------------------------------#

def Delete_Daily_Forecasts_Query(city_id):
    cursor = conn.cursor()

    with conn.cursor() as cursor:
        delete_query = 'DELETE FROM daily_forecasts WHERE city_id={}'.format(city_id)
        cursor.execute(delete_query)
    
    return delete_query

# The query removes all the weather date data that are over 7 days from today's date
def Delete_Outdated_Daily_Forecasts_Query():
    # get current year, month, and day
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    current_date = '{}-{:02d}-{:02d}'.format(year, month, day)

    cursor = conn.cursor()

    with conn.cursor() as cursor:
        delete_query = 'DELETE FROM daily_forecasts WHERE \
                        \'{}\'::date - weather_date::date >= 7'.format(current_date)
        cursor.execute(delete_query)
    
    return delete_query

#------------------------------ below are the test cases for the tempoture database ----------------------------------# 

if __name__ == '__main__': 
    # Remove all the data before testing
    Delete_Daily_Forecasts_Query(1)

    daily_forecast_id = 1

    # insert some randome daily forecasts data
    for i in range(20):
        
        average_temp = str(round(random.uniform(1,100), 1))
        pressure = str(round(random.uniform(1,100), 1))
        humidity = str(round(random.uniform(1,100), 1))
        wind_speed = str(round(random.uniform(1,100), 1))
        wind_direction = str(round(random.uniform(1,100), 1)) 
        cloudiness = str(round(random.uniform(1,100), 1))
        precipitation_volume = str(round(random.uniform(1,100), 1))
        snow_volume = str(round(random.uniform(1,100), 1))
        precipitation_probability = str(round(random.random(), 1)) 
        city_id = 1

        if i < 5:
            weather_date = '2021-03-01'
            time_updated = '2021-03-01 03:14:30'
        elif i >= 5 and i < 10:
            weather_date = '2021-02-28'
            time_updated = '2020-02-28 03:14:30'
        elif i >= 10 and i < 15:
            # Today's date is 2021-03-08
            # After removing, we should keep data with this
            # weather date and remove all the other outdated data
            weather_date = '2021-03-02'
            time_updated = '2020-03-02 03:14:30'
        else:
            weather_date = '2020-03-08'
            time_updated = '2020-03-08 03:14:30'

        result = Insert_Daily_Forecasts_Query(daily_forecast_id, weather_date, average_temp, pressure, humidity, wind_speed, wind_direction, cloudiness, 
                                precipitation_volume, snow_volume, precipitation_probability, time_updated, city_id)
        
        daily_forecast_id += 1

    Delete_Outdated_Daily_Forecasts_Query()
    print(Select_Daily_Forecasts_Query(1)) # print out the result to check its correctness
        
    # close the connection with our database
    conn.close()

   
