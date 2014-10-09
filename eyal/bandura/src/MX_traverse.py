# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 13:49:47 2014

@author: eyalshiv
"""


import re
import numpy as np
from scipy import stats
#from operator import itemgetter

import psycopg2 as psy
import oauth2 as oauth

import MX_common
from MX_common import db_connect
from MX_common import p



def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)


# use the 7digital API otget URL for mp3 preview file
def get_song_url(song_id):
    consumer = oauth.Consumer(p['consumer_key'], p['consumer_secret'])
    request_url = "http://previews.7digital.com/clip/" +  song_id
    
    req = oauth.Request(method="GET", url=request_url,is_form_encoded=True)
    
    req['oauth_timestamp'] = oauth.Request.make_timestamp()
    req['oauth_nonce'] = oauth.Request.make_nonce()
    sig_method = oauth.SignatureMethod_HMAC_SHA1()
    
    req.sign_request(sig_method, consumer, token=None)
    
    return req.to_url()


# pick a random song from the DB
@db_connect
def pickRandomSong():
    
    g_conn = psy.connect(MX_common.g_db_conn_command)
    
    g_cur = g_conn.cursor()    

    q = "SELECT "\
            +"track_7digitalid "\
        +"FROM "\
            +MX_common.song_features_table_name+" "\
        +"ORDER BY \
            RANDOM() \
        LIMIT 1;"

    g_cur.execute(q)        
    id_7digital = g_cur.fetchall()

    g_conn.close()
    
    return id_7digital[0][0]



@db_connect
def get_7digital_id( cur_song_id ):
    
   # global g_cur
    g_conn = psy.connect(MX_common.g_db_conn_command)
    
    g_cur = g_conn.cursor()    
    
    q = "SELECT \
            track_7digitalid \
        FROM "\
            +MX_common.song_features_table_name+" "\
        "WHERE \
            song_id='" + cur_song_id + "';"
    g_cur.execute(q)        
    id_7digital = g_cur.fetchall()
    
    g_conn.close()
    
    return id_7digital[0][0]



@db_connect
def get_song_id_from_7digital( digital7_id ):
    
    #global g_cur
    g_conn = psy.connect(MX_common.g_db_conn_command)
    
    g_cur = g_conn.cursor()    
    
    q = "SELECT \
            song_id \
        FROM "\
            +MX_common.song_features_table_name+" "\
        "WHERE \
            track_7digitalid='" + digital7_id + "';"
    g_cur.execute(q)        
    song_id = g_cur.fetchall()

    g_conn.close()
    
    if song_id==[]:
        print "no song found!"
        return ""
        
    return song_id[0][0]


# fetch all song features from the DB
@db_connect
def get_song_by_7digital( digital7_id ):
    
    #global g_cur
    g_conn = psy.connect(MX_common.g_db_conn_command)
    
    g_cur = g_conn.cursor()    
    
    q = "SELECT \
            * \
        FROM "\
            +MX_common.song_features_table_name+" "\
        "WHERE \
            track_7digitalid='" + digital7_id + "';"
    g_cur.execute(q)        
    song_features = g_cur.fetchall()

    g_conn.close()
    
    if song_features!=None:        
        return song_features[0]
    else:
        print "song not found"
        return None        



# fetch song ID by either ID, title or song_ID (exact match)
@db_connect
def get_song_id_by_token( token ):
    
    #global g_cur
    g_conn = psy.connect(MX_common.g_db_conn_command)
    
    g_cur = g_conn.cursor()    
    
    q = "SELECT \
            track_7digitalid \
        FROM "\
            +MX_common.song_features_table_name+" "\
        "WHERE \
            track_7digitalid='" + token + "' OR song_id='" + token + "' OR title='" + token + "' \
        LIMIT 1;"
    g_cur.execute(q)        
    song_features = g_cur.fetchall()

    g_conn.close()
    
    if song_features!=[]:        
        print song_features[0][0]
        return song_features[0][0]
    else:
        print "token not found"
        return ''        



@db_connect
def findInSongsDB( song_ids ):
        
    g_conn = psy.connect(MX_common.g_db_conn_command)
    g_cur = g_conn.cursor()    

    best_match_id  = ''
    best_match_idx = -1    
    
    for i in range(len(song_ids)):
    
        q = "SELECT \
                track_7digitalid \
            FROM "\
                +MX_common.song_features_table_name+" "\
            "WHERE \
                track_7digitalid='" + song_ids[i] + "';"                
        #print g_cur
        g_cur.execute(q)
        songinlist_id = g_cur.fetchall()

        if songinlist_id != []:
            best_match_idx = i
            best_match_id  = songinlist_id[0][0]
            break;
    
    g_conn.close()
        
    return best_match_id, best_match_idx



# pick the next N songs, iteratively (at each stage pick the first suggestions)
@db_connect
def pickNextSongsWrapped( cur_song_id ):
    
    global p
    #global g_cur    
    
    g_conn = psy.connect(MX_common.g_db_conn_command)
    g_cur = g_conn.cursor()
    
    cur_song_id2 = get_song_id_from_7digital( cur_song_id )
    
    next_song_ids2 = list()    
    for i in range(p['num_forward_song_predictions']):
        next_song_ids = pickNextSongs( g_cur, p, cur_song_id2, 1, p['conservation'] )
        next_song_ids2.append([get_7digital_id( x ) for x in next_song_ids])
        cur_song_id2 = next_song_ids2[-1][0]

    g_conn.close()

    return next_song_ids2    
    
    
# write log line    
def printSongDescription( cur_song_f, verbose, dist=0 ):
    
    max_song_title = 2000
    max_artist_name = 2000   
    
    global p

    if cur_song_f == None:
        desc = 'No Song!!'
    else:
        if verbose==1:
            desc = "%s: Tmp=%3d Lou=% 3d Fam=%0.2f Vln=%0.2f Eng=%0.2f Dnc=%0.2f Acs=%0.2f Liv=%0.2f Spc=%0.2f Ins=%0.2f Yr=%04d   %s : %s" %\
                (cur_song_f[p['invkey']['song_id']], \
                 int(cur_song_f[p['invkey']['tempo']]), cur_song_f[p['invkey']['loudness']], cur_song_f[p['invkey']['artist_familiarity']], \
                 max(0,cur_song_f[p['invkey']['valence']]), max(0,cur_song_f[p['invkey']['energy']]), max(0,cur_song_f[p['invkey']['danceability']]), max(0,cur_song_f[p['invkey']['acousticness']]), max(0,cur_song_f[p['invkey']['liveness']]), max(0,cur_song_f[p['invkey']['speechiness']]), max(0,cur_song_f[p['invkey']['instrumentalness']]), \
                 cur_song_f[p['invkey']['year']], cur_song_f[p['invkey']['artist_name']][:min(max_artist_name,len(cur_song_f[p['invkey']['artist_name']]))], cur_song_f[p['invkey']['title']][:min(max_song_title,len(cur_song_f[p['invkey']['title']]))]) 
        else:#if verbose==0:
            desc = "%s: %s %s" %\
                (cur_song_f[p['invkey']['song_id']], \
                 cur_song_f[p['invkey']['artist_name']][:min(max_artist_name,len(cur_song_f[p['invkey']['artist_name']]))], cur_song_f[p['invkey']['title']][:min(max_song_title,len(cur_song_f[p['invkey']['title']]))]) 
            
    return desc
    
        
# pick the next song - give several suggestions
def pickNextSongs( cur, p, cur_song_id, mag, conservation=None, debug_print=0 ):    

    # fetch current song features
    q = "SELECT \
            * \
        FROM "\
            +MX_common.song_features_table_name+" "\
        "WHERE \
            song_id='" + cur_song_id + "';"
    cur.execute(q)        
    cur_song_f = cur.fetchall()

    #cur = conn.cursor()    
    verbose = 1
    cur_song_desc = printSongDescription( cur_song_f[0], verbose )
    
    # Update recently-played FIFO to prevent frequent repeats:
    # push current song into recently-played FIFOs:
    # history FIFO
    p['recently_played'].appendleft( p['currently_playing'] )
#    p['recently_played'].appendleft(cur_song_id)
    if len(p['recently_played']) > p['recently_played_num']:
        p['recently_played'].pop()   
    p['currently_playing'] = (cur_song_id, cur_song_desc)

    # avoid-replay FIFO
    p['avoid_recent'].appendleft(cur_song_id)
    if len(p['avoid_recent']) > p['recent_to_avoid_num']:
        p['avoid_recent'].pop()   
       
    
    t_scale      = p['unit_vec_inv'][p['invkey_distance_features']]
    t_cur_f      = np.array([cur_song_f[0][i] for i in p['invkey_distance_features']])
   
    if conservation != None:
        t_cons_f     = np.array([conservation[key] for key in p['distance_features']])
    else:
        t_cons_f     = np.array([0.0 for key in p['distance_features']])

# previous logic of similarity - degenerated
#    t_angle      = (1-t_cons_f) / np.linalg.norm(1-t_cons_f)
#    # calculate the ideal location of the next song (in terms of the relevant distance features)    
#    t_next_f     = t_cur_f + mag*t_angle*t_scale
    
    # fetch current song neighbors (=potentials for the next song)
    q = "SELECT \
            similaro\
        FROM "\
            +MX_common.MXG_table_name+" "\
        +"WHERE "\
            +"targeto='" + cur_song_id + "';"
    cur.execute(q)   
    neighbor_songs = cur.fetchall()

    # filter out duplicates
    neighbor_songs = list(set(neighbor_songs))
    print "#neighbors = " + str(len(neighbor_songs))
    # filter out recently-played songs
    neighbor_songs = [x for x in neighbor_songs if x[0] not in p['avoid_recent'] ]
    print "#neighbors (- recent) = " + str(len(neighbor_songs))

    # for each neighbor, fetch features and calc weighted distance to current song
    nb_disted = list()
    p['debug_neighbors'] = list()
    print "#neighbors: " + str(len(neighbor_songs))
    for neighbor in neighbor_songs:
        # fetch features of all neighbors
        q = "SELECT \
                *\
            FROM "\
                +MX_common.song_features_table_name+" "\
            +"WHERE "\
                +"song_id='" + neighbor[0] + "';"
        cur.execute(q)   
        neighbor_song_f = cur.fetchall()
        
        # for each neighbor, calculate its distance from the ideal location
        t_neighbor_f = np.array([neighbor_song_f[0][i] for i in p['invkey_distance_features']])
        sdist = MX_common.calcDistanceInner(t_neighbor_f, t_cur_f, t_scale, t_cons_f, 'L2')

        # log neighbor's detailsfor debug purposes
        nb_disted.append((sdist[0], neighbor[0], printSongDescription( neighbor_song_f[0], 1 )))

    trip = list()
    for i in range(len(t_cons_f)):
        trip.append( ( p['invkey_distance_features'][i], p['distance_features'][i], t_cons_f[i], t_neighbor_f[i], t_cur_f[i] ) )
    print trip       
        
    nb_disted = sorted(nb_disted)

   # randomly pick the next song according to probabilities which correspond to the distance between current and neighboring songs
    epsilon = 0.0001
    xk = np.arange(len(nb_disted))
    pk = (np.array([x[0] for x in nb_disted]) + epsilon) ** p['noisyness']
    pk /= sum(pk)
    print (pk[:5]), sum(pk)
    custm = stats.rv_discrete(name='custm', values=(xk, pk))   

    p['debug_neighbors'] = list()
    for i in range(len(nb_disted)):
        desc = "0 %4.4f" % pk[i]
        p['debug_neighbors'].append(desc +" "+ nb_disted[i][2])
        
    # randomize a few potential next songs:
    # pick one, null its probability, resample and so on    
    ii        = list()
    ii.append(custm.rvs(size=1))
    p['debug_neighbors'][ii[-1]] = str(1) + p['debug_neighbors'][ii[-1]][1:]
    print "i0 = " + str(xk[ii[-1]]), (pk[:5]), sum(pk)
    for j in range(min(len(nb_disted),p['suggestions_num'])-1):
        pk[ii[-1]] = 0
        pk /= sum(pk)
        custm = stats.rv_discrete(name='custm', values=(xk, pk))   
        ii.append(custm.rvs(size=1))
        print "i"+ str(j+1) +" = " + str(xk[ii[-1]]), (pk[:5]), sum(pk)
        
        p['debug_neighbors'][ii[-1]] = str(2+j) + p['debug_neighbors'][ii[-1]][1:]

   
    next_song_ids = [ nb_disted[i][1] for i in ii]

    return next_song_ids


    