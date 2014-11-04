import urllib2
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
import pandas as pd
import numpy as np

# This is the raw list of URLS which have been generated by generate_search_urls() below. Each page
# listing contains list of events for that month/day/year in New York City.

df_urls = pd.read_csv('../RAUrlsFridaySept1920082014', header=None, lineterminator=',')


# Check to see if the addToBasket tag is available or not - determines if tickets are available.
def tickets_available(soup_obj):
	check = soup_obj.select('#addToBasket')
	if len(check) > 0:
		return True
	else:
		return False

# Extract the ticket cost from the css object.
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

# Returns the date of the event.
def event_date_city(soup_obj):
	detail_info = soup_obj.select('#detail')
	detail_info = str(detail_info)
	start_location = detail_info.find('events.aspx?')+12
	end_location = detail_info.find('dy=')+5
	return detail_info[start_location:end_location]

# Find the venue of the event from the html source.

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


# Returns the lineup of djs performing at the event.

def lineup(soup_obj):
	djs = []
	lineups = soup_obj.find_all("p", class_="lineup")
	soup2 = BeautifulSoup(str(lineups))
	for link in soup2.findAll('a'):
		djs.append(link.contents)
	return djs

# Returns the list of promoters at the event.
def promoter(soup_obj):
        links = soup_obj.findAll('a')
        promoters = []
        for link in links:
                if 'promoter' in str(link.attrs):
                        if link.contents[0] != 'RA Events':
                                promoters.append(link.contents)
                        else:
                                return promoters

# Returns the event number from the URL.
def get_event_number(event_url):
	return event_url[event_url.find('?')+1:]

# Code to make direct query to the ashx script to find list of users attending the event (found this in javacsript code).

def members_attending(event_number):	
	members_url = 'http://www.residentadvisor.net/WebServices/Rollcall.ashx?friends=false&eventId=' + str(event_number) + '&startRowNo=0&pageSize=10000'
	raw_page2 = urllib2.urlopen(members_url).read()
	soup_members = BeautifulSoup(raw_page2)
	return soup_members.prettify()


# Find the events first
urls = []
search_urls = []

# Generate the search URLS - this gives all possible page listings for New York City ai=8 represents NYC.
def generate_search_urls():
	for year in range(2008,2015):
		for month in range(1,13):
			for day in range(1,29):
				search_url = "http://www.residentadvisor.net/events.aspx?ai=8&v=day&mn=" + str(month) + "&yr=" + str(year) + "&dy=" + str(day)	
				search_urls.append(search_url)

# Given a page listing, from the generate_search_urls() function, find all event listings on the page and store them in urls.

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

# Given an event url, return all of the information about the event by calling the above functions.

def get_event_data(event_url):
	raw_page = urllib2.urlopen(event_url).read()
	soup = BeautifulSoup(raw_page)
	return soup.title, tickets_available(soup), event_cost(soup), event_date_city(soup), lineup(soup), promoter(soup), venue(soup), members_attending(get_event_number(event_url))



for i in range(0,len(df_urls)):
	ev_url = df_urls.ix[i,0][2:-1]
	eventdata = get_event_data(ev_url)

	# Format the title of the event to remove title tag.
	title_name = str(eventdata[0])[str(eventdata[0]).find('<title>')+8:]
	title_name = title_name[:title_name.find('</title>')]
	title_name = title_name[title_name.find('RA'):]
	title_name = title_name[:title_name.find('York')+4]

	# Output the event data sepearted by ':::' for later analysis.
	print title_name, ':::', eventdata[1:], ':::', ev_url, i

