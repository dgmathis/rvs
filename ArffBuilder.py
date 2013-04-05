#! /usr/bin/env python

import re

class ArffBuilder:
	
	@staticmethod
	def build(arffFile, words, lines, wordCount):
		print "Generating Arff file..."
		
		words = words[0:wordCount]
		
		output = open(arffFile, 'w')
		
		# Write relation title
		output.write("@RELATION rvs\n\n")
		
		# Write attributes
		output.write("@ATTRIBUTE price REAL\n")
		
		for word in words:
			output.write("@ATTRIBUTE " + word + " { n, y }\n")
			
		output.write("@ATTRIBUTE class { Class_A, Class_B, CLASS_C, Towable, Part, Other }\n\n")
		
		# Write data
		output.write("@DATA\n")
		
		for line in lines:
			lineWords = line.split(', ')
			
			# Write price
			output.write(lineWords[2] + ',')
			
			# Write words
			for word in words:
				
				foundWord = False
				
				for w in lineWords[2:]:
					if w == word:
						foundWord = True
						break
				
				if foundWord == True:
					output.write('y,')
				else:
					output.write('n,')
			
			# Write class
			output.write(lineWords[1])
			output.write('\n')
			
		print "Finished Arff file..."
