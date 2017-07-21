#-------------------------------------------------------------------------------
# Name:		Torrent
# Purpose:	This module is a generic torrent module that clients should use
#			when trying to describe torrents. Status can be added as needed.
#
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# System Includes
import time
from flannelfox.settings import settings
from flannelfox.databases import Databases

# Setup the database object
TorrentDB = Databases(settings['database']['defaultDatabaseEngine'])


class Status(object):
	Paused = 0
	QueuedForVerification = 1
	Verifying = 2
	QueuedForDownloading = 3
	Downloading = 4
	QueuedForSeeding = 5
	Seeding = 6


class Torrent(object):

	def __init__(   self,
					hashString=None,
					id=None,
					error=None,
					errorString=None,
					uploadRatio=None,
					percentDone=None,
					doneDate=None,
					activityDate=None,
					rateUpload=None,
					downloadDir=None,
					status=-1,
					**kwargs):

		'''
		status
		# 0 - paused
		# 1 - queued for downloading
		# 2 - verifying
		# 3 - queued for downloading
		# 4 - downloading
		# 5 - queued for seeding
		# 6 - seeding
		'''

		self.elements = {}
		self.elements['hashString'] = hashString
		self.elements['id'] = id
		self.elements['error'] = error
		self.elements['errorString'] = errorString
		self.elements['uploadRatio'] = float(uploadRatio)
		self.elements['percentDone'] = percentDone
		self.elements['doneDate'] = int(doneDate)
		self.elements['activityDate'] = activityDate
		self.elements['rateUpload'] = rateUpload
		self.elements['downloadDir'] = downloadDir
		self.elements['minTime'] = None
		self.elements['minRatio'] = None
		self.elements['seedTime'] = None
		self.elements['comparison'] = None
		self.elements['status'] = status

		for key,val in kwargs:
			self.elements[key] = val

	def __getitem__(self,key):
		if key not in self.elements:
			raise KeyError

		return self.elements[key]


	def __setitem__(self, key, val):

		self.elements[key] = val

		if self.elements[key] == val:
			return 0
		else:
			return -1


	def __len__(self):
		return len(self.elements)


	def __iter__(self):
		return self.iter()


	def items(self):
		return self.elements.items()


	def keys(self):
		return self.elements.keys()


	def values(self):
		return self.elements.values()


	def __contains__(self,element):
		return element in self.elements


	def __eq__(self,other):
		for key, val in other.iteritems():
			if key not in self.elements or self.elements[key] != val:
				return False

		return True


	def __str__(self):
		return unicode(self).encode('utf-8')


	def get(self, key, default=None):
		try:
			return self.__getitem__(key)

		except Exception:
			return default


	def isFinished(self):

		# Query the DB to get stats
		torrentData = self.getDatabaseData(
			self.elements['hashString']
		)

		if len(torrentData) < 1:
			return False

		else:
			torrentData = torrentData[0]

		# Convert minTime to seconds
		self.elements['minTime'] = torrentData['minTime'] = int(torrentData['minTime'])*60*60

		# Convert minRatio to float
		self.elements['minRatio'] = torrentData['minRatio'] = float(torrentData['minRatio'])

		if self.elements['doneDate'] <= 0:
			return False

		# Figure out how long the torrent has been seeding, this assumes
		# the client being on 24/7
		self.elements['seedTime'] = int(time.time()) - self.elements['doneDate']

		self.elements['comparison'] = torrentData['comparison']

		# Check for untracked torrents, 0 minRatio and minTime
		if torrentData['minRatio'] <= 0.0 and torrentData['minTime'] <= 0.0:
			return False

		# If the and comparison is invoked
		if ( torrentData['comparison'] == u'and' ):
			return self.__andCompare(
				torrentData['minTime'],
				torrentData['minRatio'],
				self.elements['seedTime'],
				self.elements['uploadRatio']
			)

		else:
			return self.__orCompare(
				torrentData['minTime'],
				torrentData['minRatio'],
				self.elements['seedTime'],
				self.elements['uploadRatio']
			)


	@classmethod
	def __andCompare(self, minTime, minRatio, seedTime, uploadRatio):
		if (
			(
				minTime <= seedTime and
				minTime > 0.0
			) and
			(
				minRatio <= uploadRatio and
				minRatio > 0.0
			)
		):
			return True

		return False

	@classmethod
	def __orCompare(self, minTime, minRatio, seedTime, uploadRatio):
		if (
			(
				minTime <= seedTime and
				minTime > 0.0
			) or
			(
				minRatio <= uploadRatio and
				minRatio > 0.0
			)
		):
			return True

		return False

	@classmethod
	def getDatabaseData(self, hashString):
		return TorrentDB.getTorrentInfo(
			hashString,
			['title','minTime','minRatio','comparison']
		)


	def isSeeding(self):
		if self.elements['status'] in [Status.Seeding, Status.QueuedForSeeding]:
			return True
		return False


	def isDownloading(self):
		if self.elements['status'] in [Status.QueuedForDownloading, Status.Downloading]:
			return True
		return False


	def isPaused(self):
		if self.elements['status'] is Status.Paused:
			return True
		return False


	def isUploading(self):
		if self.elements['rateUpload'] > 0:
			return True
		return False


	def isDormant(self):
		if self.isSeeding() and not self.isUploading():
			return True
		return False
