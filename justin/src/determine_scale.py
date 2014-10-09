# determine_scale.py

# Prints data relevant to determining what scale of lat/lon discretization should be
# chosen. For a list of tolerances, shows the number of origin/destination pairs that 
# have more trips than a given list of thresholds.

import numpy as np
import pandas as pd

# Read in (nonrandom) sample of raw data

sample_size = 10000

taxi_data = pd.read_csv('../data/taxi_data_1.csv.gz',compression='gzip',nrows=sample_size)

# Select relevant columns

taxi_data = taxi_data[['trip_time_in_secs', 'pickup_longitude', 'pickup_latitude', 
                        'dropoff_longitude', 'dropoff_latitude', 'pickup_datetime']]
                        
# Remove rows with blatantly wrong coordinates

min_lat = 40.5
max_lat = 40.9
min_lon = -74.3
max_lon = -73.7

good_pickup_lat = (taxi_data['pickup_latitude']>min_lat) \
                        & (taxi_data['pickup_latitude']<max_lat)
good_dropoff_lat = (taxi_data['dropoff_latitude']>min_lat) \
                        & (taxi_data['dropoff_latitude']<max_lat)
good_pickup_lon = (taxi_data['pickup_longitude']>min_lon) \
                        & (taxi_data['pickup_longitude']<max_lon)
good_dropoff_lon = (taxi_data['dropoff_longitude']>min_lon) \
                        & (taxi_data['dropoff_longitude']<max_lon)                       
                        
taxi_data = taxi_data[good_pickup_lat&good_dropoff_lat&good_pickup_lon&good_dropoff_lon]

# Choose list of possible rounding tolerances for latitude/longitude coordinates.

tolerances = [1, .5, .2, .1, .05, .02, .01, .005, .002, .001]

# Choose list of thresholds for number of trips between two grid elements.

thresholds = [1, 10, 100, 1000]

# Define function for rounding lat/lon and representing as string.

def roundCoord(coordinates, tol):
     return (np.rint(coordinates/tol)*tol).apply(lambda x: str(x))
     
# Convert 'pickup_datetime' to pandas datetime format, then extract
# 'day_of_week' and 'hour'.

taxi_data['pickup_datetime'] = pd.to_datetime(taxi_data['pickup_datetime'])
taxi_data['day_of_week'] = taxi_data['pickup_datetime'].apply(lambda x: x.weekday())
taxi_data['hour'] = taxi_data['pickup_datetime'].apply(lambda x: x.hour)

     
# Compute values of interest

output = []

for tol in tolerances:
    taxi_data['pick_lat_rnd'] = \
        (np.rint(taxi_data['pickup_latitude']/tol)*tol).apply(lambda x: str(x))
    taxi_data['pick_lon_rnd'] = \
        (np.rint(taxi_data['pickup_longitude']/tol)*tol).apply(lambda x: str(x))
    taxi_data['drop_lat_rnd'] = \
        (np.rint(taxi_data['dropoff_latitude']/tol)*tol).apply(lambda x: str(x))
    taxi_data['drop_lon_rnd'] = \
        (np.rint(taxi_data['dropoff_longitude']/tol)*tol).apply(lambda x: str(x))

    trip_groups = taxi_data.groupby(['pick_lat_rnd','pick_lon_rnd','drop_lat_rnd',
                                    'drop_lon_rnd','day_of_week','hour'],sort=False)
    
    counts = trip_groups['trip_time_in_secs'].count()
    
    values = []
    for thresh in thresholds:
        values.append(sum(counts > thresh))
    
    output.append(values)

# plot results

df = pd.DataFrame(output,index=tolerances,columns=thresholds)

figure = df.plot(loglog=True).get_figure()
figure.savefig('scale_plot.png')


