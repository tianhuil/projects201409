# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 11:43:55 2014

@author: eyalshiv
"""


#import os
import sys


#import glob
#import string
#import time
#import datetime
import numpy as np
import psycopg2 as psy
#import pandas as pd
#import csv



import MX_common
from MX_common import p 

import MX_traverse


sys.path.append('./MSongsDB-master/PythonSrc')
















def calcSongFeaturesStatisticsTBL(table, colHistBinSize, colNAvals):
    
    stats = dict()
    for key in table.keys():
#        i = invkey[key]
        if colNAvals!=None:
            NAval = colNAvals[key]
        else:
            NAval = ''

        stats[key] = calcColumnHistogramTBL(np.asarray(table[key]), colHistBinSize[key], NAval)

    return stats


def calcColumnHistogramTBL(column, binsize=-1, NAval=None):
    
    stats = dict()
    stats['NAval'] = NAval;
    stats['NAcount'] = sum(column==NAval)
    stats['samples'] = sum(column!=NAval)

    column = np.array([t for t in column if t!=NAval])
    
    stats['BinSize'] = binsize
    
    if len(column)>0:
        if binsize==-1:
            stats['hist'] = np.bincount(column)
            stats['edges'] = np.unique(column)
        elif binsize>0:
            bins = (column.max()-column.min()) / binsize
            stats['hist'], stats['edges'] = np.histogram(column, bins, (column.min(), column.max()))
        else:
            stats['hist'] = None
            
        if binsize!=None:
            stats['mean']        = np.mean(column)
            stats['std']         = np.std(column)
            stats['percentiles'] = np.percentile(column, range(1,100))
        else:
            stats['mean'] = -1
            stats['std'] = -1
            stats['percentiles'] = -1*np.ones((99))
            
    else:
        stats['hist'] = None
        stats['edges'] = None
        stats['mean'] = -1
        stats['std'] = -1
        stats['percentiles'] = -1*np.ones((99))
        
    return stats
   


def printSFstats(SFstats, filename):
    f = open(filename ,'wt');
    for key in SFstats.keys():
        # print key
        if SFstats[key]['percentiles']!=None:
            keyline = "key=%s, samples=%d, mean=%f, std=%f, median=%f, percentile_1=%f, percentile_99=%f\n" % (key, SFstats[key]['samples'], SFstats[key]['mean'], SFstats[key]['std'], SFstats[key]['percentiles'][49], SFstats[key]['percentiles'][0], SFstats[key]['percentiles'][98])
        else:
            keyline = "key=%s, samples=%d, mean=%f, std=%f, median=%f, percentile_1=%f, percentile_99=%f\n" % (key, SFstats[key]['samples'], SFstats[key]['mean'], SFstats[key]['std'], None, None, None)
    
        f.write(keyline)
    f.close()
    


"""
def calcSongFeaturesStatisticsDB(conn, table):
    
    
    col_hist = calcColumnHistogramDB(conn, table, column, nullval=None)
    
    return stats


def calcColumnHistogramDB(conn, table, column, nullval=None):

    # column histogram
    SELECT COUNT(grade) FROM table GROUP BY grade ORDER BY grade
        
    
    if nullval~=None
        stats['NA'] = ;
        
    
    return stats
