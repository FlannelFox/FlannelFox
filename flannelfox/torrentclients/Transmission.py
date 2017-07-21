#-------------------------------------------------------------------------------
# Name:		TransmissionRemote
# Purpose:	Interacts with transmission daemon
#
# TODO:		Modify torrent using funcs to use the torrent class
#			List out the actual generic calls
#			verify and start -> Please Verify Local Data! Piece #114 is corrupt.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import json, time


# Third party modules
import requests

# Needed to fix an SSL issue with requests
#import urllib3.contrib.pyopenssl
#urllib3.contrib.pyopenssl.inject_into_urllib3()

# flannelfox Includes
from flannelfox.settings import settings
from flannelfox.torrentclients.Torrent import Status as TorrentStatus
from flannelfox.torrentclients.Torrent import Torrent
from flannelfox.torrentclients import Trackers
from flannelfox.tools import changeCharset

# Setup the logging agent
from flannelfox import logging

class Responses(object):
	success = 'success'
	invalidArgument = 'invalid argument'
	duplicate = 'duplicate torrent'
	badTorrent = 'invalid or corrupt torrent file'
	torrentNotFound = 'gotMetadataFromURL: http error 404: Not Found'
	torrentBadRequest = 'gotMetadataFromURL: http error 400: Bad Request'
	torrentServiceUnavailable = 'gotMetadataFromURL: http error 503: Service Unavailable'
	torrentNoResponse = 'gotMetadataFromURL: http error 0: No Response'


