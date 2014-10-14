"""
# -*- coding: utf-8 -*-
Created on Thu Sep 18 00:44:51 2014

@author: eyalshiv
"""

import numpy as np
import psycopg2 as psy
import collections

from functools import wraps


g_base_dir          = "/home/vagrant/projects201409/eyal/bandura/"
g_db_conn_command   = "dbname='my_db_test' port=5432"
#g_base_dir          = '/Users/eyalshiv/DI/musixplore'
#g_db_conn_command   = "dbname='my_db_test' user='eyalshiv' host='localhost' password='' port=8787"


# DB internal globals

artists_table_name                         = 'artists'
artist_id_similarities_table_name          = 'artist_id_similarities'
artist_similarities_table_name             = 'artist_similarities'
song_features_table_name                   = 'song_features'
song_features_filtered_table_name          = 'song_features_filtered'
 
artist_id_similarities_targeto_index_name  = 'artist_id_similarities_targeto_index'
artist_id_similarities_similaro_index_name = 'artist_id_similarities_similaro_index'
 
song_features_song_id_index_name           = 'song_features_song_id_index_name'
song_features_track_id_index_name          = 'song_features_track_id_index_name'
song_features_7digital_id_index_name       = 'song_features_7digital_id_index_name'
song_features_filtered_song_id_index_name  = 'song_features_filtered_song_id_index_name'
  
MXG_table_name                             = 'mxg_graph2'

g_conn = None
g_cur = None

# algorithm globals
p = dict()

p['relevant_metadata'] = ['song_id','artist_id','artist_7digitalid','track_7digitalid','title','artist_name']
p['relevant_features'] = ['loudness','tempo','mode','mode_confidence','key','key_confidence','song_hotttnesss','artist_hotttnesss','artist_familiarity','year', 'danceability', 'energy', 'valence', 'speechiness', 'instrumentalness', 'liveness', 'acousticness']
#p['relevant_features'] = ['loudness','tempo','time_signature','time_signature_confidence','mode','mode_confidence','key','key_confidence','song_hotttnesss','artist_hotttnesss','artist_familiarity','artist_longitude','artist_latitude','year', 'danceability', 'energy', 'valence', 'speechiness', 'instrumentalness', 'liveness', 'acousticness']
p['relevant_features_all'] = p['relevant_metadata'] + p['relevant_features']
p['mandatory_features'] = list(set(p['relevant_features_all']).difference(set(['artist_longitude','artist_latitude'])))

p['interpolate_song_hotttnesss_from_artist'] = True


# 7digital globals

p['consumer_key'] = '7drussrakh7t'
p['consumer_secret'] = 'fr4sykcr47ryd8te'





def db_connect(f):

    @wraps(f)
    def wrapped(*args, **kwargs):
        global g_conn        
        global g_cur        
        
        g_conn = psy.connect( g_db_conn_command )
    
        r = f(*args, **kwargs)
        g_conn.close()        
        
        return r

    return wrapped



