import pandas as pd
import urllib2
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
import re
import numpy as np

#df_urls = pd.read_csv('RAURLS2', header=None, lineterminator=',')

def add_prices(price_str):
    price_str = re.sub("[\\\][x|a|c]",'',price_str) 
    price_str = re.sub("a",'', price_str)
    if price_str is None:
        return None
    if price_str.find('+') != -1:
	if price_str.isdigit() == True:
        	return np.float(price_str.split('+')[0]) + np.float(price_str.split('+')[1])
    	else:
		return 0
    else:
	if price_str.isdigit() == True:
        	return np.float(price_str)
	else:
		return 0

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
    url = re.sub(' ', '', sample_data[sample_data.find('http://www.residentadvisor.net/event.aspx?'):])
    return price, lineup, promoters, venue, url
#read_event_data()


#print id_index
user_id_list = []
def get_user_ids():
	id_index = [m.start() for m in re.finditer("Id", sample_data)]
	user_ids = []
	for i in id_index:
    		user_ids.append(re.sub("[^\\d]",'',sample_data[i+3:i+15]))
	#print user_ids
	return user_ids

file = open('RAScraperDumpSept22Part2_1')
lines = file.readlines()
#print 'userid cost dj1 dj2 dj3 promoter1 promoter2 promoter3 venue url'
def give_date(datestring):
	day = re.sub('\"','',datestring[datestring.find('dy=')+3:])
	month = datestring[datestring.find('mn=')+3:datestring.find('&amp;yr')]
	year = datestring[datestring.find('yr=')+3:datestring.find('&amp;dy')]
	return day,month, year
for line in lines:
	data = []
	sample_data = line
	start = sample_data.find('ai=8')
	end = sample_data.find('dy=')
	date = sample_data[start:end+5]
	start_url = sample_data.find('http://www.residentadvisor.net')
	url = re.sub(" ", "", sample_data[start_url:])
	url = re.sub("\n", "", url)
#	print date, url
	print give_date(date)[0] + '/' + give_date(date)[1] + '/' + give_date(date)[2] + '/', url
