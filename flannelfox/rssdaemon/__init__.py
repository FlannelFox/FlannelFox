#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# Name:		rssdaemon
# Purpose:	Run in the background and get new torrents from RSS
#			This app will read torrent RSS feeds and pull out the title and
#			other needed data. It will then create a list of torrents that
#			can be returned and write it to the DB.
#
# TODO:		Migrate this to a class so multiple daemons could be run (LOW)
#			Implement multiprocessing for web fetches
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-


# System Includes
import time, re, signal, os, traceback
import defusedxml.ElementTree as ET
from multiprocessing import Pool
from time import gmtime, strftime

# Third party modules
import requests
import daemon

# Needed to fix an SSL issue with requests
#import urllib3.contrib.pyopenssl
#urllib3.contrib.pyopenssl.inject_into_urllib3()

# flannelfox Includes
import flannelfox
from flannelfox import logging
from flannelfox import tools
from flannelfox.settings import settings
import flannelfox.datasources.trakttv, \
		flannelfox.datasources.rss, \
		flannelfox.datasources.goodreads, \
		flannelfox.datasources.lastfm

# rssdaemon Includes
from flannelfox.torrenttools import Torrents, TorrentQueue
from flannelfox.torrenttools.Torrents import TORRENT_TYPES


# TODO: can this be moved?
httpRegex = re.compile(r'https?://([^/]+)(?:/.*)?')

# Setup the logging agent
logger = logging.getLogger(__name__)


def readRSSFeed(url):

	response = ''
	httpCode = None
	encoding = 'utf-8'
	pid = os.getpid()

	try:

		# initialize the responses
		response = None

		# Setup the headers
		headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'}

		# Open the URL and get the data
		r = requests.get(url, headers=headers, timeout=10)
		response = r.content
		httpCode = r.status_code
		encoding = r.encoding
		logger.threadingDebug('[T:{0}] RSS fetch OK URL: [{1}]|[{2}]'.format(pid, httpRegex.match(url).group(1), r.status_code))

	except Exception as e:
		logger.threadingInfo('[T:{0}] There was a problem fetching the URL: [{1}]\n-  {2}'.format(pid, httpRegex.match(url).group(1), e))


	return (response, httpCode, encoding)


def rssToTorrents(xmlData, feedType='none', feedDestination=None, minRatio=0.0, minTime=0, comparison='or'):
	'''
	Read the RSS Feed and return a list of torrent items
	'''

	rssTorrents = []
	pid = os.getpid()

	try:
		if not isinstance(xmlData, bytes):
			raise ValueError('RSS Feed Data is not valid')

		# Parse the RSS XML
		rssItems = ET.fromstring(xmlData)

		# Check for a Channel container
		channel = rssItems.find('channel')

		if channel is not None:
			rssItems = channel

		for rssItem in rssItems.iter('item'):
			try:
				title = rssItem.find('title').text

				if title is not None and title != '':

					title = title.strip()
					title = title.replace(' & ',' and ')

				else:
					continue

			except Exception:
				continue

			# Try to get a link property, if we can't then skip this item
			try:

				link = rssItem.find('link').text.strip()
				link = link.replace(' ', '%20')

				if link is None or link == '':
					continue

			except Exception:
				continue

			# Try to create a torrent from the title
			try:

				torrentItem = TORRENT_TYPES[feedType](torrentTitle=title, url=link, minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)

				if torrentItem is not None:
					rssTorrents.append(torrentItem)

				else:
					raise TypeError('The Title given does not appear to be of type: {0}\n-  {1}'.format(feedType, title))


			except (KeyError) as e:
				logger.threadingInfo('[T:{0}] A valid Feed Type was not specified:\n-  {1}'.format(pid, e))

			except (TypeError, ValueError) as e:
				logger.threadingDebug('[T:{0}] There was a problem creating a torrent:\n-  {1}'.format(pid, e))

			except Exception as e:
				logger.threadingDebug('[T:{0}] There was a problem creating a torrent:\n-  {1}'.format(pid, e))

		rssItems = None

	except (IOError,ValueError,ET.ParseError) as e:
		logger.threadingInfo('[T:{0}]  There was a problem reading the RSS Feed:\n-  {1}'.format(pid, e))

	return rssTorrents


