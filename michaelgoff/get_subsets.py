import pandas as pd
import shapefile
import math
import numpy as np
import datetime
import json
from sklearn import tree
from matplotlib import pylab as plt
from sklearn import cross_validation
from sklearn import metrics

# Every instance of asdf indicates something to be done

# Following are some helpful filtering and aggregation functions

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
    
# Read shape files
r = shapefile.Reader('Data/NY Block Group Shapes/gz_2010_36_150_00_500k')
sr = r.shapeRecords()

station_data = pd.read_csv("map/station_data.csv")

def borough_existing(county):
    if county == 47:
        return "B"
    return "M"
    
station_data['boro'] = station_data['CensusCountyFips'].apply(lambda t: borough_existing(t))

def midtown(t):
    return float(t) > 40.75038
    
midtown_stations = station_data[station_data['lat'].apply(lambda t: midtown(t))]
brooklyn_stations = station_data[station_data['CensusCountyFips'] == 47]

def williamsburg(t):
    return float(t) > 40.7082
    
williamsburg_stations = brooklyn_stations[brooklyn_stations['lat'].apply(lambda t: williamsburg(t))]

def shape_file_record_to_block_tract(record):
    return record[0][11:18] + '.' + record[0][18:21]
# Usage example: shape_file_record_to_block_tract(sr[1234].record)

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

def block_group_near_a_station(rec,sc):
    for i in sc.index:
        for j in range(len(rec.shape.points)):
            if abs(rec.shape.points[j][1] - float(sc['lat'][i])) < 0.002 and abs(rec.shape.points[j][0] - float(sc['lon'][i])) < 0.003:
                return True
            if rec.shape.points[j][0] > -73.93 or rec.shape.points[j][0] < -74.03 or rec.shape.points[j][1] > 40.9 or rec.shape.points[j][1] < 40.6:
                return False
    return False
    
def make_block_group_data(extra_cols,sc,filename):
    BlockGroupsNearStations = []
    for i in range(len(sr)):
        rec = sr[i]
        if i%100 == 0:
            print str(i) + '/' + str(len(sr))
        if block_group_near_a_station(rec,sc):
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
    df_tracts = df_tracts[df_tracts['block_tract']!='0610143.001'] # Exclude Central Park
    df_tracts.to_csv("map/"+filename+".csv",encoding="utf-8")
    return df_tracts
    
MidtownBlockGroups = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], midtown_stations,"midtown_blockgroups")
                    
BrooklynBlockGroups = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], brooklyn_stations,"brooklyn_blockgroups")
                    
WilliamsburgBlockGroups = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], williamsburg_stations,"williamsburg_blockgroups")

json_data=open('map/new_stations.json')
data = json.load(json_data)
proposed_stations = pd.DataFrame({'lat':[s['k'] for s in data], 'lon':[s['A'] for s in data]})
proposed_stations.index = range(1000,1000+len(proposed_stations.index))
json_data.close()

def new_borough(lat):
    if lat < 40.739445:
        return 'B'
    if lat < 40.75849116:
        return 'Q'
    return 'M'
    
proposed_stations['boro'] = proposed_stations['lat'].apply(lambda t: new_borough(t))
proposed_stations['id'] = proposed_stations.index + 10000

def queens(t):
    return float(t) > 40.739445 and float(t) < 40.75849116
    
def new_brooklyn(t):
    return float(t) < 40.739445
    
queens_stations = proposed_stations[proposed_stations['lat'].apply(lambda t: queens(t))]
newbrooklyn_stations = proposed_stations[proposed_stations['lat'].apply(lambda t: new_brooklyn(t))]

allbrooklyn_stations = pd.DataFrame({'lat':brooklyn_stations['lat'].append(newbrooklyn_stations['lat']), 'lon':brooklyn_stations['lon'].append(newbrooklyn_stations['lon'])})
all_stations = pd.DataFrame({'lat':station_data['lat'].append(proposed_stations['lat']), 
                             'lon':station_data['lon'].append(proposed_stations['lon']),
                             'id':station_data['id'].append(proposed_stations['id']),
                             'boro':station_data['boro'].append(proposed_stations['boro'])})

QueensBlockGroups = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], queens_stations,"queens_blockgroups")
                    
AllBrooklynBlockGroups = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], allbrooklyn_stations,"allbrooklyn_blockgroups")
                    
AllBlockGroups = make_block_group_data([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], all_stations,"all_blockgroups")
         
# Calculate numbers of people who live in the areas served by CitiBike in various areas of the city           
WilliamsburgBlockGroups['Population'].apply(int).sum() # 36626
MidtownBlockGroups['Population'].apply(int).sum() # 166506
BrooklynBlockGroups['Population'].apply(int).sum() # 194048
QueensBlockGroups['Population'].apply(int).sum() # 19394
AllBrooklynBlockGroups['Population'].apply(int).sum() # 389433
# Calculate total and morning ridership in various regions
williamsburg_stations['COUNT'].sum() # 117405
williamsburg_stations['Hour06'].sum() +williamsburg_stations['Hour07'].sum() + williamsburg_stations['Hour08'].sum() + williamsburg_stations['Hour09'].sum() # 19811
midtown_stations['COUNT'].sum() # 2519582
midtown_stations['Hour06'].sum() +midtown_stations['Hour07'].sum() + midtown_stations['Hour08'].sum() + midtown_stations['Hour09'].sum() # 560754
brooklyn_stations['COUNT'].sum() # 809929
brooklyn_stations['Hour06'].sum() +brooklyn_stations['Hour07'].sum() + brooklyn_stations['Hour08'].sum() + brooklyn_stations['Hour09'].sum() # 164058

