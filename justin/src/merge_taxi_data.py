# merge_taxi_data.py

# Merge the two files trip_data_month.csv.gv and fare_data_month.csv.gv into one file
# taxi_data_month.csv.gv, taking the month number as a parameter. Additionally,
# converting date/times to pandas datetime format. No loss of raw information happens
# running this script.

import sys # for handling command-line arguments
import numpy as np
import pandas as pd
from datetime import datetime
import time

for argument in sys.argv[1:]:
    global_start = time.clock()

    print 'Taking argument ' + argument
    tripfilename = '../data/tripdata2013/trip_data_' + argument + '.csv.gz'
    farefilename = '../data/faredata2013/trip_fare_' + argument + '.csv.gz'
    taxifilename = '../data/taxi_data_' + argument + '.csv'
    
    local_start = time.clock()
    print 'loading ' + tripfilename
    trip_data = pd.read_csv(tripfilename, compression='gzip')
    print 'loaded ' + tripfilename,
    print ' took', time.clock() - local_start, 'seconds'
    local_start = time.clock()
    print 'loading ' + farefilename
    fare_data = pd.read_csv(farefilename, compression='gzip')
    print 'loaded ' + farefilename,
    print ' took', time.clock() - local_start, 'seconds'
    
    print 'total of', time.clock() - global_start, 'seconds so far'
    
    local_start = time.clock()
    trip_data.rename(columns=lambda x: x.strip(), inplace = True)
    fare_data.rename(columns=lambda x: x.strip(), inplace = True)
    print 'columns renamed',
    print ' took', time.clock() - local_start, 'seconds'
    
    local_start = time.clock()
    print 'merging data'    
    taxi_data = pd.merge(trip_data,fare_data,how='outer',sort=False)
    trip_data = None
    fare_data = None
    print 'data merged',
    print ' took', time.clock() - local_start, 'seconds'
   
    print 'total of', time.clock() - global_start, 'seconds so far'
    
    local_start = time.clock()
    print 'changing time formats'
    taxi_data['pickup_datetime'] = pd.to_datetime(taxi_data['pickup_datetime'])
    taxi_data['dropoff_datetime'] = pd.to_datetime(taxi_data['dropoff_datetime'])
    print 'time formats changed',
    print ' took', time.clock() - local_start, 'seconds'
    
    local_start = time.clock()
    print 'writing file'
    taxi_data.to_csv(taxifilename)
    print 'file written',
    print ' took', time.clock() - local_start, 'seconds'
    
    print 'total of', time.clock() - global_start, 'seconds'
    

    