#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# Name:		queuedaemon
# Purpose:	Watches the Transmission Queue, adding adding and removing
#			torrents when appropriate
#
# TODO:		Make this more flexable and able to handle other clients
#			Use Slowest and Dormat torrents as finished instead of finished
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import time, sys, platform, os, traceback
from time import gmtime, strftime

# Third party modules
import daemon

# FreeSpace Calculator
from flannelfox.ostools import FreeSpace, UsedSpace

# Logging
from flannelfox import logging

# Flannelfox Includes
from flannelfox.settings import settings
from flannelfox.databases import Databases
from flannelfox.torrentclients import TorrentClient
from flannelfox.tools import changeCharset

# Setup the logger.agent
logger = logging.getLogger(__name__)

class QueueReader():

	logger = logging.getLogger(__name__)

	# Setup the database object
	database = None
	defaultDatabaseType = settings['database']['defaultDatabaseEngine']

	# Torrent client object
	torrentClient = None

	def __init__(self, *args):
		self.database = Databases(
			dbType = self.defaultDatabaseType
		)
		self.torrentClient = self.setupTorrentClient()
		self.torrentClient.updateQueue()


	def setupTorrentClient(self):
		if 'client' not in settings:
			self.logger.warning('No client was configured to monitor!')
			return None

		# Try to create a torrent client instance
		try:
			if settings['client']['type'] == 'transmission':
				logger.debug("Creating Transmission Client");
				return TorrentClient()

		except Exception as e:
			self.logger.error('Could not create torrent client: {0}'.format(e))
			return None

		if torrentClient == None:
			self.logger.error('No client was configured to monitor!')
			return None


	def checkSubDirectoryFreeSpace(self):
		# Check for freespace in each directory
		# Collect all the active destinations

		destinations = []
		for torrent in self.torrentClient.getQueue():
			if torrent['downloadDir'] not in destinations:
				destinations.append(torrent['downloadDir'])

		# Check each destination for free space
		for destination in destinations:
			if platform.system() == 'Windows':
				destination = 'U:'

			while FreeSpace.check(destination,'M') < settings['minimumFreeSpace']:

				finishedTorrents = self.torrentClient.getFinishedSeeding()
				if len(finishedTorrents) <= 0:
					break

				while len(finishedTorrents) > 0:

					self.logger.info('Freeing up space in destination: [{0}|{1}]'.format(
						destination,
						FreeSpace.check(destination,'M'))
					)

					# Stop a finished torrent
					finishedTorrent = finishedTorrents.pop()
					self.torrentClient.deleteTorrent(
						hashString=finishedTorrent['hashString'],
						reason='Freespace Needed (minimumFreeSpace)'
					)

				self.torrentClient.updateQueue()


	def checkMainDirectoryFreeSpace(self):
		# Check for used space in master dir

		if settings['maxUsedSpace'] > 0:
			while int(UsedSpace.check(settings['files']['maxUsedSpaceDir'],'G')) >= int(settings['maxUsedSpace']):

				finishedTorrents = self.torrentClient.getFinishedSeeding()
				if len(finishedTorrents) <= 0:
					break

				while len(finishedTorrents) > 0:

					self.logger.info('Freeing up space in destination: [{0}|{1}]'.format(
						UsedSpace.check(settings['files']['maxUsedSpaceDir'],'G'),
						settings['maxUsedSpace'])
					)

					# Stop a finished torrent
					finishedTorrent = finishedTorrents.pop()

					self.torrentClient.deleteTorrent(hashString=finishedTorrent['hashString'],reason='Freespace Needed (maxUsedSpace)')

				self.torrentClient.updateQueue()


	def checkQueueSize(self):
		# Ensure there are not too many torrents running

		while len(self.torrentClient.getQueue()) > settings['queueManagement']['maxTorrents']:

			finishedTorrents = self.torrentClient.getFinishedSeeding()

			if len(finishedTorrents) <= 0:
				break

			while len(finishedTorrents) > 0:

				self.logger.info('Too many torrents are running, trying to remove one {0}/{1}'.format(
					settings['queueManagement']['maxTorrents'],
					len(self.torrentClient.getQueue())
				))

				# Stop a finished torrent
				finishedTorrent = finishedTorrents.pop()

				self.torrentClient.deleteTorrent(hashString=finishedTorrent['hashString'],reason='Too Many Torrents Running')

			self.torrentClient.updateQueue()


	def checkFinishedTorrents(self):
		# Remove Finished torrents is strict queue management is enabled

		while settings['queueManagement']['strictQueueManagement'] and len(self.torrentClient.getFinishedSeeding()) > 0:
			finishedTorrents = self.torrentClient.getFinishedSeeding()

			if len(finishedTorrents) <= 0:
				break

			self.logger.info('Strict Queue Management is enabled, stopping {0} finished torrents.'.format(len(finishedTorrents)))

			for finishedTorrent in finishedTorrents:
				self.torrentClient.deleteTorrent(hashString=finishedTorrent['hashString'], reason='Strict Queue Management Enabled and Torrent Finished')

			self.torrentClient.updateQueue()


	def addTorrents(self):

		# Add torrents if there is room
		while ( len(self.torrentClient.getQueue()) < settings['queueManagement']['maxTorrents'] and
				len(self.database.getQueuedTorrents(selectors=['url', 'feedDestination'],num=1)) > 0 and
				len(self.torrentClient.getDownloading()) < settings['queueManagement']['maxDownloadingTorrents'] and
				(
					int(UsedSpace.check(settings['files']['maxUsedSpaceDir'],'G')) < int(settings['maxUsedSpace']) or
					int(settings['maxUsedSpace']) == 0
				)
			):

			queuedTorrents = self.database.getQueuedTorrents(selectors=['url', 'feedDestination'])

			self.logger.info('There are {0} queued torrents, let\'s add them'.format(
				len(queuedTorrents)
			))

			# Get a new torrent
			newTorrent = queuedTorrents.pop()

			# Add new torrent
			# If a destination was not specified then don't pass one
			self.logger.info('Adding: {0}'.format(newTorrent))
			if newTorrent.get('feedDestination', None) is None:
				self.torrentClient.addTorrentURL(newTorrent['url'])
			else:
				self.torrentClient.addTorrentURL(newTorrent['url'],newTorrent['feedDestination'])

			self.torrentClient.updateQueue()


	def addTorrentsAndRemoveFinished(self):

		# Remove a finished torrent if room is needed to add a torrent
		while ( len(self.torrentClient.getQueue()) >= settings['queueManagement']['maxTorrents'] and
				len(self.database.getQueuedTorrents(selectors=['url', 'feedDestination'],num=1)) > 0 and
				len(self.torrentClient.getDownloading()) < settings['queueManagement']['maxDownloadingTorrents'] and
				(
					int(UsedSpace.check(settings['files']['maxUsedSpaceDir'],'G')) < int(settings['maxUsedSpace']) or
					int(settings['maxUsedSpace']) == 0
				)
			   ):

			queuedTorrents = self.database.getQueuedTorrents(selectors=['url', 'feedDestination'])
			dormantSeeds = self.torrentClient.getDormantSeeds()
			slowSeeds = self.torrentClient.getSlowestSeeds()

			if len(dormantSeeds) <= 0 and len(slowSeeds) <= 0:
				break

			self.logger.info('There are {0} queued torrents, let\'s make room and add them'.format(
				len(queuedTorrents)
			))


			while ( (
						len(dormantSeeds) > 0 or
						len(slowSeeds) > 0
					) and
						len(queuedTorrents) > 0
					):


				# Try to grab an old dormant seed
				if len(dormantSeeds) > 0:
					slowestFinishedSeed = dormantSeeds.pop()

				# Else get a slow seed
				else:
					slowestFinishedSeed = slowSeeds.pop()


				# Remove slow seed
				if self.torrentClient.deleteTorrent(hashString=slowestFinishedSeed['hashString'], reason='Making Room For a New Torrent'):

					# Get a new torrent
					newTorrent = queuedTorrents.pop()


					# Add new torrent
					# If a destination was not specified then don't pass one
					if newTorrent.get('feedDestination', None) is None:
						self.torrentClient.addTorrentURL(newTorrent['url'])
					else:
						self.torrentClient.addTorrentURL(newTorrent['url'],newTorrent['feedDestination'])

			self.torrentClient.updateQueue()


