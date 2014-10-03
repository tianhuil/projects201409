import pandas as pd
import shapefile
import math
import numpy as np
import datetime
import json

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

def Midtown(t):
    return float(t) > 40.75038
midtown_stations = station_data[station_data['lat'].apply(lambda t: Midtown(t))]
brooklyn_stations = station_data[station_data['CensusCountyFips'] == 47]
def Williamsburg(t):
    return float(t) > 40.7082
williamsburg_stations = brooklyn_stations[brooklyn_stations['lat'].apply(lambda t: Williamsburg(t))]

def ShapeFileRecordToBlockTract(record):
    return record[0][11:18] + '.' + record[0][18:21]
# Usage example: ShapeFileRecordToBockTract(sr[1234].record)

# Attach census tract and block group
def toBlockTract(geoid):
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

# asdf Modify this function to apply to the subsets above
def BlockGroupNearAStation(rec,sc):
    for i in sc.index:
        for j in range(len(rec.shape.points)):
            if abs(rec.shape.points[j][1] - float(sc['lat'][i])) < 0.002 and abs(rec.shape.points[j][0] - float(sc['lon'][i])) < 0.003:
                return True
            if rec.shape.points[j][0] > -73.93 or rec.shape.points[j][0] < -74.03 or rec.shape.points[j][1] > 40.9 or rec.shape.points[j][1] < 40.6:
                return False
#    return ShapeFileRecordToBlockTract(rec.record) in sc['tract_block'].values
    return False
    
def MakeBlockGroupData(extra_cols,sc,filename):
    BlockGroupsNearStations = []
    for i in range(len(sr)):
        rec = sr[i]
        if i%100 == 0:
            print str(i) + '/' + str(len(sr))
        if BlockGroupNearAStation(rec,sc):
            BlockGroupsNearStations.append([ShapeFileRecordToBlockTract(rec.record), rec.shape.points])
    df_tracts = pd.DataFrame({'block_tract':[x[0] for x in BlockGroupsNearStations], 'points':[str(x[1]) for x in BlockGroupsNearStations]})
    for i in range(len(extra_cols)):
        print extra_cols[i]['f']
        df_ext = pd.read_csv(extra_cols[i]['f'],encoding="utf-8")
        df_ext["block_tract"] = df_ext["GEO.id2"].apply(toBlockTract)
        df_merged = df_tracts.merge(df_ext, on="block_tract")
        cols = extra_cols[i]['cols']
        for j in range(len(cols)):
            df_tracts[cols[j]['in_f']] = df_merged[cols[j]['in_df']]
            
    df_tracts = df_tracts[df_tracts['Population']!='0']
    df_tracts = df_tracts[df_tracts['block_tract']!='0610143.001'] # Exclude Central Park
    df_tracts.to_csv("map/"+filename+".csv",encoding="utf-8")
    return df_tracts
    
# asdf Make several of these, one for each territory
MidtownBlockGroups = MakeBlockGroupData([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], midtown_stations,"midtown_blockgroups")
                    
BrooklynBlockGroups = MakeBlockGroupData([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], brooklyn_stations,"brooklyn_blockgroups")
                    
WilliamsburgBlockGroups = MakeBlockGroupData([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
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

def Queens(t):
    return float(t) > 40.739445 and float(t) < 40.75849116
def NewBrooklyn(t):
    return float(t) < 40.739445
queens_stations = proposed_stations[proposed_stations['lat'].apply(lambda t: Queens(t))]
newbrooklyn_stations = proposed_stations[proposed_stations['lat'].apply(lambda t: NewBrooklyn(t))]

allbrooklyn_stations = pd.DataFrame({'lat':brooklyn_stations['lat'].append(newbrooklyn_stations['lat']), 'lon':brooklyn_stations['lon'].append(newbrooklyn_stations['lon'])})
all_stations = pd.DataFrame({'lat':station_data['lat'].append(proposed_stations['lat']), 'lon':station_data['lon'].append(proposed_stations['lon'])})

QueensBlockGroups = MakeBlockGroupData([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], queens_stations,"queens_blockgroups")
                    
AllBrooklynBlockGroups = MakeBlockGroupData([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], allbrooklyn_stations,"allbrooklyn_blockgroups")
                    
AllBlockGroups = MakeBlockGroupData([{'f':"Data/AgeBySex/AgeBySex.csv",'cols':[{'in_f':'Population','in_df':'D001'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_G001_with_ann.csv",'cols':[{'in_f':'Area','in_df':'VD067'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P6_with_ann.csv",'cols':[{'in_f':'AllRaces','in_df':'D001'},{'in_f':'Black','in_df':'D003'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P29_with_ann.csv",'cols':[{'in_f':'Households','in_df':'D001'},{'in_f':'NonfamilyHouseholds','in_df':'D018'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P27_with_ann.csv",'cols':[{'in_f':'RelNonrel','in_df':'D001'},{'in_f':'Nonrelatives','in_df':'D002'}]},
                    {'f':"Data/aff_download/DEC_10_SF1_P8_with_ann.csv",'cols':[{'in_f':'AllRaceCounts','in_df':'D001'},{'in_f':'MixedRace','in_df':'D009'}]},
                    {'f':"Data/households_age/HouseholdsAges.csv",'cols':[{'in_f':'OccupiedHousing','in_df':'HD01_S01'},{'in_f':'RentedHouseholds','in_df':'HD01_S04'}]}
                    ], all_stations,"all_blockgroups")
                    
# WilliamsburgBlockGroups['Population'].apply(int).sum() # 36626
# MidtownBlockGroups['Population'].apply(int).sum() # 166506
# BrooklynBlockGroups['Population'].apply(int).sum() # 194048
# QueensBlockGroups['Population'].apply(int).sum() # 19394
# AllBrooklynBlockGroups['Population'].apply(int).sum() # 389433

# williamsburg_stations['COUNT'].sum() # 117405
# williamsburg_stations['Hour06'].sum() +williamsburg_stations['Hour07'].sum() + williamsburg_stations['Hour08'].sum() + williamsburg_stations['Hour09'].sum() # 19811
# midtown_stations['COUNT'].sum() # 2519582
# midtown_stations['Hour06'].sum() +midtown_stations['Hour07'].sum() + midtown_stations['Hour08'].sum() + midtown_stations['Hour09'].sum() # 560754
# brooklyn_stations['COUNT'].sum() # 809929
# brooklyn_stations['Hour06'].sum() +brooklyn_stations['Hour07'].sum() + brooklyn_stations['Hour08'].sum() + brooklyn_stations['Hour09'].sum() # 164058

# Currently, Midtown has a total morning ridership of 3.368 per person near a station.
# For Williamsburg, it is 0.5409
# For all of Brooklyn, it is 0.8455

# We predict a total morning ridership for Brooklyn of about 1,300,000, or 3044 per day, by assuming Brooklyn will grow to the per capita ridership that Midtown has now.
# Since Queens is disconnected by bridges, and it will only have 11 stations, we assumed that Queens will have the per capita ridership that Williamsburg has now.
# That would be 10490 morning trips, or  24.7 per day.

# asdf Define new territories: Extended Brooklyn and Queens and predict ridership based on today's Midtown, Williamsburg