@db_connect
def init_globals_static():

    global p
    
    g_conn = psy.connect( g_db_conn_command )
    g_cur = g_conn.cursor()


    # internal variable inits

    q = "SELECT \
            * \
            FROM \
            song_features\
            LIMIT \
            1"
    g_cur.execute(q)
    

    p['colnames'] = [desc[0] for desc in g_cur.description]

    print p['colnames']

    # PATCH - in the future add NA values to csv header
    p['colNAvals2'] = dict()
    p['colNAvals2']['acousticness']         = -1
    p['colNAvals2']['artist_7digitalid']    = ''
    p['colNAvals2']['artist_familiarity']   = -1
    p['colNAvals2']['artist_hotttnesss']    = -1
    p['colNAvals2']['artist_id']            = ''
    p['colNAvals2']['artist_latitude']      = -1
    p['colNAvals2']['artist_location']      = ''
    p['colNAvals2']['artist_longitude']     = -1
    p['colNAvals2']['artist_name']          = ''
    p['colNAvals2']['danceability']         = -1
    p['colNAvals2']['duration']             = 0
    p['colNAvals2']['energy']               = -1
    p['colNAvals2']['instrumentalness']     = -1
    p['colNAvals2']['key']                  = -1
    p['colNAvals2']['key_confidence']       = 0
    p['colNAvals2']['liveness']             = -1
    p['colNAvals2']['loudness']             = 0
    p['colNAvals2']['mode']                 = -1
    p['colNAvals2']['mode_confidence']      = 0
    p['colNAvals2']['song_hotttnesss']      = -1
    p['colNAvals2']['song_id']              = ''
    p['colNAvals2']['speechiness']          = -1
    p['colNAvals2']['tempo']                = 0
    p['colNAvals2']['time_signature']       = -1
    p['colNAvals2']['time_signature_confidence'] = 0
    p['colNAvals2']['title']                = ''
    p['colNAvals2']['track_7digitalid']     = 0
    p['colNAvals2']['track_id']             = ''
    p['colNAvals2']['valence']              = -1
    p['colNAvals2']['year']                 = 0

    p['colHistBinSize2'] = dict()
    p['colHistBinSize2']['acousticness']         = .01
    p['colHistBinSize2']['artist_familiarity']   = .01
    p['colHistBinSize2']['artist_hotttnesss']    = .01
    p['colHistBinSize2']['artist_latitude']      = 1
    p['colHistBinSize2']['artist_longitude']     = 1
    p['colHistBinSize2']['danceability']         = .01
    p['colHistBinSize2']['duration']             = 10
    p['colHistBinSize2']['energy']               = .01
    p['colHistBinSize2']['instrumentalness']     = .01
    p['colHistBinSize2']['key']                  = -1
    p['colHistBinSize2']['key_confidence']       = .01
    p['colHistBinSize2']['liveness']             = .01
    p['colHistBinSize2']['loudness']             = .01
    p['colHistBinSize2']['mode']                 = -1
    p['colHistBinSize2']['mode_confidence']      = .01
    p['colHistBinSize2']['song_hotttnesss']      = .01
    p['colHistBinSize2']['speechiness']          = .01
    p['colHistBinSize2']['tempo']                = 10
    p['colHistBinSize2']['time_signature']       = 1
    p['colHistBinSize2']['time_signature_confidence'] = .01
    p['colHistBinSize2']['valence']              = .01
    p['colHistBinSize2']['year']                 = 1

    p['invkey'] = dict()
    for i in range(len(p['colnames'])):
        p['invkey'][p['colnames'][i]] = i


    p['distance_features'] = ['tempo','song_hotttnesss','artist_familiarity','year', 'danceability', 'energy', 'valence', 'speechiness', 'instrumentalness', 'liveness', 'acousticness']
    p['invkey_distance_features'] = [p['invkey'][key] for key in p['distance_features']]


    # parameter inits

    p['maximal_overall_distance'] = 10000000000000 #0.01
    p['neighborhood_types'] = ['topo', 'features']    #['topo']    
    p['max_MXG_neighbors'] = dict()
    p['max_MXG_neighbors']['topo']   = 100
    p['max_MXG_neighbors']['features'] = 100
    p['max_feature_neighborhood_size'] = 10    
    p['distance_type_construct']    = 'minimum'
    p['distance_type_jump']         = 'L2'
    p['construct_neighborhood_metric_diameter'] = 0.00001

    g_conn.close()

    return p



@db_connect
def calcSongFeaturesStatistics( song_features_table_name, colHistBinSize, colNAvals ):
    
    global p    
    
    g_conn = psy.connect( g_db_conn_command )
    g_cur = g_conn.cursor()

    stats = dict()
    for key in p['relevant_features']: #table.keys():
        if colNAvals!=None:
            NAval = colNAvals[key]
        else:
            NAval = ''

        # fetch whole column for the current feature
        q = "SELECT "\
                +key+ " \
            FROM "\
                +song_features_table_name+";"

        g_cur.execute(q);
        columno = g_cur.fetchall()  

        print np.shape(columno), columno[0]
        
        # calculate feature stats
        stats[key] = calcColumnHistogramTBL(np.asarray([x[0] for x in columno]), colHistBinSize[key], NAval)
    
    g_conn.close()

    return stats


def calcColumnHistogramTBL(column, binsize=-1, NAval=None, verbose=0):
    
    if verbose == 1:    
        print "AA " + str(np.shape(column))
        print column[0:3]
        print binsize
        print NAval
    
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
  

# the unit vector is used to scale the different features to the same relative range
def initUnitVec( song_features_table_name ):
    
    global p
        
    SFstats = calcSongFeaturesStatistics( song_features_table_name, p['colHistBinSize2'], p['colNAvals2'] )
    
    #   build basic unit vector which normalizes all features to the same standard deviations (the means (=offsets) are meaningless)
    p['unit_vec']     = -1*np.ones(np.shape(p['colnames'])) 
    p['unit_vec_inv'] = -1*np.ones(np.shape(p['colnames'])) 
    
    for i in range(len(p['colnames'])): #p['relevant_features']:  
        if p['colnames'][i] in SFstats.keys():
            p['unit_vec'][i] = 1/SFstats[p['colnames'][i]]['std']
        else:
            p['unit_vec'][i] = -1
            
        p['unit_vec_inv'][i] = 1 / p['unit_vec'][i]
 
        print "unit vector field: " + p['colnames'][i] + " " + str(p['unit_vec_inv'][i]) + " " + str(p['unit_vec'][i])
    
    return SFstats
    
    

