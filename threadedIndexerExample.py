#!/usr/bin/python

# Joe Cabrera
# Example of using threaded indexer.

# just import all
from threadedSearch import *

# STORE_DIR - is the location where you want the index stored
STORE_DIR = "index"

# start the JVM
env=lucene.initVM()

# Make FSDirectory from the specified STORE_DIR
directory = SimpleFSDirectory(File(STORE_DIR))

# what directory we want to index
directoryToWalk = 'mini_newsgroups'

# For now I just use the StandardAnalyzer, but you can change this
# This one is just the Lucene default one
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
	
# we will need a writer
writer = IndexWriter(directory,analyzer,True,IndexWriter.MaxFieldLength.LIMITED)
writer.setMaxFieldLength(1048576)

# Create the indexer 
indexer = Indexer(STORE_DIR,writer,directoryToWalk)

#This allow the thread to terminate on a SIGINT
indexer.setDaemon(True)

# Start the indexer
indexer.start()