"""






def constructGraph( conn, p, song_features_table_name, artist_similarities_table_name, graph_table_name, debug_print=False ):
        
    cur = conn.cursor()


    MX_common.resetTable( conn, graph_table_name, ['targeto text', 'similaro text, dist real'] )

        
    # read songs_list
    q = "SELECT \
            song_id \
        FROM "\
            +song_features_table_name +";"
    cur.execute(q)
    songs_list = cur.fetchall()
    
    node_stats = dict()
    node_stats['neighbors_cur_artist'] = list()
    node_stats['neighbors_topo'] = list()
    node_stats['neighbors_metric'] = list()
    node_stats['mean_dist'] = list()
    node_stats['similar_artists'] = list()
    edge_stats = dict()
    edge_stats['dist'] = list()
    edge_stats['vdist'] = list()
    
    # for each song (the focal song), find its neighbors
    for focal_song_id in songs_list[::1]:        
        focal_song_id = focal_song_id[0]
        
        if debug_print:
            print "focal_song: " + focal_song_id        
        
        # fetch all focal song's features
        q = "SELECT \
                * \
            FROM "\
                +song_features_table_name+" "\
            "WHERE \
                song_id='" + focal_song_id + "';"
        cur.execute(q)        
        focal_song_f = cur.fetchall()
    
        # find all songs that are TOPOLOGICALLY close (based on artist similarity):
        
        # find all song of current artist
        q = "SELECT "\
                +"song_id "\
            +"FROM "\
                +song_features_table_name+" "\
            +"WHERE "\
                +"artist_id='" + focal_song_f[0][p['invkey']['artist_id']] + "';"
        cur.execute(q)
        song_ids_cur_artist = cur.fetchall()
    
        node_stats['neighbors_cur_artist'].append(len(song_ids_cur_artist))

        if debug_print:
            for song_id in song_ids_cur_artist:
                print "same artist songs: " + song_id[0]  
    
        
        # find all artists similar to current artist
        q = "SELECT "\
                +"similaro "\
            +"FROM "\
                +artist_similarities_table_name+" "\
            +"WHERE "\
                +"targeto='" + focal_song_f[0][p['invkey']['artist_id']] + "';"
        cur.execute(q)
        artist_ids_topo = cur.fetchall()
    
        node_stats['similar_artists'].append(len(artist_ids_topo))
    
        
        song_ids_topo = list()
        # add all song IDs of the similar artists
        for artist_id in artist_ids_topo:
            # fetch all songs of this artist
            q = "SELECT "\
                    +"song_id "\
                +"FROM "\
                    +song_features_table_name+" "\
                +"WHERE "\
                    +"artist_id='" + artist_id[0] + "';"
            cur.execute(q)
            cur_song_ids = cur.fetchall()
#            if len(cur_song_ids)>0:
#                cur_song_ids = cur_song_ids[0]
            for song_id in cur_song_ids:
                song_ids_topo.append(song_id)
        
            # stage 2 - goo deeper into the tree of artist_similarities. This requires holding a fifo of nodes / some sort of recursion                
        
        node_stats['neighbors_topo'].append(len(song_ids_topo))

        if debug_print:
            for song_id in song_ids_topo:
                print "similar artists songs: " + song_id[0]        
    
            
        # find all songs that are METRICALLY close (based on song features)
        song_ids_metric = list()
        for key in p['relevant_features']:
            key_range = ( focal_song_f[key] - p['unit_vec'][key]*p['construct_neighborhood_metric_diameter'] , focal_song_f[key] +  )
            q = "SELECT "\
                    +"song_id "\
                +"FROM "\
                    +song_features_table_name+" "\
                +"WHERE "\
                    +key+ ">="+ str(key_range[0]) + " AND "+ key+ "<="+ str(key_range[1])+";"
            cur.execute(q)
            cur_song_ids = cur.fetchall()
            for id in cur_song_ids[0]:
                song_ids_metric.append(id)
    
        node_stats['neighbors_metric'].append(len(song_ids_metric))
    
        
        # combine all potential neighbors song IDs
        song_ids_combined = list(set(song_ids_cur_artist) | set(song_ids_topo) | set(song_ids_metric))   
    
    
        # for each potential neighbor, measure its distance from the focal point
        potential_neighbors = list()
        for neighbor_song_id in song_ids_combined:    
 #           print "song id: "+neighbor_song_id
            # fetch features for each potential neighbor
            q = "SELECT \
                    *\
                FROM "\
                    +song_features_table_name+" "\
                +"WHERE "\
                    +"song_id='" + neighbor_song_id[0] + "';"
            cur.execute(q)   
            neighbor_song_f = cur.fetchall()
        
        
            # calculate distance to current song    
            sdist = MX_traverse.calcDistance(focal_song_f[0], neighbor_song_f[0], p['distance_type_construct'])
    
            # filter songs that are too distant    
            if sdist[0] < p['maximal_overall_distance']:
                potential_neighbors.append((neighbor_song_id[0],sdist[0], sdist[1]))
        
        # sort potential neighbors by distance    
    #    potential_neighbors = sorted(potential_neighbors, key=lambda x: x[1])
    
        if len(potential_neighbors)>0:
            node_stats['mean_dist'].append( np.mean([x[1] for x in potential_neighbors]) )
        else:
            node_stats['mean_dist'].append(-1)
    
    
        # add potential neighbors and truncate, if there are too many, based on distance
        for neighborhood_type in neighboorhoodtypes:
            for neighbor in potential_neighbors[neighborhood_type][0:min(max_MXG_neighbors[neighborhood_type], len(potential_neighbors[neighborhood_type]))]:
    #            print "n0 " + neighbor[0]
    #            print "n1 " + str(neighbor[1])
                q = "INSERT INTO "\
                        +graph_table_name+" \
                        (targeto, similaro, dist) \
                    VALUES \
                        ('"+ focal_song_id +"', '"+ neighbor[0] +"', '"+ str(neighbor[1]) +"');"
                cur.execute(q)
                q = "INSERT INTO "\
                        +graph_table_name+" \
                        (targeto, similaro, dist) \
                    VALUES \
                        ('"+ neighbor[0] +"', '"+ focal_song_id +"', '"+ str(neighbor[1]) +"');"
                cur.execute(q)
                
                edge_stats['dist'].append( neighbor[1] )
                edge_stats['vdist'].append( neighbor[2] )
            
            
    #            MXG_target.append( song_id[0] )
    #            MXG_source.append( potential_neighbors[0] )
    
    
    return node_stats, edge_stats













# connect to the main db (assuming it was already constructed using 'createDB')
conn_db = psy.connect("dbname='my_db_test' user='eyalshiv' host='localhost' password='' port=8787")
conn_db.autocommit = True
#    conn_out.rollback()

cur = conn_db.cursor()


# # print names of tables in the db, to make sure it is in tact
# MX_common.listTablesInDB(conn_db)



# calculate each features statistics

# TEMP PATCH ! 
# I'm starting to work primitively by fetching the whole features table instead of doing the calculations using SQL on the DB - Fui!






q = """SELECT \
        * \
    FROM \
        song_features\
