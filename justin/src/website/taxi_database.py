# taxi_database.py

# Handles all queries from the various databases related to the taxi project. As of now
# here are the different databases.

# Trip Times Database

# Trip Speeds Database

# Trip Fares Database

import sqlite3 as sql

def open_database(database):
    conn = sql.connect(database)
    return conn.cursor()

def query_database_row(database,**query):
    db = open_database(database)
    db.execute('SELECT * from main_table WHERE pickup_latitude=:start_lat_rnd \
                                      AND pickup_longitude=:start_lon_rnd \
                                      AND dropoff_latitude=:end_lat_rnd \
                                      AND dropoff_longitude=:end_lon_rnd \
                                      AND day_of_week=:day AND hour=:hour',
                    {'start_lat_rnd': query['start_lat_rnd'], 
                     'start_lon_rnd': query['start_lon_rnd'],
                     'end_lat_rnd': query['end_lat_rnd'],
                     'end_lon_rnd': query['end_lon_rnd'],
                     'day': query['day'], 'hour': query['hour']})

    output = db.fetchone()
    db.close()
    return output
