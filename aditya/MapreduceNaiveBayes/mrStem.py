from mrjob.job import MRJob

import sys
import nltk

#This is a stemmer from nltk
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

class mrStem(MRJob):

    def mapper(self, _, line):
        sentence,clas=line.split(',')
	#Stems words of a sentence and puts them back together
        yield  (" ".join(map(lemmatizer.lemmatize, sentence.split(" ")))+','+clas,1)
  
    def reducer(self, stemmed_sent, count):
	yield 	(stemmed_sent,None)
		
   
if __name__ == '__main__':
    mrStem.run()

