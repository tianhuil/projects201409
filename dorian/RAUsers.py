import pandas as pd
import urllib2
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
import re
import numpy as np
#print 'userid username'
#df_urls = pd.read_csv('RAURLS2', header=None, lineterminator=',')

def add_prices(price_str):
    if price_str is None:
        return None
    if price_str.find('+') != -1:
        return np.float(price_str.split('+')[0]) + np.float(price_str.split('+')[1])
    else:
        return np.float(price_str)


def read_event_data():
    tickets_available = re.sub("[(]",'',sample_data.split(',')[0])
    release = re.sub("[(')]", '', sample_data.split(',')[1])
    if re.sub("[ ']", '', sample_data.split(',')[1]) == 'None':
        price = 0
        istart = 3
    else:
        price = add_prices(re.sub("[u'$)( ]", '', sample_data.split(',')[2]))
        istart = 4
    split_data = sample_data.split(',')
   # print 'Release: ', release
    #print 'Tickets available: ', tickets_available
    #print 'Price: ', price
    lineup = []
    done = False
   
    #print 'Raw data: ', re.sub("[ \['\]]",'',sample_data.split(',')[istart])[0:]
    if re.sub("[ \['\]]",'',sample_data.split(',')[istart])[0:]=='':
        lineupExists=False
        #print 'No lineup!'
        istart += 1
    else:
        for i in range(istart,10):
            lineup.append(re.sub("[ \['\]]",'',sample_data.split(',')[i])[0:])
            if split_data[i][-2:] == ']]':
                done = True
                break
            else:
                pass
        istart = i+1
    #print istart, ' WHAT THE HELL'
    # NEED TO DEAL WITH NO PROMOTERS SITUATION
    promoters = []
    # istart = i+1
    
    if re.sub("[ \['\]]", '', sample_data.split(',')[istart]) == '':
            promotersExist = False
            istart += 1
    else:
            promotersExist = True
            istart -=1
# print sample_data.split(',')[istart+1]
    if promotersExist == True:        
        for j in range(istart+1,istart+5):
            promoters.append(re.sub("[ \['\]]",'',sample_data.split(',')[j])[0:])
            if split_data[j][-2:] == ']]':
                done = True
                break
            else:
                pass
        istart = j+1
#        print 'Promoters exist'
#    print 'Lineup: ', lineup
 #   print 'Promoters: ', promoters
    venue = re.sub("[' \[\]]",'',split_data[istart])
  #  print 'Venue: ', venue
    return price, lineup, promoters, venue
#read_event_data()


#print id_index
user_id_list = []
def get_user_ids():
	id_index = [m.start() for m in re.finditer("Id", sample_data)]
	username_index = [m.start() for m in re.finditer("Username", sample_data)]
	profile_index = [m.start() for m in re.finditer("Profile", sample_data)]
	user_ids = []
	usernames = []
	for i in range(0, min(len(id_index), len(username_index), len(profile_index))):
			user_ids.append(re.sub("[^\\d]",'',sample_data[id_index[i]+3:username_index[i]]))
			usernames.append(re.sub(" ", '', sample_data[username_index[i]+11:profile_index[i]-3]))
	#print user_ids
	return user_ids, usernames

file = open('RAScraperDumpSept22Part2_1')
lines = file.readlines()
#print 'userid cost dj1 dj2 dj3 promoter1 promoter2 promoter3 venue'
for line in lines:
	data = []
	sample_data = line
	user_list = get_user_ids()
	i = 0
	for i in range(0,len(user_list[0])):
		print user_list[0][i], user_list[1][i]
#	if '35983' in user_list:
#		print sample_data

	#for user_id in user_list:
	#    event_data_list = read_event_data()		
    	#    data.append(user_id)
	#    data.append(event_data_list[0])
	 #   dj_list = event_data_list[1][0:min(3,len(event_data_list[1]))]
	  #  for dj in dj_list:
	#	data.append(dj)		
	 #   for i in range(0, max(3 - len(event_data_list[1]), 0)):
	#	data.append('None')
	 #   promoter_list = event_data_list[2][0:min(3,len(event_data_list[2]))]
	  #  for promoter in promoter_list:
	#	data.append(promoter)
	 #   for i in range(0, max(3 - len(event_data_list[2]), 0)):
	#	data.append('None')
	 #   data.append(event_data_list[3])    
	  #  for item in data:
	#	print item,
	 #   print ''
	  #  data = []
