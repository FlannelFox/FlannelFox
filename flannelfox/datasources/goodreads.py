#-------------------------------------------------------------------------------
# Name:		goodreads.py
# Purpose:	Reads goodreads config files and makes filters out of them.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import traceback, os
import defusedxml.ElementTree as ET

# Third party modules
import requests

# Needed to fix an SSL issue with requests
#import urllib3.contrib.pyopenssl
#urllib3.contrib.pyopenssl.inject_into_urllib3()

from flannelfox.settings import settings
from flannelfox.datasources import common
from flannelfox import logging, tools

class goodreadsApi():

	logger = logging.getLogger(__name__)

	def __getFeed(self, url, apiKey):

		httpResponse = -1
		goodreadsListResults = []

		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'
		}

		params = {
			'key':apiKey
		}

		try:

			r = requests.get(url, headers=headers, params=params, timeout=60)
			httpResponse = r.status_code


			if httpResponse == 200:

				try:

					# Parse the RSS XML and turn it into a json list
					xmlData = tools.changeCharset(r.text, 'utf-8', 'xml')
					xmlData = ET.fromstring(xmlData)
					xmlData = xmlData.find('user')
					authors = xmlData.find('favorite_authors')

					for author in authors.iter('author'):

						try:

							name = author.find('name').text

							if name is not None and name != '':

								name = name.strip()
								name = name.replace(' & ',' and ')
								for ch in (':', '\\', '\'', ','):
									name = name.replace(ch, '')

								goodreadsListResults.append(name)

							else:
								continue

						except Exception:
							continue

				except Exception as e:
					print('There was a problem reading the goodreads xml file:\n-   {0}\n-	{1}'.format(e,traceback.format_exc()))
					self.logger.error('There was a problem reading the goodreads xml file:\n-   {0}\n-	{1}'.format(e,traceback.format_exc()))

			else:
				self.logger.error('There was a problem fetching a goodreads list file: {0}'.format(httpResponse))

		except Exception as e:

			self.logger.error('There was a problem fetching a goodreads list file: {0}'.format(e))
			goodreadsListResults = []
			httpResponse = -1

		self.logger.error('Fetching goodreads list page: [{0}]'.format(httpResponse))

		return (httpResponse, goodreadsListResults)


	def getFavouriteAuthors(self, apiKey, username):
		httpResponse, goodreadsListResults = self.__getFeed(
			url='{0}/user/show/{1}.xml'.format(settings['apis']['goodreads'], username),
			apiKey=apiKey
		)

		return goodreadsListResults


def getCacheDir():
	return settings['files']['goodreadsCacheDir']


def readGoodreadsConfigs(configFolder=settings['files']['goodreadsConfigDir']):
	'''
	Read the authors a user favorites on GoodReads
	Creates a cachefile for the authors and updates it when needed
	Returns a list of authors we want to look for
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
				goodreadsListResults = []
				feedFilterList = []

				# Make sure our list at least has some basic parts
				if feedList.get('username', None) is None:
					raise ValueError('A username must be specified')

				if feedList.get('api_key', None) is None:
					raise ValueError('A api key must be specified')

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

					goodreadsListResults = common.readCacheFile(cacheFileName)
					logger.debug('Using cache file {} for {}'.format(cacheFileName, feedName))

				else:

					goodreadsapi = goodreadsApi()

					goodreadsListResults = goodreadsapi.getFavouriteAuthors(
						apiKey=feedList.get('api_key'),
						username=feedList.get('username'),
					)

					logger.debug('Fetching new data {}'.format(feedName))

					if not isinstance(goodreadsListResults, list) or len(goodreadsListResults) < 1:

						goodreadsListResults = common.readCacheFile(cacheFileName)
						logger.debug('Using cache file {} for {}'.format(cacheFileName, feedName))

						if not isinstance(goodreadsListResults, list) or len(goodreadsListResults) < 1:
							raise ValueError('There was not a valid feed reply nor is there a valid cache for the feed')

					else:

						common.updateCacheFile(cacheFileName=cacheFileName, data=goodreadsListResults)
						logger.debug('Updating cache file {} for {}'.format(cacheFileName, feedName))

				logger.debug('Found {} items from {}'.format(len(goodreadsListResults), feedName))

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

				for item in goodreadsListResults:

					# Loop through each author and append a filter for it
					if (len(feedFilters) > 0):
						for filterItem in feedFilters:

							try:

								ruleList = []

								item = item.lower().strip().replace(' & ', ' and ')

								ruleList.append({'key':'titleLike', 'val':item, 'exclude':False})

								 # Load the excludes
								for exclude in filterItem.get('exclude', []):
									for key, val in exclude.items():
										ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':True})

								for include in filterItem.get('include', []):
									for key, val in include.items():
										ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':False})

								feedFilterList.append(ruleList)
								print(ruleList)

							except Exception as e:
								print('The {file} contains an invalid rule:\n{e}'.format(file=configFileName,e=traceback.format_exc()))
								logger.error('The {file} contains an invalid rule:\n{e}'.format(file=configFileName,e=e))
								continue
					else:
						try:

							item = item.lower().strip().replace(' & ', ' and ')

							feedFilterList.append([{'key':'titleLike', 'val':item, 'exclude':False}])

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
				logger.warning('The {file} contains an invalid rule:\n{e}'.format(file=configFileName,e=e))


	return majorFeeds
