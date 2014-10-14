# passenger_wait_proxy.py

# Computes a plot of a proxy I'm using for how difficult it is to hail a cab, which I'm 
# taking to be proportional to (num_cabs)*(avg_time_searching)*(avg_speed)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = pd.read_csv('../data/taxi_data_10.csv.gz',compression='gzip')

data = data[['hack_license','pickup_datetime','dropoff_datetime','trip_time_in_secs',
             'trip_distance','pickup_longitude','pickup_latitude','dropoff_longitude',
             'dropoff_latitude']]

data['pickup_datetime'] = pd.to_datetime(data['pickup_datetime'])
data['dropoff_datetime'] = pd.to_datetime(data['dropoff_datetime'])

data = data[data['pickup_datetime'].apply(lambda x: x.day) < 29]

data = data.sort(['hack_license','pickup_datetime'])

data['min_to_next'] = (data['pickup_datetime'].shift(-1) - \
                        data['dropoff_datetime']) / np.timedelta64(1,'m')
                        
data['avg_trip_speed'] = 3600*data['trip_distance'] / data['trip_time_in_secs']

data['day'] = data['pickup_datetime'].apply(lambda x: x.dayofweek)
data['hour'] = data['pickup_datetime'].apply(lambda x: x.hour)

             
min_time = 0
max_time = 15
min_speed = 0
max_speed = 30


data['coverage'] = np.maximum(np.minimum(data['min_to_next'],max_time),min_time) * \
                np.maximum(np.minimum(data['avg_trip_speed'],max_speed),min_speed)
                
g = data.groupby(['day','hour'])
                
for day in range(7):
    fig, axes = plt.subplots(nrows=4,ncols=6)
    for hour in range(24):
        g.get_group((day,hour)).plot(ax = axes[hour/6,hour%6],figsize=(30, 24), kind='hexbin', x='dropoff_longitude', 
                                         y='dropoff_latitude', C='coverage', reduce_C_function=np.sum, 
                                         gridsize=40, vmin = 0, vmax = 100000, extent=[-74.1,-73.9,40.65,40.85], mincnt=10)        
        axes[hour/6,hour%6].set_title(str(hour)+":00")
        day_name = {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
    fig.suptitle(day_name[day],fontsize=24)
    fig.savefig('website/static/hail_difficulty-'+day_name[day]+'.png',bbox_inches='tight')
