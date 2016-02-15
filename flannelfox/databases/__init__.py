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
import ff_sqlite3

class Databases:

    def __init__(self, dbType):
        '''
        Set the database module that should be used
        '''

        if dbType == u'SQLITE3':
            self.Database = ff_sqlite3.Database()
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.INFO: print "SQLite3 Database initialized"
        else:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue initializing the database. [{0}]{1}".format(dbType, e)


    def addBlacklistedTorrent(self, url, reason='No Reason Given'):
        '''
        Add a torrent to the blacklist

        These torrents are flagged as broken and should be ignored when
        the grabbers are looking for new torrents
        '''
        if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print 'Torrent blacklisted: {0}'.format(reason)
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

        try:
            return self.Database.addTorrentsToQueue(queue=queue)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue adding torrents to the database. {0}".format(e)
            return False

        return True


    def deleteTorrent(self, hashString=None,url=None,reason='No Reason Given'):
        '''
        Removes a torrent from the database
        
        Takes a torrent as a parameter
        '''
        try:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.INFO: print 'Torrent deleted from database: {0}'.format(reason)
            return self.Database.deleteTorrent(hashString=hashString, url=url, reason=reason)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue deleting a torrent from the database. {0}".format(e)


    def torrentExists(self, torrent=None, url=None, hashString=None):
        '''
        Checks to see if the torrent is already in the database

        Takes:
            A torrent as a parameter OR
            A hashString and url 

        Returns True if it exists or False if it does not
        '''
       
        try:
            return self.Database.torrentExists(torrent=torrent, url=url, hashString=hashString)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue checking if a torrent exists in the database. {0}".format(e)
            return False


    def torrentBlacklisted(self, url=None):
        '''
        Checks to see fi the torrent is blacklisted in the database
        '''

        try:

            if not isinstance(url, str) and not isinstance(url, unicode):
                raise ValueError('url was not a string')

            return self.Database.torrentBlacklisted(url=url)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue checking if a torrent is blacklisted in the database. {0}".format(e)
            return False



    def execDB(self, query):
        '''
        Executes a query and tries to do any cleanup if there is an issue


        '''

        try:
            return self.Database.execDB(query=query)
                
        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue executing a database execution. {0}".format(e)
            return 0


    def queryDB(self, query):
        '''
        Perform a query on the database, this should not be called directly

        Takes:
            a SQL statement as a parameter
        
        Returns:
            a list of dicts, each dict holding the row information
        '''

        try:
            return self.Database.queryDB(query=query)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue executing a database query. {0}".format(e)
            return {}


    def getTorrentInfo(self, hashString=None,fields=[]):
        '''
        Returns the desired information about a torrent

        Takes:
            hashString - The hash of the desired torrent
            fields - List of fields that you want returned

        Returns:
            Dict of key,val
        '''

        try:
            return self.Database.getTorrentInfo(hashString=hashString, fields=fields)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue getting torrent information. {0}".format(e)
            return {}


    def getQueuedTorrents(self, fields=[],num=None):
        '''
        Returns the desired information about the torrent queue

        Takes:
            fields - List of fields that you want returned
            num - Number of rows to return

        Returns:
            Dict of key,val
        '''

        try:
            return self.Database.getQueuedTorrents(fields=fields, num=num)

        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue getting queued torrents. {0}".format(e)
            return []


    def getQueuedTorrentsCount(self):
        '''
        Returns the total number of torrents waiting in queue

        Returns:
            int
        '''

        try:
            return self.Database.getQueuedTorrentsCount()
        except Exception as e:
            if flannelfox.settings['debugLevel'] >= flannelfox.debuglevels.ERROR: print "There was an issue getting a queued torrent count. {0}".format(e)
            return -1
