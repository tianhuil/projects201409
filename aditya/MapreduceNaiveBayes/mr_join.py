from mrjob.job import MRJob



class MRsalesbycountry(MRJob):

    def mapper1(self, _, line):
        lis=line.split(',')
	
	if lis[0]=='users':
		print (lis[1], {'country':lis[3]})
		yield (lis[1], {'country':lis[3]})

	if lis[0]=='sales':
		yield (lis[3], {'amount':float(lis[4])})


    def reducer1(self, user, info):
	country,amount='',0
	for inf in info:
		if 'country' in inf:
			country=inf['country']
		if 'amount' in inf:
			amount+=inf['amount']
	print country,amount
	yield (None,(country,amount))

    def mapper2(self, _, country_amount_pairs):
        yield country_amount_pairs[0],country_amount_pairs[1]

    def reducer2(self, country, amounts ):
        yield country, sum(amounts)
  
    def steps(self):
        return [
            self.mr(mapper=self.mapper1, reducer=self.reducer1),self.mr(mapper=self.mapper2, reducer=self.reducer2)]


if __name__ == '__main__':
    MRsalesbycountry.run()

