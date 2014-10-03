import pandas as pd
df_4 = pd.read_csv('RAevent_data4.csv', delim_whitespace=True,error_bad_lines=False)
df_3 = pd.read_csv('RAevent_data3.csv', delim_whitespace=True,error_bad_lines=False)
df_2 = pd.read_csv('RAevent_data2.csv', delim_whitespace=True,error_bad_lines=False)
df_1 = pd.read_csv('RAevent_data1.csv', delim_whitespace=True,error_bad_lines=False)
mylist = [df_1, df_2, df_3, df_4]
df_f = pd.concat(mylist).drop_duplicates()

future_urls = df_4.drop_duplicates()[-2500:]
import numpy as np
import itertools
def get_djs(userid):
    df_user = df_f[df_f['userid']==userid]
    mylist = list(df_user['dj1']) + list(df_user['dj2']) + list(df_user['dj3'])
    return mylist
def get_promoters(userid):
    df_user = df_f[df_f['userid']==userid]
    mylist = list(df_user['promoter1']) + list(df_user['promoter2']) + list(df_user['promoter3'])
    return mylist

def get_venues(userid):
    df_user = df_f[df_f['userid']==userid]
    mylist = list(df_user['venue'])
    return mylist

def future_dj(userid):
    dj_list = list(get_djs(userid))
    event_list = []
    dj_favs = []
    for dj in dj_list:
        if dj != 'None':
            events_dj1 = future_urls[future_urls['dj1'] == dj]
            events_dj2 = future_urls[future_urls['dj2'] == dj]
            events_dj3 = future_urls[future_urls['dj3'] == dj]
            event_list.append(list(events_dj1['url'].drop_duplicates()))
            event_list.append(list(events_dj2['url'].drop_duplicates()))
            event_list.append(list(events_dj3['url'].drop_duplicates()))
            if len(events_dj1) > 0 or len(events_dj2) > 0 or len(events_dj3) > 0 and dj != 'None' and dj not in dj_favs:
                dj_favs.append(dj)
    return list(itertools.chain(*event_list)), dj_favs, userid

def future_promoters(userid):
    promoter_list = list(get_promoters(userid))
    event_list = []
    promoter_favs = []
    for promoter in promoter_list:
        if promoter != 'None':
            events_dj1 = future_urls[future_urls['promoter1'] == promoter]
            events_dj2 = future_urls[future_urls['promoter2'] == promoter]
            events_dj3 = future_urls[future_urls['promoter3'] == promoter]
            event_list.append(list(events_dj1['url'].drop_duplicates()))
            event_list.append(list(events_dj2['url'].drop_duplicates()))
            event_list.append(list(events_dj3['url'].drop_duplicates()))
            if len(events_dj1) > 0 or len(events_dj2) > 0 or len(events_dj3) > 0 and promoter != 'None' and promoter not in promoter_favs:
                promoter_favs.append(promoter)
    return list(itertools.chain(*event_list)), promoter_favs, userid
    
def future_venue(userid):
    venue_list = list(get_venues(userid))
    event_list = []
    venue_favs = []
    for venue in venue_list:
        if venue != 'None':
            events_dj1 = future_urls[future_urls['venue'] == venue]
            event_list.append(list(events_dj1['url'].drop_duplicates()))
            if len(events_dj1) > 0 and venue != 'None' and venue not in venue_favs:
                venue_favs.append(venue)
    return list(itertools.chain(*event_list)), venue_favs, userid

# Next need to find future events with these particular performers!

def generate_favs(userid):
    urls1, djs, uid = future_dj(userid)
    urls2, promoters, uid = future_promoters(userid)
    urls3, venues, uid = future_venue(userid)
    length1 = len(urls1)
    length2 = len(urls2)
    length3 = len(urls3)
    url_djs = []
    url_promoters = []
    url_venues = []
    for i in range(0, min(length1,5)):
        url_djs.append(urls1[i])
    for i in range(0, min(length2,5)):
        url_promoters.append(urls2[i])
    for i in range(0, min(length3,5)):
        url_venues.append(urls3[i])
      
    if length1 < 5:
        for i in range(length1, 5):
            url_djs.append('None')
    if length2 < 5:
        for i in range(length2, 5):
            url_promoters.append('None')
    if length3 < 5:
        for i in range(length3, 5):
            url_venues.append('None')
    return url_djs, url_promoters, url_venues
userid = 347080
#print userid, generate_favs(userid)
result = generate_favs(userid)
print userid,
for i in range(0,3):
    for j in range(0,5):
        print result[i][j],

for user in list(df_f['userid'].drop_duplicates()):
	result = generate_favs(user)
	print user,
	for i in range(0,3):
    		for j in range(0,5):
        		print result[i][j],
	print ''
