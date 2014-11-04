#Read the output from mrjob and write to a dictionary that stores all the counts you did

f=open('out.txt')
Count={}
for line in f.readlines():
	wordcat,number=line[:-1].split('\t')
	wordcat=wordcat[1:-1]
	try:	
		word,cat=wordcat.split('|')
		Count[(word,cat)]=float(number)
	except ValueError: Count[wordcat]=float(number)
f.close()


#for item in  Count.items():
#	print item

#Don't know how to get vocab

f=open('Vocab.txt')
Vocab={}
for line in f.readlines():
	word,value=line[:-1].split('\t')
	Vocab[word]=True
#print Vocab


#ML estimates 
def prob_xgiveny(word,clas):
	#print 'Prob('+x+'|'+y+')'
	try: count_wordclas=float(Count[(word,clas)])
	except KeyError: count_wordclas=0 
	return (count_wordclas+1.0)/(float(Count['number of words in class '+ clas])+len(Vocab))

#print prob_xgiveny('Chinese','c')

#Finds prior prob estimate for each class
def prob_clas(clas):
  	return Count['number of docs in '+clas]/Count['total number of docs']

#print prob_clas('c')

#Finds posterior probablities given a bag of words
def prob_clasgivensent(clas,lis_of_words):
	ans=prob_clas(clas)
	for word in lis_of_words:
		ans*=prob_xgiveny(word,clas)
	return ans

#classifies a sentence by finding the most likely class given the sentence
def classify(sentence):
	lis_of_words=sentence.split(' ')
	#print map(lambda clas:prob_clasgivensent(clas,lis_of_words),['c','j'])
	return sentence,max( ['POSITIVE','NEGATIVE'], key=lambda clas:prob_clasgivensent(clas,lis_of_words))

print classify('good')
print classify('bad')

print classify('awful')
print classify('terrible')

print classify('terrific')
print classify('feel good')

print classify('awesome')
print classify('cool')

print classify('I hate this movie')
print classify('love this movie')