def init_globals_run(  ):

    global p
        
    initUnitVec( song_features_table_name )

    # internal params inits

    p['conservation'] = dict()
    for key in p['colnames']:
        p['conservation'][key] = 0
    p['conservation']['valence'] = 0.8
    
    p['currently_playing']     = ('', '')

    p['suggestions']         = collections.deque([])
    p['suggestions'].append( ('YY', 'YY') )
    p['recently_played']     = collections.deque([])

    p['avoid_recent']     = collections.deque([])
    p['debug_neighbors'] = []

    # parameter inits    

    p['recently_played_num'] = 300
    p['recent_to_avoid_num'] = 10
    p['suggestions_num']     = 4     
    
    p['noisyness'] = -3
    p['max_jump_recommendations'] = 4

    p['num_forward_song_predictions'] = 1

    
    print "MX_traverse ready to go!"

    return p
    









# general-purpose functions

def doesTableExist( cur, table_name ):
    
    cur.execute("SELECT relname FROM pg_class WHERE relname = '"+ table_name +"';")
    z = cur.fetchall()
    
    return len(z) > 0


def listTablesInDB(cur):

    cur.execute("""SELECT table_name FROM information_schema.tables 
       WHERE table_schema = 'public'""")    
        
    rows = cur.fetchall()
 
    for row in rows:
        print row[0]


def resetTable( cur, table_name, columns_list ):
    
    if doesTableExist( cur, table_name ):
        cur.execute("DROP TABLE "+ table_name +";")
    
    q = "CREATE TABLE \
            " + table_name + " (" + ",".join(columns_list) + ");"
    cur.execute(q)


# import from csv file into PostgreSQL db
# 1. funtion that reads headers, builds a corresponding table and loads csv into it
# NOTE! I assume a special format for column headers: [field-Name]:[field_type] 
def importFromDbCsv(cur, csv_name, table_name):        
    f = open(csv_name, 'r');
    print csv_name
    header_line = f.readline();
    print header_line
    f.readline()
    columns_line = header_line.replace(':',' ');
    token_pairs = [t.split(':') for t in header_line.split(",")]
    fields = [t[0] for t in token_pairs];
    
    if doesTableExist( cur, table_name ):
        print "dropping table"
        cur.execute("DROP TABLE "+ table_name +";")
    
    print columns_line
    q = """CREATE TABLE \
            """ + table_name + " ("+columns_line+");"
    print q            
    cur.execute(q);
    cur.copy_from(f, table_name, columns=fields, sep=',')



def getTableHeaderLine():
    return 'song_id:text,	title:text,	track_7digitalid:text,	year:int,	song_hotttnesss:real,	danceability:real,	duration:real,	energy:real,	key:int,	key_confidence:real,	loudness:real,	mode:int,	mode_confidence:real,	tempo:real,	time_signature:int,	time_signature_confidence:real,	artist_id:text,	artist_7digitalid:text,	artist_latitude:real,	artist_longitude:real,	artist_location:text,	artist_name:text,	artist_hotttnesss:real,	artist_familiarity:real'



def calcDistanceInner(t_1_f, t_2_f, t_scale, t_weights, distance_type):
    
    t_vdist = np.abs( t_weights * t_scale * (t_1_f - t_2_f) )
    
    if  distance_type == 'minimum':
        dist = np.min( t_vdist )
    if  distance_type == 'maximum':
        dist = np.max( t_vdist )
    elif distance_type == 'L2':
        dist = np.sqrt(np.mean( t_vdist**2 ))
    
    return dist, t_vdist



def calcDistance(song1_f, song2_f, distance_type):
    
    vdist = np.zeros(np.shape(song1_f))
    dist  = 0
    
    
    t_scale = p['unit_vec'][p['invkey_distance_features']]
    t_1_f   = np.array([song1_f[i] for i in p['invkey_distance_features']])
    t_2_f   = np.array([song2_f[i] for i in p['invkey_distance_features']])

    
    st_dist = calcDistanceInner(t_1_f, t_2_f, t_scale, np.ones(np.shape(t_scale)), distance_type)

    dist = st_dist[0]    
        
    vdist[p['invkey_distance_features']] = st_dist[1]
    
    return dist, vdist




# Run init functions!
init_globals_static()
init_globals_run()

