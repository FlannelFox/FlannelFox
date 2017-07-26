# -*- coding: utf-8 -*-
import os, json
import flannelfox.tools
from collections import OrderedDict

if os.environ.get('FF_ROOT', False):
	HOME_DIR = os.environ.get('FF_ROOT')
else:
	HOME_DIR = os.path.expanduser('~')

# #############################################################################
# Special variables to handle formatting names
# #############################################################################

# These are torrentTitle prefixes that should be ignored when creating torrent
# objects. This is mainly to fix rss feeds that have bad file entries in front.
BAD_PREFIXES = [
	'autofill fail',
	'TvHD \d+ \d+',
	'TvSD \d+ \d+'
]


# These are keywords such as sources that come in multiple forms, but need to
# be reconciled into one to make it easier to grab them
# ORDER IS IMPORTANT
KEYWORD_SYNONYMS = OrderedDict([
	('blu\-ray','bluray'),
	('bdrip','bluray'),
	('brrip','bluray'),
	('hd\-dvd','hddvd'),
	('web\-dl','webdl'),
	('web\-rip','webrip'),
	('x264','h264'),
	('h.264','h264'),
	('h264.?hi10p','h264hi10p'),
	('vc\-1','vc1'),
	('v0 ?\(?vbr\)?','v0vbr'),
	('v1 ?\(?vbr\)?','v1vbr'),
	('v2 ?\(?vbr\)?','v2vbr'),
	('v8 ?\(?vbr\)?','v8vbr'),
	('aps ?\(?vbr\)?','apsvbr'),
	('apx ?\(?vbr\)?','apxvbr')
])


# This is a list of properties that are ignored during torrent comparison
FUZZY_PROPERTIES = [

# Properties ignored in a comparison, in order to achieve a preference
# of certain quality then you need to make the source feed "upgradable"
	'quality',
	'source',
	'container',
	'codec',

# Properties ignored due to being related to RSS
	'torrentTitle',
	'url',

# Properties ignored due to being related to storage
	'feedDestination',

# Properties ignored due to being based on ratio/timing
	'addedOn',
	'added',
	'queuedOn',
	'minTime',
	'minRatio',
	'comparison',
	'hashString',

# Properties ignored due to being based on transmission responses
	'id',
	'error',
	'errorString',
	'uploadRatio',
	'percentDone',
	'doneDate',
	'activityDate',
	'rateUpload',
	'downloadDir',
	'seedTime',
	'status'
]

# #############################################################################

settings = {
	'files':{
		'defaultTorrentLocation': os.path.join(HOME_DIR, 'files'),
		'maxUsedSpaceDir': os.path.join(HOME_DIR, 'files'),
		'privateDir': os.path.join(HOME_DIR, '.flannelfox'),
		'configDir': os.path.join(HOME_DIR, '.flannelfox/config'),
		'logDir': os.path.join(HOME_DIR, '.flannelfox/logs'),
		'toolsDir': os.path.join(HOME_DIR, 'tools'),
		'settingsConfigFile': os.path.join(HOME_DIR, '.flannelfox/config/settings.json'),
		'feedConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds'),
		'rssConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/rssfeeds'),
		'lastfmConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/lastfmfeeds'),
		'lastfmCacheDir': os.path.join(HOME_DIR, '.flannelfox/cache/LastfmArtistsConfigCache'),
		'traktConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/traktfeeds'),
		'traktCacheDir': os.path.join(HOME_DIR, '.flannelfox/cache/TraktConfigCache'),
		'goodreadsConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/goodreadsfeeds'),
		'goodreadsCacheDir': os.path.join(HOME_DIR, '.flannelfox/cache/GoodreadsConfigCache')
	},
	'apis':{
		'lastfm':'https://ws.audioscrobbler.com/2.0',
		'trakt':'https://api-v2launch.trakt.tv',
		'goodreads':'https://www.goodreads.com'
	},
	'database':{
		'defaultDatabaseEngine': 'SQLITE3'
	},
	'queueManagement':{
		'maxTorrents': 300,
		'maxDownloadingTorrents': 5,
		'strictQueueManagement': False
	},
	'client':{
		'name': 'transmission-server1',
		'type': 'transmission',
		'host': '127.0.0.1',
		'https': False,
		'port': '9091',
		'rpcLocation': 'transmission/rpc',
		'user': '',
		'password': ''
	},
	'tvTitleMappings': {
		'teen titans go':'teen titans go!',
		'uncle buck':'uncle buck 2016',
		'chicago p d':'chicago p.d.',
		'chicago pd':'chicago p.d.',
		'guardians of the galaxy':'marvels guardians of the galaxy',
		'ultimate spider man vs the sinister 6':'ultimate spider man',
		'marvels ultimate spider man vs the sinister 6':'ultimate spider man',
		'scandal us':'scandal',
		'scandal 2012':'scandal',
		'doctor who':'doctor who 2005',
		'house of cards 2013':'house of cards us',
		'the flash':'the flash 2014',
		'dcs legends of tomorrow':'dc\'s legends of tomorrow',
		'dc s legends of tomorrow':'dc\'s legends of tomorrow',
		'the magicians 2016':'the magicians 2015',
		'the magicians us':'the magicians 2015',
		'law and order special victims unit':'law and order: svu'
	},
	'debugLevel': 'info',
	'minimumFreeSpace': 0,
	'maxUsedSpace': 600,
	'queueDaemonThreadSleep': 60,
	'rssDaemonThreadSleep': 60,
	'maxRssThreads': 8
}


def getSettings():
	return settings


def readSettingsFile(settingsFile=settings['files']['settingsConfigFile']):
	try:
		with open(settingsFile,'r') as importedSettings:
			return importedSettings.read()

	except Exception:
		return '{}'


def updateSettings(settingsFile=settings['files']['settingsConfigFile']):
		importedSettings = readSettingsFile(settingsFile)
		settings = flannelfox.tools.dictMerge(getSettings(), json.loads(importedSettings))


updateSettings()