# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 13:49:47 2014

@author: eyalshiv
"""


import re
#import collections
import numpy as np
from scipy import stats
from operator import itemgetter

import psycopg2 as psy
import oauth2 as oauth

import MX_common
from MX_common import db_connect
from MX_common import p
#from MX_common import g_cur
#from MX_common import g_conn

#from MX_constructGraph import init_globals_static





#g_unit_vec = []
#g_unit_vec_inv = []
#g_conservation = []



def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)






"""
@db_connect
def createPlayList_Constant( first_song_id, length, conservation, p ):
    
    global g_cur    
    
    recent = collections.deque([])
    playlist = list()
    
    playlist.append(first_song_id)
    recent.appendleft(first_song_id)
    
    for i in range(length-1):
        next_rec = pickNextSongs( g_cur, p, playlist[-1], 1, conservation )
        j = 0
        print next_rec
        while next_rec in recent[0:p['recent_to_avoid_num']] and j<p['avoid_recent_max_retries']:
            print "recent: " + next_rec
            j += 1
            next_rec = pickNextSongs( g_cur, p, next_rec, 1, conservation )
        
        playlist.append(next_rec)
        recent.appendleft(next_rec)
        if len(recent) > p['avoid_recent_num']:
            recent.pop()   
        
    return playlist
    

def addSongToPlaylist( filename, song_features, song_url=''):
    
    f = open(filename, 'at')
    
    f.write(",".join([str(x) for x in song_features]) + "," + song_url + "\n")
    
    f.close()

    

@db_connect    
def savePlayList( song_features_table_name, playlist, filename ):
    
    global g_cur    
    #cur = conn.cursor()
        
    f = open(filename, 'wt')

    # write headers
    f.write( MX_common.getTableHeaderLine() + "\n" )

    for song_id in playlist:
        # fetch song row
        q = "SELECT \
                * \
            FROM "\
                +song_features_table_name + " \
            WHERE \
                song_id='"+ song_id +"';"
        g_cur.execute(q)
        row = g_cur.fetchall()
        
        # write song row
        f.write(",".join([str(x) for x in row]) + "\n")

    f.close()
