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
rows = np.array(df_rowcols['row'])
columns = np.array(df_rowcols['column'])

data = [1]*len(columns)
X = coo_matrix((data, (rows,columns)), shape=(75988+1,25022+1))
Y = X.dot(X.T)


#row1 = np.squeeze(np.asarray(y.getrow(1).todense()))
df_nn = pd.read_csv('knn_2013.csv', delim_whitespace=True)
def get_events(user_row):
    user_events = np.squeeze(np.asarray(X.getrow(user_row).todense()))[-3500:]
    nonzeroind = np.nonzero(user_events)[0]
    nonzeroind = np.add(nonzeroind, 25022+1-3500)
    return nonzeroind
        
sample = np.squeeze(np.asarray(df_nn.ix[0]))

def print_top_events(user_row_list):
    event_list = []
    reversed_list = user_row_list[::-1]
    for user_row in reversed_list[2:]:
        events = get_events(user_row)
        for event in events:
                event_object = df_rowcols[df_rowcols['column'] == event]['url'].drop_duplicates()
                event_object = str(event_object)[str(event_object).find('http:'):str(event_object).find('\n')]
                event_list.append(event_object)
    return event_list


event_list = print_top_events(sample)
print 'userid',
for i in range(0,100):
	mystr = 'url' + str(i)
	print mystr,
print ''
for i in range(0,len(df_nn)): #len(df_nn)):
    sample = np.squeeze(np.asarray(df_nn.ix[i]))
    event_list = print_top_events(sample)
    max_num=0
    if len(event_list) > 0:
	print str(df_rowcols[df_rowcols['row']==i]['userid'].drop_duplicates()).split()[1],
        for event in event_list:
            if max_num >= 100:
                break
            else:
                print event,
                max_num += 1
        print ''
