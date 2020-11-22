from Cipher import _encrypt, _decrypt, CRYPTO_KEY, CRYPTO_IV  
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import random
import string

#------------------------------ below are the select queries for the tempoture database ------------------------------#

def Select_User_Query(email, password):

    engine = create_engine(os.environ['DB_URI'])
    cipher_text = _encrypt(password, CRYPTO_KEY, CRYPTO_IV)

    with engine.connect() as connection:
        select_query = """SELECT * FROM "User" WHERE email=:input_1 AND password=:input_2;""" 
        query_result = connection.execute(text(select_query), input_1 = email, input_2 = cipher_text ).fetchone()

    return query_result

def Select_Cities_Query(state_id):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        select_query = """SELECT * FROM "Cities" WHERE state_id=:input;""" 
        query_result = connection.execute(text(select_query), input = state_id ).fetchone()

    return query_result

def Select_States_Query(state):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        select_query = """SELECT * FROM "states" WHERE state_name=:input;""" 
        query_result = connection.execute(text(select_query), input = state ).fetchone()

    return query_result

def Select_Countries_Query(country):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        select_query = """SELECT * FROM "countries" WHERE country_name=:input;""" 
        query_result = connection.execute(text(select_query), input = country ).fetchone()

    return query_result


def Select_Daily_Forecasts_Query(city_id):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        select_query = """SELECT * FROM "daily_forecasts" WHERE city_id =:input;""" 
        query_result = connection.execute(text(select_query), input = city_id ).fetchone()

    return query_result

#------------------------------ below are the insert queries for the tempoture database ------------------------------#
#---Temporary password Generator for User---#
def get_random_string(length):
    #characters is all possible password characters
    characters = string.ascii_lowercase 
    characters += string.ascii_uppercase
    characters += string.digits

    password = ''
    #create random combination of 16 letters from the characters list
    for i in range(16):
        password += password.join(random.choice(characters))

    return password

def Insert_User_Query(email, spotify_id, date, time, city_id):
    generated_password = get_random_string(16)
    engine = create_engine(os.environ['DB_URI'])
    cipher_text = _encrypt(generated_password, CRYPTO_KEY, CRYPTO_IV)

    with engine.connect() as connection:
        connection.autocommit = True

        insert_query =  """INSERT INTO "users"(user_id, email, password, spotify_id, date_created, time_updated, city_id) 
                            VALUES (DEFAULT, :input_1, :input_2, :input_3, :input_4, :input_5, :input_6);""" 
        connection.execute(text(insert_query),  input_1 = email, input_2 = cipher_text, input_3 = spotify_id    , 
                                                input_4 = date, input_5 = time , input_6 = city_id )
        
#---This will be for after we have implemented User logins---#        
"""
def Insert_User_Query(email, password, spotify_id, date, time, city_id):

    engine = create_engine(os.environ['DB_URI'])
    cipher_text = _encrypt(password, CRYPTO_KEY, CRYPTO_IV)

    with engine.connect() as connection:
        connection.autocommit = True

        insert_query =  ""INSERT INTO "users"(user_id, email, password, spotify_id, date_created, time_updated, city_id) 
                            VALUES (DEFAULT, :input_1, :input_2, :input_3, :input_4, :input_5, :input_6);"" 
        connection.execute(text(insert_query),  input_1 = email, input_2 = cipher_text, input_3 = spotify_id    , 
                                                input_4 = date, input_5 = time , input_6 = city_id )
"""
def Insert_Cities_Query(city_name, state_id):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        connection.autocommit = True

        insert_query =  """INSERT INTO "cities"(city_id, city_name, state_id) 
                            VALUES(DEFAULT, :input_1, :input_2);""" 
        connection.execute(text(insert_query), input_1 = city_name, input_2 = state_id) 

    return query_result

def Insert_States_Query(state_name, country_id):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        connection.autocommit = True

        insert_query =  """INSERT INTO "states"(state_id, state_name, country_id) 
                            VALUES(DEFAULT, :input_1, :input_2);""" 
        connection.execute(text(insert_query), input_1 = state_name, input_2 = country_id )

    return query_result

def Insert_Countries_Query(country_name):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        connection.autocommit = True

        insert_query =  """INSERT INTO "countries"(country_id, country_name) VALUES(DEFAULT, :input);""" 
        connection.execute(text(insert_query), input = country_name )

    return query_result

def Insert_Daily_Forecasts_Query(weather_date, average_temp, pressure, humidity, wind_speed, wind_direction, cloudiness, 
                            precipitation_volume, snow_volume, precipitation_probability, time_updated, city_id):

    engine = create_engine(os.environ['DB_URI'])

    with engine.connect() as connection:
        connection.autocommit = True

        insert_query =  """INSERT INTO "daily_forecasts"(daily_forecast_id, weather_date, average_temp, pressure, humidity, wind_speed, wind_direction, 
                                                        cloudiness, precipitation_volume, snow_volume, precipitation_probability, time_updated, city_id) 
                            VALUES (DEFAULT, :input_1, :input_2, :input_3, :input_4, :input_5, :input_6, :input_7, :input_8,:input_9, :input_10, :input_11, :input_12);""" 
        connection.execute(text(insert_query),  input_1 = weather_date, input_2 = average_temp, input_3 = pressure, input_4 = humidity, input_5 = wind_speed, 
                                                input_6 = wind_direction, input_7 = cloudiness, input_8 = precipitation_volume, input_9 = snow_volume, 
                                                input_10 = precipitation_probability, input_11 = time_updated, input_12 = city_id)

    return query_result

