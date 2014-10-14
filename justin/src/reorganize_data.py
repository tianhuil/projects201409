# reorganize_data.py

# To be run after data is merged using merge_taxi_data.py (if necessary).
# Imports taxi_data_*.csv.gz files, and reorganizes/pares down the data to what's 
# necessary for the project

import numpy as np
import pandas as pd
# from datetime import datetime # unnecessary due to pandas datetime

# Read in data

taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip')

# If things get too slow:
# taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip',nrows=10000)

# Select columns we care about

# taxi_data = taxi_data[['hack_license','pickup_datetime','dropoff_datetime',
#                        'trip_time_in_secs', 'trip_distance', 'pickup_longitude', 
#                        'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 
#                        'tip_amount', 'total_amount']]

taxi_data = taxi_data[['hack_license','trip_time_in_secs', 'trip_distance', 
                        'pickup_longitude', 
                        'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude']]

# Change times to pandas datetime format

taxi_data['pickup_datetime'] = pd.to_datetime(taxi_data['pickup_datetime'])
taxi_data['dropoff_datetime'] = pd.to_datetime(taxi_data['dropoff_datetime'])

# Sort by hack_license, then by pickup_datetime. Then reindex.

taxi_data.sort(['hack_license','pickup_datetime'], inplace = True)
taxi_data.index = range(len(taxi_data))

# Round lat/long coordinates with some tolerance tol, convert to string because of
# weird things happening with rounding. We only need as index anyways.

tol = .01

taxi_data['pick_lat_rnd'] = \
    (np.rint(taxi_data['pickup_latitude']/tol)*tol).apply(lambda x: str(x))
taxi_data['pick_lon_rnd'] = \
    (np.rint(taxi_data['pickup_longitude']/tol)*tol).apply(lambda x: str(x))
taxi_data['drop_lat_rnd'] = \
    (np.rint(taxi_data['dropoff_latitude']/tol)*tol).apply(lambda x: str(x))
taxi_data['drop_lon_rnd'] = \
    (np.rint(taxi_data['dropoff_longitude']/tol)*tol).apply(lambda x: str(x))

# Group trips according to origin and destination.

# orig_groups = taxi_data.groupby(['pick_lat_rnd','pick_lon_rnd'])
# dest_groups = taxi_data.groupby(['drop_lat_rnd','drop_lon_rnd'])

trip_groups = taxi_data.groupby(['pick_lat_rnd','pick_lon_rnd',
                                    'drop_lat_rnd','drop_lon_rnd'])
                                    
# Print out the mean travel time organized by type of trip, sorted by number of trips

trip_groups['trip_time_in_secs'].agg([np.mean,len]).sort('len')

# May be less memory intensive to do it this way:
# trip_groups['trip_time_in_secs'].mean
# trip_groups['trip_time_in_secs'].count

# For testing purposes

trip_groups['trip_time_in_secs'].agg([lambda x: np.percentile(x,50),len]).sort('len')

# Useful command:
# trip_groups.get_group(('83.0', '-33.0', '84.0', '-115.0'))

# Plot a histogram of trip times between 


