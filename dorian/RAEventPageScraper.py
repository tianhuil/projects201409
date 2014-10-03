import urllib2
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
import pandas as pd
import numpy as np
df_urls = pd.read_csv('RAUrlsFridaySept1920082014', header=None, lineterminator=',')

# This is our test URL
#url = "http://www.residentadvisor.net/event.aspx?600651"
#url = "http://www.residentadvisor.net/event.aspx?628196"
#url = "http://www.residentadvisor.net/event.aspx?624741"
#url = "http://www.residentadvisor.net/event.aspx?632416"
#url = "http://www.residentadvisor.net/event.aspx?616862" # City fox
#url = "http://www.residentadvisor.net/event.aspx?602534" # Blackmarket TBA
#url = "http://www.residentadvisor.net/event.aspx?617887" # Thugfucker boat party sold out
urlt = "http://www.residentadvisor.net/event.aspx?633330" # TBA Brooklyn

day = 12
year = 2012
month = 9
search_url = "http://www.residentadvisor.net/events.aspx?ai=8&v=day&mn=" + str(month) + "&yr=" + str(year) + "&dy=" + str(day)

#print df_urls
#exit()
#raw_page = urllib2.urlopen(urlt).read()
#soup = BeautifulSoup(raw_page)

def tickets_available(soup_obj):
	check = soup_obj.select('#addToBasket')
	if len(check) > 0:
		return True
	else:
		return False

def event_cost(soup_obj):
	cost_text = soup_obj.find_all("li", class_="onsale but")
	soup2 = BeautifulSoup(str(cost_text))
	p = soup2.findAll('p')
	soup3 = BeautifulSoup(str(p))
	spans = soup3.find('span')
	if tickets_available(soup_obj) == True:
		price = spans.text
		release = str(p)[4]
		return release, price
	else:
		cost_text = soup_obj.find_all("li", class_="closed")
                if cost_text:
                    soup2 = BeautifulSoup(str(cost_text))
                    p = soup2.findAll('p')
                    soup3 = BeautifulSoup(str(p))
                    spans = soup3.find('span')
                    price = spans.text
                    return 'F', price
                else:
                    return None

def event_date_city(soup_obj):
	detail_info = soup_obj.select('#detail')
	detail_info = str(detail_info)
	start_location = detail_info.find('events.aspx?')+12
	end_location = detail_info.find('dy=')+5
	return detail_info[start_location:end_location]


def venue(soup_obj):
    venue = soup_obj.find_all("li", class_="wide")
    venue_string = str(venue)
    venue_soup = BeautifulSoup(venue_string)
    strv = 'Venue /</div>'
    start_position = venue_string.find(strv) + len(strv)
    strv2 = '<br/>'
    end_position = venue_string[start_position:].find(strv2)
    
    venue_soup = BeautifulSoup(venue_string[start_position:])
    for link in venue_soup.findAll('a'):
        if len(str(link.contents)) < 100:
            return link.contents
        else:
            return venue_string[start_position:end_position+start_position]

def event_release():
	pass

def lineup(soup_obj):
	djs = []
	lineups = soup_obj.find_all("p", class_="lineup")
	soup2 = BeautifulSoup(str(lineups))
	for link in soup2.findAll('a'):
		djs.append(link.contents)
	return djs

def ticket_type():
	pass

def promoter(soup_obj):
        links = soup_obj.findAll('a')
        promoters = []
        for link in links:
                if 'promoter' in str(link.attrs):
                        if link.contents[0] != 'RA Events':
                                promoters.append(link.contents)
                        else:
                                return promoters

def get_event_number(event_url):
	return event_url[event_url.find('?')+1:]

# For each user we are going to add them into a SQL database with the above information.
def members_attending(event_number):	
	#members_url = 'http://www.residentadvisor.net/WebServices/Rollcall.ashx?friends=false&eventId=600651&startRowNo=0&pageSize=10000'
	members_url = 'http://www.residentadvisor.net/WebServices/Rollcall.ashx?friends=false&eventId=' + str(event_number) + '&startRowNo=0&pageSize=10000'
	raw_page2 = urllib2.urlopen(members_url).read()
	soup_members = BeautifulSoup(raw_page2)
	return soup_members.prettify()

#day = 12
year = 2008
month = 9

# Find the events first
urls = []
search_urls = []
# Generate the search URLS
def generate_search_urls():
	for year in range(2008,2015):
		for month in range(1,13):
			for day in range(1,29):
				search_url = "http://www.residentadvisor.net/events.aspx?ai=8&v=day&mn=" + str(month) + "&yr=" + str(year) + "&dy=" + str(day)	
				search_urls.append(search_url)
#generate_search_urls()
def get_event_urls(search_url):
	raw_page = urllib2.urlopen(search_url).read()
	soup = BeautifulSoup(raw_page)
	links = soup.findAll('a')
	for link in links:
		if '/event.aspx?' in str(link.attrs):
			if 'title' in link.attrs:
				url_str = 'http://www.residentadvisor.net' + str(link.attrs[u'href'])
				urls.append(url_str)
	return urls
#workers = Pool(30)
#urls  = workers.map(get_event_urls, search_urls)
#print urls

def get_event_data(event_url):
	raw_page = urllib2.urlopen(event_url).read()
	soup = BeautifulSoup(raw_page)
	return soup.title, tickets_available(soup), event_cost(soup), event_date_city(soup), lineup(soup), promoter(soup), venue(soup), members_attending(get_event_number(event_url))

#workers = Pool(30)
#workers.map(get_event_urls, 
#url_data= df_urls.ix[0:10,0][2:-1]
#response = workers.map(get_event_data, url_data)
#print response
#url = df_urls.ix[100000,0][2:-1]

eventdata= get_event_data(df_urls.ix[26695,0][2:-1])
title_name = str(eventdata[0])[str(eventdata[0]).find('<title>')+8:]
title_name = title_name[:title_name.find('</title>')]
title_name = title_name[title_name.find('RA'):]
title_name = title_name[:title_name.find('York')+4]

for i in range(26500,len(df_urls)):
	ev_url = df_urls.ix[i,0][2:-1]
	#response = get_event_data(ev_url)
	#date = response[3]
	#month_text = date.find('mn=')
	#month_end_text = date[month_text+3:].find('&')+month_text+3
	#year_text = date.find('yr=')
	#year_end_text = date.find('&amp;dy')
	#month = np.int(date[month_text+3:month_end_text])
	#year = np.int(date[year_text+3:year_end_text])
	eventdata = get_event_data(ev_url)
	title_name = str(eventdata[0])[str(eventdata[0]).find('<title>')+8:]
	title_name = title_name[:title_name.find('</title>')]
	title_name = title_name[title_name.find('RA'):]
	title_name = title_name[:title_name.find('York')+4]

	print title_name, ':::', eventdata[1], ':::', ev_url, i

