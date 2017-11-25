#-------------------------------------------------------------------------------
# Name: 	Settings
# Purpose:  Contains the settings for the application and threads
#
# TODO: Move the reading of config xml into this file
#		Move some setting into external xml file
#		Move the config files to ~/.flannelfox
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import datetime, json, math, time, os

from flannelfox import logging


def getConfigFiles(directory):

	logger = logging.getLogger(__name__)
	configFiles = []

	if os.path.isdir(directory):

		for configFile in os.listdir(directory):
			configFilePath = os.path.join(directory,configFile)

			try:
				if configFile.endswith('.json'):
					configFileJson = __readConfigFile(configFilePath)

					if configFile != None:
						configFiles.append((configFilePath, configFileJson))
			except Exception as e:
				logger.warning('There was a problem reading the a config file\n{}\n{}'.format(
					configFilePath,
					e
				))
				continue

	return configFiles


def __readConfigFile(file):
	# Try to read in the rss lists

	logger = logging.getLogger(__name__)

	try:
		logger.debug('Reading RSS config file: {0}'.format(file))
		with open(file) as rssJson:
			return json.load(rssJson)
	except Exception as e:
		logger.error('There was a problem reading the rss config file\n{0}'.format(e))
		return []

def __getModificationDate(filename):
	'''
	Checks the modification time of the file it is given

	filename: The full path of the file to return the timestamp of.

	Returns the timestamp in seconds since epoch
	'''
	logger = logging.getLogger(__name__)
	try:
		return int(datetime.datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%s'))

	except Exception:
		logger.error('There was a problem getting the timestamp for:\n{0}'.format(filename))
		return -1


def isCacheStillValid(force=False, cacheFileName=None, frequency=360):
	'''
	Used to determine if a cachefile needs to be updated

	force: force an update
	cacheFileName: The full path of the file to check
	frequency: how often the file should be updated in minutes

	Returns Boolean
	'''
	logger = logging.getLogger(__name__)
	try:

		if not os.path.exists(os.path.dirname(cacheFileName)):
			try:
				os.makedirs(os.path.dirname(cacheFileName))
			except OSError: # Guard against race condition
				pass

		lastModified = __getModificationDate(cacheFileName)

		if lastModified == -1:
			return False

		logger.debug('Checking cache: {0} {1}:{2}'.format(cacheFileName, frequency, math.ceil((time.time()/60 - lastModified/60))))

		difference = math.ceil((time.time()/60 - lastModified/60))

		if difference >= frequency:
			logger.debug('Cache update needed')
			return False

		else:
			logger.debug('Cache update not needed')
			return True

	except Exception:
		logger.error('Cache validity for {0} could not be determined'.format(cacheFileName))
		return False


def readCacheFile(cacheFileName):

	logger = logging.getLogger(__name__)

	try:
		logger.debug('Reading cache file for [{0}]'.format(cacheFileName))
		with open(cacheFileName) as cacheFile:
			return json.load(cacheFile)
	except Exception as e:
		logger.error('There was a problem reading a lastfm list cache file: {0}'.format(e))
		return []


def updateCacheFile(force=False, cacheFileName=None, data=None):
	'''
	Used to update cache files for api calls. This is needed so we do not keep
	asking the api servers for the same information on a frequent basis. The
	fault frequency is to ask once an hour.

	force: preform the update regardless of frequency
	location: where to save the file
	frequency: how often to update the file in minutes
	'''

	directory = os.path.dirname(cacheFileName)

	if not os.path.exists(directory):
		os.makedirs(directory)

	logger = logging.getLogger(__name__)

	try:
		logger.debug('Cache update for {0} needed'.format(cacheFileName))
		with open(cacheFileName, 'w') as cache:
			cache.write(json.dumps(data))

	except Exception as e:
		logger.error('There was a problem writing a cache file {0}: {1}'.format(cacheFileName, e))
