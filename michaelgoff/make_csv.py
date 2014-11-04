import pandas as pd
import shapefile
import math
import numpy as np
import datetime

# Following are some helpful filtering and aggregation functions

# Restrict trip data to morning trips
def restrict_hours(t, first_hour, last_hour):
    i = int(t[11:13]) # Extract the appropriate characters from the starttime field for the hour
    return i >= first_hour and i <= last_hour

# Apply an age bracket to the rider, given the birth year.  Assumes data from 2014
def age_bracket(age_str,brackets):
    try:
        a = int(age_str)
    except ValueError:
        return 'uxxxx'
    lower = '00'
    for i in range(len(brackets)):
        if a >= 2014 - brackets[i]:
            return 'u' + lower + str(brackets[i])
        lower = str(brackets[i]+1)
    if a >= 1901:
        return 'u' + lower + 'xx'
    return 'uxxxx'

############################################################

# Apply a sequence of filters to the data
def trip_data_filter(tripdata, filters):
    for f in filters:
        if f['type'] == 'RestrictHours':
            tripdata = tripdata[tripdata['starttime'].apply(lambda t: restrict_hours(t,f['first'],f['last']))]
    return tripdata
    
def is_round_trip(s,e):
    if (s==e):
        return "Round"
    return "NotRound"
    
def gender(g):
    if g == "1":
        return 'Male'
    elif g == "2":
        return 'Female'
    return 'GenderUnknown'
    
def get_weekday(t):
    y = int(t[0:4])
    m = int(t[5:7])
    d = int(t[8:10])
    return ['Mon','Tues','Wednes','Thurs','Fri','Satur','Sun'][datetime.date(y,m,d).weekday()] + 'day'
    
def hour_bracket(t): # Classifies times according to hour
    return "Hour" + str(t[11:13]) # For now, we ignore the brackets and use 24 buckets

def add_classifiers(tripdata, classifiers):
    for c in classifiers:
        if c['t'] == "AgeBrackets": # Create age bracket classifiers where c['brackets'] contains the division points
            tripdata[c['colname']] = tripdata['birth year'].apply(lambda x: age_bracket(x,c['brackets']))
        if c['t'] == "Counter":
            tripdata[c['colname']] = 'COUNT'
        if c['t'] == "Round":
            tripdata[c['colname']] = map(lambda s, e: is_round_trip(s,e), 
               tripdata['start station id'], tripdata['end station id'])
        if c['t'] == "Gender":
            tripdata[c['colname']] = map(lambda s: gender(s), tripdata['gender'])
        if c['t'] == "Weekday":
            tripdata[c['colname']] = tripdata['starttime'].apply(lambda x: get_weekday(x))
        if c['t'] == "HourBrackets":
            tripdata[c['colname']] = tripdata['starttime'].apply(lambda x: hour_bracket(x))
    return tripdata   

# Create a dataframe that has counts of values of ref by index
def group_by_count(data,index,column_names = None,refs=[]):
    gb = data.groupby([index]+refs)
    agg = gb[index].count()
    for i in range(len(refs)):
        agg = agg.unstack()
    agg = agg.fillna(0)
    if (column_names):
        agg.rename(columns=column_names,inplace=True)
    return agg

def group_variables(data,index,agg_pipeline):
    gb = data.groupby(index)
    ret = 0
    ret = pd.DataFrame(gb[index].count())
    del ret[index]
    for a in agg_pipeline:
        col_names = None
        if 'column_names' in a:
            col_names = a['column_names']
        suffixes = ['','']
        if 'suffixes' in a:
            suffixes = a['suffixes']
        ret = ret.join(group_by_count(data,index,refs=a['refs'],column_names = col_names),rsuffix = suffixes[1])
    return ret

# Read in the trip data and combine it into a dataframe with statistics
def read_data(y,m,filters=[],classifiers=[],groups=[],dfindex=''):
    print "Reading " + str([y,m])
    y = str(y)
    m = str(m)
    if (len(m)==1):
        m = '0'+m
    cb2 = pd.read_csv("Data/"+y+"-"+m+" - Citi Bike trip data.csv",dtype=object)
    cb2 = trip_data_filter(cb2, filters)
    cb2 = add_classifiers(cb2, classifiers)
    grouped = group_variables(cb2,dfindex,groups)
    grouped.fillna(0)
    return grouped

def read_multi_data(dates,filters=[],classifiers=[],groups=[],dfindex=''):
    StationCount = read_data(dates[0][0],dates[0][1], filters=filters, classifiers=classifiers, groups=groups,dfindex=dfindex)
    StationCount.fillna(0)
    for i in range(1,len(dates)):
        new_data = read_data(dates[i][0],dates[i][1], filters=filters, classifiers=classifiers,groups=groups,dfindex=dfindex)
        for col in new_data.columns.values:
            if col not in StationCount.columns.values:
                StationCount[col] = 0
        for col in StationCount.columns.values:
            if col not in new_data.columns.values:
                new_data[col] = 0
        for row in new_data.index:
            if row not in StationCount.index:
                StationCount.ix[row,:] = 0
        for col in StationCount.index:
            if row not in new_data.index:
                new_data[row,:] = 0
        StationCount = StationCount.add(new_data,fill_value=0)
    return StationCount

# Courtesy of http://www.johndcook.com/python_longitude_latitude.html
def distance_on_unit_sphere(lat1, long1, lat2, long2):
    
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    if cos >= 1:
        return 0
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6378.1 # In kilometers

