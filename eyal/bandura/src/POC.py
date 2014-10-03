



# usual imports
import os
import sys
import time
import glob
import datetime
import sqlite3
import numpy as np # get it at: http://numpy.scipy.org/
import matplotlib as mp
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib import pylab as pl

# path to the Million Song Dataset subset (uncompressed)
# CHANGE IT TO YOUR LOCAL CONFIGURATION
msd_subset_path='/Users/eyalshiv/DI/download/data/MillionSongSubset'
msd_subset_data_path=os.path.join(msd_subset_path,'data')
msd_subset_addf_path=os.path.join(msd_subset_path,'AdditionalFiles')
assert os.path.isdir(msd_subset_path),'wrong path' # sanity check
# path to the Million Song Dataset code
# CHANGE IT TO YOUR LOCAL CONFIGURATION
msd_code_path='/Users/eyalshiv/DI/musixplore/code/MSongsDB-master'
assert os.path.isdir(msd_code_path),'wrong path' # sanity check
# we add some paths to python so we can import MSD code
# Ubuntu: you can change the environment variable PYTHONPATH
# in your .bashrc file so you do not have to type these lines
sys.path.append( os.path.join(msd_code_path,'PythonSrc') )

# imports specific to the MSD
import hdf5_getters as GETTERS

# the following function simply gives us a nice string for
# a time lag in seconds
def strtimedelta(starttime,stoptime):
    return str(datetime.timedelta(seconds=stoptime-starttime))

# we define this very useful function to iterate the files
def apply_to_all_files(basedir,func=lambda x: x,ext='.h5'):
    """
    From a base directory, go through all subdirectories,
    find all files with the given extension, apply the
    given function 'func' to all of them.
    If no 'func' is passed, we do nothing except counting.
    INPUT
       basedir  - base directory of the dataset
       func     - function to apply to all filenames
       ext      - extension, .h5 by default
    RETURN
       number of files
    """
    cnt = 0
    # iterate over all files in all subdirectories
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        # count files
        cnt += len(files)
        # apply function to all files
        for f in files :
            func(f)
            
#        if cnt > 2000:
#            break
            
    return cnt



features_tuples = {}
#artist_ids = []

# we prepare the function to get the track's features for each file
def func_to_extract_features(filename):
    """
    This function extracts all features: per-track, per-section and per-segment
    """
#    - open the song file
    h5 = GETTERS.open_h5_file_read(filename)
#    - get per-track features and put them

    artist_id = GETTERS.get_artist_id(h5)
    song_id   = GETTERS.get_song_id(h5)

    artist_familiarity          = GETTERS.get_artist_familiarity(h5)
    artist_hotttnesss           = GETTERS.get_artist_hotttnesss(h5)
    artist_latitude             = GETTERS.get_artist_latitude(h5)
    artist_longitude            = GETTERS.get_artist_longitude(h5)
    danceability                = GETTERS.get_danceability(h5)
    energy                      = GETTERS.get_energy(h5)
    loudness                    = GETTERS.get_loudness(h5)
    song_hotttnesss             = GETTERS.get_song_hotttnesss(h5)
    tempo                       = GETTERS.get_tempo(h5)
    year                        = GETTERS.get_year(h5)

#   artist_ids.add(artist_id)

#    features_tuple = (artist_id, artist_familiarity, artist_hotttnesss, artist_latitude, artist_longitude, danceability, energy, loudness, song_hotttnesss, tempo, year)
    features_tuple = (artist_id, artist_familiarity, artist_hotttnesss, loudness, song_hotttnesss, tempo, year)
 #   print features_tuple
    
    features_tuples[song_id] = features_tuple
    
#    files_per_artist[artist_id] += 1
#    - close the file
    h5.close()


feature_labels = ['artist_familiarity', 'artist_hotttnesss', 'loudness', 'song_hotttnesss', 'tempo', 'year']







# we can now easily count the number of files in the dataset
print 'number of song files:',apply_to_all_files(msd_subset_data_path)

# let's now get all artist names in a set(). One nice property:
# if we enter many times the same artist, only one will be kept.
all_artist_names = set()

# we define the function to apply to all files
def func_to_get_artist_name(filename):
    """
    This function does 3 simple things:
    - open the song file
    - get artist ID and put it
    - close the file
    """
    h5 = GETTERS.open_h5_file_read(filename)
    artist_name = GETTERS.get_artist_name(h5)
    all_artist_names.add( artist_name )
    h5.close()



    
# let's apply the previous function to all files
# we'll also measure how long it takes
if 1:
    t1 = time.time()
    apply_to_all_files(msd_subset_data_path,func=func_to_extract_features)
    t2 = time.time()
    print 'all features extracted in:',strtimedelta(t1,t2)


# extract numeric features from dictionary to a 2D array
features_2D = np.asarray(features_tuples.values())
#features_2D = np.asarray(features_2D[:,[1,2,7,8,9,10]],'float')
features_2D = np.asarray(features_2D[:,1:], 'float')

a = np.isnan(features_2D);



features_2D = features_2D[ np.logical_and( a.sum(axis=1)==0 , features_2D[:,-1]>0 ),:];
#f_max = (features_2D.max(axis=0))
#f_min = (features_2D.min(axis=0))
#features_2D = features_2D[:,f_max>f_min];

f_max = (features_2D.max(axis=0))
f_min = (features_2D.min(axis=0))

# normalize each feature to [0,1]
for i in range(features_2D.shape[1]):
    features_2D[:,i] = (features_2D[:,i]-f_min[i]) / (f_max[i]-f_min[i])


for i in range(features_2D.shape[1]):
    hist, bins = np.histogram(features_2D[:,i], bins=50)
    plt.bar((bins[:-1]+bins[1:])/2,hist, width=0.7*(bins[1]-bins[0]))
    pylab.savefig('hist'+str(i)+'.png')
    plt.show()




# calculate correlation matrix
features_corr = np.corrcoef(features_2D.T)

fig = pl.figure(1)
fig.clf()
ax = fig.add_subplot(1,1,1)
cax = ax.imshow(features_corr, interpolation='none', vmin=0.0, vmax=1.0)
fig.colorbar(cax)
pl.savefig("corr_matrix.png", bbox_inches='tight')
pl.show()





# calculate variance-covariance matrix
features_cov = np.cov(features_2D, None, 0)


# PCA etc...

eig_val_cov, eig_vec_cov = np.linalg.eig(features_cov)






# Make a list of (eigenvalue, eigenvector) tuples
eig_pairs = [(np.abs(eig_val_cov[i]), eig_vec_cov[:,i]) for i in range(len(eig_val_cov))]

# Sort the (eigenvalue, eigenvector) tuples from high to low
eig_pairs.sort()
eig_pairs.reverse()

fig = pl.figure(1)
fig.clf()
ax = fig.add_subplot(1,1,1)
cax = ax.imshow(eig_vec_cov, interpolation='none', vmin=-1.0, vmax=1.0)
fig.colorbar(cax)
pl.savefig("PCA_matrix.png", bbox_inches='tight')
pl.show()






# play a song






