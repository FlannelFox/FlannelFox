#-------------------------------------------------------------------------------
# Name:     TorrentDB
# Purpose:	These functions handle writing/reading torrent information
#			to/from the sqlite database
#
# TODO: update the sql statements so they are injection proof
#		https://docs.python.org/2/library/sqlite3.html
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-


# System Includes
import sqlite3 as sql
import time, os

# flannelfox Includes
import flannelfox
from flannelfox.settings import settings

# Setup the logging agent
from flannelfox import logging

# Database info
QUEUED_TORRENTS_TABLE = "QueuedTorrents"
BLACKLISTED_TORRENTS_TABLE = "BlacklistedTorrents"
ADDED_TORRENTS_VIEW = "AddedTorrentsView"
QUEUED_TORRENTS_VIEW = "QueuedTorrentsView"
TV_TORRENTS_VIEW = "TVTorrentsView"
MOVIE_TORRENTS_VIEW = "MovieTorrentsView"
MUSIC_TORRENTS_VIEW = "MusicTorrentsView"
GENERIC_TORRENTS_VIEW = "GenericTorrentsView"

class Database(object):

	databaseSettings = {
		'databaseLocation': os.path.join(settings['files']['privateDir'],'flannelfox.db')
	}

	dbSetup = ( "PRAGMA foreign_keys = off;"
		"BEGIN TRANSACTION;"
		"CREATE TABLE QueuedTorrents (comparison TEXT, hashString TEXT, feedDestination TEXT, minRatio REAL, minTime INTEGER, addedOn INTEGER, added INTEGER, queuedOn INTEGER, torrentType INTEGER, proper TEXT, source TEXT, container TEXT, codec TEXT, quality TEXT, day INTEGER, month INTEGER, year INTEGER, torrentTitle TEXT, url TEXT, title TEXT, season INTEGER, episode INTEGER, releaseType TEXT, album TEXT, artist TEXT);"
		"CREATE TABLE BlacklistedTorrents (url STRING PRIMARY KEY);"
		"CREATE INDEX idx_Queue ON QueuedTorrents (added COLLATE BINARY ASC, queuedOn COLLATE BINARY ASC);"
		"CREATE INDEX idx_FeedDestination ON QueuedTorrents (feedDestination COLLATE BINARY ASC);"
		"CREATE INDEX idx_Added ON QueuedTorrents (added COLLATE BINARY DESC);"
		"CREATE INDEX idx_HashString ON QueuedTorrents (hashString COLLATE BINARY ASC);"
		"CREATE INDEX idx_TorrentType ON QueuedTorrents (torrentType COLLATE BINARY ASC);"
		"CREATE VIEW GenericTorrentsView AS SELECT QueuedTorrents.comparison, QueuedTorrents.hashstring, QueuedTorrents.feeddestination, QueuedTorrents.minratio, QueuedTorrents.mintime, QueuedTorrents.addedon, QueuedTorrents.added, QueuedTorrents.queuedon, QueuedTorrents.day, QueuedTorrents.month, QueuedTorrents.year, QueuedTorrents.torrenttitle, QueuedTorrents.url, QueuedTorrents.title, QueuedTorrents.season, QueuedTorrents.episode, QueuedTorrents.codec, QueuedTorrents.container, QueuedTorrents.proper, QueuedTorrents.quality, QueuedTorrents.source, QueuedTorrents.torrentType FROM QueuedTorrents WHERE torrentType = 'none';"
		"CREATE VIEW QueuedTorrentsView AS SELECT QueuedTorrents.comparison, QueuedTorrents.hashstring, QueuedTorrents.feeddestination, QueuedTorrents.minratio, QueuedTorrents.mintime, QueuedTorrents.addedon, QueuedTorrents.added, QueuedTorrents.queuedon, QueuedTorrents.day, QueuedTorrents.month, QueuedTorrents.year, QueuedTorrents.torrenttitle, QueuedTorrents.url, QueuedTorrents.title, QueuedTorrents.season, QueuedTorrents.episode, QueuedTorrents.codec, QueuedTorrents.container, QueuedTorrents.proper, QueuedTorrents.quality, QueuedTorrents.source, QueuedTorrents.torrentType FROM QueuedTorrents WHERE added = 0 ORDER BY queuedOn ASC;"
		"CREATE VIEW MovieTorrentsView AS SELECT QueuedTorrents.comparison, QueuedTorrents.hashstring, QueuedTorrents.feeddestination, QueuedTorrents.minratio, QueuedTorrents.mintime, QueuedTorrents.addedon, QueuedTorrents.added, QueuedTorrents.queuedon, QueuedTorrents.year, QueuedTorrents.torrenttitle, QueuedTorrents.url, QueuedTorrents.title, QueuedTorrents.codec, QueuedTorrents.container, QueuedTorrents.proper, QueuedTorrents.quality, QueuedTorrents.source, QueuedTorrents.torrentType FROM QueuedTorrents WHERE torrentType = 'movie';"
		"CREATE VIEW MusicTorrentsView AS SELECT QueuedTorrents.comparison, QueuedTorrents.hashstring, QueuedTorrents.feeddestination, QueuedTorrents.minratio, QueuedTorrents.mintime, QueuedTorrents.addedon, QueuedTorrents.added, QueuedTorrents.queuedon, QueuedTorrents.year, QueuedTorrents.torrenttitle, QueuedTorrents.url, QueuedTorrents.title, QueuedTorrents.album, QueuedTorrents.artist, QueuedTorrents.codec, QueuedTorrents.releaseType, QueuedTorrents.container, QueuedTorrents.proper, QueuedTorrents.quality, QueuedTorrents.source, QueuedTorrents.torrentType FROM QueuedTorrents WHERE torrentType = 'music';"
		"CREATE VIEW AddedTorrentsView AS SELECT QueuedTorrents.comparison, QueuedTorrents.hashstring, QueuedTorrents.feeddestination, QueuedTorrents.minratio, QueuedTorrents.mintime, QueuedTorrents.addedon, QueuedTorrents.added, QueuedTorrents.queuedon, QueuedTorrents.day, QueuedTorrents.month, QueuedTorrents.year, QueuedTorrents.torrenttitle, QueuedTorrents.url, QueuedTorrents.title, QueuedTorrents.season, QueuedTorrents.episode, QueuedTorrents.codec, QueuedTorrents.container, QueuedTorrents.proper, QueuedTorrents.quality, QueuedTorrents.source, QueuedTorrents.torrentType FROM QueuedTorrents WHERE added = 1 ORDER BY queuedOn ASC;"
		"CREATE VIEW TVTorrentsView AS SELECT QueuedTorrents.comparison, QueuedTorrents.hashstring, QueuedTorrents.feeddestination, QueuedTorrents.minratio, QueuedTorrents.mintime, QueuedTorrents.addedon, QueuedTorrents.added, QueuedTorrents.queuedon, QueuedTorrents.day, QueuedTorrents.month, QueuedTorrents.year, QueuedTorrents.torrenttitle, QueuedTorrents.url, QueuedTorrents.title, QueuedTorrents.season, QueuedTorrents.episode, QueuedTorrents.codec, QueuedTorrents.container, QueuedTorrents.proper, QueuedTorrents.quality, QueuedTorrents.source, QueuedTorrents.torrentType FROM QueuedTorrents WHERE torrentType = 'tv';"
		"COMMIT TRANSACTION;"
		"PRAGMA foreign_keys = on;" )


	def __init__(self, databaseSettings=None):

		databaseSettings = databaseSettings or {}

		self.logger = logging.getLogger(__name__)

		directory = os.path.dirname(self.databaseSettings['databaseLocation'])

		if not os.path.exists(directory):
			os.makedirs(directory)

		self.databaseSettings.update(databaseSettings)

		self.setupDB()


	def __execDB(self, query, vals=None):
		'''
		Executes a query and tries to do any cleanup if there is an issue


		'''

		try:
			# SQL Connection
			sqlConnection = sql.connect(self.databaseSettings['databaseLocation'])

			with sqlConnection:

				# Set the results to be in dictionary form
				sqlConnection.row_factory = self.dictFactory

				# Establish a cursor and then make the query
				sqlCursor = sqlConnection.cursor()

				if vals is None:
					sqlCursor.execute(query)
				else:
					sqlCursor.execute(query, vals)

				return sqlCursor.rowcount

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem executing the SQL exec:\n{0}\n{1}".format(e, query))
			return -2


	def __execScriptDB(self, script):
		'''
		Executes a query and tries to do any cleanup if there is an issue


		'''

		try:
			# SQL Connection
			sqlConnection = sql.connect(self.databaseSettings['databaseLocation'])

			with sqlConnection:

				# Set the results to be in dictionary form
				sqlConnection.row_factory = self.dictFactory

				# Establish a cursor and then make the query
				sqlCursor = sqlConnection.cursor()

				sqlCursor.executescript(script)

				return sqlCursor.rowcount

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem executing the SQL execscript:\n{0}\n{1}".format(e, script))
			return -2


	def __queryDB(self, query, vals=None):
		'''
		Perform a query on the database, this should not be called directly

		Takes:
			a SQL statement as a parameter

		Returns:
			a list of dicts, each dict holding the row information
		'''

		try:
			# SQL Connection
			sqlConnection = sql.connect(self.databaseSettings['databaseLocation'])

			with sqlConnection:

				# Set the results to be in dictionary form
				sqlConnection.row_factory = self.dictFactory

				# Establish a cursor and then make the query
				sqlCursor = sqlConnection.cursor()

				if vals is None:
					sqlCursor.execute(query)
				else:
					sqlCursor.execute(query, vals)

				rows = sqlCursor.fetchall()

				# Check for None, this might happen and should return an empty dict
				if rows is None:
					rows = []

			return rows

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem executing the SQL query:\n{0}\n{1}".format(e, query))
			return []


	def setupDB(self):
		self.__execScriptDB(self.dbSetup)


	@classmethod
	def dictFactory(self, cursor, row, ignore=None):
		'''
		Used to return an actual dict of values instead of Row
		'''
		if ignore is None:
			ignore=[]

		d = {}
		for idx, col in enumerate(cursor.description):

			# If the column is empty then skip it
			# If the column is queue management related then skip it

			if row[idx] is None or col[0] in ignore:
				pass	# Ignore these fields during conversion
			else:
				d[col[0]] = row[idx]

		return d


	def addBlacklistedTorrent(self, url, reason='No Reason Given'):
		'''
		Add a torrent to the blacklist

		These torrents are flagged as broken and should be ignored when
		the grabbers are looking for new torrents
		'''

		query = 'INSERT OR IGNORE INTO {table} ("url") VALUES (?)'.format(table=BLACKLISTED_TORRENTS_TABLE)

		result = self.__execDB(query, (url, ))


	def updateHashString(self, data=None, where=None):
		'''
		Update the hashString that the database is holding
		'''

		data = data or {}
		where = where or {}

		dataKeys = []
		dataVals = []

		whereKeys = []
		whereVals = []

		for key,val in data.items():
				dataKeys.append(key)

				if val is None:
					dataVals.append('')
				else:
					dataVals.append(val)

		for key,val in where.items():
				whereKeys.append(key)

				if val is None:
					whereVals.append('')
				else:
					whereVals.append(val)

		query = "UPDATE {table} SET {data} WHERE {where}".format(
			table=QUEUED_TORRENTS_TABLE,
			data=', '.join(
				['"{col}" = ?'.format(col=k) for k in dataKeys]
			),
			where=' AND '.join(
				['"{col}" = ?'.format(col=k) for k in whereKeys]
			)
		)

		result = self.__execDB(query, tuple( dataVals + whereVals ))

		if result < 0:
			self.logger.warning('There was a problem updating the hashstring of a torrent:\n{0}'.format(query))


	def addTorrentsToQueue(self, queue):
		'''
		Write the Current Torrent Queue to the database

		Takes a queue of torrents as a parameter
		'''

		# Get current time, used for queuedOn field in DB

		for torrent in queue:

			sinceEpoch = int(time.time())

			keys = ['queuedOn', 'added']
			vals = [sinceEpoch, 0]

			for key, val in torrent.items():

				keys.append(key)

				if val is None:
					vals.append('')
				else:
					vals.append(val)

			query = "INSERT INTO {table} ({cols}) VALUES ({vals})".format(
				table=QUEUED_TORRENTS_TABLE,
				cols=','.join(('"{}"'.format(x) for x in keys)),
				vals=','.join(('?' for x in keys))
			)

			try:
				insertedRows = self.__execDB(query, tuple(vals))

				if insertedRows < 0:
					self.logger.warning('There was a problem adding torrents to the queue')

			except (sql.Error, Exception) as e:
				self.logger.warning('There was a problem adding torrents to the queue:\n{0}'.format(e))
				return False

		return True


	def deleteTorrent(self, hashString=None, url=None, reason='No Reason Specified'):
		'''
		Removes a torrent from the database

		Takes a torrent as a parameter
		'''

		try:

			keys = []
			vals = []

			if hashString is not None:
				keys.append('hashString')
				vals.append(hashString)
			elif url is not None:
				keys.append('url')
				vals.append(url)
			else:
				return

			query = 'DELETE FROM {table} WHERE {where}'.format(
				table=QUEUED_TORRENTS_TABLE,
				where=' AND '.join(
					['"{col}" = ?'.format(col=k) for k in keys]
				)
			)

			self.__execDB(query, tuple(vals))

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem deleting a torrent:\n{0}".format(e))


	def torrentBlacklisted(self, url=None):
		'''
		Checks to see if the torrent is blacklisted in the database
		'''

		query = 'SELECT count("url") as "hits" FROM {table} WHERE "url" = ?'.format(table=BLACKLISTED_TORRENTS_TABLE)
		results = self.__queryDB(query, (url, ))
		hits = int(results[0]['hits'])

		return bool(hits > 0)


	def torrentExists(self, torrent=None, url=None, hashString=None):
		'''
		Checks to see if the torrent is already in the database

		Takes:
			A torrent as a parameter OR
			A hashString and url

		Returns True if it exists or False if it does not
		'''

		try:


			if torrent is not None:

				keys = []
				vals = []

				for key, val in torrent.items():

					if key not in flannelfox.settings.FUZZY_PROPERTIES:

						keys.append(key)

						# TODO: See if this should be removed in favour of simply
						# using iff val is not None
						if val is None:
							vals.append('')
						else:
							vals.append(val)

				if torrent['torrentType'] == 'tv':
					currentView = TV_TORRENTS_VIEW

				elif torrent['torrentType'] == 'movie':
					currentView = MOVIE_TORRENTS_VIEW

				elif torrent['torrentType'] == 'music':
					currentView = MUSIC_TORRENTS_VIEW

				else:
					currentView = GENERIC_TORRENTS_VIEW

				query = 'SELECT "torrentTitle" FROM {table} WHERE {where}'.format(
					table=currentView,
					where=' AND '.join(
						['"{col}" = ?'.format(col=k) for k in keys]
					)
				)

				rows = self.__queryDB(query, tuple(vals))

			elif url is not None and hashString is not None:

				keys = ['hashString', 'url']
				vals = [hashString, url]

				query = 'SELECT "torrentTitle" FROM {table} WHERE {where}'.format(
					table=QUEUED_TORRENTS_TABLE,
					where=' AND '.join(
						['"{col}" = ?'.format(col=k) for k in keys]
					)
				)

				rows = self.__queryDB(query, tuple(vals))

			return bool(len(rows) > 0)

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem checking if a torrent exists:\n{0}".format(e))
			return False


	def getTorrentInfo(self, hashString=None, selectors=None):
		'''
		Returns the desired information about a torrent

		Takes:
			hashString - The hash of the desired torrent
			fields - List of fields that you want returned

		Returns:
			Dict of key,val
		'''

		selectors = selectors or {}

		try:
			if isinstance( selectors, list ) and len( selectors ) > 0:
				selectors = ','.join(['"{}"'.format(f) for f in selectors])

			elif isinstance( selectors, str):
				selectors = '"{}"'.format(selectors)

			else:
				selectors = '*'


			query = 'SELECT {selectors} FROM {table} WHERE "hashString" = ?'.format(
				selectors=selectors,
				table=QUEUED_TORRENTS_TABLE
			)

			results = self.__queryDB(query, (hashString, ))

			if results is None:
				results = {}

			return results

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem getting torrent info:\n{0}".format(e))
			return {}


	def getQueuedTorrents(self, selectors=None, num=None):
		'''
		Returns the desired information about the torrent queue

		Takes:
			fields - List of fields that you want returned
			num - Number of rows to return

		Returns:
			Dict of key,val
		'''

		selectors = selectors or []

		try:

			if isinstance( selectors, list ) and len( selectors ) > 0:
				selectors = ','.join(['"{}"'.format(f) for f in selectors])

			elif isinstance( selectors, str):
				selectors = '"{}"'.format(selectors)

			else:
				selectors = '*'

			# Build the query
			query = 'SELECT {selectors} FROM {table}'.format(
				selectors=selectors,
				table=QUEUED_TORRENTS_VIEW
			)

			if num is not None:
				query += ' LIMIT {0}'.format(num)

			# Query DB
			results = self.__queryDB(query)

			if results is None:
				return []
			else:
				return results

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem getting queued torrents:\n{0}".format(e))
			return []


	def getQueuedTorrentsCount(self):
		'''
		Returns the total number of torrents waiting in queue

		Returns:
			int
		'''

		try:

			# Build the query
			query = 'SELECT count("added") AS "downloadsQueued" FROM {table} WHERE "added"=0'.format(table=QUEUED_TORRENTS_VIEW)

			# Query DB
			results = self.__queryDB(query)

			return results[0]["downloadsQueued"]

		except ( sql.Error, Exception ) as e:
			self.logger.warning("There was a problem getting a count of queued torrents:\n{0}\n{1}".format(e, query))
			return -1
