# split_by_license.py

# splits up the taxi data into seperate files corresponding to the first two digits of
# the hack_license. Since these are hex digits, this should result in 256 separate files
# each roughly 130 MB (uncompressed).

import pandas as pd
import os.path

for month in range(1,13):

    read_file_name = '../data/taxi_data_'+str(month)+'.csv.gz'
    
    print 'Loading ' + read_file_name

    taxi_data = pd.read_csv(read_file_name,compression='gzip')
    
    print 'Loaded'

    taxi_data['group_key'] = taxi_data['hack_license'].apply(lambda x: x[:2])    
    groups = taxi_data.groupby(['group_key'],sort=False)

    for group in groups:

        file_name = '../data/license/'+group[0]+'.csv'
        if (not os.path.isfile(file_name)):
            group[1].to_csv(file_name,header=True,index=False,mode='a')
        else:
            group[1].to_csv(file_name,header=False,index=False,mode='a')
    
     