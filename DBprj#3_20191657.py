#-*- coding: utf-8 -*-
import datetime
import time
import sys
import MeCab
import operator
import math
from pymongo import MongoClient
from bson import ObjectId
from itertools import combinations
import re


def printMenu():
    print "1. WordCount"
    print "2. TF-IDF"
    print "3. Similarity"
    print "4. MorpAnalysis"
    print "5. CopyData"

#In this project, we assume a word seperated by a space is a morpheme.

def MorphAnalysis(docs, col_tfidf):
	print("MorphAnalysis")

	# step 1
	stop_word = {}
	f = open("stopword_list.txt", "r")
	while True:
		line = f.readline()
		if not line: break
		stop_word[line.strip('\n')] = line.strip('\n')
	f.close()

	# step 2
	for doc in docs:
		content = doc['text']
		# delete non-alphabetical ch
		content = re.sub('[^a-zA-Z]', ' ', content)
		# change to small letter
		content = content.lower().split()

		MorpList = []

		for arg in content:
			if not arg in stop_word:
				MorpList.append(arg)

	# step 3
		col_tfidf.update({'_id':doc['_id']}, {'$set': {'morph': MorpList}}, True)
	#TO-DO in open lab

def WordCount(docs, col_tfidf):
	print("WordCount")
	#TO-DO in project
	
	for doc in docs:
		WordCountList = []
		content = doc['text']
		content = re.sub('[^a-zA-Z]', ' ', content)
		content = content.lower().split()
		
		for morp in doc['morph']:
			count = 0
			count = content.count(morp)
			WordCountList.append(count)
			
		col_tfidf.update({'_id':doc['_id']}, {'$set': {'word_count': WordCountList}}, True)

	objectid = raw_input("Input ObjectId> ")
	#print(objectid)

	doc = col_tfidf.find_one({'_id':ObjectId(objectid)})
	
	morph = doc['morph']
	wc = doc['word_count']
	for i, j in zip(morph, wc):
		print(i + ' ' + str(j))
	#print(doc['morph'])
	#print(doc['wordcount'])
	#print(doc)

def TfIdf(docs, col_tfidf):
	print("TF-IDF")

	for doc in docs:
		tflist = []
		if len(doc['morph']) == 0: # list = [0]
			tflist.append(0)
			col_tfidf.update({'_id': doc['_id']}, {'$set': {'tfidf': tflist}}, True)
		
		else:
			tf = 0
			for i in doc['word_count']:
				tf += i
			for i in doc['word_count']:
				tflist.append(float(i) / float(tf)) # tf

			i = 0
			colcount = col_tfidf.count()
			for word in doc['morph']:
				idf = 0
				for d in col_tfidf.find():
					if d['morph'].count(word) > 0:
						idf += 1
				#if(word == "word"):
				#	print(word + ' ' + str(tflist[i]) + ' ' + str(idf))
				tflist[i] = tflist[i] * math.log(colcount / idf)
				i += 1
		
			col_tfidf.update({'_id': doc['_id']}, {'$set': {'tfidf': tflist}}, True)
	
	objectid = raw_input("Input ObjectId> ")
	doc = col_tfidf.find_one({'_id':ObjectId(objectid)})

	#for word, f in zip(doc['morph'], doc['tfidf']):
	#	print(word + '\t' + str(f))

	if len(doc['morph']) == 0:
		print('0')
		return

	temp = []
	for morph, tfidf in zip(doc['morph'], doc['tfidf']):
		temp.append([tfidf, morph])
	temp.sort(reverse = True)
	
	count = len(temp)
	if count > 10: count = 10

	for i in range(count):
		print('%-15s' % temp[i][1] + str(temp[i][0]))
	#print(doc['morph'].count('love'))	
    	#TO-DO in project

def Similarity(docs, col_tfidf):
	print("Similiarity")
	objid1 = raw_input("Insert Object ID(1): ")
	objid2 = raw_input("Insert Object ID(2): ")

	doc1 = col_tfidf.find_one({'_id':ObjectId(objid1)})
	doc2 = col_tfidf.find_one({'_id':ObjectId(objid2)})

	wordlist = []

	for morph in doc1['morph']:
		wordlist.append(morph)

	for morph in doc2['morph']:
		if morph in wordlist: continue
		else: wordlist.append(morph)

	list1 = [0.0] * len(wordlist)
	list2 = [0.0] * len(wordlist)

	for morph, num in zip(doc1['morph'], doc1['tfidf']):
		list1[wordlist.index(morph)] = num
	for morph, num in zip(doc2['morph'], doc2['tfidf']):
		list2[wordlist.index(morph)] = num

	sim = 0.0
	ai = 0.0
	bi = 0.0
	for x, y in zip(list1, list2):
		sim += x * y
		ai += x * x
		bi += y * y

	ai = math.sqrt(ai)
	bi = math.sqrt(bi)

	if len(doc1['morph']) == 0 or len(doc2['morph']) == 0: sim = 0.0
	else: sim = sim / (ai * bi)

	print(sim)
	#TO-DO in project

def copyData(docs, col_tfidf):
	col_tfidf.drop()
	for doc in docs:
		contentDic = {}
		for key in doc.keys():
			if key != "_id":
				contentDic[key] = doc[key]
		col_tfidf.insert(contentDic)
	#TO-Do in open lab

def PrintMorph(docs, col_tfidf):
	objid = raw_input('Insert Object ID: ')
	
	doc = col_tfidf.find_one({'_id':ObjectId(objid)})

	print('Morph List')
	if len(doc['morph']) == 0:
		print('not morph in here')
	else: 
		for morph in doc['morph']:
			print(morph)

	
#Access MongoDB
conn = MongoClient('localhost')

#fill it with your DB name - db+studentID ex) db20120121
db = conn['db20191657']

#fill it with your MongoDB( db + Student ID) ID and Password(default : 1234)
db.authenticate('db20191657', '1234')

col = db['tweet']
col_tfidf = db['tweet_tfidf']

if __name__ == "__main__":
	printMenu()
	selector = input()
	
	if selector == 1:
		docs = col_tfidf.find()
        	WordCount(docs, col_tfidf)

	elif selector == 2:
		docs = col_tfidf.find()
        	TfIdf(docs, col_tfidf)
    
	elif selector == 3:
		docs = col_tfidf.find()
		Similarity(docs, col_tfidf)

	elif selector == 4:
		docs = col_tfidf.find()
		MorphAnalysis(docs, col_tfidf)

		# call new function that get input(object id) from user and print morph 
		PrintMorph(docs, col_tfidf)
	
	elif selector == 5:
		docs = col.find()
		copyData(docs,col_tfidf)
