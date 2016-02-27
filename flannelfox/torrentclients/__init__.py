#-------------------------------------------------------------------------------
# Name:        torrentclients
# Purpose:     This should be a generic torrent client that other clients
#              can and should extend from in order to keep certain things sane.  
#
# TODO: 
#              Build a base class that other torrent clients can use.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re, json, time


# Third party modules
import requests
# Needed to fix an SSL issue with requests
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# flannelfox Includes
import flannelfox
import Trackers
from flannelfox import Settings
from Torrent import Status as TorrentStatus
from Torrent import Torrent
from flannelfox.databases import Databases

# Setup the logging agent
from flannelfox import logging
logger = logging.getLogger(__name__)

import transmission

# Setup the database object
TorrentDB = Databases(flannelfox.settings['database']['defaultDatabaseEngine'])


class Client(object):
    '''
    This should be a generic class that torrent clients can extend from and use as a roadmap
    all the functions in here need to be defined in the client module in order for it to work

    TODO: instantiate a class of the given client type based on the config setup. We will
          also need to return it when this is instantiated.

    '''


    def __init__(self, host=u"localhost", port=u"9091", user=None, password=None, rpcLocation=None, https=False):
        self.elements = {}
        self.elements["queue"] = []

            
    def __generateTag(self):
        '''
        Generates an int to be used for tag numbers in rpc calls
        '''
        while True:
            for n in xrange(65535):
                yield n


    def updateHashString(self, using=None, update=None):
        '''
        TODO: this was __updateHansString()
        Updated the hash string for a torrent in the database

        Takes:
            using - A list of database properties that are used to identify the
                torrent to be updated

            update - Field to update in the database
        '''
        TorrentDB.updateHashString(update=update, using=using)



    def updateQueue(self):
        '''
        Updates the class variable queue with the latest torrent queue info

        Returns:
            Tuple (transmissionResponseCode, httpResponseCode)
        '''
        pass


    def getQueue(self):
        '''
        Returns:
            List [torrents]
        '''
        return self.elements["queue"]


    def verifyTorrent(self,hashString=None):
        '''
        Verifies a corrupted torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        pass


    def StopTorrent(self,hashString=None):
        '''
        Stops a torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        pass


    def StartTorrent(self,hashString=None):
        '''
        Starts a torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        pass


    def removeBadTorrent(self,hashString=None,reason='No Reason Given'):
        '''
        Removes a torrent from both transmission and the database
        this should be called when there is a bad torrent.

        Takes:
            hashString - Hash of the specific torrent to remove
        '''

        # Remove the torrent from the client
        self.removeTorrent(hashString=hashString,deleteData=True,reason=reason)

        # Remove the torrent from the DB
        TorrentDB.deleteTorrent(hashString=hashString,reason=reason)


    def removeDupeTorrent(self, hashString=None, url=None):
        '''
        Removes a duplicate torrent from transmission if it does not exist
        and is in the database but does in transmission. This is checked via
        the url and the bashString. TODO: Handle hash collision

        Takes:
            hashString - Hash of the specific torrent to remove
            url - Url of the torrent we are adding
        '''

        if not TorrentDB.torrentExists(hashString=hashString, url=url):

            # Remove the torrent from the client
            self.removeTorrent(hashString=hashString,deleteData=False, reason='Duplicate Torrent')

            return True
        else:
            # Remove the torrent from the DB
            # TODO: Perhaps this should be changed to just mark the torrent as added
            #       or blacklisted
            TorrentDB.deleteTorrent(url=url, reason='Duplicate Torrent')

            return True

    def removeTorrent(self,hashString=None,deleteData=False,reason='No Reason Given'):
        '''
        Removes a torrent from transmission

        Takes:
            hashString - Hash of the specific torrent to remove

            deleteData - bool, tells if the torrent data should be removed

            TODO: if hashString is not specified then we should remove the torrent
            that has the longest time since active.

        Returns:
            bool True is action completed
        '''
        pass


    def deleteTorrent(self,hashString=None,reason='No Reason Given'):
        '''
        Removes a torrent from transmission and deletes the associated data

        Takes:
            hashString - Hash of the specific torrent to remove

            TODO: if hashString is not specified then we should remove the torrent
            that has the longest time since active.

        Returns:
            bool True is action completed
        '''

        # Logging is skipped here and put into the removeTorrent function to prevent
        # duplicate logging
        return self.removeTorrent(hashString=hashString,deleteData=True, reason=reason)


    def addTorrentURL(self,url=None,destination=flannelfox.settings['files']['defaultTorrentLocation']):
        '''
        Attempts to load the torrent at the given url into transmission

        Takes:
            url - url of the torrent file to be added

            destination - where the torrent should be saved

        Returns:
            bool True is action completed successfully
        '''
        pass


    def getSlowestSeeds(self,num=None):
        '''
        Look for the slowest seeding torrents, slowest first

        Takes:
            num - Int, the number of torrent objects to return
        '''
        pass


    def getDormantSeeds(self,num=None):
        '''
        Looks for a seeding torrent with the longest time since active, returns
        torrents, oldest first
        '''
        pass


    def getDownloading(self,num=None):
        '''
        Returns a list of torrents that are downloading

        Takes:
            num - Int, the number of torrents to return
        '''
        pass


    def getSeeding(self,num=None):
        '''
        Returns a list of torrents that are Seeding

        Takes:
            num - Int, the number of torrents to return
        '''
        pass

        
    def getFinishedSeeding(self, num=None):
        '''
        Returns a list of torrents that are finished seeding

        Takes:
            num - Int, the number of torrents to return
        '''
        pass

            
    def restart(self):
        pass

        
    def start(self):
        pass

        
    def stop(self):
        pass
