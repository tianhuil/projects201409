from scipy import sparse
from numpy import linalg
from numpy.random import rand
import pandas as pd
import numpy as np

df_eventurl0 = pd.read_csv('RAUseridEventurl.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl1 = pd.read_csv('RAUseridEventurl-1.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl2 = pd.read_csv('RAUseridEventurl-2.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl3 = pd.read_csv('RAUseridEventurl-3.csv', delim_whitespace=True, error_bad_lines=False)
df_eventurl0 = df_eventurl0.drop_duplicates()
df_eventurl1 = df_eventurl1.drop_duplicates()
df_eventurl2 = df_eventurl2.drop_duplicates()
df_eventurl3 = df_eventurl3.drop_duplicates()
mylist = [df_eventurl0, df_eventurl1, df_eventurl2, df_eventurl3]
df_eventurl = pd.concat(mylist).drop_duplicates()
#print df_eventurl

def get_event_num(event_url):
    try:
        pos = event_url.find('?')
    except:
        return 0
    if pos:
        return event_url[pos+1:]
    else:
        return 0
row = np.array(df_eventurl['userid'])
df_eventurl['url2'] = df_eventurl['url'].apply(get_event_num)
col = np.array(df_eventurl['url'].apply(get_event_num))
#print col.min()


#row = map(int,row)
#print row
#df_eventurl = df_eventurl[df_eventurl['userid'][0] != 'h']
#print df_eventurl['userid'].drop_duplicates().index.tolist()
df_userids = df_eventurl['userid'].drop_duplicates()

	#column = np.int(get_event_num(str(df_eventurl['url'][i])))
       #A[row,column] = 1
#       print row, column
def userid_to_row(userid):
    return np.int(df_userids[df_userids == userid].index.tolist()[0])


df_eventurl = df_eventurl[df_eventurl['url'].notnull()]
df_eventurl = df_eventurl[df_eventurl['url'] != 'e']
df_eventurl = df_eventurl[df_eventurl['userid'] != 'e']
df_eventurl['url2'] = df_eventurl['url'].apply(get_event_num)
#df_eventurl['user_row'] = df_eventurl['userid'].apply(userid_to_row)


df_useridrow = df_eventurl['userid'].drop_duplicates()
df_eventcolumn = df_eventurl['url'].drop_duplicates()
#print df_useridrow
#print df_eventcolumn
def userid_row(userid):
    return df_useridrow[df_useridrow == userid].index.tolist()[0]

#print 'hello'
print 'row column'
#for user in df_eventurl['userid'].drop_duplicates():
	#print df_useridrow[df_useridrow == user].index.tolist()[0], user

#for url in df_eventurl['url'].drop_duplicates():
#	print df_eventcolumn[df_eventcolumn == url].index.tolist()[0], url

for i in range(0, len(df_eventurl)):
	try:
		print df_useridrow[df_useridrow == df_eventurl['userid'][i]].index.tolist()[0], df_eventcolumn[df_eventcolumn == df_eventurl['url'][i]].index.tolist()[0]
	except:
		pass