def rssThread(majorFeed):

	error = None
	processed = 0
	pid = os.getpid()

	try:

		rssTorrents = []

		logger.threadingInfo('[T:{0}] Thread Started'.format(pid))

		# This is needed to ensure Keyboard driven interruptions are handled correctly
		# signal.signal(signal.SIGINT, signal.SIG_IGN)

		# Check each feed for a list of possible torrents
		# Set the default type for untyped feeds
		if isinstance(majorFeed['feedType'],str) and majorFeed['feedType'] != '':
			majorFeed['feedType'] = majorFeed['feedType']

		else:
			majorFeed['feedType'] = 'none'

		# Aggregate all the minorFeed items
		for minorFeed in majorFeed['minorFeeds']:

			rssData, httpCode = readRSSFeed(minorFeed['url'])[:2]

			logger.threadingDebug('[T:{0}] Checking URL: {1} [{2}]'.format(pid, httpRegex.match(minorFeed['url']).group(1), httpCode))

			if rssData is None or httpCode != 200:
				continue

			# Ensure data is utf-8
			rssData = tools.changeCharset(rssData, 'utf-8', 'xml')

			# Create a list of torrents from the RSS Feed
			torrents = rssToTorrents(rssData, feedType=majorFeed['feedType'], feedDestination=majorFeed['feedDestination'],minRatio=minorFeed['minRatio'],comparison=minorFeed['comparison'],minTime=minorFeed['minTime'])

			# Update the processed count
			processed += len(torrents)

			for torrent in torrents:
				if torrent.filterMatch(majorFeed['feedFilters']):
					rssTorrents.append(torrent)


				#	logger.debug('Matched Torrent: ')
				#	logger.debug('======================')
				#	logger.debug('{0}'.format(torrent))
				#	logger.debug('======================')
				#else:
				#	logger.debug('UnMatched Torrent: ')
				#	logger.debug('======================')
				#	logger.debug('{0}'.format(torrent))
				#	logger.debug('======================')
				#	logger.debug('{0}'.format(majorFeed['feedFilters']))
				#	logger.debug('======================')


		# Garbage Collection
		minorFeed = rssData = torrents = None

	except Exception as e:

		error = 'ERROR: [T:{0}]: {0}\nException: {1}\nTraceback: {2}'.format(minorFeed['url'],e, traceback.format_exc())
		rssTorrents = []

	logger.threadingInfo('[T:{0}] Thread Done'.format(pid))

	return (pid, rssTorrents, error, processed)


def rssReader():
	'''
	This thread will take care of Processing RSS Feeds
	'''

	logger.info('RSSDaemon Started')

	logger.debug('Pool Created')

	try:
		totalProcessed = 0

		startTime = time.time()

		# Reads the RSSFeedConfig file each loop to ensure new entries are picked up
		# rssFeeds
		majorFeeds = {}

		results = []

		majorFeeds.update(flannelfox.datasources.trakttv.readTraktTvConfigs())
		majorFeeds.update(flannelfox.datasources.lastfm.readLastfmArtistsConfigs())
		majorFeeds.update(flannelfox.datasources.goodreads.readGoodreadsConfigs())
		majorFeeds.update(flannelfox.datasources.rss.readRssConfigs())

		# Holds all the torrents that are in the feeds, filtered, and new
		rssTorrents = TorrentQueue.Queue()


		try:

			logger.info('Pool fetch of RSS Started {0}'.format(strftime('%Y-%m-%d %H:%M:%S', gmtime())))

			with Pool(processes=settings['maxRssThreads'], maxtasksperchild=10) as rssPool:
				for result in rssPool.imap_unordered(rssThread, (f for f in majorFeeds.values())):
					results.append(result)

		except Exception as e:
			logger.error('ERROR: There was an error fetching the RSS Feeds.\n-  {0}'.format(e))


		# Try to get the rssFeeds and return the resutls
		logger.info('Appending items to the queue')

		for result in results:

			#Take each item in the result and append it to the Queue
			pid, torrents, error, processed = result

			if error is not None:
				logger.error('ERROR: There was a problem processing a rss feed:\n-  {0}'.format(error))

			totalProcessed += processed

			logger.debug('Processing results of thread {0}'.format(pid))

			for t in torrents:
				try:
					rssTorrents.append(t)

				except Exception as e:
					logger.error('ERROR: There was a problem appending data to the queue.\n-  {0}'.format(e))

			logger.debug('Finished processing results of thread {0}'.format(pid))

		logger.info('Pool fetch of RSS Done {0} {1} records loaded'.format(strftime('%Y-%m-%d %H:%M:%S', gmtime()), len(rssTorrents)))

		# Log the number of records processed
		logger.info('Processed {0} items in {1:.2f} second(s)'.format(totalProcessed, time.time() - startTime))
		if len(rssTorrents) > 0:
			logger.info('Found {0} new items'.format(len(rssTorrents)))

		# Write matching filters to database
		logger.debug('Writing {0} Torrents to DB'.format(len(rssTorrents)))
		rssTorrents.writeToDB()

		# Garbage collection
		logger.debug('Garbage Collection')
		majorFeeds = rssTorrents = results = result = rssPool = None

	except Exception as e:
		logger.error('ERROR: rssReader Failed {0} {1}\n-  {2}'.format(
			strftime('%Y-%m-%d %H:%M:%S', gmtime()),
			e,
			traceback.format_exc())
		)


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

				logger.critical('rssReader Started')

				while True:
					rssReader()

					# Put the app to sleep
					logger.info('Sleep for a bit')
					time.sleep(settings['rssDaemonThreadSleep'])

			except KeyboardInterrupt as e:

				logger.critical('Application Aborted')
				break

			except Exception as e:

				logger.critical('Application Stopped {0}'.format(e))

				# Sleep for 10 seconds to give a bit of time for the error to try and resolve itself
				# This is mainly related to the occurance of an error that can be generated randomly
				#   [Errno 11] Resource temporarily unavailable
				time.sleep(10)


	logger.critical('Application Exited')


if __name__ == '__main__':
	main()
