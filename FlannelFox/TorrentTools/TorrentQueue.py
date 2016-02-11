#-------------------------------------------------------------------------------
# Name:        TorrentQueue
# Purpose:
#
# TODO: Fille out a complete purpose for this module
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# Sytem Includes
import time

# flannelfox Includes
from flannelfox.TorrentTools import Torrents
from flannelfox.databases import Databases
from flannelfox import Settings
import flannelfox

# Setup the database object
TorrentDB = Databases(flannelfox.settings['database']['defaultDatabaseEngine'])

class Queue(object):
    '''
    Used to Track a list of torrents and interact with the torrent database
    '''


    def __init__(self, *args):
        self.elements = list(*args)


    def __getitem__(self,idx):

        # Ensure the index is in the correct range
        if idx < 0 or idx >= len(self.elements):
            raise IndexError(ur'Index out of range')

        return self.elements[idx]


    def __setitem__(self,idx, val):
        self.elements[idx] = val

        # Ensure the value was taken
        if self.elements[idx] == val:
            return 0
        else:
            return -1


    def __len__(self):
        return len(self.elements)


    def __iter__(self):
        return iter(self.elements)


    def __contains__(self,element):
        return element in self.elements


    def append(self, val):

        # Check and see if the value already exists in elements
        if val in self.elements:
            return -1

        # Check and see if the value already exists in DB
        elif TorrentDB.torrentExists(val):
            return -1

        # Append the value to elements
        else:
            self.elements.append(val)

            # Ensure the value was taken
            if val in self.elements:
                return 0
            else:
                return -1


    def writeToDB(self):
        TorrentDB.addTorrentsToQueue(self.elements)


    def __str__(self):
        out = ur''
        for element in self.elements:
            out += u'{0}\n'.format(element)
        return out
