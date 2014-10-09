# split_by_day_hour.py

# splits up the taxi data into seperate files corresponding to a (day, hour) pair, so 168
# files in total. Hopefully, with the total taxi data being roughly 12 GB (compressed)
# these files will chunk the data into reasonable size increments for analysis, which 
# can then be analyzed and written into a sql database.

import pandas as pd

for month in range(1,13):

    read_file_name = '../data/taxi_data_'+str(month)+'.csv.gz'
    
    print 'Loading ' + read_file_name

    taxi_data = pd.read_csv(read_file_name,compression='gzip')
    
    print 'Loaded'

    taxi_data['pickup_datetime'] = pd.to_datetime(taxi_data['pickup_datetime'])
    taxi_data['day_of_week'] = taxi_data['pickup_datetime'].apply(lambda x: x.weekday())
    taxi_data['hour'] = taxi_data['pickup_datetime'].apply(lambda x: x.hour)
    
    print 'Data transformed'

    time_groups = taxi_data.groupby(['day_of_week','hour'],sort=False)

    for group in time_groups:

        file_name = '../data/dayhour/'+str(group[0][0])+'-'+str(group[0][1])+'.csv'

        group[1].to_csv(file_name,header=False,index=False,mode='a')
    
     