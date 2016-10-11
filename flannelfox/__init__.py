#-------------------------------------------------------------------------------
# Name:        flannelfox
# Purpose:     Main module
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import os, json

class debuglevels(object):
    '''
    This is a class that allows for easy and reliable access to the debug level
    the user would like to use as specified in the config file.

    Usage:
    import debuglevels from flannelfox
    debuglevels.getLevel()


    '''

    CRITICAL=50
    ERROR=40
    WARNING=30
    INFO=20
    THREADINGINFO=15
    DEBUG=10
    THREADINGDEBUG=5
    NOTSET=0

    levelStrings = {
        "CRITICAL": 50,
        "ERROR": 40,
        "WARNING": 30,
        "INFO": 20,
        "THREADINGINFO": 15,
        "DEBUG": 10,
        "THREADINGDEBUG": 5,
        "NOTSET": 0,
        "50": 50,
        "40": 40,
        "30": 30,
        "20": 20,
        "15": 15,
        "10": 10,
        "5": 5,
        "0": 0
    }

    @classmethod
    def __sanitizeLevel(cls, lvl="NOTSET"):
        '''
        Makes sure the level returned is consistent
        '''
        if lvl == "":
            lvl="NOTSET"
        return lvl.upper()

    @classmethod
    def getLevel(cls):
        lvl = settings["debugLevel"]
        lvl = cls.__sanitizeLevel(lvl)
        return cls.levelStrings[lvl]


# Initial Setup, these must be at the top
HOME_DIR = os.path.expanduser(ur'~')
settings = {
    'files':{
        'defaultTorrentLocation': os.path.join(HOME_DIR, 'files'),
        'maxUsedSpaceDir': os.path.join(HOME_DIR, 'files'),
        'privateDir': os.path.join(HOME_DIR, '.flannelfox'),
        'configDir': os.path.join(HOME_DIR, '.flannelfox/config'),
        'toolsDir': os.path.join(HOME_DIR, 'tools'),
        'settingsConfigFile': os.path.join(HOME_DIR, '.flannelfox/config/settings.json'),
        'feedConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds'),
        'rssConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/rssfeeds'),
        'lastfmConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/lastfmfeeds'),
        'lastfmCacheDir': os.path.join(HOME_DIR, '.flannelfox/config/LastfmArtistsConfigCache'),
        'traktConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/traktfeeds'),
        'traktCacheDir': os.path.join(HOME_DIR, '.flannelfox/config/TraktConfigCache'),
        'goodreadsConfigDir': os.path.join(HOME_DIR, '.flannelfox/config/feeds/goodreadsfeeds'),
        'goodreadsCacheDir': os.path.join(HOME_DIR, '.flannelfox/config/GoodreadsConfigCache')
    },
    'apis':{
        'lastfm':'https://ws.audioscrobbler.com/2.0/',
        'trakt':'https://api-v2launch.trakt.tv',
        'goodreads':'https://www.goodreads.com/'
    },
    'database':{
        'defaultDatabaseEngine': 'SQLITE3'
    },
    "queueManagement":{
        "maxTorrents": 300,
        "maxDownloadingTorrents": 5,
        "strictQueueManagement": False
    },
    "client":{
        "name": "transmission-server1",
        "type": "transmission",
        "host": "127.0.0.1",
        "https": False,
        "port": "9091",
        "rpcLocation": "transmission/rpc",
        "user": "",
        "password": ""
    },
    "debugLevel": "info",
    "minimumFreeSpace": 0,
    "maxUsedSpace": 600,
    "queueDaemonThreadSleep": 60,
    "rssDaemonThreadSleep": 60,
    "maxRssThreads": 8
}

# Setup the logging agent
from flannelfox import logging
logger = logging.getLogger(__name__)

def update(a, b):
    '''
    updates a with b recursively
    '''
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                update(a[key], b[key])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


try:
    with open(settings['files']['settingsConfigFile'],'r') as config:
        settings = update(settings, json.load(config))
        logger.info('External settings file found')
except Exception as e:
    logger.warning('Could not load external settings file: {0}'.format(e))

import Settings