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

from flannelfox.torrentclients import Transmission

# Setup the database object
TorrentDB = Databases(flannelfox.settings['database']['defaultDatabaseEngine'])


class TorrentClient(object):
    '''
    This should be a generic class that torrent clients can extend from and use as a roadmap
    all the functions in here need to be defined in the client module in order for it to work

    TODO: instantiate a class of the given client type based on the config setup. We will
          also need to return it when this is instantiated.

    '''

    def __init__(self, settings={}):

        self.logger = logging.getLogger(__name__)
        self.logger.debug("TorrentClient INIT")        

        if settings['type'] == "transmission":
            self.logger.debug("TorrentClient Settings: {0}".format(settings))
            self.client = Transmission.Client(settings=settings)
        else:
            raise ValueError("Torrent client type not defined!")
            

    def __updateHashString(self, using=None, update=None):
        '''
        TODO: This should be used instead of the function in the Transmission Class
        
        Updates the hash string for a torrent in the database

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
        return self.client.updateQueue()


    def getQueue(self):
        '''
        Returns:
            List [torrents]
        '''
        return self.client.getQueue()


    def verifyTorrent(self,hashString=None):
        '''
        Verifies a corrupted torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        return self.client.verifyTorrent(hashString=hashString)


    def StopTorrent(self,hashString=None):
        '''
        Stops a torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        return self.client.StopTorrent(hashString=hashString)


    def StartTorrent(self, hashString=None):
        '''
        Starts a torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        return self.client.StopTorrent(hashString=hashString)


    def removeBadTorrent(self, hashString=None, reason='No Reason Given'):
        '''
        Removes a torrent from both transmission and the database
        this should be called when there is a bad torrent.

        Takes:
            hashString - Hash of the specific torrent to remove
        '''

        # Remove the torrent from the client
        self.client.removeTorrent(hashString=hashString, deleteData=True, reason=reason)

        # Remove the torrent from the DB
        TorrentDB.deleteTorrent(hashString=hashString, reason=reason)


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
            self.removeTorrent(hashString=hashString, deleteData=False, reason='Duplicate Torrent')

            return True
        else:
            # Remove the torrent from the DB
            # TODO: Perhaps this should be changed to just mark the torrent as added
            #       or blacklisted
            TorrentDB.deleteTorrent(url=url, reason='Duplicate Torrent')

            return True

    def removeTorrent(self, hashString=None, deleteData=False, reason='No Reason Given'):
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
        return self.client.removeTorrent(hashString=hashString, deleteData=deleteData, reason=reason)


    def deleteTorrent(self, hashString=None, reason='No Reason Given'):
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
        return self.client.removeTorrent(hashString=hashString, deleteData=True, reason=reason)


    def addTorrentURL(self, url=None, destination=flannelfox.settings['files']['defaultTorrentLocation']):
        '''
        Attempts to load the torrent at the given url into transmission

        Takes:
            url - url of the torrent file to be added

            destination - where the torrent should be saved

        Returns:
            bool True is action completed successfully
        '''
        self.logger.debug("TorrentClient adding torrent")
        result, response = self.client.addTorrentURL(url=url, destination=destination)

        self.logger.debug("TorrentClient responded with ({0}, {1})".format(result, response))

        if result == 0:

            # Get Current Time
            sinceEpoch = int(time.time())

            # update hash, addedOn, added in DB
            self.__updateHashString(using={u"url":url}, update={u"hashString":response, u"addedOn":sinceEpoch, u"added":1})

            time.sleep(10)

            return True

        elif result == 1:
            # Torrent is broken so lets delete it from the DB, this leaves the opportunity
            # for the torrent to later be added again
            self.removeDupeTorrent(url=url, hashString=response)

            time.sleep(10)

            return False

        elif result == 2:
            TorrentDB.deleteTorrent(url=url, reason=response)

            return False

        elif result == 3:
            TorrentDB.addBlacklistedTorrent(url=url, reason=response)

            return False


    def getSlowestSeeds(self, num=None):
        '''
        Look for the slowest seeding torrents, slowest first

        Takes:
            num - Int, the number of torrent objects to return
        '''
        return self.client.getSlowestSeeds(num=num)


    def getDormantSeeds(self, num=None):
        '''
        Looks for a seeding torrent with the longest time since active, returns
        torrents, oldest first
        '''
        return self.client.getDormantSeeds(num=num)


    def getDownloading(self, num=None):
        '''
        Returns a list of torrents that are downloading

        Takes:
            num - Int, the number of torrents to return
        '''
        return self.client.getDownloading(num=num)


    def getSeeding(self, num=None):
        '''
        Returns a list of torrents that are Seeding

        Takes:
            num - Int, the number of torrents to return
        '''
        return self.client.getSeeding(num=num)

        
    def getFinishedSeeding(self, num=None):
        '''
        Returns a list of torrents that are finished seeding

        Takes:
            num - Int, the number of torrents to return
        '''
        return self.client.getFinishedSeeding(num=num)

            
    def restart(self):
        return self.client.restart()

        
    def start(self):
        return self.client.start()

        
    def stop(self):
        return self.client.stop()