"""

cur.execute(q);
song_features = cur.fetchall()  



SFtable = dict()
for key in p['colnames']:
    SFtable[key] = [row[p['invkey'][key]] for row in song_features]

 
SFstats = calcSongFeaturesStatisticsTBL(SFtable, p['colHistBinSize2'], p['colNAvals2']);


printSFstats(SFstats, 'SFstats_summary.txt')

# Specify the features used, and filter the song_features table to only those row which have all relevant fields
# Stage 2 - allow missing fields

# # ~PATCH - interpolate song_hotttnesss from artist_hotttnesss when it's missing
# if p['interpolate_song_hotttnesss_from_artist'] == True:
#     for i in range(len(SFtable['song_id'])):
#         if SFtable['song_hotttnesss'][i] == SFstats['song_hotttnesss']['NAval']:
#             SFtable['song_hotttnesss'][i] = SFtable['artist_hotttnesss'][i]

 


# PATCH! - this should be implemented against the SQL db

# # find rows which have data for all mandatory fields
# full_row = np.ones(np.shape(SFtable['song_id']))

# for key in p['mandatory_features']:
#     exists = SFtable[key] != np.tile(SFstats[key]['NAval'],len(SFtable[key]))
#     full_row = np.logical_and( full_row, exists )

# # filtering the songs
# SFtable2 = dict()
# for key in p['relevant_features_all']:
#     SFtable2[key] = [SFtable[key][i] for i in range(len(full_row)) if full_row[i]] 



# Normalize the features:

# #   recalculate the distribution of features since we filtered out many of the songs
# SFstats2 = calcSongFeaturesStatisticsTBL(SFtable2, p['colHistBinSize2'], p['colNAvals2']);
# printSFstats(SFstats2, 'SFstats2_summary.txt')




# tmp_csv_songs_filtered_file = '/Users/eyalshiv/DI/musixplore/data/work/df_songs_filtered4.csv'
# 
# f = open(tmp_csv_songs_filtered_file, 'wt')
# f.write( getTableHeaderLine() + "\n" )
# for row in song_features:
#     if row[0] in SFtable2['song_id']:
#         f.write(",".join([str(x) for x in row]) + "\n")
# f.close()
# 
# MX_common.importFromDbCsv(conn_db, tmp_csv_songs_filtered_file, MX_common.song_features_filtered_table_name)





# build the MX graph - yoohoo!
mxg_stats = constructGraph( conn_db, p, MX_common.song_features_filtered_table_name, MX_common.artist_id_similarities_table_name, MX_common.MXG_table_name )


# # DEBUG
# cur.execute("SELECT * FROM "+MX_common.MXG_table_name+";")
# z = cur.fetchall()
# 
# vz = [np.mean([x[i] for x in mxg_stats[1]['vdist']]) for i in range(len(colnames))]


# cur.execute("SELECT * FROM "+MX_common.song_features_filtered_table_name+";")
# w = cur.fetchall()




#   build basic unit vector which normalizes all features to the same standard deviations (the means (=offsets) are meaningless)
p['unit_vec']     = -1*np.ones(np.shape(p['colnames'])) 
p['unit_vec_inv'] = -1*np.ones(np.shape(p['colnames'])) 

for i in range(len(p['colnames'])): #p['relevant_features']:  
    if p['colnames'][i] in SFstats2.keys():
        p['unit_vec'][i]     = 1/SFstats2[p['colnames'][i]]['std']
        p['unit_vec_inv'][i] = SFstats2[p['colnames'][i]]['std']
    else:
        p['unit_vec'][i] =-1
        p['unit_vec_inv'][i] =-1
 

p['conservation'] = dict()
for key in p['relevant_features']:
    p['conservation'][key] = 0;
    
p['conservation']['year']=1








# wrap-up
# close connections    

conn_db.close()

