# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 16:43:16 2014

@author: eyalshiv
"""
import os
import sys
sys.path.append('~/DI/musixplore/code/MSongsDB-master/PythonSrc')

os.chdir('./MSongsDB-master/PythonSrc')
import hdf5_getters as hdf5

#%%

h5 = hdf5.open_h5_file_read('/Users/eyalshiv/DI/download/data/MillionSongSubset/data/A/H/H/TRAHHPE128F934AC3B.h5')
duration = hdf5.get_duration(h5)
h5.close()


print duration



#%%