# Currently, Midtown has a total morning ridership of 3.368 per person near a station.
# For Williamsburg, it is 0.5409
# For all of Brooklyn, it is 0.8455

# Build a dataframe that, for all pairs of stations, gives distance, number of riders, and presence of a bridge.
def make_dist_df():
    cols = ['dist','count','bridge'] # Distance between stations and the count
    ids = station_data.index
    full_index = [str(id1)+'x'+str(id2) for id1 in ids for id2 in ids]
    df = pd.DataFrame(index=full_index, columns=cols)
    count = 0
    for id1,id2 in [(id1,id2) for id1 in ids for id2 in ids]:
        # Put the ridership between the two stations into the table
        second = station_data.ix[id2,'id']
        df.ix[str(id1)+'x'+str(id2),'count'] = station_data[str(second)][int(id1)]
        # Get distance
        lat1 = station_data['lat'][int(id1)]
        lat2 = station_data['lat'][int(id2)]
        lon1 = station_data['lon'][int(id1)]
        lon2 = station_data['lon'][int(id2)]
        c1 = station_data['CensusCountyFips'][int(id1)]
        c2 = station_data['CensusCountyFips'][int(id2)]
        d = distance_on_unit_sphere(lat1,lon1, lat2,lon2)
        if count < 400:
            print str(c1) + "   " + str(c2)
        if (c1 != c2):
            df.ix[str(id1)+'x'+str(id2),'bridge'] = 1
        else:
            df.ix[str(id1)+'x'+str(id2),'bridge'] = 0
        count += 1
        if (count%1000 == 0):
            print count
        df.ix[str(id1)+'x'+str(id2),'dist'] = d
    return df
    
df = make_dist_df()

# Estimate ridership based on bridge and distance properties.
def build_model(data_frame):
    indices = np.random.permutation(xrange(len(data_frame)))
    df_rand = data_frame.ix[indices,:]
    X = df_rand.ix[:,['dist','bridge']]
    y = df_rand['count']
    
    X_, X_cv, y_, y_cv = cross_validation.train_test_split(X, y, test_size=0.20, random_state=42)
    best_mse = 9999999
    best_d = 0
    best_model = []
    for d in range(1,20):
        clf = tree.DecisionTreeRegressor(max_depth=d)
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X_, y_, test_size=0.25, random_state=43)
        clf = clf.fit(X_train, y_train)
                
        y_pred = clf.predict(X_test)
        mse = metrics.mean_squared_error(y_test, y_pred)
        
        if mse < best_mse:
            best_mse, best_d, best_model = mse, d, clf
    best_pred = best_model.predict(X_cv)
    cv_mse = metrics.mean_squared_error(y_cv, best_pred)
    return [best_d, cv_mse, y_cv.var(), best_model]
        
mod = build_model(make_dist_df())
    
def make_full_dist_df():
    cols = ['dist','bridge'] # Distance between stations and the count
    ids = all_stations.index
    full_index = [str(id1)+'x'+str(id2) for id1 in ids for id2 in ids]
    df = pd.DataFrame(index=full_index, columns=cols)
    count = 0
    for id1,id2 in [(id1,id2) for id1 in ids for id2 in ids]:
        # Get distance
        lat1 = all_stations['lat'][int(id1)]
        lat2 = all_stations['lat'][int(id2)]
        lon1 = all_stations['lon'][int(id1)]
        lon2 = all_stations['lon'][int(id2)]
        c1 = all_stations['boro'][int(id1)]
        c2 = all_stations['boro'][int(id2)]
        d = distance_on_unit_sphere(lat1,lon1, lat2,lon2)
        if count < 500:
            print str(c1) + "   " + str(c2)
        if (c1 != c2):
            df.ix[str(id1)+'x'+str(id2),'bridge'] = 1
        else:
            df.ix[str(id1)+'x'+str(id2),'bridge'] = 0
        count += 1
        if (count%1000 == 0):
            print count
        df.ix[str(id1)+'x'+str(id2),'dist'] = d
    return df

all_dists = make_full_dist_df()
all_dists['projected_usage'] = mod.predict(all_dists)

def unpack_dists(df_dists, df_stations): # Turn the all_dists data frame above into a more usable form
    rows = df_stations.id.values
    ret = pd.DataFrame(index = rows, columns = rows)
    ret = ret.fillna(0)
    ret['proj'] = 0
    ret['gain'] = 0
    count = 0
    for i in df_dists.index:
        count += 1
        if (count%1000 == 0):
            print count
        start, end = i.split('x')
        start_index = df_stations['id'][int(start)]
        end_index = df_stations['id'][int(end)]
        ret.ix[start_index, end_index] = df_dists['projected_usage'][i]
        ret.ix[start_index,'proj'] += df_dists['projected_usage'][i]
        if start_index > 10000 or end_index > 10000: # Add this gain only for new stations
            ret.ix[start_index,'gain'] += df_dists['projected_usage'][i]
    return ret
    
def attach_boros(d_matrix, a_stations):
    d_matrix['boro'] = ""
    for i in a_stations.index:
        thisid = a_stations.ix[i,'id']
        d_matrix.ix[thisid,'boro'] = a_stations.ix[i,'boro']
    return d_matrix