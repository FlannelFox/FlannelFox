#-------------------------------------------------------------------------------
# Name:		Ebook.py
# Purpose:	Parsing rules from ebooks. All files that represent ebook
#			have author and title extracted
#
# TODO: Add a way to import Regex rules
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re

# flannelfox Includes
from flannelfox import settings
from flannelfox.scenetools import VideoProperties, SeparatorCharacters


def parseTitle(title):
	'''
	Read the given title and return a dict of valid property matches
	'''

	# Strip all the possible bad prefixes form the string
	title = re.sub(r'(?:'+')|(?:'.join(settings.BAD_PREFIXES)+r')', '', title, flags=re.IGNORECASE)

	# Meta data sanitization
	for key, val in settings.KEYWORD_SYNONYMS.items():
		title = re.sub(key, val, title, flags=re.IGNORECASE)

	'''
	List of parsing regex to try and extract data from the file title,
	this list should also be in order of searching preference
	'''
	parsingOrder = [

		# Find Showname.S00.E00.Meta
		re.compile(r'(?P<title>.+?)$', re.UNICODE)
	]

	# Check each rule and see if there is a match
	for rule in parsingOrder:
		parsedData = rule.match(title)

		return {}

		# Check if any matches were found
		if parsedData and parsedData.group('title') not in ['', None]:
			break

	# Check if any pattern matches were found, if not return None
	if parsedData is None:
		return None


def parseMetaData(meta):
	'''
	Try to extract meta data out of the remaining file title and return a dict
	of metadata
	'''
	meatdata = {'placeHolder':None}

	return metaData