# Attach census tract and block group
def to_block_tract(geoid):
    geoid = str(geoid)
    try:
        tract = geoid[2:9]
    except ValueError:
        return "0"
    try:
        block = geoid[9:12]
    except ValueError:
        return "0"
    return tract + '.' + block
    
def shape_file_record_to_block_tract(record):
    return record[0][11:18] + '.' + record[0][18:21]
# Usage example: shape_file_record_to_block_tract(sr[1234].record)
    
# Read the basic station data with census information attached
station_census = pd.read_csv("Data/citibike_stations_census.csv",dtype=object)
station_census = station_census.ix[:331,:]
station_census = station_census.set_index('id')
station_census['tract_block'] = station_census.apply(lambda row: row.CensusCountyFips + row.CensusTract + row.CensusBlockGroup,axis=1)

# Read shape files
r = shapefile.Reader('Data/NY Block Group Shapes/gz_2010_36_150_00_500k')
sr = r.shapeRecords()

def block_group_near_a_station(rec,sc):
    for i in range(332):
        for j in range(len(rec.shape.points)):
            if abs(rec.shape.points[j][1] - float(sc['lat'][i])) < 0.002 and abs(rec.shape.points[j][0] - float(sc['lon'][i])) < 0.003:
                return True
            if rec.shape.points[j][0] > -73.93 or rec.shape.points[j][0] < -74.03 or rec.shape.points[j][1] > 40.9 or rec.shape.points[j][1] < 40.6:
                return False
    return False
    
def make_block_group_data(extra_cols):
    BlockGroupsNearStations = []
    for i in range(len(sr)):
        rec = sr[i]
        if i%100 == 0:
            print str(i) + '/' + str(len(sr))
        if block_group_near_a_station(rec, station_census):
            BlockGroupsNearStations.append([shape_file_record_to_block_tract(rec.record), rec.shape.points])
    df_tracts = pd.DataFrame({'block_tract':[x[0] for x in BlockGroupsNearStations], 'points':[str(x[1]) for x in BlockGroupsNearStations]})
    for i in range(len(extra_cols)):
        print extra_cols[i]['f']
        df_ext = pd.read_csv(extra_cols[i]['f'],encoding="utf-8")
        df_ext["block_tract"] = df_ext["GEO.id2"].apply(to_block_tract)
        df_merged = df_tracts.merge(df_ext, on="block_tract")
        cols = extra_cols[i]['cols']
        for j in range(len(cols)):
            df_tracts[cols[j]['in_f']] = df_merged[cols[j]['in_df']]
            
    df_tracts = df_tracts[df_tracts['Population']!='0']
    df_tracts = df_tracts[df_tracts['block_tract']!='0610143.001']
    df_tracts.to_csv("map/blockgroup_data.csv",encoding="utf-8")
    return df_tracts
    
BlockGroupsNearStations = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ])

all_months = [[2013,i] for i in range(7,13)] + [[2014,i] for i in range(1,9)]

StationCount = read_multi_data(all_months,
                             filters = [],
                             classifiers = [{'t':'AgeBrackets','colname':'age','brackets':[17,24,34,44,54,64]},
                                            {'t':'Counter','colname':'COUNT'},
                                            {'t':'Round','colname':'ROUND'},
                                            {'t':'Gender','colname':'GENDER'},
                                            {'t':'Weekday','colname':'WEEKDAY'},
                                            {'t':'HourBrackets','colname':'HOUR'}],
                             dfindex='start station id',
                             groups = [{'refs':['end station id']},{'refs':['COUNT']},{'refs':['ROUND']},{'refs':['GENDER']},{'refs':['WEEKDAY']},{'refs':['HOUR']}])
station_census = station_census.join(StationCount)

def irange(lat,lon): # return an array of distances from (x,y) to all stations
    dists = map(lambda s_lat, s_lon: distance_on_unit_sphere(lat,lon,float(s_lat),float(s_lon)), 
               station_census['lat'], station_census['lon'])
    dists.sort()
    return np.mean(dists[:5])
    
station_census['Sparsity'] = map(lambda s_lat, s_lon: irange(float(s_lat),float(s_lon)), 
               station_census['lat'], station_census['lon'])
               
# Attach average travel distance to the data frame
station_census['avg_dist'] = 0
for i in station_census.index:
    dist = 0
    lat1 = float(station_census.ix[i,'lat'])
    lon1 = float(station_census.ix[i,'lon'])
    for j in station_census.index:
        lat2 = float(station_census.ix[j,'lat'])
        lon2 = float(station_census.ix[j,'lon'])
        dist += station_census.ix[i,j] * distance_on_unit_sphere(lat1, lon1, lat2, lon2)
    station_census.ix[i,'avg_dist'] = dist / station_census.ix[i,'COUNT']
    
# Attach average travel time
def avg_time(y,m): # Get the average travel time and count for one month
    y = str(y)
    m = str(m)
    if (len(m)==1):
        m = '0'+m
    cb2 = pd.read_csv("Data/"+y+"-"+m+" - Citi Bike trip data.csv",dtype=object)
    cb2['tripduration'] = cb2['tripduration'].astype(float)
    gb = cb2.groupby('start station id')
    return gb['tripduration'].sum()
    
def GetAverageTravelTime(dates):
    StationCount = avg_time(dates[0][0],dates[0][1])
    for i in range(1,len(dates)):
        new_data = avg_time(dates[i][0],dates[i][1])
        StationCount += new_data
    return StationCount
station_census['AverageTripTime'] = GetAverageTravelTime(all_months)
        
station_census.to_csv("map/station_data.csv",encoding="utf-8")