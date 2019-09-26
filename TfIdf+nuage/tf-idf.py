#!/usr/bin/python

import sys
import os
import glob
import re 
import math
from nltk.stem.snowball import SnowballStemmer


#! Check input -------------------------------------------------------------------------------------------
if len(sys.argv) > 4 and len(sys.argv) < 2:
	sys.stderr.write("--Usage : tf-idf folderName \n--use  -t for trace \n \t\t -o for tresholded output \n")
	sys.exit(1)

if sys.argv == 3 and (sys.argv[1] != "-t" or sys.argv[1] != "-o"):
	sys.stderr.write("--Usage : tf-idf -t -o folderName \n--use  -t for trace \n \t\t -o for tresholded output \n")
	sys.exit(1)

if sys.argv == 4 and sys.argv[1] != "t" and sys.argv[2] != "-o" :
	sys.stderr.write("--Usage : tf-idf -t -o folderName \n--use  -t for trace \n \t\t -o for tresholded output \n")
	sys.exit(1)

#! end check input--------------------------------------------------------------------------------------


"""
Read fold function

Open a folder and return list of file path
"""
def readFolder(Folder):
	if(Folder[(len(Folder)-1)] != '/'):
		Folder = Folder + "/"
	Folder = Folder + "*"
	return glob.glob(Folder)


"""
Normalize function

Normalize text file

1. Read whole file
2. Remove unwanted char
3. Split on space
4. Return word list
"""
def normalize(open_file) :
	word_list = open_file
	word_list = re.sub("[()]|,|\.|\t|\n|\r","",word_list)
	word_list = word_list.split(" ")
	if(word_list[len(word_list)-1] == "" or word_list[len(word_list)-1] == " "):
		del word_list[len(word_list)-1]
	return word_list



"""
Normalize function

eturn library call list after finding them in trace

Normalize trace file

1. Read File line by line
2. Remove unwanted part
3. Split on '('
4. Return library call list
"""
def normalize_trace(open_file) :	
	word_list = []
	for line in open_file :
		call = line.split("(")
		if call[0] != "--- SIGINT ":
			word_list.append(call[0])
	if word_list[len(word_list)-1] == "+++ killed by SIGINT +++\n" or word_list[len(word_list)-1] == "+++ exited " :
		del word_list[len(word_list)-1]
	return word_list

"""
TF score function

Compute TF score

1. For each word
2. Stem the word
4. Switch TF for pourcentage of word in the file because 
   it is more significative when comparing text which size is variable
3. Return Dictionnary
"""
def buildTfDico (word_list,size) :    # build term frequency dico
	tf_dico = {}
	stemmer2 = SnowballStemmer("english", ignore_stopwords=True)
	for word in word_list :
		word = stemmer2.stem(word)
		if word in tf_dico :
			tf_dico[word] = tf_dico[word] + 1.0 
		else : 
			tf_dico[word] = 1.0
	for element in tf_dico :
		tf_dico[element] = (tf_dico[element] / size)*100
	return tf_dico

"""
Remove name function

remove unnecessary information in text
"""
def remove_name(file):
	result = ""
	for line in file:
		sentence = line.split(">")[1][1:]
		result += sentence
	return result

"""
TF for one file

1. Normalize
2. Build TF dico
"""
conversation_script = True
def getTf(File):
	opened_file = open(File,"r", encoding="utf8")
	if sys.argv[1] == "-t" or sys.argv[2] == "-t":
		word_list = normalize_trace(opened_file)
	else :
		if conversation_script:
			word_list = normalize(remove_name(opened_file))
		else:
			word_list = normalize(opened_file.read())
	#!print("---------------------" + File + "--------------------------")
	tf_dico = buildTfDico(word_list,len(word_list))
	opened_file.close()
	return tf_dico

"""
TF For all file

1. for all file, get TF dico
"""
def getTfAll(list_file): 
	list_tf = []
	for file in list_file :
		list_tf.append(getTf(file))
	return list_tf


"""
Build Set function

Build the Set of word in the corpus + COMPUTE IDF
"""
def buildLargeDico(list_cf):
	large_dico = {}
	for dico in list_cf:
		for word in dico :
			if word in large_dico :
				large_dico[word] = large_dico[word]+1
			else :
				large_dico[word] = 1
	return large_dico


"""
IDF function

Compute IDF     

	idf = log(N / N(t))

with: - N the number of documents in the corpus
	  - N(t) the number of documents in the corpus where the word t appears 

We use log here so that it allows us to remove stopwords (these words appear in every text file)
"""
def getIdf(list_tf):
	large_dico = buildLargeDico(list_tf)
	number_doc = len(list_tf)
	dico_idf = {}
	for word in large_dico:
		dico_idf[word] = math.log10(number_doc / large_dico[word])
	return dico_idf


