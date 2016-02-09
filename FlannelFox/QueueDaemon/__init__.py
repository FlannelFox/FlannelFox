#!/usr/bin/python2.7
#-------------------------------------------------------------------------------
# Name:        QueueDaemon
# Purpose:     Watches the Transmission Queue, adding adding and removing
#              torrents when appropriate
#
# TODO:        Make this more flexable and able to handle other clients
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import time, sys, platform
from time import gmtime, strftime
import os.path as OsPath

# #############################################################################
# Setup the python path
# #############################################################################
HOME_DIR = OsPath.expanduser(ur'~')

# Location to look for config files and DB, no trailing slash
APP_PATH = HOME_DIR+ur'/tools'

sys.path.append(APP_PATH)
# #############################################################################

# FreeSpace Calculator
from FlannelFox.OSTools import FreeSpace
from FlannelFox.OSTools import UsedSpace

# Transmission Includes
from FlannelFox import Settings
from FlannelFox import TorrentDB
from FlannelFox.TorrentClients import Transmission

def queueReader():
    '''
    Connects to the rpc daemon and attempts to manange the queue

    Steps:
        Update queue list
        Checks for freespace on feedDestinations
        TODO: Checks for torrent errors and attempts to fix them
        TODO: Get list of torrents that have met seeding requirements

        TODO: if len(seeding torrents) > Settings.MAX_TORRENTS:
            Stop (len(seeding torrents) - Settings.MAX_TORRENTS) torrents

        TODO: if Settings.STRICT_QUEUE_MANAGEMENT:
            Remove all torrents that have met seeding requirements

        TODO: Get list of queued torrents, up to Settings.MAX_DOWNLOADING_TORRENTS (x)
            for each queued torrent:
                remove seeding torrent
                add new torrents
    '''

    # ######################################################################
    # Create a transmission client to interact with
    # ######################################################################
    transClient = Transmission.Client(host=Settings.TRANSMISSION_RPC_INFO["host"],
                                            port=Settings.TRANSMISSION_RPC_INFO["port"],
                                            user=Settings.TRANSMISSION_RPC_INFO["user"],
                                            password=Settings.TRANSMISSION_RPC_INFO["password"],
                                            rpcLocation=Settings.TRANSMISSION_RPC_INFO["rpcLocation"],
                                            https=Settings.TRANSMISSION_RPC_INFO["https"]
    )

    while True:
        print "Loop Started {0}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))


        # Torrent Data
        # ["hashString","id","error","errorString","uploadRatio","percentDone","doneDate","activityDate","rateUpload","downloadDir"]

        # ######################################################################
        # Get the initial queue listing
        # ######################################################################
        transmissionResponseCode,httpResponseCode = transClient.updateQueue()

        # ######################################################################
        # TODO: Check for torrent errors and attempts to fix them
        # ######################################################################
        for torrent in transClient.getQueue():
            # Remove torrents that have the following errors

            if (torrent["errorString"] == u"unregistered torrent" or
                torrent["errorString"] == u"unregistered torrent: dupe" or
                torrent["errorString"] == u"unregistered torrent: trump" or
                torrent["errorString"] == u"unregistered torrent: bad file names" or
                torrent["errorString"] == u"unregistered torrent: bad tags" or
                torrent["errorString"] == u"torrent not registered with this tracker" or
                torrent["errorString"] == u"torrent not registered with this tracker, probably deleted. (code 2)" or
                torrent["errorString"] == u"invalid torrent!"):
                transClient.removeBadTorrent(hashString=torrent["hashString"])

            # Error Messages that should be ignored
            elif ("tracker down for scheduled maintenance" in torrent["errorString"]):
                torrent["errorString"] = u''

            # Check torrents that have a corrupt piece
            elif ("please verify local data" in torrent["errorString"]):
                # Ensure a Check is not already in place
                if (torrent["status"] != 0 and 
                    torrent["status"] != 1 and 
                    torrent["status"] != 2):
                    transClient.verifyTorrent(hashString=torrent["hashString"])
                elif torrent["status"] == 0:
                    transClient.StartTorrent(hashString=torrent["hashString"])
                print "Corrupted torrent: {1} STAT: {0}".format(torrent["status"], torrent["hashString"])

            # Report all other errors
            elif torrent["errorString"] != u'':
                print "Error encountered: {0} {1}".format(torrent["hashString"],torrent["errorString"])


        # ######################################################################
        # Check for freespace in each directory
        # Collect all the active destinations
        # ######################################################################
        destinations = []
        for torrent in transClient.getQueue():
            if torrent["downloadDir"] not in destinations:
                destinations.append(torrent["downloadDir"])

        # Check each destination for free space
        for destination in destinations:
            if platform.system() == u"Windows":
                destination = u"U:"

            while FreeSpace.check(destination,u'M') < Settings.MINIMUM_FREE_SPACE:

                finishedTorrents = transClient.getFinishedSeeding()
                if len(finishedTorrents) <= 0:
                    break

                print "{0} Finished Torrents".format(len(finishedTorrents))
                print "Free space is needed {0} | {1}".format(destination,FreeSpace.check(destination,u'M'))

                # Stop a finished torrent
                finishedTorrent = finishedTorrents[0]

                if Settings.DEBUG_LEVEL >= 1:
                    print "Torrent to remove:"
                    print finishedTorrent

                transClient.deleteTorrent(hashString=finishedTorrent["hashString"])

                transClient.updateQueue()



        # ######################################################################
        # Check for used space in master dir
        # ######################################################################
        if Settings.DEBUG_LEVEL >= 10: print "Used Space: {0} | Max Space: {1}".format(UsedSpace.check(Settings.MAX_USED_SPACE_DIR,u'G'),Settings.MAX_USED_SPACE)
        if Settings.MAX_USED_SPACE > 0:
            while int(UsedSpace.check(Settings.MAX_USED_SPACE_DIR,u'G')) >= int(Settings.MAX_USED_SPACE):
                if Settings.DEBUG_LEVEL >= 1: print "Used Space: {0} | Max Space: {1}".format(UsedSpace.check(Settings.MAX_USED_SPACE_DIR,u'G'),Settings.MAX_USED_SPACE)

                finishedTorrents = transClient.getFinishedSeeding()
                if len(finishedTorrents) <= 0:
                    if Settings.DEBUG_LEVEL >= 1: print "There are no finished Seeds to stop"
                    # TODO: If there are no torrents to be removed and we need space,
                    # alert someone
                    break

                # Stop a finished torrent
                finishedTorrent = finishedTorrents[0]

                if Settings.DEBUG_LEVEL >= 1:
                    print "Torrent to remove:"
                    print finishedTorrent

                transClient.deleteTorrent(hashString=finishedTorrent["hashString"])

                transClient.updateQueue()



        # ######################################################################
        # TODO: Ensure there are not too many torrents running
        # ######################################################################
        while len(transClient.getQueue()) > Settings.MAX_TORRENTS:

            finishedTorrents = transClient.getFinishedSeeding()
            if len(finishedTorrents) <= 0:
                break

            if Settings.DEBUG_LEVEL >= 1:
                print "Too many torrents are running, trying to remove one"
                print "=================================================="
                print "# Max Queue: {0}".format(Settings.MAX_TORRENTS)
                print "# Queue: {0}".format(len(transClient.getQueue()))
                print "# Finished Seeding {0}".format(len(finishedTorrents))
                print "=================================================="

            # Stop a finished torrent
            finishedTorrent = finishedTorrents[0]

            if Settings.DEBUG_LEVEL >= 1:
                print "Torrent to remove:"
                print finishedTorrent

            transClient.deleteTorrent(hashString=finishedTorrent["hashString"])

            transClient.updateQueue()



        # ######################################################################
        # TODO: if Settings.STRICT_QUEUE_MANAGEMENT the remove all finished torrents
        # ######################################################################
        while Settings.STRICT_QUEUE_MANAGEMENT and transClient.getFinishedSeeding() > 0:
            finishedTorrents = transClient.getFinishedSeeding()


            if Settings.DEBUG_LEVEL >= 10:
                print "Strict management is enabled, checking for finished torrents"

            if len(finishedTorrents) <= 0:
                break

            # Stop a finished torrent
            print "=================================================="
            print " Finished Seeding: {0}".format(len(finishedTorrents))
            print "=================================================="

            deleteCount = 0
            for finishedTorrent in finishedTorrents:
                transClient.deleteTorrent(hashString=finishedTorrent["hashString"])
                deleteCount += 1

                if Settings.DEBUG_LEVEL >= 1:
                    print "Torrent to remove:"
                    print finishedTorrent

                print "Torrents Deleted: {0}/{1}".format(deleteCount,len(finishedTorrents))

            transClient.updateQueue()



        if Settings.DEBUG_LEVEL >= 10:
                print "Is there room in the queue, {0}".format(len(transClient.getQueue()) < Settings.MAX_TORRENTS)
                print "Are there queued torrents, {0}".format(len(TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'],num=1)) > 0)
                print "Are there too many torrents downloading, {0}".format(len(transClient.getDownloading()) > Settings.MAX_DOWNLOADING_TORRENTS)
                
                print "MAX USED: {0}".format(int(Settings.MAX_USED_SPACE))

                if int(Settings.MAX_USED_SPACE) > 0:
                    print "Is there enough room, {0}".format(int(UsedSpace.check(Settings.MAX_USED_SPACE_DIR,u'G')) < int(Settings.MAX_USED_SPACE))
                else:
                    print "Is there enough room, True"
        # ######################################################################
        # TODO: if there are torrents in the queue and there is room for more
        # to be added then add them till the queue is full
        # ######################################################################
        while ( len(transClient.getQueue()) < Settings.MAX_TORRENTS and
                len(TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'],num=1)) > 0 and
                len(transClient.getDownloading()) < Settings.MAX_DOWNLOADING_TORRENTS and
                (
                    int(UsedSpace.check(Settings.MAX_USED_SPACE_DIR,u'G')) < int(Settings.MAX_USED_SPACE) or
                    int(Settings.MAX_USED_SPACE) == 0
                )
               ):


            print "There are torrents in the Queue"

            serverQueue = transClient.getQueue()
            queuedTorrents = TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'])
            downloadingTorrents = transClient.getDownloading()

            if Settings.DEBUG_LEVEL >= 1:
                print "There is room in the queue for more torrents so let's add them"
                print "=================================================="
                print "# Queue: {0}".format(len(serverQueue))
                print "# Queued Torrents: {0}".format(len(queuedTorrents))
                print "# Downloading Torrents: {0}".format(len(downloadingTorrents))
                print "=================================================="

            # Get a new torrent
            newTorrent = queuedTorrents[0]

            # Add new torrent
            # If a destination was not specified then don't pass one
            if newTorrent.get("feedDestination", None) is None:
                transClient.addTorrentURL(newTorrent["url"])
            else:
                transClient.addTorrentURL(newTorrent["url"],newTorrent["feedDestination"])

            transClient.updateQueue()



        # ######################################################################
        # TODO: if there are finished torrents and queued torrents then remove a
        # finished one and add a new torrent
        # ######################################################################
        while ( len(transClient.getQueue()) >= Settings.MAX_TORRENTS and
                len(TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'],num=1)) > 0 and
                len(transClient.getDownloading()) < Settings.MAX_DOWNLOADING_TORRENTS and
                (
                    int(UsedSpace.check(Settings.MAX_USED_SPACE_DIR,u'G')) < int(Settings.MAX_USED_SPACE) or
                    int(Settings.MAX_USED_SPACE) == 0
                )
               ):

            finishedTorrents = transClient.getFinishedSeeding()
            serverQueue = transClient.getQueue()
            queuedTorrents = TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'])
            downloadingTorrents = transClient.getDownloading()
            dormantSeeds = transClient.getDormantSeeds()

            if len(finishedTorrents) <= 0:
                if Settings.DEBUG_LEVEL >= 10:
                    print "There are no finished torrents to remove."
                break

            if Settings.DEBUG_LEVEL >= 1:
                print "Let's remove a finished seed and add a new torrent"
                print "=================================================="
                print "= Finished Seeding: {0}".format(len(finishedTorrents))
                print "= Queued Torrents: {0}".format(len(queuedTorrents))
                print "=================================================="

            # Try to grab an old dormant seed
            if len(dormantSeeds) > 0:
                slowestFinishedSeed = dormantSeeds
            # Else get a slow seed
            else:
                slowestFinishedSeed = transClient.getSlowestSeeds(num=1)

            slowestFinishedSeed = slowestFinishedSeed[0]
            print slowestFinishedSeed

            # Remove slow seed
            if transClient.deleteTorrent(hashString=slowestFinishedSeed['hashString']):

                # Get a new torrent
                newTorrent = queuedTorrents[0]


                # Add new torrent
                # If a destination was not specified then don't pass one
                if newTorrent.get("feedDestination", None) is None:
                    transClient.addTorrentURL(newTorrent["url"])
                else:
                    transClient.addTorrentURL(newTorrent["url"],newTorrent["feedDestination"])

            transClient.updateQueue()


        if Settings.DEBUG_LEVEL >= 10: print u"HttpCode: {0} | TransmissionCode: {1} | Downloading: {2} | Seeding: {3} | Total: {4}".format(httpResponseCode,transmissionResponseCode,len(transClient.getDownloading()),len(transClient.getSeeding()),len(transClient.getQueue())).encode("utf-8")

        print "Loop Stopped {0}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

        # Put the app to sleep
        time.sleep(Settings.QUEUEDAEMON_THREAD_SLEEP)

def main():
    '''
    Main entry point for the Application
    TODO: Implement threading or multiprocessing
    '''

    try:
        queueReader()

    except KeyboardInterrupt as e:
        if Settings.DEBUG_LEVEL >= 1: print "Application Aborted"

    finally:
        if Settings.DEBUG_LEVEL >= 1: print "Application Exited"

if __name__ == '__main__':
    main()
