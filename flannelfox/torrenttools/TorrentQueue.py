#-------------------------------------------------------------------------------
# Name:        TorrentQueue
# Purpose:
#
# TODO: Fille out a complete purpose for this module
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# flannelfox Includes
from flannelfox.databases import Databases
from flannelfox.settings import settings

class Queue():
    '''
    Used to Track a list of torrents and interact with the torrent database
    '''

    # Setup the database object
    database = None
    defaultDatabaseType = settings['database']['defaultDatabaseEngine']


    def __init__(self, *args):
        self.elements = list(*args)
        self.database = Databases(
            dbType = self.defaultDatabaseType
        )


    def __getitem__(self, idx):
        # Ensure the index is in the correct range
        if idx < 0 or idx >= len(self.elements):
            raise IndexError('Index out of range')

        return self.elements[idx]


    def __setitem__(self, idx, torrent):
        self.elements[idx] = torrent

        # Ensure the value was taken
        if self.elements[idx] == torrent:
            return 0
        else:
            return -1


    def __len__(self):
        return len(self.elements)


    def __iter__(self):
        return iter(self.elements)


    def __contains__(self, element):
        return element in self.elements


    def databaseTorrentExists(self, torrent):
        return self.database.torrentExists(torrent=torrent)
        #return False


    def databaseTorrentBlacklisted(self, torrent):
        return self.database.torrentBlacklisted(torrent.get('url',''))
        #return False


    def append(self, torrent):

        # Check and see if the value already exists in elements
        if torrent in self.elements:
            return -1

        # Check and see if the value already exists in DB
        elif self.databaseTorrentExists(torrent):
            return -1

        # Ensure it is not Blacklisted
        elif self.databaseTorrentBlacklisted(torrent):
            return -1

        # Append the value to elements
        else:
            self.elements.append(torrent)

            # Ensure the value was taken
            if torrent in self.elements:
                return 0
            else:
                return -1


    def writeToDB(self):
        self.database.addTorrentsToQueue(self.elements)


    def __str__(self):
        out = ''
        for element in self.elements:
            out += u'{0}\n'.format(element)
        return out