"""
TF-IDF function

Compute TF-IDF score

	tf-idf = TF * IDF
"""
def getTfIdfScore(list_tf,dico_idf):
	score_list = list_tf
	i = 0
	for dico in list_tf:
		for word in dico:
			score_list[i][word] = dico[word] * dico_idf[word]
		i = i + 1
	return score_list

"""
Treshold function

remove word with score < 0.5

Todo: 
parametrable treshold
"""
def treshold(dico, value):
	treated = {}
	for word in dico :
		if dico[word] > value :
			treated[word] = dico[word]
	return treated


def find_best(dico):					#!search the best score for file name
	name = ""
	best = 0
	for word in dico :
		if dico[word] > best :
			best = dico[word]
			name = word
	return name

"""
Write function

write the score dico in file

Todo:
Filename is the name of the file before tf-idf + score, not of the best word
"""
def write(dico, name):
	where = os.path.abspath("output/")
	names = name.split('.')
	filee = open(where+"\\"+ name[0] + "_result" + name[1],"w", encoding="utf8")
	for word in dico :
		filee.write(str(word) + ":"+str(dico[word])+"\n")
	filee.close()
	return

"""
Output Result function

create and write all files in ouptut directory
"""
def makeText(score_list, list_file):				
	treated = {}
	i = 0
	for dico in score_list :
		treated = treshold(dico, 0.1)
		write(treated, os.path.basename(os.path.normpath(list_file[i])))
		i += 1
	return 


"""
GetBestResult function

Todo:
Sort the by score
change the function to be more modulable
"""
def threeBest(dico) :
	to_display = { 'first' : 0 ,'nameFirst': 'default' ,'second' : 0, 'nameSecond': 'default', "third" : 0, 'nameThird': 'default' }
	for word in dico :
		if dico[word] > to_display['first'] :
			to_display['third'] = to_display['second']
			to_display['nameThird'] = to_display['nameSecond']
			to_display['second'] = to_display['first']
			to_display['nameSecond'] = to_display['nameFirst']
			to_display['first'] = dico[word]
			to_display['nameFirst'] = word
		else :
			if dico[word] > to_display['second']:
					to_display['third'] = to_display['second']
					to_display['nameThird'] = to_display['nameSecond']
					to_display['second'] = dico[word]
					to_display['nameSecond'] = word
			else :
				if dico[word] > to_display['third']:
							to_display['third'] = dico[word]
							to_display['nameThird'] = word
	return to_display
		
"""
Display function

Todo:
change file name to display
"""
def affiche(score_list):
	i = 1
	for dico in score_list:
		to_display = threeBest(dico)
		print("--------file"+str(i)+"-------")
		print("| "+to_display['nameFirst']+" | "+str(to_display['first']))
		print("| "+to_display['nameSecond']+" | "+str(to_display['second']))
		print("| "+to_display['nameThird']+" | "+str(to_display['third']))
		print("----------------------------")
		i = i +1

		
"""
Main function

1. Check if tf-idf is called for text or binary analysis
2. Read Folder for file which compose the corpus
3. Build TF score for each file
4. Build IDF score for the corpus
5. Compute TF-IDF score
6. If output option is specified, output the result for each file of the corpus in the directory output
7. Print the word with best score for each file

Todo:
change manual parsing for pyparse
"""
def main() :
	#1.
	if sys.argv[1] == "-t" or sys.argv[1] == "-o" :
		if sys.argv[2] == "-o" or sys.argv[2] == "-t":
			folder = os.path.abspath(sys.argv[3])	
		else :
			folder = os.path.abspath(sys.argv[2])
	else:
		folder = os.path.abspath(sys.argv[1])
	#2.
	list_file = readFolder(folder)
	#3.
	list_tf = getTfAll(list_file)
	#4.
	dico_idf = getIdf(list_tf)
	#5.
	score_list = getTfIdfScore(list_tf,dico_idf)
	#6.
	if sys.argv[1] == "-o" or sys.argv[2] == "-o" :
		makeText(score_list, list_file)
	#7.
	if len(list_tf):
		if sys.argv[1] == "-t" or sys.argv[2] == "-t" :
			print("If you see only default score = 0 for a trace file (often happen) that mean that the trace contain no noteworthy call")
		affiche(score_list)
	#No error so return 0
	return 0

main()
	

