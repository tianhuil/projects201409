# mr_num_arrivals.py

# map reduce program using mrjob that goes through a file of taxi records and returns
# the number of taxis arriving at given lat/long coordinates rounded to the
# specified tolerance.

from mrjob.job import MRJob

tol = 0.1
def roundCoord(number,tol):
    return int(round(number/tol))

class CountArrivals(MRJob):

    def mapper(self, _, line):
        data = line.split(',')
        rnd_lat = roundCoord(float(data[13]),tol)
        rnd_lon = roundCoord(float(data[14]),tol)
        yield (rnd_lat, rnd_lon), 1
        
    def reducer(self, key, values):
        yield key, sum(values)

if __name__ == '__main__':
    CountDepartures.run()