import sys
import os
import glob
import re 
import math


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
Remove name function

remove unnecessary information in text
"""
def remove_name(file):
	result = ""
	for line in file:
		sentence = line.split(">")[1][1:]
		result += sentence
	return result


def buildTfDico (word_list,size) :    # build term frequency dico
	tf_dico = {}
	for word in word_list :
		if word in tf_dico :
			tf_dico[word] = tf_dico[word] + 1.0 
		else : 
			tf_dico[word] = 1.0
	return tf_dico


def getTf(File):
	opened_file = open(File,"r", encoding="utf8")
	word_list = normalize(remove_name(opened_file))
	#!print("---------------------" + File + "--------------------------")
	tf_dico = buildTfDico(word_list,len(word_list))
	opened_file.close()
	return tf_dico


def getTfAll(list_file): 
	list_tf = []
	for file in list_file :
		list_tf.append(getTf(file))
	return list_tf

"""
Read fold function

Open a folder and return list of file path
"""
def readFolder(Folder):
	if(Folder[(len(Folder)-1)] != '/'):
		Folder = Folder + "/"
	Folder = Folder + "*"
	return glob.glob(Folder)

def buildLargeDico(list_cf):
	large_dico = {}
	for dico in list_cf:
		for word in dico :
			if word in large_dico :
				large_dico[word] = large_dico[word]+1
			else :
				large_dico[word] = 1
	return large_dico

def fusion_score_list(score_list):
	result = {}
	for dico in score_list:
		for word in dico:
			if word not in result:
				result[word] = dico[word]
	return result


def write(dico, name):
	where = os.path.abspath("output/")
	filee = open(where+"\\"+ name,"w", encoding="utf8")
	for word in dico :
		filee.write(str(dico[word]) + "    "+ word +"\n")
	print("done")
	filee.close()
	return

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


def treshold(dico, value):
	treated = {}
	for word in dico :
		if dico[word] > value :
			treated[word] = dico[word]
	return treated

def combine(large_dico, usefull):
	result = {}
	for word in large_dico:
		if word in usefull:
			result[word] = large_dico[word]
	return result

def main():
	folder = os.path.abspath(sys.argv[1])
	list_file = readFolder(folder)
	list_tf = getTfAll(list_file)
	large_dico = buildLargeDico(list_tf)
	dico_idf = getIdf(list_tf)
	#5.
	score_list = getTfIdfScore(list_tf,dico_idf)
	#6.
	usefull = treshold(fusion_score_list(score_list), 8)

	write(combine(large_dico, usefull), "result")
	return 0

main()