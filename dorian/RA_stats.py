from scipy import sparse
from numpy import linalg
from numpy.random import rand
import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np

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
bad_index1 = df_eventurl['userid'].str.contains("h")
df_eventurl = df_eventurl[bad_index1 == False]
df_eventurl = df_eventurl[df_eventurl['url'].str.contains("http") == True]

# Will return the number of events user attended based on 2013 predictions
df_2014_pred = pd.read_csv('RA_nearest_events_2013_test.csv', delim_whitespace=True, error_bad_lines=False)
df_2014= df_eventurl.ix[350000:]
from random import randrange
import random

def predicted_from_2013(userid, urls):
	df_user = df_2014[df_2014['userid'] == str(userid)]
	count = 0 
        for url in urls:
	    	df_user_attended = df_user[df_user['url'] == str(url)]
            	if len(df_user_attended) > 0:
                	count += 1
        return count, len(df_user)



scores = []
score1 = 0.0
mycount = 0
people = 0
def prediction_accuracy():
	mycount=0
	for i in range(0, len(df_2014)):
    		urls = []
		try:
			userid = df_2014_pred.ix[i]['userid']
			urls.append(df_2014_pred.ix[i]['url1'])
			urls.append(df_2014_pred.ix[i]['url2'])
			urls.append(df_2014_pred.ix[i]['url3'])
			urls.append(df_2014_pred.ix[i]['url4'])
			urls.append(df_2014_pred.ix[i]['url5'])
    			urls.append(df_2014_pred.ix[i]['url6'])
    			urls.append(df_2014_pred.ix[i]['url7'])
    			urls.append(df_2014_pred.ix[i]['url8'])
			urls.append(df_2014_pred.ix[i]['url9'])
			urls.append(df_2014_pred.ix[i]['url10'])
			df_user_2014 = df_2014[df_2014['userid'] == str(userid)]
	   		num_urls = 0
			for url in urls:
				if len(str(url)) > 10: # ensure its a valid URL
					num_urls += 1
			if len(df_user_2014['url']) > 3:
	        		result = predicted_from_2013(userid, urls)
				#if int(result[0]) > 0:
				#	mycount += 1
				#print np.float(mycount)/(i+1)
				scores.append(np.float(result[0])/num_urls)#
				print sum(scores)/len(scores)
		except:
			print 'error'
#prediction_accuracy()
#exit()
print 'NOW RANDOM'
#print sum(scores)/len(scores)
scores2 = []
df_2014 = df_2014.reset_index()
df_2014_urls = df_2014.drop_duplicates()
for j in range(0,len(df_2014)):
    try:
    	userid = df_2014_pred.ix[j]['userid']
    	urls = []
    	for j in range(0,5):
     		urls.append(df_2014_urls.ix[random.randint(0,len(df_2014_urls))]['url'])
	df_user_2014 = df_2014[df_2014['userid'] == str(userid)]
    	if len(df_user_2014['url']) > 3:
        	result = predicted_from_2013(userid, urls)
        	scores2.append(np.float(result[0])/10.0)
		print sum(scores2)/len(scores2)
    except:
	pass

