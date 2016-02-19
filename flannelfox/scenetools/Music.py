#-------------------------------------------------------------------------------
# Name:        Music.py
# Purpose:     Parsing rules from Music. The app attempts to separeate the
#              title into artist/album/codec/quality/etc
#
# TODO: Add a way to import Regex rules
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re

# flannelfox Includes
import flannelfox
from flannelfox import Settings
import AudioProperties, SeparatorCharacters

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
        #Waffles Rule
        re.compile(ur"(?P<artist>.+?) - (?P<album>.+?) (?P<metaData>(?:\[[^\]]+\]))$", re.UNICODE),

        #What.cd Rule
        re.compile(ur"(?P<artist>.+?) - (?P<album>.+?) (?P<metaData>(?:(?:\[[^\]]+\]\s)?(?:\[[^\]]+\]\s)?-.*))$", re.UNICODE),
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
        for ch in [u'(',u')',u'[',u']']:
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
        for ch in [u'(',u')',u'[',u']']:
            if ch in audioProperties["album"]:
                audioProperties["album"] = audioProperties["album"].replace(ch, u'')

    # Key and Val are strings
    if "metaData" in parsedData.groupdict():
        for key, val in parseMetaData(parsedData.group("metaData")).iteritems():
            if val is not None:
               audioProperties[unicode(key)] = unicode(val.strip(SeparatorCharacters.SeparatorCharactersStr+SeparatorCharacters.SeparatorSpecialCharactersStr))

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

    for quality in AudioProperties.Quality:
        if quality.lower() in meta:
            metaData["quality"] = unicode(quality)
            break

    for releaseType in AudioProperties.ReleaseType:
        if releaseType.lower() in meta:
            metaData["releaseType"] = unicode(releaseType)
            break

    for codec in AudioProperties.Codec:
        if codec.lower() in meta:
            if "codec" not in metaData or len(metaData["codec"]) < len(codec):
                metaData["codec"] = unicode(codec)
                break

    for source in AudioProperties.Source:
        if source.lower() in meta:
            metaData["source"] = unicode(source)
            break

    for proper in AudioProperties.Proper:
        if proper.lower() in meta:
            metaData["proper"] = unicode(True)
            break

    return metaData
