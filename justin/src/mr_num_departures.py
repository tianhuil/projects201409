# mr_departure_data.py

# map reduce program using mrjob that goes through a file of taxi records and returns
# information about the departures leaving at a particular day and hour from rounded
# lat/long coordinates. Namely, the total number of such departures, and the average speed 
# of medium length departures leaving the area in order to estimate local traffic speed.

from mrjob.job import MRJob

tol = 0.001
def roundCoord(number,tol):
    return int(round(number/tol))

class DepartureData(MRJob):

    def mapper(self, _, line): 
        min_dist = 1
        max_dist = 2
        min_time = 60
        max_time = 3600
           
        data = line.split(',')
        lat = float(data[11])
        lon = float(data[12])
        time_of_day = data[6]
        trip_time = int(data[9])
        trip_distance = float(data[10])
        day = int(data[22])
        hour = int(data[23])

        rnd_lat = roundCoord(float(data[11]),tol)
        rnd_lon = roundCoord(float(data[12]),tol)
        
        short_trip_speed = 0
        short_trip_count = 0
        
        if trip_time > min_time and trip_distance > min_dist \
            and trip_time < max_time and trip_distance < max_dist:
            
            short_trip_count = 1
            short_trip_speed = trip_distance/trip_time            
        
        yield (rnd_lat, rnd_lon, day, hour), (1, short_trip_count, short_trip_speed)
        
    def reducer(self, key, values):
        yield key, reduce(lambda x,y:(x[0]+y[0],x[1]+y[1], x[2]+y[2]),values)

if __name__ == '__main__':
    DepartureData.run()