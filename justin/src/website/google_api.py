# google_api.py

# Code for interfacing with Google APIs for geocoding, trip distance, and static
# map representations

import simplejson as json
import urllib as url

class NoPlaceError(Exception):
    def __init__(self):
        pass
        
# Take in a string description of a location, along with some optional geographic arguments
# and an API key, and returns the lat/lon coordinates of the first result from google 
# matching that location

def get_lat_lon_coords(location, key='AIzaSyDg3Rx-2nU5CtR3DnhUUwAcmgrN6ITUopg', **geo_args):
    url_prefix = 'https://maps.googleapis.com/maps/api/geocode/json'
    
    geo_args.update({'address': location})
    geo_args.update({'key': key})
    
    url_query = url_prefix + '?' + url.urlencode(geo_args)
    print url_query
    
    result = json.load(url.urlopen(url_query))
    
    if result['status'] == 'OK':
        most_likely_place = result['results'][0]
        most_likely_lat = most_likely_place['geometry']['location']['lat']
        most_likely_lon = most_likely_place['geometry']['location']['lng']
        return [most_likely_lat, most_likely_lon]
    else:
        raise NoPlaceError
        
# Take in an origin and destination (as either a string, or lat/lon coordinates), along
# with an API key, and return the driving distance in miles between the two points

# Note: based on testing it's probably wise to submit coordinates instead of a string for
# the origin and destination. The request for a trip from San Francisco to Penn Station
# chooses the "wrong" Penn Station for a New Yorker, with no alternative.        
    
def get_trip_distance(origin, destination, key='AIzaSyDg3Rx-2nU5CtR3DnhUUwAcmgrN6ITUopg'):
    url_prefix = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    
    dict = {'origins': origin, 'destinations': destination, 'key': key}
    url_query = url_prefix + '?' + url.urlencode(dict)
        
    result = json.load(url.urlopen(url_query))
    
    if result['status'] == 'OK':
        dist_in_meters = result['rows'][0]['elements'][0]['distance']['value']
    else:
        raise exception_to_be_defined
    
    return float(dist_in_meters)/1609.34   # convert meters to miles

# Make a url for accessing a static google map centered so that both origin and destination
# are visible. Maybe a little pointless.

def make_static_map_url(origin, destination,
                    key='AIzaSyDg3Rx-2nU5CtR3DnhUUwAcmgrN6ITUopg', **map_args):
                    
    url_prefix = 'http://maps.googleapis.com/maps/api/staticmap'
    
    map_args.update({'visible': origin + '|' + destination, 'key': key})
    
    return url_prefix + '?' + url.urlencode(map_args)
    
    