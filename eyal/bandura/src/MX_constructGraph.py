# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 11:43:55 2014

@author: eyalshiv
"""


#import os
import sys
import time
import datetime

#import glob
#import string
import numpy as np
import psycopg2 as psy
#import pandas as pd
#import csv



import MX_common
from MX_common import db_connect 
from MX_common import p 
#from MX_common import g_conn 
#from MX_common import g_cur 

#import MX_traverse


sys.path.append('./MSongsDB-master/PythonSrc')










 


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
    








@db_connect
def constructGraph( song_features_table_name, artist_similarities_table_name, graph_table_name, debug_print=False ): #graph_song_list_table_name, 

    global p
    #global g_cur
    #global g_conn


    SFstats = MX_common.initUnitVec( song_features_table_name )

    #SFstats = calcSongFeaturesStatistics( song_features_table_name, p['colHistBinSize2'], p['colNAvals2'] )


    g_conn = psy.connect( MX_common.g_db_conn_command )
    g_conn.autocommit = True
#    conn_out.rollback()
    g_cur = g_conn.cursor()


    # calc features statistics and set corresponding unit_vector


    """
    #   build basic unit vector which normalizes all features to the same standard deviations (the means (=offsets) are meaningless)
    p['unit_vec']     = -1*np.ones(np.shape(p['colnames'])) 
    p['unit_vec_inv'] = -1*np.ones(np.shape(p['colnames'])) 
    
    for i in range(len(p['colnames'])): #p['relevant_features']:  
        if p['colnames'][i] in SFstats.keys():
            p['unit_vec'][i] = 1/SFstats[p['colnames'][i]]['std']
        else:
            p['unit_vec'][i] = -1
            
        p['unit_vec_inv'][i] = 1 / p['unit_vec'][i]
 
        print "unit vector field: " + p['colnames'][i] + " " + str(p['unit_vec_inv'][i]) + " " + str(p['unit_vec'][i])"""


        
    #neighboorhoodtypes = ['topo', 'features']    
        



        
    # read song_id list
    q = "SELECT \
            song_id \
        FROM "\
            +song_features_table_name +";"
    g_cur.execute(q)
    songs_list = g_cur.fetchall()
    
    node_stats = dict()
    node_stats['neighbors_cur_artist'] = list()
    node_stats['neighbors_topo'] = list()
    node_stats['neighbors_metric'] = list()
    node_stats['mean_dist'] = list()
    node_stats['similar_artists'] = list()
    edge_stats = dict()
    edge_stats['dist'] = list()
    edge_stats['vdist'] = list()
    
    

    MX_common.resetTable( g_cur, graph_table_name, ['targeto text', 'similaro text'] )
#    MX_common.resetTable( conn, graph_table_name, ['targeto text', 'similaro text, dist real'] )


    
    # for each song (the focal song), find its neighbors
    for focal_song_id in songs_list[::1]: #::100        
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
        g_cur.execute(q)        
        focal_song_f = g_cur.fetchall()
        
#        print focal_song_f[0]

    
        # find all songs that are TOPOLOGICALLY close (based on artist similarity):
    
        potential_neighbors = dict()
        potential_neighbors_dist = dict()

        nbkey = 'topo'
        if nbkey in p['neighborhood_types']:
            potential_neighbors[nbkey] = list()            
            
            #   find all songs of current artist
            q = "SELECT "\
                    +"song_id "\
                +"FROM "\
                    +song_features_table_name+" "\
                +"WHERE "\
                    +"artist_id='" + focal_song_f[0][p['invkey']['artist_id']] + "';"
            g_cur.execute(q)
            song_ids_cur_artist = g_cur.fetchall()
            song_ids_cur_artist = [x[0] for x in song_ids_cur_artist]
            
            node_stats['neighbors_cur_artist'].append(len(song_ids_cur_artist))
    
            if debug_print:
                for song_id in song_ids_cur_artist:
                    print "same artist songs: " + song_id[0]  
        
            
            #   find all artists similar to current artist
            q = "SELECT "\
                    +"similaro "\
                +"FROM "\
                    +artist_similarities_table_name+" "\
                +"WHERE "\
                    +"targeto='" + focal_song_f[0][p['invkey']['artist_id']] + "';"
            g_cur.execute(q)
            artist_ids_topo = g_cur.fetchall()
        
            node_stats['similar_artists'].append(len(artist_ids_topo))
        
            
            song_ids_topo = list()
            #   add all songs of similar artists
            for artist_id in artist_ids_topo:
                # fetch all songs of this artist
                q = "SELECT "\
                        +"song_id "\
                    +"FROM "\
                        +song_features_table_name+" "\
                    +"WHERE "\
                        +"artist_id='" + artist_id[0] + "';"
                g_cur.execute(q)
                cur_song_ids = g_cur.fetchall()
#                print [x[0] for x in cur_song_ids]
    #            if len(cur_song_ids)>0:
    #                cur_song_ids = cur_song_ids[0]
                for song_id in cur_song_ids:
                    song_ids_topo.append(song_id[0])
            
                # stage 2 - goo deeper into the tree of artist_similarities. This requires holding a fifo of nodes / some sort of recursion                
            
            node_stats['neighbors_topo'].append(len(song_ids_topo))
    
            if debug_print:
                for song_id in song_ids_topo:
                    print "similar artists songs: " + song_id[0]        
        
            
            # combine all potential TOPOLOGICAL neighbors
            potential_neighbors[nbkey] = list(set(song_ids_cur_artist) | set(song_ids_topo))
        

        
        # find all songs that are METRICALLY close (based on song features)
        nbkey = 'features'
        if nbkey in p['neighborhood_types']:
            potential_neighbors[nbkey] = list()  

            for key in p['relevant_features']:
                radius = abs(p['unit_vec_inv'][p['invkey'][key]]) * p['construct_neighborhood_metric_diameter']
                key_range = ( focal_song_f[0][p['invkey'][key]] - radius , focal_song_f[0][p['invkey'][key]] + radius )
#                print key, p['unit_vec'][p['invkey'][key]]
                q = "SELECT "\
                        +"song_id "\
                    +"FROM "\
                        +song_features_table_name+" "\
                    +"WHERE "\
                        +key+ ">="+ str(key_range[0]) + " AND "+ key+ "<="+ str(key_range[1]) + " "\
                    +"ORDER BY \
                        RANDOM() \
                    LIMIT "\
                        + str(p['max_feature_neighborhood_size']) +";"
    
#                print q
    
                g_cur.execute(q)
                cur_song_ids = g_cur.fetchall()
#                print [x[0] for x in cur_song_ids]
                for id in cur_song_ids:
                    potential_neighbors[nbkey].append(id[0])
        
            node_stats['neighbors_metric'].append(len(potential_neighbors[nbkey]))
        
        
        # for each potential neighbor, measure its distance from the focal point
        for nbkey in p['neighborhood_types']:
#            print "nbkey = " + nbkey
            potential_neighbors_dist[nbkey] = list()
            
            for neighbor_song_id in potential_neighbors[nbkey]:
                # fetch features for each potential neighbor
                q = "SELECT \
                        *\
                    FROM "\
                        +song_features_table_name+" "\
                    +"WHERE "\
                        +"song_id='" + neighbor_song_id + "';"
                g_cur.execute(q)   
                neighbor_song_f = g_cur.fetchall()
        
                # calculate distance to current song  
#                print "focal: "
#                print focal_song_f[0]
#                print "neighbor: "
#                print neighbor_song_id, len(neighbor_song_f)
#                print neighbor_song_f[0]
                sdist = MX_common.calcDistance(focal_song_f[0], neighbor_song_f[0], p['distance_type_construct'])
    
#                # filter songs that are too distant    
#                if sdist[0] < p['maximal_overall_distance']:
#                    potential_neighbors[neighboorhoodtypes].append((neighbor_song_id[0],sdist[0], sdist[1]))
                potential_neighbors_dist[nbkey].append((neighbor_song_id,sdist[0], sdist[1]))
    
            # sort potential neighbors by distance    
            potential_neighbors_dist[nbkey] = sorted(potential_neighbors_dist[nbkey], key=lambda x: x[1])
#            print len(potential_neighbors_dist[nbkey])
            if len(potential_neighbors_dist[nbkey])>0:
#                print potential_neighbors_dist[nbkey]
#                print [x[1] for x in potential_neighbors_dist[nbkey]]
                node_stats['mean_dist'].append( np.mean([x[1] for x in potential_neighbors_dist[nbkey]]) )
            else:
                node_stats['mean_dist'].append(-1)
    
    
        print "#Feature NBs = " + str(len(potential_neighbors_dist[nbkey])) + ", Topo same artist NBs = " + str(len(song_ids_cur_artist)) + ", Topo similar artists NBs = " + str(len(song_ids_topo))

    
    
        # add potential neighbors and truncate, if there are too many, based on distance
        for nbkey in p['neighborhood_types']:
#            print "truncated: " + nbkey + "=" + str(len(potential_neighbors_dist[nbkey][0:min(p['max_MXG_neighbors'][nbkey], len(potential_neighbors_dist[nbkey]))]))
            for neighbor in potential_neighbors_dist[nbkey][0:min(p['max_MXG_neighbors'][nbkey], len(potential_neighbors_dist[nbkey]))]:
    #            print "n0 " + neighbor[0]
    #            print "n1 " + str(neighbor[1])
            
                # add both direction of the edge (later on we call a function that filters duplicate edges)
                q = "INSERT INTO "\
                        +graph_table_name+" \
                        (targeto, similaro) \
                    VALUES \
                        ('"+ focal_song_id +"', '"+ neighbor[0] +"');"
                g_cur.execute(q)
                q = "INSERT INTO "\
                        +graph_table_name+" \
                        (targeto, similaro) \
                    VALUES \
                        ('"+ neighbor[0] +"', '"+ focal_song_id +"');"
                g_cur.execute(q)
                
                edge_stats['dist'].append( neighbor[1] )
                edge_stats['vdist'].append( neighbor[2] )
            
            
    #            MXG_target.append( song_id[0] )
    #            MXG_source.append( potential_neighbors[0] )

    
        
        
    # prune non-unique esges (how?)
        
    # prune isolated nodes (how? more generally, we need to have a single connected component - maybe add artifical bridges?)    
        
    g_conn.close()
       
    return SFstats, node_stats, edge_stats








# connect to the main db (assuming it was already constructed using 'createDB')
#conn_db = psy.connect("dbname='my_db_test' user='eyalshiv' host='localhost' password='' port=8787")
#conn_db.autocommit = True
#    conn_out.rollback()

#cur = conn_db.cursor()




t3 = time.time()

# build the MX graph - yoohoo!
mxg_stats2 = constructGraph( MX_common.song_features_table_name, MX_common.artist_id_similarities_table_name, MX_common.MXG_table_name )
#mxg_stats = constructGraph( conn_db, p, MX_common.song_features_filtered_table_name, MX_common.artist_id_similarities_table_name, MX_common.MXG_table_name )

t4 = time.time()
stimelength = str(datetime.timedelta(seconds=t4-t3))
print stimelength


# # DEBUG
# cur.execute("SELECT * FROM "+MX_common.MXG_table_name+";")
# z = cur.fetchall()
# 
# vz = [np.mean([x[i] for x in mxg_stats[1]['vdist']]) for i in range(len(colnames))]


# cur.execute("SELECT * FROM "+MX_common.song_features_filtered_table_name+";")
# w = cur.fetchall()











# wrap-up
# close connections    

#conn_db.close()

