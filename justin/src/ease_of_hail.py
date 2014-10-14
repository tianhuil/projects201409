# ease_of_hail.py

# Analysis of easiest places to hail cab in the city

# Idea: divide the city up into tiny grids (.001 degrees latitude and longitude). 
# For simplicity we want to aggregate all the information relevant to determining how
# hard it is to hail a cab in that grid element at that single point.

# Information we need:
#   1. The number of cabs in the area. Ideally the number of cabs picking people up in
#       the area (which of course we know).
#   2. The time it takes between dropping off a fare and picking up the next one---up to a
#       point. Obviously we don't want to count breaks/shift changes. Similarly, beyond 
#       a certain value it's safe to assume the cab just left the neighborhood, so it
#       shouldn't matter if it's 20 or 40 minutes outside the neighborhood.
#   3. The average speed of a cab in the area, perhaps computed from the average speed
#       of short journeys either starting or ending in the area.

#   With these three pieces of information, we can estimate the area covered by cabs
#   looking for a fare, which should be proportional to num_cabs*time*speed. This should
#   reflect the probability of someone appearing at random being in the grid being
#   passed by an available cab.

import numpy as np
import pandas as pd
import os

for filename in os.listdir('../data/license'):
    
    path = '../data/license' + str(filename)
    data = pd.read_csv(path)
    
    data = data[['hack_license','pickup_datetime','dropoff_datetime','trip_time_in_secs',  
        'trip_distance', 'pickup_longitude', 'pickup_latitude', 'dropoff_longitude',
        'dropoff_latitude']]
    
    data['pickup_datetime'] = pd.to_datetime(data['pickup_datetime'])
    data['dropoff_datetime'] = pd.to_datetime(data['dropoff_datetime'])
    
    data['avg_speed'] = 3600*data['trip_distance']/data['trip_time_in_secs']
    data['time_to_next'] = (data['pickup_datetime'].shift(-1) - data['dropoff_datetime']) \
                                / np.timedelta64(1,'m')
    
    data['rnd_start_lat'] = (np.rint(data['pickup_latitude']/.001)*.001).apply(lambda x: str(x))
    data['rnd_start_lon'] = (np.rint(data['pickup_longitude']/.001)*.001).apply(lambda x: str(x))
    data['rnd_end_lat'] = (np.rint(data['dropoff_latitude']/.001)*.001).apply(lambda x: str(x))
    data['rnd_end_lon'] = (np.rint(data['dropoff_longitude']/.001)*.001).apply(lambda x: str(x))
    
    data['day'] = data['pickup_datetime'].apply(lambda x: x.dayofweek)
    data['hour'] = data['pickup_datetime'].apply(lambda x: x.hour)
    
    def truncate(x,too_low,too_high,cap):
        if x < too_low or x > too_high:
            return 0
        elif x > cap:
            return cap
        else:
            return x

    data['trunc_time_to_next'] = data['time_to_next'].apply(lambda x: truncate(x,0,30,15))

    data['trip_time_in_secs'] = (data['dropoff_datetime'] - data['pickup_datetime'])/np.timedelta64(1,'s')

    data['short_trip'] = (data['trip_distance']<2) & (data['avg_speed']>2) & (data['avg_speed']<30)
    data['short_trip_distance'] = data['trip_distance']*data['short_trip']
    data['short_trip_time'] = data['trip_time_in_secs']*data['short_trip']
    
    group_start = data.groupby(['rnd_start_lat','rnd_start_lon','day','hour'])
    group_end = data.groupby(['rnd_end_lat','rnd_end_lon','day','hour'])
    
    
    
    group_start.agg({'trunc_time_to_next': [lambda x: len(x), np.sum],
                 'short_trip': np.sum,
                 'short_trip_time': np.sum})
    
    