"""


def get_song_url(song_id):
    consumer = oauth.Consumer(p['consumer_key'], p['consumer_secret'])
    request_url = "http://previews.7digital.com/clip/" +  song_id
    
    req = oauth.Request(method="GET", url=request_url,is_form_encoded=True)
    
    req['oauth_timestamp'] = oauth.Request.make_timestamp()
    req['oauth_nonce'] = oauth.Request.make_nonce()
    sig_method = oauth.SignatureMethod_HMAC_SHA1()
    
    req.sign_request(sig_method, consumer, token=None)
    
    return req.to_url()



def savePlayList_7digitalURLs( song_features_table_name, playlist, filename ):

    global g_cur

    #cur = conn.cursor()

    f = open(filename, 'wt')

    # write headers
    f.write( "URL_7digital:text\n" )

    for song_id in playlist:
        # fetch song row
        q = "SELECT \
                track_7digitalid \
            FROM "\
                +song_features_table_name + " \
            WHERE \
                song_id='"+ song_id +"';"
        g_cur.execute(q)
        row = g_cur.fetchall()
        
        print row[0][0]
        
        URL = get_song_url(row[0][0])
        
        f.write(URL + "\n")

    f.close()



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
    
#    print q
#    print id_7digital

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
    
#    print q
    if song_id==[]:
        print "no song found!"
        return ""
        
    return song_id[0][0]



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
#        print "song_features:"
#        print song_features[0]
        return song_features[0]
    else:
        print "song not found"
        return None        



@db_connect
def findInSongsDB( song_ids ):
    
    #global g_conn
    #global g_cur
    #g_cur = g_conn.cursor()
    #print g_cur
    
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



@db_connect
def pickNextSongsWrapped( cur_song_id ):
    
    global p
    #global g_cur    
    
#    print p
    g_conn = psy.connect(MX_common.g_db_conn_command)
    g_cur = g_conn.cursor()
    
    cur_song_id2 = get_song_id_from_7digital( cur_song_id )
#    if (cur_song_id[0]).isdigit():
#        cur_song_id2 = get_song_id_from_7digital( cur_song_id )
#    else:
#        cur_song_id2 = cur_song_id
    
    next_song_ids2 = list()    
    for i in range(p['num_forward_song_predictions']):
        next_song_ids = pickNextSongs( g_cur, p, cur_song_id2, 1, p['conservation'] )
        next_song_ids2.append([get_7digital_id( x ) for x in next_song_ids])
        cur_song_id2 = next_song_ids2[-1][0]
#    if (cur_song_id[0]).isdigit():
#        next_song_ids2 = [get_7digital_id( x ) for x in next_song_ids]
#    else:
#        next_song_ids2 = next_song_ids


    g_conn.close()

#    print next_song_ids2
    return next_song_ids2

    
    
    
    
def printSongDescription( cur_song_f, verbose, dist=0 ):
    
    max_song_title = 2000
    max_artist_name = 2000   
    
    global p

    if cur_song_f == None:
        desc = 'No Song!!'
    else:
        if verbose==1:
            desc = "%s: Tmp=%3d Lou=% 3d Fam=%0.2f Vln=%0.2f Eng=%0.2f Dnc=%0.2f Acs=%0.2f Liv=%0.2f Spc=%0.2f Ins=%0.2f Yr=%04d   %s   %s" %\
                (cur_song_f[p['invkey']['song_id']], \
                 int(cur_song_f[p['invkey']['tempo']]), cur_song_f[p['invkey']['loudness']], cur_song_f[p['invkey']['artist_familiarity']], \
                 max(0,cur_song_f[p['invkey']['valence']]), max(0,cur_song_f[p['invkey']['energy']]), max(0,cur_song_f[p['invkey']['danceability']]), max(0,cur_song_f[p['invkey']['acousticness']]), max(0,cur_song_f[p['invkey']['liveness']]), max(0,cur_song_f[p['invkey']['speechiness']]), max(0,cur_song_f[p['invkey']['instrumentalness']]), \
                 cur_song_f[p['invkey']['year']], cur_song_f[p['invkey']['artist_name']][:min(max_artist_name,len(cur_song_f[p['invkey']['artist_name']]))], cur_song_f[p['invkey']['title']][:min(max_song_title,len(cur_song_f[p['invkey']['title']]))]) 
        else:#if verbose==0:
            desc = "%s: %s %s" %\
                (cur_song_f[p['invkey']['song_id']], \
                 cur_song_f[p['invkey']['artist_name']][:min(max_artist_name,len(cur_song_f[p['invkey']['artist_name']]))], cur_song_f[p['invkey']['title']][:min(max_song_title,len(cur_song_f[p['invkey']['title']]))]) 
            
    return desc
    
    
    
    
    

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

       
    
    #print cur_song_f[0]
    t_scale      = p['unit_vec_inv'][p['invkey_distance_features']]
    t_cur_f      = np.array([cur_song_f[0][i] for i in p['invkey_distance_features']])
   
    if conservation != None:
        t_cons_f     = np.array([conservation[key] for key in p['distance_features']])
    else:
        t_cons_f     = np.array([0.0 for key in p['distance_features']])
        
#    t_angle      = (1-t_cons_f) / np.linalg.norm(1-t_cons_f)
#    
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

    #print q
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
        #print neighbor
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
 #       sdist = calcDistanceInner(t_neighbor_f, t_next_f, t_scale, p['distance_type_jump'])


        # log neighbor's detailsfor debug purposes
        nb_disted.append((sdist[0], neighbor[0], printSongDescription( neighbor_song_f[0], 1 )))

 

    trip = list()
    for i in range(len(t_cons_f)):
        trip.append( ( p['invkey_distance_features'][i], p['distance_features'][i], t_cons_f[i], t_neighbor_f[i], t_cur_f[i] ) )
    print trip

       
        
    nb_disted = sorted(nb_disted) #key=itemgetter(0)    

   # randomly pick the next song according to probabilities which correspond to the distance between current and neighboring songs

    epsilon = 0.0001
    xk = np.arange(len(nb_disted))
    pk = (np.array([x[0] for x in nb_disted]) + epsilon) ** p['noisyness']
    pk /= sum(pk)
    print (pk[:5]), sum(pk)
    custm = stats.rv_discrete(name='custm', values=(xk, pk))   

    #print pk
 
    p['debug_neighbors'] = list()
    for i in range(len(nb_disted)):
        desc = "0 %4.4f" % pk[i]
        p['debug_neighbors'].append(desc +" "+ nb_disted[i][2])
     
   
    # randomize a few potential next songs
    ii        = list()
    ii.append(custm.rvs(size=1))
    p['debug_neighbors'][ii[-1]] = str(1) + p['debug_neighbors'][ii[-1]][1:]
    print "i0 = " + str(xk[ii[-1]]), (pk[:5]), sum(pk)
    for j in range(min(len(nb_disted),p['suggestions_num'])-1):
        # update the probability toward the choice of the next song byt remving the last chosen song
        #xk = np.concatenate((xk[:ii[-1]],xk[ii[-1]+1:]))
        #pk = np.concatenate((pk[:ii[-1]],pk[ii[-1]+1:]))
        pk[ii[-1]] = 0
        pk /= sum(pk)
        custm = stats.rv_discrete(name='custm', values=(xk, pk))   
        ii.append(custm.rvs(size=1))
        print "i"+ str(j+1) +" = " + str(xk[ii[-1]]), (pk[:5]), sum(pk)
        
        p['debug_neighbors'][ii[-1]] = str(2+j) + p['debug_neighbors'][ii[-1]][1:]


    #p['debug_neighbors'] = sorted(p['debug_neighbors'])


        
    #for i in range(len(dists)):
    #    print isorted[i], dists[isorted[i]], pk[isorted[i]]

    #print ii,  dists[ii]
   
   
    #if debug_print==2:
     #   plt.plot( range(len(pk)), sorted(pk) )
   
    next_song_ids = [ nb_disted[i][1] for i in ii]
#    print next_song_ids

    return next_song_ids
#    return suggested[0:min(len(suggested), p['max_jump_recommendations'])]



#pickNextSong( conn_db, p, z[0][0], 1, p['conservation'] )


"""
def findClosestSongByFeatures( features ):

    global p

    closest_song_id = ''
    close_song_features = None
    search_steps = 0;
    initial_search_step = p['search_song_by_features_search_step']

    conn = psy.connect(MX_common.g_db_conn_command)
    cur = conn.cursor()
    while len( close_song_features ) == 0 and search_steps < 10:
    
        
        q = "SELECT \
                *\
            FROM "\
                +MX_common.song_features_table_name+" "\
            +"WHERE "\
                +"song_id='" + "xxx" + "';"
        cur.execute(q)   
        close_song_features = cur.fetchall()
        search_steps+=1    


    conn.close()
    
    
#    if len( close_song_features ) > 0:
#        measure distances of all songs in the cube
    
    return closest_song_id    
"""
    