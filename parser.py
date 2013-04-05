#! /usr/bin/env python

import sys, getopt
import string
import re
from collections import Counter, OrderedDict
from ArffBuilder import *


# Scans through a string to find a price.  If more than
# one price is found, the highest price is returned.
#
def getPrice(line):
	prices = re.findall('\$[0-9,]+', line)
	
	maxPrice = 0;
	
	for price in prices:
		price = long(re.sub('[$,]', '', price))
		if price > maxPrice:
			maxPrice = price
			
	if maxPrice == 0:
		return '?'		
	else:
		return str(maxPrice)

# Replaces all chunks of whitespace in a string
# with single spaces
#
def cleanupWhitespace(line):
	result = re.sub('\s+', ' ', line)
	
	return result


# Removes all punctuation from a string
#
def stripPunctuation(line):
	result = re.sub('[^A-Za-z0-9\s]+', '', line)
	
	return result


# Iterates through a list of ngrams and searches for the
# ngrams in a string.  If an ngram is found in the string,
# it is stored in a list and removed from the string.
#
def handleNgrams(ngramFile, line):
	
	ngrams = list()
	
	file = open(ngramFile, 'r')
	
	for ngram in file:
		ngram = ngram.strip()

		if re.search(ngram, line) is not None:
			line = re.sub(ngram, '', line)
			ngrams.append(ngram)

	return line, ngrams


# Iterates through a list of stop words and searches for
# the stop words in a string.  If a word is found in the
# string, it is removed from the string.
#
def filterStopwords(stopFile, line):
	
	file = open(stopFile, 'r')
	
	for stopword in file:
		stopword = stopword.strip()
		
		if re.search('\s' + stopword + '\s', line) is not None:
			line = re.sub('\s' + stopword + '\s', ' ', line)
		
	return line


# Preprocess a file by identifying ngrams, removing stopwords,
# stripping punctuation, and removing unnecessary whitespace.
#
# Generates a list of lines.  A line is a comma separated string 
# that contains the following:
#
#   1.  URL (example: http://example.com)
#   2.  Classification (Class_A, Class_B, etc.)
#	3.  Price (example: 18000 - represents $18,000.00)
#   4.  ngrams (example: holiday rambler)
#   5.  words
#
# @param inFile - the name of the input file
# @param ngramFile - the name of the ngrams file
# @param stopFile - the name of the stopwords file
# @returns all words in preprocessed file and a list of lines
#
def preprocessFile(inFile, ngramFile, stopFile):
	
	print "Preprocessing " + inFile + "..."
	
	allWords = list()
	lines = list()

	input = open(inFile, 'r')
	
	# read in the input file.  For each line, handle the n-grams,
	# filter out all of the stop words, count the words, and write
	# the new line to the output file.
	for line in input:
		words= line.split()
		line = string.join(words[2:]).lower()
		
		# URL
		url = words[0]
	
		# Classification
		classification = words[1]
	
		# Price
		price = getPrice(line)
	
		# punctuation
		line = stripPunctuation(line)
	
		# ngrams
		line, ngrams = handleNgrams(ngramFile, line)
		
		# stopwords
		line = filterStopwords(stopFile, line)
	
		# whitespace
		line = cleanupWhitespace(line)
		
		allWords += line.split()
		allWords += ngrams
		
		# build word lisgs
		words = list()
		words.append(url)
		words.append(classification)
		words.append(price)
		words += ngrams
		words += line.split()
	
		lines.append(string.join(words, ', '))
	
	input.close()
	
	print "Finished preprocessing\n"
	
	return allWords, lines


# Sorts words in descending order by the number of times they
# appear in allWords
#
def sortWordsByCount(allWords):
	print "Sorting words by count..."
	
	# get the ordered list of words by their count
	wordCounts = OrderedDict(sorted(Counter(allWords).items(), key = lambda t: t[1], reverse = True))

	print "Finished sorting words\n"
	
	return wordCounts


# Generates an output file.  The output file contains the
# following:
#
#   1.  A count of the top most common words found in the file
#   2.  The top most common words found in the file.  Each word
#       is on its own line
#   3.  The preprocessed lines.  Look in the comment for the
#       function preprocessFile() for more details of what is
#       contained in a line.
#
def writeToOutput(outFile, words, lines, wordCount):

	print "Writing output to " + outFile + "..."
	
	output = open(outFile, 'w')

	# First: write the number of words
	output.write("-----\n");
	output.write("wordcount=" + str(wordCount) + "\n")
	
	# Second: write the most common words
	output.write("-----\n");
	for i in range(wordCount):
		output.write(words[i] + '\n')

	# Third: write the preprocessed lines
	output.write("-----\n");
	for line in lines:
		output.write(line + '\n')
	
	output.close()
		
	print "Finished writing to output\n"


def main(argv):

	usage = 'parser.py -i <input file> -o <output file> -a <arff file> -n <n-grams file> -s <stopwords file> -w <word count>'

	try:
		opts, args = getopt.getopt(argv, "hi:o:a:n:s:w:")
	except getopt.GetoptError:
		print usage
		sys.exit(2)
		
	inFile = ''
	outFile = 'output.txt'
	arffFile = ''
	ngramFile = ''
	stopFile = ''	
	wordCount = 300
	
	for opt, arg in opts:
		if opt == '-h':
			print usage
			sys.exit()
		elif opt == '-i':
			inFile = arg
		elif opt == '-n':
			ngramFile = arg
		elif opt == '-s':
			stopFile = arg
		elif opt == '-o':
			stopFile = arg
		elif opt == '-w':
			wordCount = int(arg)
		elif opt == '-a':
			arffFile = arg
	
	if inFile == '':
		print usage
		sys.exit(2)
	
	# Preprocess file
	allWords, lines = preprocessFile(inFile, ngramFile, stopFile)
	
	# Sort all words in descending order
	wordCounts = sortWordsByCount(allWords)
	
	# Write to output
	writeToOutput(outFile, wordCounts.keys(), lines, wordCount)
	
	# Write to arff file
	if arffFile != '':
		ArffBuilder.build(arffFile, wordCounts.keys(), lines, wordCount)


if __name__ == '__main__':
	main(sys.argv[1:])
	