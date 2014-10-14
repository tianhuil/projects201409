# hex_data.py

# Returns the centers of the hexagons for a tiling of the region [-74.1,-73.9]x[40.65,40.85]
# as well as a computed quantity for each hexagon representing the ease of hailing a 
# yellow cab in that region.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

days_of_week = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday',
            5: 'Saturday', 6: 'Sunday'}

print 'Loading data...'

data = pd.read_csv('../data/taxi_data_10.csv.gz',compression='gzip')

print 'Loaded.'

data = data[['hack_license','pickup_datetime','dropoff_datetime','trip_time_in_secs',
             'trip_distance','pickup_longitude','pickup_latitude','dropoff_longitude',
             'dropoff_latitude']]
             
data['pickup_datetime'] = pd.to_datetime(data['pickup_datetime'])
data['dropoff_datetime'] = pd.to_datetime(data['dropoff_datetime'])

data = data[data['pickup_datetime'].apply(lambda x: x.day) < 29]

data = data.sort(['hack_license','pickup_datetime'])

data['time_finding_fare'] = (data['pickup_datetime'] - \
                            data['dropoff_datetime'].shift(1)) / np.timedelta64(1,'m')

data['avg_trip_speed'] = 3600*data['trip_distance'] / data['trip_time_in_secs']

data['day'] = data['pickup_datetime'].apply(lambda x: x.dayofweek)
data['hour'] = data['pickup_datetime'].apply(lambda x: x.hour)

min_time = 0
max_time = 15
min_speed = 0
max_speed = 30

data['coverage'] = np.maximum(np.minimum(data['time_finding_fare'],max_time),min_time) * \
                np.maximum(np.minimum(data['avg_trip_speed'],max_speed),min_speed)
                
g = data.groupby(['day','hour'])
grid_size = 50

for day in range(7):
    for hour in range(24):
        fig = plt.figure()
#         figure = plt.hexbin(x=g.get_group((day,hour))['dropoff_longitude'], 
#                     y=g.get_group((day,hour))['dropoff_latitude'], 
#                     C=g.get_group((day,hour))['coverage'], 
#                     reduce_C_function=np.sum, 
#                     gridsize=grid_size,extent=[-74.021865,-73.936549,
#                                                 40.686398,40.8143615],
#                     vmin = 0, vmax = 100000, cmap='Oranges') 
#                     
#         figure.get_axes().set_axis_off()
#         fig = plt.gcf()
#         
# For short label at top

        fig.set_size_inches(2.5, 5.0)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax = plt.hexbin(x=g.get_group((day,hour))['dropoff_longitude'], 
                    y=g.get_group((day,hour))['dropoff_latitude'], 
                    C=g.get_group((day,hour))['coverage'], 
                    reduce_C_function=np.sum, mincnt=2,
                    gridsize=grid_size,extent=[-74.021865,-73.936549,
                                                40.686398,40.8143615],
                    vmin = 0, vmax = 40000, cmap='Oranges')
        plt.text(0.5, .975,str(hour)+':00 on '+days_of_week[day],
             size=14, horizontalalignment='center',
             verticalalignment='center',
             transform = fig.gca().transAxes)

        print 'Saving hex-'+str(day)+'-'+str(hour)+'.png'
        plt.savefig('../data/hexdata/hex-'+str(day)+'-'+str(hour)+'.png')       
        
# For long label at bottom
        
#         fig.text(.5,0,'Ease of hailing yellow cab at '+str(hour)+':00 on '+days_of_week[day], 
#            horizontalalignment='center',transform=fig.gca().transAxes, size=8)
#      
#         print 'Saving hex-'+str(day)+'-'+str(hour)+'.png'
#         plt.savefig('../data/hexdata/hex-'+str(day)+'-'+str(hour)+'-large.png',
#                     bbox_inches='tight')       
#         
        
#         hex_data = pd.DataFrame(figure.get_offsets(),columns=['longitude','latitude'])
#         hex_data['counts'] = figure.get_array()
#         
#         print 'Writing hex-'+str(day)+'-'+str(hour)+'.csv'
#         
#         hex_data.to_csv('../data/hexdata/hex-'+str(day)+'-'+str(hour)+'.csv')