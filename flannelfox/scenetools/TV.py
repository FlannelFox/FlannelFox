#-------------------------------------------------------------------------------
# Name:		TV.py
# Purpose:	Parsing rules from TV shows. All files that represent tv
#			have season, part, episode and/or other meta data extracted.
#
# TODO:		Parse titles for multiple episodes and return the nummbers
# TODO:     Add a way to import Regex rules
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re

# flannelfox Includes
from flannelfox import settings
from flannelfox.scenetools import VideoProperties, SeparatorCharacters

# Logging
from flannelfox import logging

def parseTitle(title):


	'''
	Read the given title and return a dict of valid property matches
	'''

	# Strip all the possible bad prefixes form the string
	# badPrefixRegex = re.compile(r'(?:'+')|(?:'.join(settings.BAD_PREFIXES)+r')')
	title = re.sub(r'(?:'+r')|(?:'.join(settings.BAD_PREFIXES)+r')', r'', title, flags=re.IGNORECASE)

	# Meta data sanitization
	for key, val in settings.KEYWORD_SYNONYMS.items():
		title = re.sub(key, val, title, flags=re.IGNORECASE)

	# Used to store information on multiple episode instances
	multiData = None


	'''
	List of parsing regex to try and extract data from the file title,
	this list should also be in order of searching preference
	'''
	parsingOrderSingle = [

		# Find Showname.S00.E00.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[sS](?P<season>\d{1,3})[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']*(?:[eE](?P<episode>\d+))+(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# Find Showname.S00.E00A.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[sS](?P<season>\d{1,3})[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']*(?:[eE](?P<episode>\d+[abcde]?))+(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# Find Showname.ep00.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Ee][Pp](?P<episode>\d{1,3})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Ee][Pp](?P<episode>[CcLlXxVvIi]+)(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$',
			)),
			re.UNICODE
		),

		# Find Showname.e00.Meta
		re.compile(
			r''.join((
				r'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Ee](?P<episode>\d{1,3})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),


		# find Showname.0000.00.00.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<year>\d{4})[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<month>\d{2})[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<day>\d{2})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# find Showname.00.00.0000.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<day>\d{2})[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<month>\d{2})[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<year>\d{4})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# find Showname.0x00.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<season>\d+)[Xx](?P<episode>\d+)(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# Find Showname.part00.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Pp][Aa][Rr][Tt][',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']*(?P<episode>\d{1,2})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Pp][Aa][Rr][Tt][',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']*(?P<episode>[CcLlXxVvIi]+)(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# Find Showname.pt00.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Pp][Tt][',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']*(?P<episode>\d{1,2})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[Pp][Tt][',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']*(?P<episode>[CcLlXxVvIi]+)(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		),

		# find Showname.000.Meta
		re.compile(
			r''.join((
				'(?P<title>.+?)[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+(?P<season>\d)(?P<episode>\d{2})(?P<metaData>[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+.*)?$'
			)),
			re.UNICODE
		)
	]

	parsingOrderMultiple = [

		# Find Showname.S00.E00.S00.E00.Meta
		re.compile(
			''.join((
				'[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[sS]\d+[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[eE](\d+)+'
			)),
			re.UNICODE
		),

		# Find Showname.S00.E00.E00.E00.Meta
		re.compile(
			''.join((
				'[',
				SeparatorCharacters.SeparatorCharactersRegexStr,
				']+[eE](\d+)+'
			)),
			re.UNICODE
		)
	]

	# Check each rule and see if there is a match
	for rule in parsingOrderSingle:
		parsedData = rule.match(title)

		# Check if any matches were found
		if parsedData and parsedData.group('title') not in ['', None]:
			break

	# Check if any pattern matches were found, if not return None
	if parsedData is None:
		return None


	'''
	TODO: Multiple episode pattern checking

	# See if we need to check for multiple episodes
	if 'season' in parsedData.groupdict():
		# Check for season multi
		for rule in parsingOrderMultiple:
			multiData = rule.findall(title)

			if multiData:
				break

	elif 'episode' in parsedData.groupdict():
		# Check for episode multi
		pass
	'''


	# Use discovered pattern to build a dict to return
	videoProperties = {}

	if 'title' in parsedData.groupdict():
		videoProperties['title'] = parsedData.group('title').strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)
		videoProperties['title'] = SeparatorCharacters.SeparatorCharactersRegexCompiled.sub(' ', videoProperties['title'])

		# Change amperstands to and
		videoProperties['title'] = videoProperties['title'].replace(u' & ', u' and ')

		# Strip white space from beginning and end
		videoProperties['title'] = videoProperties['title'].strip()

		# String year in parenthesis from end of title
		videoProperties['title'] = re.sub(r'(.+) \([\d]+\)$', r'\1', videoProperties['title'])

		# Strip out some characters that can cause problems matching, this is due to scene naming
		for ch in [u'(', u')', u'[', u']', '{', '}']:
			if ch in videoProperties['title']:
				videoProperties['title'] = videoProperties['title'].replace(ch, u'')

		if 'tvTitleMappings' in settings.settings:
			videoProperties['title'] = settings.settings['tvTitleMappings'].get(videoProperties['title'].lower(), videoProperties['title'])

	if 'episode' in parsedData.groupdict():
		if multiData: # if there is multiple episodes then collapse them into a single csv
			videoProperties['episode'] = u','.join(multiData)
		else:
			videoProperties['episode'] = parsedData.group('episode').strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr).lstrip('0')

	if 'season' in parsedData.groupdict():
		videoProperties['season'] = parsedData.group('season').strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr).lstrip('0')

	if 'year' in parsedData.groupdict():
		videoProperties['year'] = parsedData.group('year').strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr).lstrip('0')

	if 'month' in parsedData.groupdict():
		videoProperties['month'] = parsedData.group('month').strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr).lstrip('0')

	if 'day' in parsedData.groupdict():
		videoProperties['day'] = parsedData.group('day').strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr).lstrip('0')

	# Key and Val are strings
	if 'metaData' in parsedData.groupdict():
		for key, val in parseMetaData(parsedData.group('metaData')).items():
			if isinstance(val, str):
				videoProperties[key] = val.strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)
			elif val is not None:
				videoProperties[key] = val

	return videoProperties


