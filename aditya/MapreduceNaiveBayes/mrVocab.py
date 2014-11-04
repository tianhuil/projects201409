from mrjob.job import MRJob
import sys

class mrVocab(MRJob):

    def mapper(self, _, line):
        sentence,clas=line.split(',')
	#print sentence,clas
	words=sentence.split(' ')
	#print words
	for word in words:
		yield (word,1)
    
    def reducer(self, word, count):
	yield 	word,True
   
if __name__ == '__main__':
    mrVocab.run()

