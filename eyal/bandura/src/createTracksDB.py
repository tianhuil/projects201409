"""

"""

import os
import sys

os.chdir('/users/eyalshiv/DI/musixplore/src')

import time
import datetime

import psycopg2 as psy
import pandas as pd
import csv
import sqlite3


import requests


import MX_common

sys.path.append(MX_common.g_base_dir + '/src')
sys.path.append(MX_common.g_base_dir + '/src/MSongsDB-master/PythonSrc')


import hdf5_getters as GETTERS


g_export = 0

if __name__ == '__main__':

    dbsongfeats_file = MX_common.g_base_dir + '/data/MillionSongSubset/AdditionalFiles/subset_msd_summary_file.h5'
    dbartsims_file   = MX_common.g_base_dir + '/data/MillionSongSubset/AdditionalFiles/subset_artist_similarity.db'
    workdir          = MX_common.g_base_dir + '/data/work'

    os.chdir(workdir)

    tmp_csv_songs_file = 'df_MSD_songs.csv'
    tmp_csv_artist_id_similarities_file = 'df_MSD_artist_id_similarities.csv'


    # start time
    t1 = time.time()

# LOAD TRACKS FEATURES AND SAVE TO POSTGRESQL

    # convert h5 DB to csv table
    h5 = GETTERS.open_h5_file_read( dbsongfeats_file )

    nsongs = GETTERS.get_num_songs(h5)

    dsongs={'song_id:text': h5.root.metadata.songs.cols.song_id[0:nsongs],
            'track_id:text': h5.root.analysis.songs.cols.track_id[0:nsongs],
            'title:text': h5.root.metadata.songs.cols.title[0:nsongs],
            'track_7digitalid:text': h5.root.metadata.songs.cols.track_7digitalid[0:nsongs],
            'year:int': h5.root.musicbrainz.songs.cols.year[0:nsongs],
            
            'song_hotttnesss:real': h5.root.metadata.songs.cols.song_hotttnesss[0:nsongs],
            'duration:real': h5.root.analysis.songs.cols.duration[0:nsongs],
            'key:int': h5.root.analysis.songs.cols.key[0:nsongs],
            'key_confidence:real': h5.root.analysis.songs.cols.key_confidence[0:nsongs],
            'loudness:real': h5.root.analysis.songs.cols.loudness[0:nsongs],
            'mode:int': h5.root.analysis.songs.cols.mode[0:nsongs],
            'mode_confidence:real': h5.root.analysis.songs.cols.mode_confidence[0:nsongs],
            'tempo:real': h5.root.analysis.songs.cols.tempo[0:nsongs],
            'time_signature:int': h5.root.analysis.songs.cols.time_signature[0:nsongs],
            'time_signature_confidence:real': h5.root.analysis.songs.cols.time_signature_confidence[0:nsongs],

            'artist_id:text': h5.root.metadata.songs.cols.artist_id[0:nsongs],
            'artist_7digitalid:text': h5.root.metadata.songs.cols.artist_7digitalid[0:nsongs],
            'artist_latitude:real': h5.root.metadata.songs.cols.artist_latitude[0:nsongs],
            'artist_longitude:real': h5.root.metadata.songs.cols.artist_longitude[0:nsongs],
            'artist_location:text': h5.root.metadata.songs.cols.artist_location[0:nsongs],
            'artist_name:text': h5.root.metadata.songs.cols.artist_name[0:nsongs],
            'artist_hotttnesss:real': h5.root.metadata.songs.cols.artist_hotttnesss[0:nsongs],
            'artist_familiarity:real': h5.root.metadata.songs.cols.artist_familiarity[0:nsongs]
            };

    # creae DataFrame to export table to csv
    dfsongs = pd.DataFrame(dsongs, columns=[\
    'song_id:text', 'track_id:text', 'title:text', 'track_7digitalid:text', 'year:int', 'song_hotttnesss:real', 'duration:real', 'key:int', 'key_confidence:real', 'loudness:real', 'mode:int', 'mode_confidence:real', 'tempo:real', 'time_signature:int', 'time_signature_confidence:real',\
    'artist_id:text', 'artist_7digitalid:text', 'artist_latitude:real', 'artist_longitude:real', 'artist_location:text', 'artist_name:text', 'artist_hotttnesss:real', 'artist_familiarity:real']);

    # patch some formatting issues in external input 
    dfsongs['song_hotttnesss:real'] = dfsongs['song_hotttnesss:real'].fillna(-1);
    dfsongs['artist_latitude:real'] = dfsongs['artist_latitude:real'].fillna(0);
    dfsongs['artist_longitude:real'] = dfsongs['artist_longitude:real'].fillna(0);
    dfsongs['artist_location:text'] = dfsongs['artist_location:text'].fillna('-');
    dfsongs['artist_familiarity:real'] = dfsongs['artist_familiarity:real'].fillna(-1);

    dfsongs['artist_name:text'] = [t.replace(',',';') for t in dfsongs['artist_name:text']];
    dfsongs['artist_location:text'] = [t.replace(',',';') for t in dfsongs['artist_location:text']];
    dfsongs['title:text'] = [t.replace(',',';') for t in dfsongs['title:text']];


    # load acoustic features for each track

    v_danceability = list()
    v_energy = list()
    v_acousticness = list()
    v_speechiness      = list()   
    v_liveness = list()
    v_valence = list()
    v_instrumentalness = list()

    t3 = time.time()

    for i  in range(len(v_instrumentalness),len(dfsongs['track_id:text'])): #dfsongs['track_id:text'][0:100]:
        track_id = dfsongs['track_id:text'][i]
        url_query = 'http://developer.echonest.com/api/v4/track/profile?api_key=%206KAVUC8IMVFAEUBAV&format=json&id=' + track_id + '&bucket=audio_summary'
        jj = requests.get(url_query)
        jj_dict = jj.json()
        while jj_dict['response']['status']['code']==3:
            time.sleep(10)
            jj = requests.get(url_query)
            jj_dict = jj.json()
            
        v_danceability.append(jj_dict['response']['track']['audio_summary']['danceability'])
        v_energy.append(jj_dict['response']['track']['audio_summary']['energy'])
        v_acousticness.append(jj_dict['response']['track']['audio_summary']['acousticness'])
        v_speechiness.append(jj_dict['response']['track']['audio_summary']['speechiness'])
        v_liveness.append(jj_dict['response']['track']['audio_summary']['liveness'])
        v_valence.append(jj_dict['response']['track']['audio_summary']['valence'])
        v_instrumentalness.append(jj_dict['response']['track']['audio_summary']['instrumentalness'])

    t4 = time.time()
    stimelength = str(datetime.timedelta(seconds=t4-t3))
        
    dfsongs['danceability:real']         = pd.Series(v_danceability, index=dfsongs.index)
    dfsongs['energy:real']               = pd.Series(v_energy, index=dfsongs.index)
    dfsongs['acousticness:real']         = pd.Series(v_acousticness, index=dfsongs.index)
    dfsongs['speechiness:real']          = pd.Series(v_speechiness, index=dfsongs.index)
    dfsongs['liveness:real']             = pd.Series(v_liveness, index=dfsongs.index)
    dfsongs['valence:real']              = pd.Series(v_valence, index=dfsongs.index)
    dfsongs['instrumentalness:real']     = pd.Series(v_instrumentalness, index=dfsongs.index)
     
    dfsongs['danceability:real'] = dfsongs['danceability:real'].fillna(-1);
    dfsongs['energy:real'] = dfsongs['energy:real'].fillna(-1);
    dfsongs['acousticness:real'] = dfsongs['acousticness:real'].fillna(-1);
    dfsongs['speechiness:real'] = dfsongs['speechiness:real'].fillna(-1);
    dfsongs['liveness:real'] = dfsongs['liveness:real'].fillna(-1);
    dfsongs['valence:real'] = dfsongs['valence:real'].fillna(-1);
    dfsongs['instrumentalness:real'] = dfsongs['instrumentalness:real'].fillna(-1);
    


    # write to csv file as an intermediate
    pd.DataFrame.to_csv(dfsongs, tmp_csv_songs_file, index=False)    

    # open PostgreSQL
    conn_out = psy.connect("dbname='my_db_test' user='eyalshiv' host='localhost' password='' port=8787")
    conn_out.autocommit = True

    cur = conn_out.cursor()

            
    MX_common.importFromDbCsv(conn_out, tmp_csv_songs_file, MX_common.song_features_table_name)

    cur.execute("CREATE INDEX "\
                    +MX_common.song_features_song_id_index_name +" \
                ON "\
                    +MX_common.song_features_table_name +" \
                (song_id);")  
    cur.execute("CREATE INDEX "\
                    +MX_common.song_features_track_id_index_name +" \
                ON "\
                    +MX_common.song_features_table_name +" \
                (track_id);")  
    cur.execute("CREATE INDEX "\
                    +MX_common.song_features_7digital_id_index_name +" \
                ON "\
                    +MX_common.song_features_table_name +" \
                (track_7digitalid);")  


