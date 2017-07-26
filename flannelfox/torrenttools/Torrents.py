#-------------------------------------------------------------------------------
# Name:		Torrents.py
# Purpose:
#
# TODO: Fill out a complete purpose for this module
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re, html


# flannelfox Include
from flannelfox import settings

# SceneTools Include
import flannelfox.scenetools.TV
import flannelfox.scenetools.Movie
import flannelfox.scenetools.Music
import flannelfox.scenetools.Ebook


class Generic():
	'''
	Basic Torrent Object
	'''

	elements = {}


	def __init__(self, torrentTitle, url=None, minTime=0, minRatio=0.0, comparison='or', feedDestination=None):
		if not isinstance(torrentTitle, str):
			raise AttributeError(u'torrentTitle must be a string:\n{0}'.format(torrentTitle))

		self.elements = {}

		# Let's make sure double quotes are escaped
		self.elements['torrentType'] = 'none'
		self.elements['torrentTitle'] = torrentTitle.replace('"', '')
		self.elements['title'] = torrentTitle.replace('"', '').lower()
		self.elements['minTime'] = minTime
		self.elements['minRatio'] = minRatio
		self.elements['comparison'] = comparison
		self.elements['feedDestination'] = feedDestination

		if url is not None:
			self.elements['url'] = url

		self.populateProperties(self.elements)


	def __getitem__(self, key):

		# Ensure the key exists
		if key not in self.elements:
			raise KeyError

		return self.elements[key]


	def __setitem__(self, key, val):
		self.elements[key] = val

		# Ensure the value was taken
		if self.elements[key] == val:
			return 0
		else:
			return -1


	def __len__(self):
		return len(self.elements)


	def __iter__(self):
		return self.elements.iter()


	def __contains__(self, element):
		return element in self.elements


	def __str__(self):
		return str(self.elements)


	def __eq__(self, other):
		'''
		Test if two torrents are the same or not
		'''

		for key, val in other.items():
			if key in settings.FUZZY_PROPERTIES:
				continue
			elif key not in self.elements or self.elements[key] != val:
				return False

		return True

	def get(self, key, default=None):
		try:
			return self.__getitem__(key)
		except Exception:
			return default

	def items(self):
		return self.elements.items()


	def keys(self):
		return self.elements.keys()


	def values(self):
		return self.elements.values()


	def filterMatch(self, currentFilters):
		'''
		Checks the current torrent against the passed filters
		Returns True if it is a match, False if it is not
		'''

		# If the filter passed is empty then always return a match
		# This is for feeds that want to pull all torrents and not use filters
		if currentFilters is None or len(currentFilters) < 1:
			return True

		for currentFilterList in currentFilters:

			# Tracks if the torrent makes a complete match with one of the rule
			# sets
			doesMatch = []

			# Check each rule in the set
			for f in currentFilterList:
				# Extract the key, value, and exclude option from data
				key = f["key"]
				val = f["val"]
				exclude = f["exclude"]

				if key == 'wordMatch':
					if val.lower() in self.elements.get('torrentTitle', None).lower():
						if exclude == True:
							doesMatch.append(False)

					else:
						if exclude == False:
							doesMatch.append(False)

				elif key == 'wordMatchStrict':
					if val in self.elements.get('torrentTitle', None):
						if exclude == True:
							doesMatch.append(False)

					else:
						if exclude == False:
							doesMatch.append(False)

				elif key == 'titleLike':
					if val.lower() in self.elements.get('title', None).lower():
						if exclude == True:
							doesMatch.append(False)

					else:
						if exclude == False:
							doesMatch.append(False)

				elif key not in self.elements:
					doesMatch.append(False)

				elif val != self.elements.get(key, None) and exclude == False:
					doesMatch.append(False)

				elif val == self.elements.get(key, None) and exclude == True:
					doesMatch.append(False)

			if not False in doesMatch:
				return True

		return False


	def populateProperties(self, parsedData):
		'''
		Check the parsed data, if valid then populate the properties of the torrent
		'''

		if parsedData is None:
			raise TypeError('The Title given does not appear to be of type: {0}\n{1}'.format(self.elements['torrentType'],self.elements['torrentTitle']))

		# Clean out special characters and things that could cause an issue
		for key, val in parsedData.items():

			# Fix title entries
			if key == 'title':

				# Normalize and, AND, &, ...
				val = re.sub(r'&', r'and', val, flags=re.IGNORECASE)

				# Clean out HTML entities
				val = html.unescape(val)

				# Clean out unneeded punctuation
				val = val.replace('.',' ')
				for ch in (':', '\\', '\'', ','):
					val = val.replace(ch, '')

			self.elements[key] = val


class Music(Generic):
	'''
	Torrent Object Specified to Music
	'''

	def __init__(self, torrentTitle=None, url=None, metaData=None, minTime=0, minRatio=0.0, comparison='or', feedDestination=None):
		if metaData is None:
			super(Music, self).__init__(torrentTitle, url, minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
			self.elements['torrentType'] = 'music'

			# Try to get metadata DICT
			metaData = flannelfox.scenetools.Music.parseTitle(self.elements['title'])

		else:
		   super(Music, self).__init__(metaData['torrentTitle'], metaData['url'], minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
		   self.elements['torrentType'] = 'music'

		self.populateProperties(metaData)


class TV(Generic):
	'''
	Torrent Object Specific to TV Shows
	'''

	def __init__(self, torrentTitle=None, url=None, metaData=None, minTime=0, minRatio=0.0, comparison='or', feedDestination=None):
		if metaData is None:
			super(TV, self).__init__(torrentTitle, url, minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
			self.elements['torrentType'] = 'tv'

			# Try to get metadata DICT
			metaData = flannelfox.scenetools.TV.parseTitle(self.elements['title'])

		else:
		   super(TV, elf).__init__(metaData['torrentTitle'], metaData['url'], minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
		   self.elements['torrentType'] = 'tv'

		self.populateProperties(metaData)


class Movie(Generic):
	'''
	Torrent Object Specific to Movies
	'''

	def __init__(self, torrentTitle=None, url=None, metaData=None, minTime=0, minRatio=0.0, comparison='or', feedDestination=None):

		if metaData is None:
			super(Movie, self).__init__(torrentTitle, url, minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
			self.elements['torrentType'] = 'movie'

			# Try to get metadata Dict
			metaData = flannelfox.scenetools.Movie.parseTitle(self.elements['title'])

		else:
			super(Movie, self).__init__(metaData['torrentTitle'], metaData['url'], minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
			self.elements['torrentType'] = 'movie'

		self.populateProperties(metaData)


class Ebook(Generic):
	'''
	Torrent Object Specific to EBooks
	'''

	def __init__(self, torrentTitle=None, url=None, metaData=None, minTime=0, minRatio=0.0, comparison='or', feedDestination=None):

		if metaData is None:
			super(Ebook, self).__init__(torrentTitle, url, minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
			self.elements['torrentType'] = 'ebook'

			# Try to get metadata Dict
			metaData = flannelfox.scenetools.Ebook.parseTitle(self.elements['title'])

		else:
			super(Ebook, self).__init__(metaData['torrentTitle'], metaData['url'], minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)
			self.elements['torrentType'] = 'ebook'

		self.populateProperties(metaData)


# These are acceptable types in the RSSFeedsConfig File
TORRENT_TYPES = {'tv':TV, 'movie':Movie, 'none':Generic, 'music':Music, 'ebook':Ebook}
