# analyze_data.py, created 2014 Aug 22

# This python script performs a preliminary analysis on 2013 NYC taxi cab data. 
# The data was originally found here:

# http://chriswhong.com/open-data/foil_nyc_taxi/

# Some reorganization of the data has already been performed. In particular, the data
# downloadable from the torrent at that link is in two separate ZIP archives: one called
# tripdata2013.zip and one called faredata2013.zip. Each ZIP archive in turn contains
# 12 zipped CSV files, one for each month of data. Some of these, however, contain 
# duplicate data, so the files I work with here are gzipped versions of each of 
# the 24 CSV files with duplicated removed. These I've in turn placed into two gzipped 
# TAR archives: tripdata2013.tar.gz and faredata2013.tar.gz

# This script assumes it's in a folder Project/code/ and that the data is stored in
# Project/data/tripdata2013 and Project/data/faredata2013

# To use this remotely with live plotting, use ssh -X

import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Create file to write output to (instead of terminal)

f = open('analysis.txt','w')

# Read in compressed data

trip_data = pd.read_csv('../data/tripdata2013/trip_data_1.csv.gz',compression='gzip')
fare_data = pd.read_csv('../data/faredata2013/trip_fare_1.csv.gz',compression='gzip')

# Remove whitespace from column headings

trip_data = trip_data.rename(columns=lambda x: x.strip())
fare_data = fare_data.rename(columns=lambda x: x.strip())

# This may save memory (takes too long, seemingly, regardless):
# trip_data.rename(columns=lambda x: x.strip(), inplace = True)
# fare_data.renmae(columns=lambda x: x.strip(), inplace = True)

# Print names of columns

f.write('Names of columns for trip data:\n\n') 
trip_data.columns.values.tofile(f,sep=', ')
f.write('\n\n')

f.write('Names of columns for fare data:\n\n') 
fare_data.columns.values.tofile(f,sep=', ')
f.write('\n\n')

# Print number of rows

f.write('Number of rows in trip data: ')
f.write(str(len(trip_data)))
f.write('\n')
f.write('Number of rows in fare data: ')
f.write(str(len(fare_data)))
f.write(' (should be the same)\n\n')

# Merge data frames and free up memory

data = pd.merge(trip_data,fare_data,how='outer',sort=False)
trip_data = None
fare_data = None

f.write('Number of columns in merged data: ')
f.write(str(len(data.columns)))
f.write(' (should be 21)\n\n')

# Convert times to python time format

data['pickup_datetime'] = pd.to_datetime(data['pickup_datetime'])
data['dropoff_datetime'] = pd.to_datetime(data['dropoff_datetime'])

# Compute number of pickups by hour:

trips_by_hour = data['pickup_datetime'].map(lambda x: x.hour)
trips_by_hour.value_counts()

# Compare different days of the week.

data['day_of_week'] = data['pickup_datetime'].apply(lambda x: x.dayofweek)

list_of_days = []
for day in range(7):
    list_of_days.append(data[data['day_of_week'] == day]['pickup_datetime']\
                            .map(lambda x: x.hour).value_counts())
trips_by_day = pd.concat(list_of_days,axis=1)

# Plot a quick result

trips_by_day.plot()
plt.show()

# Plot a slightly more ambitious visual of pickups and dropoffs

data.plot(kind='hexbin', x='pickup_longitude', y='pickup_latitude', 
            gridsize=200, bins='log', extent=[-74.0,-73.93,40.7,40.8])
data.plot(kind='hexbin', x='dropoff_longitude', y='dropoff_latitude', 
            gridsize=200, bins='log', extent=[-74.0,-73.93,40.7,40.8])
            
# Sort the data by hack_license and then pickup_time, to allow for analysis
# of dropoff to pickup times (as well as investigate whether any license_numbers
# are dubious because of impossible overlaps

data['same_driver_as_next'] = np.equal(data['hack_license'],
                                            data['hack_license'].shift(-1))

data['time_difference_to_next'] = data['pickup_datetime'].shift(-1) 
                                            - data['dropoff_datetime']
                                
# Kind of a hack to get this to represent seconds:

data['time_difference_to_next'] = data['time_difference_to_next']/np.timedelta64(1, 's')

# Might be useful to reindex:
# data.index = range(len(data)) 

# Close f

f.close()

# Geocoding problem

# Python iterators and generators

# Groupby in SQL (alternatively MapReduce)

# MR Job



