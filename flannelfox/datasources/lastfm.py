#-------------------------------------------------------------------------------
# Name:		lastfm.py
# Purpose:	Reads lastfm config files and makes filters out of them.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import os

# Third party modules
import requests

# Needed to fix an SSL issue with requests
#import urllib3.contrib.pyopenssl
#urllib3.contrib.pyopenssl.inject_into_urllib3()

from flannelfox.settings import settings
from flannelfox.datasources import common
from flannelfox import logging


class lastfmApi():

	logger = logging.getLogger(__name__)


	def __getLibraryArtistsFeed(self, apiKey, username):

		currentPage = 1
		maxPages = 1
		httpResponse = -1
		artists = []

		headers = {
			'Content-Type':'application/json',
			'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'
		}

		params = {
			'method':'library.getArtists',
			'api_key': apiKey,
			'user':username,
			'format':'json',
			'page':currentPage
		}

		while currentPage <= maxPages:

			reply = None
			params['page'] = currentPage

			try:

				r = requests.get(settings['apis']['lastfm'], headers=headers, params=params, timeout=60)
				httpResponse = r.status_code
				self.logger.debug('Fetched LastFm album page {0} of {1}: [{2}]'.format(currentPage, maxPages, httpResponse))

				if httpResponse == 200:
					reply = r.json()

				else:
					raise ValueError


			except Exception:
				httpResponse = -1
				logger.error('There was a problem fetching a Lastfm album page\n{0}'.format(httpResponse))
				return artists


			maxPages = int(reply['artists']['@attr']['totalPages'])
			currentPage = currentPage + 1

			artists.extend(
				[artist['name'] for artist in reply['artists']['artist']]
			)

		return (httpResponse, artists)


	def getLibraryArtists(self, apiKey, username):

		httpResponse, artists = self.__getLibraryArtistsFeed(
			username=username,
			apiKey=apiKey
		)

		return artists


def getCacheDir():
	return settings['files']['lastfmCacheDir']


def readLastfmArtistsConfigs(configFolder=settings['files']['lastfmConfigDir']):
	'''
	Read the artists from a users lastfm library.
	Creates a cachefile for the artists and updates it when needed
	Returns a list of artists we want to look for
	'''
	logger = logging.getLogger(__name__)

	majorFeeds = {}

	for configFileName, configFileData in common.getConfigFiles(configFolder):

		logger.debug('Found {} feed(s) in {}'.format(len(configFileData), configFileName))

		for feedList in configFileData:

			try:

				# Setup some variables for the feed
				feedName = None
				feedType = None
				feedDestination = None
				minorFeeds = []
				feedFilters = []
				lastfmListResults = []
				feedFilterList = []

				# Make sure our list at least has some basic parts
				if feedList.get('username', None) is None:
					raise ValueError('A lastfm username must be specified')

				if feedList.get('api_key', None) is None:
					raise ValueError('A lastfm api key must be specified')

				if feedList.get('minorFeeds', None) is None:
					raise ValueError('You must specify one or more minorFeeds')

				# Get the feedName
				feedName = feedList.get('list_name','').lower().strip()

				if feedName == '':
					raise ValueError('Feeds with out names are not permitted')

				# Get the feedType
				feedType = feedList.get('type','none').lower().strip()

				# Get the feedDestination
				feedDestination = feedList.get('feedDestination','').strip()

				if feedDestination == '':
					raise ValueError('The feed has an invalid destination value')
				# TODO: Check if the location exists

				cacheFileName = os.path.join(getCacheDir(), feedName)

				if common.isCacheStillValid(cacheFileName=cacheFileName):

					lastfmListResults = common.readCacheFile(cacheFileName)
					logger.debug('Using cache file {} for {}'.format(cacheFileName, feedName))

				else:

					lastfmapi = lastfmApi()

					lastfmListResults = lastfmapi.getLibraryArtists(
						apiKey=feedList.get('api_key'),
						username=feedList.get('username')
					)

					logger.debug('Fetching new data {}'.format(feedName))

					if not isinstance(lastfmListResults, list) or len(lastfmListResults) < 1:

						lastfmListResults = common.readCacheFile(cacheFileName)
						logger.debug('Using cache file {} for {}'.format(cacheFileName, feedName))

						if not isinstance(lastfmListResults, list) or len(lastfmListResults) < 1:
							raise ValueError('There was not a valid feed reply nor is there a valid cache for the feed')

					else:

						common.updateCacheFile(cacheFileName=cacheFileName, data=lastfmListResults)
						logger.debug('Updating cache file {} for {}'.format(cacheFileName, feedName))

				logger.debug('Found {} items from {}'.format(len(lastfmListResults), feedName))

				logger.debug('{} contains {} minorFeed(s)'.format(feedName, len(feedList.get('minorFeeds',[]))))

				for minorFeed in feedList.get('minorFeeds',[]):

					try:

						url = minorFeed.get('url',''.strip())
						minTime = int(minorFeed.get('minTime','0').strip()) # Hours Int
						minRatio = float(minorFeed.get('minRatio','0.0').strip()) # Ratio Float
						comparison = minorFeed.get('comparison','or').strip() # Comparison String
						minorFeeds.append({'url':url,'minTime':minTime,'minRatio':minRatio,'comparison':comparison})

					except (ValueError, KeyError, TypeError) as e:

						logger.warning('The feed contains an invalid minorFeed:\n{0}'.format(e))
						continue

				feedFilters = feedList.get('filters', [])


				for item in lastfmListResults:

					# Loop through each show and append a filter for it
					for filterItem in feedFilters:

						try:

							ruleList = []

							# Clean the artist name
							item = item.lower().strip().replace(' & ', ' and ')

							ruleList.append({'key':'artist', 'val':item, 'exclude':False})

							# Load the excludes
							for exclude in filterItem.get('exclude', []):
								for key, val in exclude.items():
									ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':True})

							for include in filterItem.get('include', []):
								for key, val in include.items():
									ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':False})

							feedFilterList.append(ruleList)

						except Exception as e:

							logger.error('The {file} contains an invalid rule:\n{e}'.format(file=configFileName,e=e))
							continue

				# Append the Config item to the dict
				majorFeeds['{}.{}'.format(configFileName,feedName)] = {
					'feedName':feedName,
					'feedType':feedType,
					'feedDestination':feedDestination,
					'minorFeeds':minorFeeds,
					'feedFilters':feedFilterList
				}


			except Exception as e:

				logger.error('The {file} contains an invalid rule:\n{e}'.format(file=configFileName,e=e))
				continue


	return majorFeeds
