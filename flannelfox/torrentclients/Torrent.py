#-------------------------------------------------------------------------------
# Name:         Torrent
# Purpose:      This module is a generic torrent module that clients should use
#               when trying to describe torrents. Status can be added as needed.
#
# 
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# System Includes
import time
import flannelfox
from flannelfox.databases import Databases

# Setup the database object
TorrentDB = Databases(flannelfox.settings['database']['defaultDatabaseEngine'])


class Status(object):
    Paused = 0
    QueuedForVerification = 1
    Verifying = 2
    QueuedForDownloading = 3
    Downloading = 4
    QueuedForSeeding = 5
    Seeding = 6


class Torrent(object):

    def __init__(   self,
                    hashString=None,
                    id=None,
                    error=None,
                    errorString=None,
                    uploadRatio=None,
                    percentDone=None,
                    doneDate=None,
                    activityDate=None,
                    rateUpload=None,
                    downloadDir=None,
                    status=-1,
                    **kwargs):

        '''
        status
        # 0 - paused
        # 1 - queued for downloading
        # 2 - verifying
        # 3 - queued for downloading
        # 4 - downloading
        # 5 - queued for seeding
        # 6 - seeding
        '''

        self.elements = {}
        self.elements["hashString"] = hashString
        self.elements["id"] = id
        self.elements["error"] = error
        self.elements["errorString"] = errorString
        self.elements["uploadRatio"] = uploadRatio
        self.elements["percentDone"] = percentDone
        self.elements["doneDate"] = doneDate
        self.elements["activityDate"] = activityDate
        self.elements["rateUpload"] = rateUpload
        self.elements["downloadDir"] = downloadDir
        self.elements["minTime"] = None
        self.elements["minRatio"] = None
        self.elements["seedTime"] = None
        self.elements["comparison"] = None
        self.elements["status"] = status

        for key,val in kwargs:
            self.elements[key] = unicode(val)

    def __getitem__(self,key):
        # Ensure the key exists
        if key not in self.elements:
            raise KeyError

        return self.elements[key]


    def __setitem__(self, key, val):
        self.elements[key] = val

        # Ensure the value was taken
        if self.elements[key] == val:
            return 0
        else:
            return -1


    def __len__(self):
        return len(self.elements)


    def __iter__(self):
        return self.iterkeys()


    def __contains__(self,element):
        return element in self.elements


    def __eq__(self,other):
        for key, val in other.iteritems():
            if key not in self.elements or self.elements[key] != val:
                return False
        return True


    def __unicode__(self):
        output = "========================================\n"
        for key, val in self.elements.iteritems():
            output += "= "+unicode(key)+": ["+unicode(val)+"]\n"
        output += "========================================\n"
        return output


    def __str__(self):
        return unicode(self).encode("utf-8")


    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default


    def iteritems(self):
        return self.elements.iteritems()


    def iterkeys(self):
        return self.elements.iterkeys()


    def itervalues(self):
        return self.elements.itervalues()


    def isFinished(self):

        # Query the DB to get stats
        hashString = self.elements["hashString"]
        torrentData = TorrentDB.getTorrentInfo(self.elements["hashString"],["title","minTime","minRatio","comparison"])

        # If the torrent was not added by the script it should not be in the
        # database and as such will not have a hashString. This ensures non-scripted
        # torrents are exempt from being auto removed
        if len(torrentData) < 1:
            return False
        # If a torrent was found then use it
        else:
            torrentData = torrentData[0]

        # Convert minTime to seconds
        self.elements["minTime"] = float(torrentData["minTime"])*60*60
        torrentData["minTime"] = float(torrentData["minTime"])*60*60

        # Convert minRatio to float
        self.elements["minRatio"] = float(torrentData["minRatio"])
        torrentData["minRatio"] = float(torrentData["minRatio"])

        # Figure out how long the torrent has been seeding, this is subjective
        # based on the client being on 24/7

        # If self.elemets[u"doneDate"] <= 0 then something when wrong
        if self.elements["doneDate"] <= 0:
            return False

        self.elements["seedTime"] = int(time.time()) - self.elements["doneDate"]
        seedTime = int(time.time()) - self.elements["doneDate"]

        self.elements["comparison"] = torrentData["comparison"]

        # Check for untracked torrents, 0 minRatio and minTime
        if torrentData["minRatio"] <= 0.0 and torrentData["minTime"] <= 0.0:
            return False
        

        # If the and comparison is invoked
        if (
            torrentData["comparison"] == u"and" and
            (torrentData["minTime"] <= seedTime and torrentData["minTime"] > 0.0) and
            (torrentData["minRatio"] <= self.elements["uploadRatio"] and torrentData["minRatio"] > 0.0)
        ):
            return True

        # Otherwise assume this is an or comparison
        elif (
            torrentData["comparison"] != u"and" and 
            (
                (torrentData["minTime"] <= seedTime and torrentData["minTime"] > 0.0) or
                (torrentData["minRatio"] <= self.elements["uploadRatio"] and torrentData["minRatio"] > 0.0)
            )
        ):
            return True

        else:
            return False

    def isSeeding(self):
        if self.elements["status"] in [Status.Seeding, Status.QueuedForSeeding]:
            return True
        return False

    def isDownloading(self):
        if self.elements['status'] in [Status.QueuedForDownloading, Status.Downloading]:
            return True
        return False

    def isPaused(self):
        if self.elements['status'] is Status.Paused:
            return True
        return False        

    def isUploading(self):
        if self.elements["rateUpload"] > 0:
            return True
        return False

    def isDormant(self):
        if self.isSeeding() and not self.isUploading():
            return True
        return False
