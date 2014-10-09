# mr_trip_speed.py

# For each rou

from mrjob.job import MRJob

tol = 0.1
def roundCoord(number,tol):
    return int(round(number/tol))
    
min_dist = 1
max_dist = 2
min_time = 60
max_time = 3600

class CountDepartures(MRJob):

    def mapper(self, _, line):
        data = line.split(',')
        rnd_lat = roundCoord(float(data[11]),tol)
        rnd_lon = roundCoord(float(data[12]),tol)
        distance = float(data[10])
        time = float(data[9])
        if time > min_time and distance > min_dist:
            yield (rnd_lat, rnd_lon), (distance/time,1)
        
    def reducer(self, key, values):
        (speed,count) = reduce(lambda x,y:(x[0]+y[0],x[1]+y[1]),values)
        yield key, speed/count

if __name__ == '__main__':
    CountDepartures.run()