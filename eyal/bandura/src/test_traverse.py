# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 15:45:49 2014

@author: eyalshiv
"""




import MX_traverse








conservation = p['conservation'].copy()

for key in conservation.keys():
    conservation[key] = 1

conservation['jump_randomness'] = 10000

v = range(np.shape(w)[0])
random.shuffle(v)
playlist0 = [w[i][0] for i in v[0:200]]
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist0, 'test_random.csv' )



playlist1 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist1, 'test_nodirection.csv' )

for key in conservation.keys():
    conservation[key] = 0

conservation['year'] = 1

conservation['jump_randomness'] = 10

playlist3 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist3, 'test_year_loose.csv' )

conservation['jump_randomness'] = 0.1

playlist2 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist2, 'test_year_tight.csv' )



for key in conservation.keys():
    conservation[key] = 0

conservation['artist_familiarity'] = 1

conservation['jump_randomness'] = 0.1

playlist5 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist5, 'test_artfam_loose.csv' )

conservation['jump_randomness'] = 0.01

playlist4 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist4, 'test_artfam_tight.csv' )





for key in conservation.keys():
    conservation[key] = 0

conservation['tempo'] = 1


conservation['jump_randomness'] = 1

playlist6 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist6, 'test_tempo_loose.csv' )

conservation['jump_randomness'] = 0.1

playlist7 = createPlayList_Constant( conn_db, z[0][0], 200, conservation, p )
savePlayList( conn_db, MX_common.song_features_filtered_table_name, playlist7, 'test_tempo_tight.csv' )






#pickNextSong( conn_db, p, z[0][0], 1, p['conservation'] )
