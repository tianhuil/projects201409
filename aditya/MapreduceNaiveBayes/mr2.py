from mrjob.job import MRJob



class MRsalesbycountry(MRJob):

    def mapper(self, _, line):
        lis=line.split(',')
	
	if lis[0]=='users':
		print (lis[1], {'country':lis[3]})
		yield (lis[1], lis[3])

	if lis[0]=='sales':
		yield (lis[3], float(lis[4]))


    def reducer(self, user, info):
	country,amount='',0
	for inf in info:
		if type(inf)==type('c'):
			country=inf
		if type(inf)==type(0.0):
			amount+=inf
	yield (None,(country,amount))

   
if __name__ == '__main__':
    MRsalesbycountry.run()