class Client(object):

	elements = {
		'host': 'localhost',
		'port': '9091',
		'user': None,
		'password': None,
		'rpcLocation': None,
		'https': False,
		'queue': [],
		'sessionId': None
	}

	TRANSMISSION_MAX_RETRIES = 3

	SLEEP_SHORT = 5
	SLEEP_LONG = 10

	logger = None

	def __init__(self):

		self.logger = logging.getLogger(__name__)
		self.logger.info('TransmissionClient INIT')
		self.logger.debug('TransmissionClient Settings: {0}'.format(settings['client']))

		if settings['client'] != {}:
			self.elements.update(settings['client'])

		self.logger.debug('TransmissionClient Settings 2: {0}'.format(self.elements))

		# Strip off the leading slash if it exists
		self.elements['rpcLocation'] = self.elements['rpcLocation'].lstrip('/')

		# tag generator the keep transmisison calls matched
		self.tagGenerator = self.__generateTag()

		# Build the server URI
		self.elements['uri'] = 'http'

		if self.elements['https']:
			self.elements['uri'] += 's'

		self.elements['uri'] += '://{0}:{1}'.format(self.elements['host'], self.elements['port'])
		self.logger.debug('TransmissionClient URL: {0}'.format(self.elements['uri']))


	@classmethod
	def __transmissionInit(self, action='restart'):
		'''
		Used to restart the transmission daemon
		'''

		response,error = subprocess.Popen([TORRENT_DAEMON_INIT,action], stdout=subprocess.PIPE).communicate()

		if error is not None:
			raise ValueError


	@classmethod
	def __generateTag(self):
		'''
		Generates an int to be used for tag numbers in the transmission-rpc
		calls
		'''
		while True:
			for n in range(65535):
				yield n


	def __sendRequest(self, queryString=None, postData=None):
		'''
		Handles making calls to the transmission-rpc interface

		Takes:
			queryString - GET data
			postData - PostData

		Returns:
			Tuple (response and httpCode)
		'''

		response = ''
		httpCode = None
		encoding = 'utf-8'
		headers = {}
		uri = None
		auth = None

		# Check if authentication should be used
		if self.elements['user'] is not None:
			auth=(self.elements['user'], self.elements['password'])

		if self.elements['sessionId'] is not None:
			headers.update({'X-Transmission-Session-Id':self.elements['sessionId']})

		if postData is not None:
			headers.update({'Content-type':'application/json'})

		# Add RPC path to the URI
		if queryString is not None:
			uri = '{0}/{1}?{2}'.format(self.elements['uri'],self.elements['rpcLocation'],queryString)
		else:
			uri = '{0}/{1}'.format(self.elements['uri'],self.elements['rpcLocation'])

		self.logger.debug('Trying to communicate with the Transmission Server')
		try:
			# Connect to the RPC server
			if postData is None:
				if auth is not None:
					r = requests.get(uri, auth=auth, headers=headers)
				else:
					r = requests.get(uri, headers=headers)
			else:
				if auth is not None:
					r = requests.post(uri, auth=auth, headers=headers, data=postData)
				else:
					r = requests.post(uri, headers=headers, data=postData)

			response = r.content
			httpCode = r.status_code
			encoding = r.encoding

			# Look for the X-Transmission-Session-Id header and save it, then
			# make the request again
			if httpCode == 409:
				self.elements['sessionId'] = r.headers.get('X-Transmission-Session-Id')
				self.logger.debug('X-Transmission-Session-Id Error')

				response, httpCode, encoding = self.__sendRequest(queryString,postData)

			self.logger.debug('Transmission call completed')
		except Exception as e:
			self.logger.debug('There was a problem communicating with Transmission:\n{0}'.format(e))
			try:
				httpCode = e.code
			except (AttributeError):
				httpCode = -1

		return (response, httpCode, encoding)


	def __parseTransmissionResponse(self, postData, tries=0):
		'''
		Parse a transmission response

		Takes:
			tries - Limits the recursion of this call when tags do not match
			postData - The data posted to transmission-rpc

		Returns:
			Tuple (torrents,httpResponseCode,transmissionResponseCode)
		'''

		response = None
		httpResponseCode = -1
		transmissionResponseCode = 'failed'

		if tries >= self.TRANSMISSION_MAX_RETRIES:
			return (response, httpResponseCode, transmissionResponseCode)

		# Make the call
		response, httpResponseCode = self.__sendRequest(postData = postData.encode('utf-8'))[:2]

		if httpResponseCode == 401:
			return (response, httpResponseCode, 'Authorization Error')

		# Ensure the result is in utf-8
		response = changeCharset(response,'utf-8','html.parser')

		# parse the json if it exists
		if response is not None:
			try:
				response = json.loads(response.decode('utf-8'))

			# If there is a problem parsing the response then return an empty set
			except (ValueError) as e:
				pass

		# Make sure we got a result
		if isinstance(response,dict):

			# Get Tag, if tag is available and ensure the response matches
			posted = json.loads(postData)
			if isinstance(posted,dict) and 'tag' in posted:
				if isinstance(response,dict) and 'tag' in response:
					if posted['tag'] != response['tag']:
						time.sleep(self.SLEEP_SHORT)
						response,httpResponseCode = self.__parseTransmissionResponse(
							postData=postData,
							tries=tries+1
						)


			# Get Transmission Response Code
			if isinstance(response,dict) and 'result' in response:
				transmissionResponseCode = response['result']

		return (response, httpResponseCode, transmissionResponseCode)


	def __getTorrents(self, fields=None):
		'''
		Fetch a set of torrents with the provided information

		Takes:
			fields - Fields to be returned in the transmission-rpc

		Returns:
			Tuple (torrents,httpResponseCode,transmissionResponseCode)
		'''
		fields = fields or [
			'hashString',
			'id',
			'error',
			'errorString',
			'uploadRatio',
			'percentDone',
			'doneDate',
			'activityDate',
			'rateUpload',
			'status',
			'downloadDir',
			'trackerStats'
		]


		# Method
		commandJson = '{"method":"torrent-get",'

		# Arguments
		commandJson += '"arguments":{'

		# Fields
		commandJson += '"fields":["'
		commandJson += '","'.join(fields)
		commandJson += '"]'

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Extract the values so we can replace the response with only torrents
		response,httpResponseCode,transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

		# Get Torrents
		torrents = []

		if isinstance(response,dict) and 'arguments' in response:
			if isinstance(response['arguments'],dict) and 'torrents' in response['arguments']:
				if isinstance(response['arguments']['torrents'],list):
					torrents = response['arguments']['torrents']

		return (torrents,httpResponseCode,transmissionResponseCode)


	def updateQueue(self):
		'''
		Updates the class variable queue with the latest torrent queue info

		Returns:
			Tuple (transmissionResponseCode, httpResponseCode)
		'''

		# Initial attempt at fetching data
		torrents,httpResponseCode,transmissionResponseCode = self.__getTorrents()

		# Incase we get an incomplete answer or fail let's retry
		tries = 0
		while transmissionResponseCode != Responses.success and tries < self.TRANSMISSION_MAX_RETRIES:
			torrents, httpResponseCode, transmissionResponseCode = self.__getTorrents()
			tries += 1

		if isinstance(torrents,list):
			self.elements['queue'] = []

			for torrent in torrents:

				trackers = torrent['trackerStats']

				# Look to make sure at least one tracker is working
				# This is due to bug #5775
				# https://trac.transmissionbt.com/ticket/5775
				if torrent['status'] == TorrentStatus.Downloading and torrent['percentDone'] == 0.0 and torrent['errorString'] == '':

					workingTrackerExists = False

					for tracker in trackers:
						if not workingTrackerExists:

							if tracker['lastAnnounceResult'] != '' and tracker['lastAnnounceResult'] != None:
								workingTrackerExists = True
								self.logger.debug('Rewriting errorString: {0}'.format(tracker['lastAnnounceResult']))
								torrent['errorString'] = tracker['lastAnnounceResult']

							elif tracker['lastAnnounceSucceeded']:
								workingTrackerExists = True

					if not workingTrackerExists and torrent['errorString'] == '':
						torrent['error'] = -1
						torrent['errorString'] = 'No Connectable Trackers Found'
						torrent['error'] = 99
						torrent['errorString'] = 'No Connectable Trackers Found'

				# Check for torrents that should be removed
				for error in Trackers.Responses.Remove:
					if error in torrent['errorString']:
						self.logger.debug('Removing torrent do to errorString: {0}'.format(torrent['errorString']))
						self.removeBadTorrent(hashString=torrent['hashString'], reason=torrent['errorString'])
						continue

				# Check if the torrent is corrupted
				if 'please verify local data' in torrent['errorString']:

					# Ensure a Check is not already in place
					if (torrent['status'] not in [TorrentStatus.Paused, TorrentStatus.QueuedForVerification, TorrentStatus.Verifying]):
						self.verifyTorrent(hashString=torrent['hashString'])
						continue

					elif torrent['status'] == TorrentStatus.Paused:
						self.startTorrent(hashString=torrent['hashString'])
						continue

					self.logger.debug('Corrupted torrent: {1} STAT: {0}'.format(torrent['status'], torrent['hashString']))

				elif torrent['errorString'] != '':
					self.logger.debug('Error encountered: {0} {1}'.format(torrent['hashString'],torrent['errorString']))


				t = Torrent(hashString=torrent['hashString'],
							id=torrent['id'],
							error=torrent['error'],
							errorString=torrent['errorString'],
							uploadRatio=torrent['uploadRatio'],
							percentDone=torrent['percentDone'],
							doneDate=torrent['doneDate'],
							activityDate=torrent['activityDate'],
							rateUpload=torrent['rateUpload'],
							downloadDir=torrent['downloadDir'],
							status=torrent['status']
				)

				self.elements['queue'].append(t)

		return (transmissionResponseCode, httpResponseCode)


	def getQueue(self):
		'''
		Returns:
			List [torrents]
		'''
		return self.elements['queue']


	def verifyTorrent(self, hashString=None):
		'''
		Verifies a corrupted torrent

		Takes:
			hashString - Hash of the specific torrent to remove

		Returns:
			bool True is action completed
		'''
		time.sleep(self.SLEEP_SHORT)

		if hashString is None:
			return False

		# Method
		commandJson = '{"method":"torrent-verify",'

		# Arguments
		commandJson += '"arguments":{'

		# Ids
		commandJson += '"ids":"{0}"'.format(hashString)

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Stop the torrent first
		if not self.stopTorrent(hashString=hashString):
			# Could not stop the torrent... This should not happen
			pass

		# Make sure the call worked
		# *_ acts as a list to eat all data except what is before or after it
		*_, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

		if transmissionResponseCode == Responses.success:
			self.logger.debug('Verification Succeeded')
			return True
		else:
			self.logger.debug('Verification Failed')
			return False


	def stopTorrent(self, hashString=None):
		'''
		Stops a torrent

		Takes:
			hashString - Hash of the specific torrent to remove

		Returns:
			bool True is action completed
		'''
		time.sleep(self.SLEEP_SHORT)

		if hashString is None:
			return False

		# Method
		commandJson = '{"method":"torrent-stop",'

		# Arguments
		commandJson += '"arguments":{'

		# Ids
		commandJson += '"ids":"{0}"'.format(hashString)

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Make sure the call worked
		*_, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

		if transmissionResponseCode == Responses.success:
			self.logger.debug('Stop Succeeded')
			return True
		else:
			self.logger.debug('Stop Failed')
			return False


	def startTorrent(self, hashString=None):
		'''
		Starts a torrent

		Takes:
			hashString - Hash of the specific torrent to remove

		Returns:
			bool True is action completed
		'''
		time.sleep(self.SLEEP_LONG)

		if hashString is None:
			return False

		# Method
		commandJson = '{"method":"torrent-start",'

		# Arguments
		commandJson += '"arguments":{'

		# Ids
		commandJson += '"ids":"{0}"'.format(hashString)

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Make sure the call worked
		response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

		if transmissionResponseCode == Responses.success:
			self.logger.debug('Start Succeeded')
			return True
		else:
			self.logger.debug('Start Failed')
			return False


	def removeBadTorrent(self, hashString=None, reason='No Reason Given'):
		'''
		Removes a torrent from both transmission and the database
		this should be called when there is a bad torrent.

		Takes:
			hashString - Hash of the specific torrent to remove
		'''

		# Remove the torrent from the client
		self.removeTorrent(hashString=hashString, deleteData=True, reason=reason)


	def removeTorrent(self, hashString=None, deleteData=False, reason='No Reason Given'):
		'''
		Removes a torrent from transmission

		Takes:
			hashString - Hash of the specific torrent to remove

			deleteData - bool, tells if the torrent data should be removed

			TODO: if hashString is not specified then we should remove the torrent
			that has the longest time since active.

		Returns:
			bool True is action completed
		'''
		time.sleep(self.SLEEP_SHORT)

		if hashString is None:
			return False

		# Method
		commandJson = '{"method":"torrent-remove",'

		# Arguments
		commandJson += '"arguments":{'

		# Ids
		commandJson += '"ids":"{0}",'.format(hashString)

		# Delete Option
		commandJson += '"delete-local-data":{0}'.format(str(deleteData).lower())

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Make sure the call worked
		response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)


		if deleteData:
			self.logger.debug('Torrent deleted from client: {0}'.format(reason))
		else:
			self.logger.debug('Torrent Removed from client: {0}'.format(reason))

		if transmissionResponseCode == Responses.success:
			self.logger.debug('Torrent Removal Succeeded')
			return True
		else:
			self.logger.debug('Torrent Removal Failed')
			return False


	def removeExtraTrackers(self, hashString=None):
		'''
		Attempts to remove extra trackers from torrents that can cause automation issues.
		'''
		# Method
		commandJson = '{"method":"torrent-set",'

		# Arguments
		commandJson += '"arguments":{'

		# Tracker remove
		commandJson += '"trackerRemove":[1],'

		# Torrent Id
		commandJson += '"ids":"{0}"'.format(hashString)

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		self.logger.debug('Trying to remove extra trackers')
		while (True):

		# Remove a tracker
			response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

			# If the call did not work then we are down to
			# the last tracker so break out of the loop
			if transmissionResponseCode == Responses.invalidArgument:
				break

			self.logger.debug('Tracker removed')

			# Wait 3 seconds before removing the next tracker
			time.sleep(self.SLEEP_SHORT)

		return True


	def addTorrentURL(self, url=None, destination=settings['files']['defaultTorrentLocation']):
		'''
		Attempts to load the torrent at the given url into transmission

		Takes:
			url - url of the torrent file to be added

			destination - where the torrent should be saved

		Returns:
			bool True is action completed successfully
		'''
		self.logger.info('TransmissionClient adding torrent')
		# Make sure a URL was passed
		if url is None:
			raise ValueError('A url must be provided to add a torrent')

		self.logger.debug('Trying to add a new torrent:\n{0}'.format(url))

		# Method
		commandJson = '{"method":"torrent-add",'

		# Arguments
		commandJson += '"arguments":{'

		# Download Dir
		if destination is not None:
			commandJson += '"download-dir":"{0}",'.format(destination)

		# Filename
		commandJson += '"filename":"{0}"'.format(url)

		# Close Arguments
		commandJson += '},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Make sure the call worked
		response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

		if httpResponseCode != 200:
			self.logger.info('Torrent Add Failed: {0}'.format(httpResponseCode))

		# Get Duplicated Torrents
		if isinstance(response,dict) and 'arguments' in response:
			if isinstance(response['arguments'],dict) and 'torrent-duplicate' in response['arguments']:

				# Duplicate Torrent
				duplicateTorrent = response['arguments']['torrent-duplicate']
				self.logger.info('Duplicate Torrent Detected: {0}'.format(transmissionResponseCode))
				return (1, duplicateTorrent['hashString'])

		# Get Added Torrents
		if isinstance(response,dict) and 'arguments' in response:
			if isinstance(response['arguments'],dict) and 'torrent-added' in response['arguments']:

				torrentAdded = response['arguments']['torrent-added']

		if transmissionResponseCode == Responses.success:
			# TODO: Remove extra trackers, this is needed due to a bug in
			# transmission that prevents non-communication related errors
			# from being seen when there is a back tracker.
			self.logger.info('Torrent Added: {0}'.format(transmissionResponseCode))
			return (0, torrentAdded['hashString'])

		else:
			# Here we need to handle any special errors encountered when
			# trying to add a torrent

			if (transmissionResponseCode in [
						Responses.torrentBadRequest,
						Responses.torrentServiceUnavailable,
						Responses.torrentNoResponse
					]
				):
				# Torrent is broken so lets delete it from the DB, this leaves the opportunity
				# for the torrent to later be added again
				self.logger.info('Torrent failed, but we can retry')
				return (2, transmissionResponseCode)


			elif (transmissionResponseCode in [
						Responses.badTorrent,
						Responses.torrentNotFound
					]
				):
				self.logger.info('Torrent is bad, so let\'s blacklist it')
				return (3, transmissionResponseCode)

			else:
				self.logger.info('Torrent Add Failed: {0}'.format(transmissionResponseCode))
				return (4, 'Unknown Error/Failed')


	def getSlowestSeeds(self, num=None):
		'''
		Look for the slowest seeding torrents, slowest first

		Takes:
			num - Int, the number of torrent objects to return
		'''
		slowestSeeds = []

		torrents = self.getFinishedSeeding()

		for torrent in torrents:
			if torrent.isSeeding():
				slowestSeeds.append(torrent)

		# Sort torrents if we have any
		if len(slowestSeeds) > 0:
			slowestSeeds.sort(key=lambda torrent: torrent['rateUpload'])

		if len(slowestSeeds) == 0 or num is None:
			return slowestSeeds
		return slowestSeeds[:num]


	def getDormantSeeds(self, num=None):
		'''
		Looks for a seeding torrent with the longest time since active, returns
		torrents, oldest first
		'''
		dormantSeeds = []


		torrents = self.getFinishedSeeding()

		for torrent in torrents:
			if torrent.isDormant():
				dormantSeeds.append(torrent)

		# Sort torrents if we have any
		if len(dormantSeeds) > 0:
			dormantSeeds.sort(key=lambda torrent: torrent['activityDate'])

		if len(dormantSeeds) == 0 or num is None:
			return dormantSeeds
		return dormantSeeds[:num]


	def getDownloading(self, num=None):
		'''
		Returns a list of torrents that are downloading

		Takes:
			num - Int, the number of torrents to return
		'''
		downloadingTorrents = []

		torrents = self.elements['queue']

		for torrent in torrents:
			if torrent.isDownloading():
				downloadingTorrents.append(torrent)

		if len(downloadingTorrents) == 0 or num is None:
			return downloadingTorrents
		return downloadingTorrents[:num]


	def getSeeding(self, num=None):
		'''
		Returns a list of torrents that are Seeding

		Takes:
			num - Int, the number of torrents to return
		'''
		seedingTorrents = []

		torrents = self.elements['queue']

		for torrent in torrents:
			if torrent.isSeeding():
				seedingTorrents.append(torrent)

		if len(seedingTorrents) == 0 or num is None:
			return seedingTorrents
		return seedingTorrents[:num]


	def getFinishedSeeding(self, num=None):
		'''
		Returns a list of torrents that are finished seeding

		Takes:
			num - Int, the number of torrents to return
		'''
		torrents = self.getSeeding()
		finishedSeeding = []

		for torrent in torrents:
			if torrent.isFinished():
				finishedSeeding.append(torrent)

		if len(finishedSeeding) == 0 or num is None:
			return finishedSeeding
		return finishedSeeding[:num]


	def setAltSpeed(self, enabled=False):
		'''
		Enables/Disables the altSpeed setting in transmission

		Takes:
			enabled - bool, True is ON, False is OFF

		Returns:
			bool, True if action completed
		'''

		# Method
		commandJson = '{"method":"session-set",'

		# Arguments
		commandJson += '"arguments":{'

		# Ids
		commandJson += '"alt-speed-time-enabled":{0}'.format(str(enabled).lower())

		# Close Arguments
		commandJson += '"},'

		# Tag (not strictly needed)
		commandJson += '"tag":{0}'.format(next(self.tagGenerator))+'}'

		# Make sure the call worked
		response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

		return bool(transmissionResponseCode == Responses.success)


	def restart(self):
		self.__transmissionInit(action='restart')


	def start(self):
		self.__transmissionInit(action='restart')


	def stop(self):
		self.__transmissionInit(action='restart')