def __queueReader():
	'''
	Connects to the rpc daemon and attempts to manange the queue

	Steps:
		Update queue list
		Checks for freespace on feedDestinations
		Checks to see if torrents need to be stopped so new ones can be added
		Check for strict queue management and stop finished torrents if enabled
		Checks for broken torrents and removes them
	'''
	logger.info('QueueDaemon Started')


	queueReader = QueueReader()

	queueReader.checkSubDirectoryFreeSpace()
	queueReader.checkMainDirectoryFreeSpace()
	queueReader.checkQueueSize()
	queueReader.checkFinishedTorrents()
	queueReader.addTorrents()
	queueReader.addTorrentsAndRemoveFinished()


	logger.debug('Downloading: {0} | Seeding: {1} | Total: {2}'.format(
		len(queueReader.torrentClient.getDownloading()),
		len(queueReader.torrentClient.getSeeding()),
		len(queueReader.torrentClient.getQueue())
	))

	logger.info('Loop Stopped {0}'.format(strftime('%Y-%m-%d %H:%M:%S', gmtime())))

	# Put the app to sleep
	time.sleep(settings['queueDaemonThreadSleep'])


def main():
	'''
	Main entry point for the Application
	TODO: Implement threading or multiprocessing
	'''

	with daemon.DaemonContext(
		files_preserve = [
			logging.getFileHandle(__name__).stream
		]
	):
		while True:

			try:
				__queueReader()

			except KeyboardInterrupt as e:
				logger.warning('Application Aborted')
				break

			except Exception as e:
				logger.error('Application Stopped {0}\nTrace: {1}'.format(e, traceback.format_exc() ))

				# Sleep for 10 seconds to give a bit of time for the error to try and resolve itself
				# This is mainly related to the occurance of an error that can be generated randomly
				#   [Errno 11] Resource temporarily unavailable
				time.sleep(10)

	logger.info('Application Exited')


if __name__ == '__main__':
	main()
