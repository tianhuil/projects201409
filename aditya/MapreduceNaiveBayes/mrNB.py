from mrjob.job import MRJob

import sys

class mrNB(MRJob):

    def mapper(self, _, line):
        sentence,clas=line.split(',')
	words=sentence.split(' ')
	for word in words:
		yield ((word+'|'+clas),1)
		yield ('number of words in class '+clas,1)
	yield ('number of docs in ' +clas,1)
	yield ('total number of docs',1)
    
    def reducer(self, word, count):
	yield 	word, sum(count)
	
	
if __name__ == '__main__':
    mrNB.run()

