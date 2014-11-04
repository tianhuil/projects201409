# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 11:43:55 2014

@author: eyalshiv
"""


import sys
import time
import datetime

import numpy as np
import psycopg2 as psy

import MX_common
from MX_common import db_connect 
from MX_common import p 

sys.path.append('./MSongsDB-master/PythonSrc')



def printSFstats(SFstats, filename):
    
    f = open(filename ,'wt');
    for key in SFstats.keys():
        if SFstats[key]['percentiles']!=None:
            keyline = "key=%s, samples=%d, mean=%f, std=%f, median=%f, percentile_1=%f, percentile_99=%f\n" % (key, SFstats[key]['samples'], SFstats[key]['mean'], SFstats[key]['std'], SFstats[key]['percentiles'][49], SFstats[key]['percentiles'][0], SFstats[key]['percentiles'][98])
        else:
            keyline = "key=%s, samples=%d, mean=%f, std=%f, median=%f, percentile_1=%f, percentile_99=%f\n" % (key, SFstats[key]['samples'], SFstats[key]['mean'], SFstats[key]['std'], None, None, None)
    
        f.write(keyline)
    f.close()



@db_connect
def constructGraph( song_features_table_name, artist_similarities_table_name, graph_table_name, debug_print=False ): #graph_song_list_table_name, 

    global p

    SFstats = MX_common.initUnitVec( song_features_table_name )

    g_conn = psy.connect( MX_common.g_db_conn_command )
    g_conn.autocommit = True
    g_cur = g_conn.cursor()

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
                for song_id in cur_song_ids:
                    song_ids_topo.append(song_id[0])
            
                # TBD - goo deeper into the tree of artist_similarities. This requires holding a fifo of nodes / some sort of recursion                
            
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
    
                g_cur.execute(q)
                cur_song_ids = g_cur.fetchall()
                for id in cur_song_ids:
                    potential_neighbors[nbkey].append(id[0])
        
            node_stats['neighbors_metric'].append(len(potential_neighbors[nbkey]))
                
        # for each potential neighbor, measure its distance from the focal point
        for nbkey in p['neighborhood_types']:
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
                sdist = MX_common.calcDistance(focal_song_f[0], neighbor_song_f[0], p['distance_type_construct'])
    
                potential_neighbors_dist[nbkey].append((neighbor_song_id,sdist[0], sdist[1]))
    
            # sort potential neighbors by distance    
            potential_neighbors_dist[nbkey] = sorted(potential_neighbors_dist[nbkey], key=lambda x: x[1])
            if len(potential_neighbors_dist[nbkey])>0:
                node_stats['mean_dist'].append( np.mean([x[1] for x in potential_neighbors_dist[nbkey]]) )
            else:
                node_stats['mean_dist'].append(-1)
        
        print "#Feature NBs = " + str(len(potential_neighbors_dist[nbkey])) + ", Topo same artist NBs = " + str(len(song_ids_cur_artist)) + ", Topo similar artists NBs = " + str(len(song_ids_topo))
    
    
        # add potential neighbors and truncate, if there are too many, based on distance
        for nbkey in p['neighborhood_types']:
            for neighbor in potential_neighbors_dist[nbkey][0:min(p['max_MXG_neighbors'][nbkey], len(potential_neighbors_dist[nbkey]))]:
            
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
                                
    g_conn.close()
       
    return SFstats, node_stats, edge_stats




# Run the construction of the graph!
t3 = time.time()

# build the MX graph - yoohoo!
mxg_stats2 = constructGraph( MX_common.song_features_table_name, MX_common.artist_id_similarities_table_name, MX_common.MXG_table_name )

t4 = time.time()
stimelength = str(datetime.timedelta(seconds=t4-t3))
print stimelength


