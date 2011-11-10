#!/usr/bin/python

# Joe Cabrera
# Multithreading Searcher and Indexer. 
# One Thread Indexes new documents in the background while thread in the foreground waits for new user queries
# This searcher and indexer works from the terminal, simply start it. It begins indexing files in the directory
# you point it to. 

# import needed system modules
import os, sys, time, math, random, subprocess
from random import choice
import re

# Import necessary Py-Lucene modules
import lucene
from lucene import SimpleFSDirectory, System, File, Document, Field, StandardAnalyzer, IndexWriter, Version, VERSION
from lucene import QueryParser, IndexSearcher
from lucene import IndexReader

import threading, signal

class Indexer(threading.Thread):

	# set some initial values for the class, the root directory to start indexing and pass in a writer instance
	def __init__(self, root, writer):
		threading.Thread.__init__(self)
		self.root = root
		self.writer = writer
		
	def run(self):
		env.attachCurrentThread()
		# begin the index
		for dirname, dirnames, filenames in os.walk('mini_newsgroups'):
			for subdirname in dirnames:
		
				# the first directory to index
				self.root = os.path.join(dirname, subdirname)
				#print "Adding the folder: ", self.root
			
				# call the indexer
				self.indexDocs()
				
				# sleep for a bit
				time.sleep(3)
		
	# start indexing beginning at the root directory
	def indexDocs(self):
		for self.root, dirnames, filenames in os.walk(self.root):
			for filename in filenames:
				#print "adding", filename
			
				try:
					path = os.path.join(self.root,filename)
					file = open(path)
					contents = unicode(file.read(), 'iso-8859-1')
					file.close()
					doc = Document()
					doc.add(Field("name",filename,Field.Store.YES, Field.Index.NOT_ANALYZED))
					doc.add(Field("path",path,Field.Store.YES, Field.Index.NOT_ANALYZED))
				
					if len(contents) > 0:
						doc.add(Field("contents", contents, Field.Store.NO, Field.Index.ANALYZED))
					else:
						print "warning: the file is empty %s" % filename
					self.writer.addDocument(doc)
				except Exception, e:
					print "Failed in indexDocs:", e
				#reader = writer.getReader()
				#addedDoc = reader.document(0)
				#print addedDoc
				#time.sleep(20)
				
		# optimize for fast search and commit the changes
		self.writer.optimize()
		self.writer.commit()

# before we close we always want to close the writer to prevent corruptions to the index
def quit_gracefully(*args):
	writer.close()
	print "Cleaning up and terminating"
	exit(0)

def run(writer, analyzer):
	while True:
		print 
		print "Hit enter with no input to quit."
		command = raw_input("Query:")
		if command == '':
			#searcher.close()
			return

		print "Searching for:", command
		IndexReader = writer.getReader()
		searcher = IndexSearcher(IndexReader)
		query = QueryParser(Version.LUCENE_CURRENT, "contents", analyzer).parse(command)
		scoreDocs = searcher.search(query, 50).scoreDocs
		print "%s total matching documents." % len(scoreDocs)

		for scoreDoc in scoreDocs:
			doc = searcher.doc(scoreDoc.doc)
			print 'path:', doc.get("path"), 'name:', doc.get("name")


if __name__ == '__main__':
	# always declare the signal handler first
	signal.signal(signal.SIGINT, quit_gracefully)
	STORE_DIR = "index"
	#lucene.initVM()
	env=lucene.initVM()
	print 'Using Directory: ', STORE_DIR
	
	notExist = 0
        
        # both the main program and the background indexer will share the same directory and analyzer
	if not os.path.exists(STORE_DIR):
		os.mkdir(STORE_DIR)
		notExist = 1
		
	directory = SimpleFSDirectory(File(STORE_DIR))
	
	# For now I just use the StandardAnalyzer, but you can change this
	analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
	
	# we will need a writer
	writer = IndexWriter(directory,analyzer,True,IndexWriter.MaxFieldLength.LIMITED)
	writer.setMaxFieldLength(1048576)
	
	if notExist == 1:
		writer.close()
	
	# and start the indexer
	# note the indexer thread is set to daemon causing it to terminate on a SIGINT
	indexer = Indexer(STORE_DIR,writer)
	indexer.setDaemon(True)
	indexer.start()
	print 'Starting Indexer in background...'
	
	# start up the terminal query Interface
	run(writer, analyzer)
	
	# If return from Searcher, then call the signal handler to clean up the indexer cleanly
	quit_gracefully()
