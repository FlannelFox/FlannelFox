#-------------------------------------------------------------------------------
# Name: 	trakttv.py
# Purpose:	Reads trakttv config files and makes filters out of them.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import os, traceback

# Third party modules
import requests

# Needed to fix an SSL issue with requests
#import urllib3.contrib.pyopenssl
#urllib3.contrib.pyopenssl.inject_into_urllib3()

from flannelfox.settings import settings
from flannelfox.datasources import common
from flannelfox import logging


class trakttvApi():

	logger = logging.getLogger(__name__)

	def __getFeed(self, url, apiKey):

		httpResponse = -1
		traktListResults = []

		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36',
			'Content-Type':'application/json',
			'trakt-api-version':'2',
			'trakt-api-key':apiKey
		}

		try:

			r = requests.get(url, headers=headers, timeout=60)
			httpResponse = r.status_code

			if httpResponse == 200:
				traktListResults = r.json()

			else:

				traktListResults = []
				self.logger.error('There was a problem fetching a trakt list file: {0}'.format(httpResponse))

		except Exception as e:

			self.logger.error('There was a problem fetching a trakt list file: {0}'.format(e))
			traktListResults = []
			httpResponse = -1

		return httpResponse, traktListResults


	def getPublicList(self, apiKey, username, listname):

		httpResponse, traktListResults = self.__getFeed(
			url='{0}/users/{1}/lists/{2}/items'.format(settings['apis']['trakt'], username, listname),
			apiKey=apiKey
		)

		return traktListResults


def getCacheDir():
	return settings['files']['traktCacheDir']


def readTraktTvConfigs(configFolder=settings['files']['traktConfigDir']):
	'''
	Reads the titles and other information from a specified trakt.tv list
	Content-Type:application/json
	trakt-api-version:2
	trakt-api-key:XXXX
	'''

	logger = logging.getLogger(__name__)

	validTypes = ['tv', 'movie']

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
				traktListResults = []
				title = None
				year = None
				feedFilterList = []

				# Make sure our list at least has some basic parts
				if feedList.get('username', None) is None:
					raise ValueError('A trakttv username must be specified')

				if feedList.get('api_key', None) is None:
					raise ValueError('A trakttv api key must be specified')

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

				cacheFileName = os.path.join(getCacheDir(),feedName)

				if common.isCacheStillValid(cacheFileName=cacheFileName):

					traktListResults = common.readCacheFile(cacheFileName)
					logger.debug('Using cache file {} for {}'.format(cacheFileName, feedName))

				else:

					traktapi = trakttvApi()

					traktListResults = traktapi.getPublicList(
						apiKey=feedList.get('api_key'),
						username=feedList.get('username'),
						listname=feedName
					)

					logger.debug('Fetching new data {}'.format(feedName))

					if not isinstance(traktListResults, list) or len(traktListResults) < 1:

						traktListResults = common.readCacheFile(cacheFileName)
						logger.debug('Using cache file {} for {}'.format(cacheFileName, feedName))

						if not isinstance(traktListResults, list) or len(traktListResults) < 1:
							raise ValueError('There was not a valid feed reply nor is there a valid cache for the feed')

					else:

						common.updateCacheFile(cacheFileName=cacheFileName, data=traktListResults)
						logger.debug('Updating cache file {} for {}'.format(cacheFileName, feedName))

				logger.debug('Found {} items from {}'.format(len(traktListResults), feedName))

				# Collect the feeds
				logger.debug('{} contains {} minorFeed(s)'.format(feedName, len(feedList.get('minorFeeds',[]))))

				for minorFeed in feedList.get('minorFeeds',[]):

					try:

						url = minorFeed.get('url','').strip()
						minTime = int(minorFeed.get('minTime','0').strip()) # Hours Int
						minRatio = float(minorFeed.get('minRatio','0.0').strip()) # Ratio Float
						comparison = minorFeed.get('comparison','or').strip() # Comparison String
						minorFeeds.append({'url':url,'minTime':minTime,'minRatio':minRatio,'comparison':comparison})

					except (ValueError, KeyError, TypeError) as e:

						logger.warning('The feed contains an invalid minorFeed:\n{0}'.format(e))
						continue


				feedFilters = feedList.get('filters', [])

				# Loop through each show and append a filter for it
				for item in traktListResults:

					try:

						ruleList = []

						if feedList.get('like', False):
							titleMatchMethod = 'titleLike'

						else:
							titleMatchMethod = 'title'

						if 'show' not in item and feedType == 'tv':
							# This happens if you select the wrong type of media tv/movie
							raise ValueError('Media type is not show, but feed type is tv {0}'.format(title))

						elif 'movie' not in item and feedType == 'movie':
							# This happens if you select the wrong type of media tv/movie
							raise ValueError('Media type is not movie, but feed type is movie {0}'.format(title))

						elif 'show' in item and feedType == 'tv':

							item = item['show']
							title = item['title'].lower().strip().replace(' & ', ' and ')
							for ch in (':', '\\', '\'', ','):
								title = title.replace(ch, '')

						elif 'movie' in item and feedType == 'movie':

							item = item['movie']
							title = item['title'].lower().strip().replace(' & ', ' and ')
							for ch in (':', '\\', '\'', ','):
								title = title.replace(ch, '')

							year = str(item['year']).strip()

						else:
							raise ValueError('Could not use the trakt feed data')


						for filterItem in feedFilters:

							ruleList.append({'key':titleMatchMethod, 'val':title, 'exclude':False})

							if year is not None:
								ruleList.append({'key':'year', 'val':year, 'exclude':False})

							# Load the excludes
							for exclude in filterItem.get('exclude', []):
								for key, val in exclude.items():
									ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':True})

							for include in filterItem.get('include', []):
								for key, val in include.items():
									ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':False})

							feedFilterList.append(ruleList)

					except Exception as e:

						logger.warning('The {file} contains an invalid rule:\n{e}\n{t}'.format(file=configFileName,e=e,t=traceback.format_exc()))
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

				logger.warning('The {file} contains an invalid rule:\n{e}\n{t}'.format(file=configFileName,e=e,t=traceback.format_exc()))
				continue

	return majorFeeds
