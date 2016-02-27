#-------------------------------------------------------------------------------
# Name:        TorrentDB
# Purpose:     These functions handle writing/reading torrent information
#              to/from the sqlite database
#
# TODO: Turn this into a class that can be instantiated as various
#       database types.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-


# flannelfox Includes
import flannelfox
from flannelfox import Settings

# Setup the logging agent
from flannelfox import logging
logger = logging.getLogger(__name__)

import ff_sqlite3




class Databases(object):

    def __init__(self, dbType):
        '''
        Set the database module that should be used
        '''

        if dbType == u'SQLITE3':
            self.Database = ff_sqlite3.Database()
            logger.debug("SQLite3 Database initialized")
            
        else:
            logger.critcal("There was an issue initializing the database. [{0}]{1}".format(dbType, e))


    def addBlacklistedTorrent(self, url, reason='No Reason Given'):
        '''
        Add a torrent to the blacklist

        These torrents are flagged as broken and should be ignored when
        the grabbers are looking for new torrents
        '''
        self.Database.addBlacklistedTorrent(url=url, reason=reason)


    def updateHashString(self, update, using):
        '''
        Update the hashString that the database is holding
        '''

        self.Database.updateHashString(update=update, using=using)


    def addTorrentsToQueue(self, queue):
        '''
        Write the Current Torrent Queue to the database

        Takes a queue of torrents as a parameter
        '''
        return self.Database.addTorrentsToQueue(queue=queue)


    def deleteTorrent(self, hashString=None,url=None,reason='No Reason Given'):
        '''
        Removes a torrent from the database
        
        Takes a torrent as a parameter
        '''
        return self.Database.deleteTorrent(hashString=hashString, url=url, reason=reason)


    def torrentExists(self, torrent=None, url=None, hashString=None):
        '''
        Checks to see if the torrent is already in the database

        Takes:
            A torrent as a parameter OR
            A hashString and url 

        Returns True if it exists or False if it does not
        '''
        return self.Database.torrentExists(torrent=torrent, url=url, hashString=hashString)


    def torrentBlacklisted(self, url=None):
        '''
        Checks to see fi the torrent is blacklisted in the database
        '''

        try:

            if not isinstance(url, str) and not isinstance(url, unicode):
                raise ValueError('url was not a string')

            return self.Database.torrentBlacklisted(url=url)

        except Exception as e:
            logger.error("There was an issue checking if a torrent is blacklisted in the database. {0}".format(e))
            return False



    def execDB(self, query):
        '''
        Executes a query and tries to do any cleanup if there is an issue


        '''
        return self.Database.execDB(query=query)


    def queryDB(self, query):
        '''
        Perform a query on the database, this should not be called directly

        Takes:
            a SQL statement as a parameter
        
        Returns:
            a list of dicts, each dict holding the row information
        '''
        return self.Database.queryDB(query=query)


    def getTorrentInfo(self, hashString=None,fields=[]):
        '''
        Returns the desired information about a torrent

        Takes:
            hashString - The hash of the desired torrent
            fields - List of fields that you want returned

        Returns:
            Dict of key,val
        '''
        return self.Database.getTorrentInfo(hashString=hashString, fields=fields)


    def getQueuedTorrents(self, fields=[],num=None):
        '''
        Returns the desired information about the torrent queue

        Takes:
            fields - List of fields that you want returned
            num - Number of rows to return

        Returns:
            Dict of key,val
        '''
        return self.Database.getQueuedTorrents(fields=fields, num=num)


    def getQueuedTorrentsCount(self):
        '''
        Returns the total number of torrents waiting in queue

        Returns:
            int
        '''
        return self.Database.getQueuedTorrentsCount()
