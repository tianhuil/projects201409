from scipy import sparse
from numpy import linalg
from numpy.random import rand
import pandas as pd
from scipy.sparse import coo_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import KNeighborsClassifier
from scipy.sparse.linalg import eigs
import numpy as np
from scipy import linalg

df_eventurl0 = pd.read_csv('RAUseridEventurl.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl1 = pd.read_csv('RAUseridEventurl-1.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl2 = pd.read_csv('RAUseridEventurl-2.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl3 = pd.read_csv('RAUseridEventurl-3.csv', delim_whitespace=True, error_bad_lines=False)
df_uidevent = pd.read_csv('RA_row_cols_indexreset2.csv', delim_whitespace=True)
df_rowcols1 = pd.read_csv('RA_row_col_id_urlSept25_2.csv', delim_whitespace=True)
df_rowcols2 = pd.read_csv('RA_row_col_id_urlSept25_2Part2.csv', delim_whitespace=True)
rowcols = [df_rowcols1,df_rowcols2]
df_rowcols = pd.concat(rowcols, ignore_index=True).drop_duplicates()
df_eventurl0 = df_eventurl0.drop_duplicates()
df_eventurl1 = df_eventurl1.drop_duplicates()
df_eventurl2 = df_eventurl2.drop_duplicates()
df_eventurl3 = df_eventurl3.drop_duplicates()
mylist = [df_eventurl0, df_eventurl1, df_eventurl2, df_eventurl3]
df_eventurl = pd.concat(mylist, ignore_index=True).drop_duplicates()
rows = df_uidevent['row']


bad_index1 = df_eventurl['userid'].str.contains("h")

df_eventurl = df_eventurl[bad_index1 == False]
df_eventurl = df_eventurl[df_eventurl['url'].str.contains("http") == True]
df_rowcols = df_rowcols[:-85000]
rows = np.array(df_rowcols['row'])
columns = np.array(df_rowcols['column'])

data = [1.0]*len(columns)
X = coo_matrix((data, (rows,columns)), shape=(75988+1,25022+1))
from sklearn.preprocessing import normalize
X_n = normalize(X, norm='l2', axis=1)
Y = X_n.dot(X_n.T)

print 'n1 n2 n3 n4 n5 row'
for i in range(0, 75988+1):
	row_nn = np.squeeze(np.asarray(Y.getrow(i).todense()))
	nnarr = np.argsort(row_nn)[-5:]
	print nnarr[0], nnarr[1], nnarr[2], nnarr[3], nnarr[4], i