# LOAD ARTIST SIMILARITIES AND SAVE TO POSTGRESQL

    # connect to the SQLite database
    conn = sqlite3.connect(dbartsims_file)

    # from that connection, get a cursor to do queries
    # NOTE: we could query directly from the connection object
    cur = conn.cursor()

    # list all tables in that dataset
    # note that sqlite does the actual job when we call fetchall() or fetchone()
    q = """SELECT   name \
            FROM    sqlite_master \
            WHERE   type='table' \
            ORDER   BY name"""
    res = cur.execute(q)
    print "* tables contained in that SQLite file/database (there should be 3):"
    print res.fetchall()

    # list all indices
    q = """SELECT    name \
            FROM     sqlite_master \
            WHERE    type='index' \
            ORDER BY name"""
    res = cur.execute(q)
    print '* indices in the database to make reads faster:'
    print res.fetchall()

    # list all artist ID
    q = """SELECT   artist_id \
            FROM    artists"""
    res = cur.execute(q)
    print "* number of artist Echo Nest ID in 'artists' table:"
    print len(res.fetchall())


    conn_artfam = sqlite3.connect('../artist_similarity.db')

    cur = conn_artfam.cursor();

    q = """SELECT   * \
            FROM    similarity"""
    cur.execute(q)
    similarities = cur.fetchall();
    

    with open(tmp_csv_artist_id_similarities_file, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(['targeto:text', 'similaro:text'])
        writer.writerows(similarities)


    MX_common.importFromDbCsv(conn_out, tmp_csv_artist_id_similarities_file, MX_common.artist_id_similarities_table_name)
    
    cur.execute("CREATE INDEX "\
                    +MX_common.artist_id_similarities_targeto_index_name +" \
                ON "\
                    +MX_common.artist_id_similarities_table_name +" \
                (targeto);")  
    cur.execute("CREATE INDEX "\
                    +MX_common.artist_id_similarities_similaro_index_name +" \
                ON "\
                    +MX_common.artist_id_similarities_table_name +" \
                (similaro);")  
    
    
    conn_artfam.close()
    conn.close()
    conn_out.close()
    