#-------------------------------------------------------------------------------
# Name:		rss.py
# Purpose:	 Reads rss config files and makes filters out of them.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

from flannelfox.datasources import common
from flannelfox.settings import settings
from flannelfox import logging


def readRssConfigs(configFolder=settings['files']['rssConfigDir']):
	'''
	Read the RSSFeedConfig file

	rssFilter children are stackable and help to refine the filter

	An empty or non-existant rssFilters will result in all items being a
	match

	Takes the location of the config file as a parameter
	Returns a dict of filters to match torrents with
	'''

	logger = logging.getLogger(__name__)
	logger.debug('Reading RSS Feeds')

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
				feedFilterList = []

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

				# Collect the feeds
				if not isinstance(feedList.get('minorFeeds',[]), list):
					raise ValueError('The minorFeeds value must be an array/list')

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

				# Collect the feedFilters
				feedFilters = feedList.get('filters', [])

				# Loop through each show and append a filter for it
				for filterItem in feedFilters:
					try:

						ruleList = []

						# Load the excludes
						for exclude in filterItem.get('exclude', []):
							for key, val in exclude.items():
								ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':True})

						for include in filterItem.get('include', []):
							for key, val in include.items():
								ruleList.append({'key':key.strip(), 'val':val.strip(), 'exclude':False})

						feedFilterList.append(ruleList)

					except Exception as e:
						logger.warning('The {file} contains an invalid rule:\n{e}'.format(file=configFileName,e=e))
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
