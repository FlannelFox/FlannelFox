#-------------------------------------------------------------------------------
# Name:		SeparatorCharacters
# Purpose:
#
# TODO: Fill out the complete purpose for this module
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import re


'''
list of characters that should be removed from string as they are normally
padding. These are separate as they require escaping in regex.
'''

SeparatorSpecialCharacters = ['.', '|', '-']

# list of characters, should not include regex entries that require escaping
SeparatorCharacters = ['_', ' ']

'''
Convert SeparatorCharacters and pre-escaped SeparatorSpecialCharacters into a
list of Regex ready characters.
'''
SeparatorCharactersRegex = []

for char in SeparatorSpecialCharacters:
	SeparatorCharactersRegex.append('\\{0}'.format(char))

for char in SeparatorCharacters:
	SeparatorCharactersRegex.append(char)

# Compiled SeparatorCharacters
SeparatorCharactersRegexCompiled = re.compile(r'['+r''.join(SeparatorCharactersRegex)+r']+')

# String of chars
SeparatorCharactersRegexStr = r''.join(SeparatorCharactersRegex)
SeparatorCharactersStr = r''.join(SeparatorCharacters)
SeparatorSpecialCharactersStr = r''.join(SeparatorSpecialCharacters)