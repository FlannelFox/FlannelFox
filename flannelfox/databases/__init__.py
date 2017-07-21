#-------------------------------------------------------------------------------
# Name:		TorrentDB
# Purpose:	These functions handle writing/reading torrent information
#			to/from the sqlite database
#
# TODO: Turn this into a class that can be instantiated as various
#		database types.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-


# flannelfox Includes
import flannelfox
from flannelfox.databases import ff_sqlite3

# Setup the logging agent
from flannelfox import logging

class Databases(object):

	def __init__(self, dbType, databaseSettings=None):
		'''
		Set the database module that should be used
		'''

		databaseSettings = databaseSettings or {}

		self.logger = logging.getLogger(__name__)

		if dbType == u'SQLITE3':
			self.Database = ff_sqlite3.Database(databaseSettings = databaseSettings)
			self.logger.debug("SQLite3 Database initialized")

		else:
			self.logger.critcal("There was an issue initializing the database. [{0}]{1}".format(dbType, e))


	def addBlacklistedTorrent(self, url, reason='No Reason Given'):
		'''
		Add a torrent to the blacklist

		These torrents are flagged as broken and should be ignored when
		the grabbers are looking for new torrents
		'''
		self.Database.addBlacklistedTorrent(url=url, reason=reason)


	def updateHashString(self, data=None, where=None):
		'''
		Update the hashString that the database is holding
		'''

		data = data or {}
		where = where or {}
		self.Database.updateHashString(data=data, where=where)


	def addTorrentsToQueue(self, queue):
		'''
		Write the Current Torrent Queue to the database

		Takes a queue of torrents as a parameter
		'''
		return self.Database.addTorrentsToQueue(queue=queue)


	def deleteTorrent(self, hashString=None,url=None,reason='No Reason Given'):
		'''
		Removes a torrent from the database

		Takes a torrent as a parameter
		'''
		return self.Database.deleteTorrent(hashString=hashString, url=url, reason=reason)


	def torrentExists(self, torrent=None, url=None, hashString=None):
		'''
		Checks to see if the torrent is already in the database

		Takes:
			A torrent as a parameter OR
			A hashString and url

		Returns True if it exists or False if it does not
		'''
		return self.Database.torrentExists(torrent=torrent, url=url, hashString=hashString)


	def torrentBlacklisted(self, url=None):
		'''
		Checks to see if the torrent is blacklisted in the database
		'''

		try:

			if not isinstance(url, str):
				raise ValueError('url was not a string')

			return self.Database.torrentBlacklisted(url=url)

		except Exception as e:
			self.logger.error("There was an issue checking if a torrent is blacklisted in the database. {0}".format(e))
			return False



	def execDB(self, query):
		'''
		Executes a query and tries to do any cleanup if there is an issue


		'''
		return self.Database.execDB(query=query)


	def queryDB(self, query):
		'''
		Perform a query on the database, this should not be called directly

		Takes:
			a SQL statement as a parameter

		Returns:
			a list of dicts, each dict holding the row information
		'''
		return self.Database.queryDB(query=query)


	def getTorrentInfo(self, hashString=None,selectors=None):
		'''
		Returns the desired information about a torrent

		Takes:
			hashString - The hash of the desired torrent
			selectors - List of fields that you want returned

		Returns:
			Dict of key,val
		'''

		selectors = selectors or []

		return self.Database.getTorrentInfo(hashString=hashString, selectors=selectors)


	def getQueuedTorrents(self, selectors=None, num=None):
		'''
		Returns the desired information about the torrent queue

		Takes:
			selectors - List of fields that you want returned
			num - Number of rows to return

		Returns:
			Dict of key,val
		'''

		selectors = selectors or []

		return self.Database.getQueuedTorrents(selectors=selectors, num=num)


	def getQueuedTorrentsCount(self):
		'''
		Returns the total number of torrents waiting in queue

		Returns:
			int
		'''
		return self.Database.getQueuedTorrentsCount()
