import nb

def rev2rating():
	sentence=raw_input('Type in a review')
	sentence=sentence.lower()
	print nb.classify(sentence)

rev2rating()