def extractMultipleSeasonAndEpisode(sne):
	'''
	TODO: use this to dertermine if there are multiple episoded in the file

	Check if the show contains multiple episodes
	'''
	for multiRule in MultiEpisodeRules:
		multiMatch = ''


def parseMetaData(meta):
	'''
	Try to extract meta data out of the remaining file title and return a dict
	of metadata
	'''

	metaData = {}

	if meta is None:
		return metaData

	meta = meta.lower()
	for ch in ('.', '[', ']', '-'):
		meta = meta.replace(ch, ' ')

	meta = ' {0} '.format(meta.strip())

	for quality in VideoProperties.Quality:
		if ' {0} '.format(quality.lower()) in meta:
			if 'quality' not in metaData:
				metaData['quality'] = quality
				break

	for container in VideoProperties.Container:
		if ' {0} '.format(container.lower()) in meta:
			if 'container' not in metaData:
				metaData['container'] = container
				break

	for codec in VideoProperties.Codec:
		if ' {0} '.format(codec.lower()) in meta:
			if 'codec' not in metaData or len(metaData['codec']) < len(codec):
				metaData['codec'] = codec

	for source in VideoProperties.Source:
		if ' {0} '.format(source.lower()) in meta:
			if 'source' not in metaData:
				metaData['source'] = source
				break

	for proper in VideoProperties.Proper:
		if ' {0} '.format(proper.lower()) in meta:
			if 'proper' not in metaData:
				metaData['proper'] = True
				break

	return metaData
