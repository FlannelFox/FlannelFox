#-------------------------------------------------------------------------------
# Name:        Movie.py
# Purpose:     Parsing rules from Movies. All files that represent movies
#              have title, year, and/or other meta data extracted.
#
# TODO:        Parse titles for multiple episodes and return the nummbers
# TODO:        Add a way to import Regex rules
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re

# FlannelFox Includes
from FlannelFox import Settings
import VideoProperties, SeparatorCharacters

def parseTitle(title):
    '''
    Read the given title and return a dict of valid property matches
    '''

    # Strip all the possible bad prefixes form the string
    # badPrefixRegex = re.compile(ur"(?:"+")|(?:".join(Settings.BAD_PREFIXES)+ur")")
    title = re.sub(ur"(?:"+")|(?:".join(Settings.BAD_PREFIXES)+ur")", "", title, flags=re.IGNORECASE)

    # Meta data sanitization
    for key, val in Settings.KEYWORD_SYNONYMS.iteritems():
        title = re.sub(key, val, title, flags=re.IGNORECASE)

    '''
    List of parsing regex to try and extract data from the file title,
    this list should also be in order of searching preference
    '''
    parsingOrderSingle = [

        # Find Showname.ep00.Meta
        #re.compile(ur"(?P<title>.+?)["+SeparatorCharacters.SeparatorCharactersRegexStr+ur"]+(?P<year>\d{4})["+SeparatorCharacters.SeparatorCharactersRegexStr+"]+(?P<metaData>["+SeparatorCharacters.SeparatorCharactersRegexStr+"]+.*)?$", re.UNICODE)
        re.compile(ur"(?P<title>.+?)["+SeparatorCharacters.SeparatorCharactersRegexStr+ur"]+(?P<year>\d{4})["+SeparatorCharacters.SeparatorCharactersRegexStr+"]+(?P<metaData>.*)", re.UNICODE)
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
    videoProperties = {}

    if "title" in parsedData.groupdict():
        videoProperties["title"] = parsedData.group("title").strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)
        videoProperties["title"] = SeparatorCharacters.SeparatorCharactersRegexCompiled.sub(" ",videoProperties["title"])
        videoProperties["title"] = videoProperties["title"].strip()

        # Strip out some characters that can cause problems matching, this is due to scene naming
        for ch in [u'(',u')',u'[',u']']:
            if ch in videoProperties["title"]:
                videoProperties["title"] = videoProperties["title"].replace(ch, u'')


    if "year" in parsedData.groupdict():
        videoProperties["year"] = parsedData.group("year").strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr)

    # Key and Val are strings
    if "metaData" in parsedData.groupdict():
        for key, val in parseMetaData(parsedData.group("metaData")).iteritems():
            if val is not None:
               videoProperties[unicode(key)] = unicode(val.strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr))

    return videoProperties


def parseMetaData(meta):
    '''
    Try to extract meta data out of the remaining file title and return a dict
    of metadata
    '''
    metaData = {}

    if meta is None:
        return metaData

    for quality in VideoProperties.Quality:
        if quality.lower() in meta.lower():
            metaData["quality"] = unicode(quality)
            break

    for container in VideoProperties.Container:
        if container.lower() in meta.lower():
            metaData["container"] = unicode(container)
            break

    for codec in VideoProperties.Codec:
        if codec.lower() in meta.lower():
            if "codec" not in metaData or len(metaData["codec"]) < len(codec):
                metaData["codec"] = unicode(codec)
                break

    for source in VideoProperties.Source:
        if source.lower() in meta.lower():
            metaData["source"] = unicode(source)
            break

    for proper in VideoProperties.Proper:
        if proper.lower() in meta.lower():
            metaData["proper"] = unicode("true")
            break

    return metaData
