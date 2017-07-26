#-------------------------------------------------------------------------------
# Name:		Music.py
# Purpose:	Parsing rules from Music. The app attempts to separeate the
#			title into artist/album/codec/quality/etc
#
# TODO: Add a way to import Regex rules
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re

# flannelfox Includes
from flannelfox import settings
from flannelfox.scenetools import AudioProperties, SeparatorCharacters

def parseTitle(title):
	'''
	Read the given title and return a dict of valid property matches
	'''

	# Strip all the possible bad prefixes form the string
	# badPrefixRegex = re.compile(r'(?:'+")|(?:".join(settings.BAD_PREFIXES)+r')')
	title = re.sub(r'(?:'+")|(?:".join(settings.BAD_PREFIXES)+r')', "", title, flags=re.IGNORECASE)

	# Meta data sanitization
	for key, val in settings.KEYWORD_SYNONYMS.items():
		title = re.sub(key, val, title, flags=re.IGNORECASE)


	'''
	List of parsing regex to try and extract data from the file title,
	this list should also be in order of searching preference
	'''
	parsingOrderSingle = [

		# Artist - Album [meta] [meta] - meta
		# [meta] is optional, - meta is not
		re.compile(r'(?P<artist>.+?) - (?P<album>.+?)(?: (?P<metaData>(?:(?:\[[^\]]+\]\s)?(?:\[[^\]]+\]\s)?-.*)))$', re.UNICODE),

		# Artist - Album [meta]
		re.compile(r'(?P<artist>.+?) - (?P<album>.+?)(?: (?P<metaData>(?:\[[^\]]+\])))$', re.UNICODE),

		# Artist - Album
		re.compile(r'(?P<artist>.+?) - (?P<album>.+?)$', re.UNICODE)
	]

	# Check each rule and see if there is a match
	for rule in parsingOrderSingle:
		parsedData = rule.match(title)

		# Check if any matches were found
		if parsedData:
			break

	# Check if any pattern matches were found, if not return None
	if parsedData is None:
		return None

	# Use discovered pattern to build a dict to return
	audioProperties = {}

	if "artist" in parsedData.groupdict():
		audioProperties["artist"] = parsedData.group("artist").strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)
		audioProperties["artist"] = SeparatorCharacters.SeparatorCharactersRegexCompiled.sub(" ",audioProperties["artist"])

		# Change amperstands to and
		audioProperties["artist"] = audioProperties["artist"].replace(u" & ", u" and ")

		# Strip white space from beginning and end
		audioProperties["artist"] = audioProperties["artist"].strip()

		# Strip out some characters that can cause problems matching, this is due to scene naming
		for ch in [u'(',u')',u'[',u']', '{', '}']:
			if ch in audioProperties["artist"]:
				audioProperties["artist"] = audioProperties["artist"].replace(ch, u'')

	if "album" in parsedData.groupdict():
		audioProperties["album"] = parsedData.group("album").strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)
		audioProperties["album"] = SeparatorCharacters.SeparatorCharactersRegexCompiled.sub(" ",audioProperties["album"])

		# Change amperstands to and
		audioProperties["album"] = audioProperties["album"].replace(u" & ", u" and ")

		# Strip white space from beginning and end
		audioProperties["album"] = audioProperties["album"].strip()

		# Strip out some characters that can cause problems matching, this is due to scene naming
		for ch in [u'(',u')',u'[',u']', '{', '}']:
			if ch in audioProperties["album"]:
				audioProperties["album"] = audioProperties["album"].replace(ch, u'')

	# Key and Val are strings
	if "metaData" in parsedData.groupdict():
		for key, val in parseMetaData(parsedData.group("metaData")).items():
			if isinstance(val, str):
				audioProperties[key] = val.strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)
			elif val is not None:
				audioProperties[key] = val

	return audioProperties


def parseMetaData(meta):
	'''
	Try to extract meta data out of the remaining file title and return a dict
	of metadata
	'''

	metaData = {}

	if meta is None:
		return metaData

	meta = meta.lower()
	for ch in ('.', '[', ']', '(', ')', '{', '}', '-'):
		meta = meta.replace(ch, ' ')

	meta = ' {0} '.format(meta.strip())

	for quality in AudioProperties.Quality:
		if ' {0} '.format(quality.lower()) in meta:
			metaData["quality"] = quality
			break

	for releaseType in AudioProperties.ReleaseType:
		if ' {0} '.format(releaseType.lower()) in meta:
			if "releaseType" not in metaData or len(metaData["releaseType"]) < len(releaseType):
				metaData["releaseType"] = releaseType
				break

	for codec in AudioProperties.Codec:
		if ' {0} '.format(codec.lower()) in meta:
			if "codec" not in metaData or len(metaData["codec"]) < len(codec):
				metaData["codec"] = codec
				break

	for source in AudioProperties.Source:
		if ' {0} '.format(source.lower()) in meta:
			metaData["source"] = source
			break

	for proper in AudioProperties.Proper:
		if ' {0} '.format(proper.lower()) in meta:
			metaData["proper"] = True
			break

	return metaData
