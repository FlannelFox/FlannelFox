#!/usr/bin/python2.7
#-------------------------------------------------------------------------------
# Name:        queuedaemon
# Purpose:     Watches the Transmission Queue, adding adding and removing
#              torrents when appropriate
#
# TODO:        Make this more flexable and able to handle other clients
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import time, sys, platform, os, traceback
from time import gmtime, strftime

# Third party modules
import daemon

import flannelfox

# FreeSpace Calculator
from flannelfox.ostools import FreeSpace
from flannelfox.ostools import UsedSpace

# Logging
from flannelfox import logging

# Transmission Includes
from flannelfox.databases import Databases
from flannelfox.torrentclients import TorrentClient

# Setup the database object
TorrentDB = Databases(flannelfox.settings['database']['defaultDatabaseEngine'])

# Setup the logger.agent
logger = logging.getLogger(__name__)

def __queueReader():
    '''
    Connects to the rpc daemon and attempts to manange the queue

    Steps:
        Update queue list
        Checks for freespace on feedDestinations
        Checks to see if torrents need to be stopped so new ones can be added
        Check for strict queue management and stop finished torrents if enabled
        Checks for broken torrents and removes them
    '''
    logger.info('QueueDaemon Started')

    torrentClient = None

    # ######################################################################
    # Create a transmission client to interact with
    # ######################################################################
    if 'client' not in flannelfox.settings:
        logger.warning('No client was configured to monitor!')
        return

    # Try to create a torrent client instance
    try:
        if flannelfox.settings['client']['type'] == "transmission":
            torrentClient = TorrentClient(settings=flannelfox.settings['client'])
    except Exception as e:
        logger.error("Could not create torrent client: {0}".format(e))
        return

    if torrentClient == None:
        logger.error('No client was configured to monitor!')
        return

    while True:
        logger.info("Loop Started {0}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))


        # Torrent Data
        # ["hashString","id","error","errorString","uploadRatio","percentDone","doneDate","activityDate","rateUpload","downloadDir"]

        # Get the initial queue listing
        transmissionResponseCode, httpResponseCode = torrentClient.updateQueue()



        # Check for freespace in each directory
        # Collect all the active destinations
        destinations = []
        for torrent in torrentClient.getQueue():
            if torrent["downloadDir"] not in destinations:
                destinations.append(torrent["downloadDir"])

        # Check each destination for free space
        for destination in destinations:
            if platform.system() == u"Windows":
                destination = u"U:"

            while FreeSpace.check(destination,u'M') < flannelfox.settings['minimumFreeSpace']:

                finishedTorrents = torrentClient.getFinishedSeeding()
                if len(finishedTorrents) <= 0:
                    break

                logger.info("Freeing up space in destination: [{0}|{1}]".format(destination,FreeSpace.check(destination,u'M')))

                # Stop a finished torrent
                finishedTorrent = finishedTorrents[0]

                torrentClient.deleteTorrent(hashString=finishedTorrent["hashString"],reason='Freespace Needed (minimumFreeSpace)')

                torrentClient.updateQueue()



        # Check for used space in master dir
        if flannelfox.settings['maxUsedSpace'] > 0:
            while int(UsedSpace.check(flannelfox.settings['files']['maxUsedSpaceDir'],u'G')) >= int(flannelfox.settings['maxUsedSpace']):

                finishedTorrents = torrentClient.getFinishedSeeding()
                if len(finishedTorrents) <= 0:
                    break
                
                logger.info("Freeing up space in destination: [{0}|{1}]".format(
                    UsedSpace.check(flannelfox.settings['files']['maxUsedSpaceDir'],u'G'),
                    flannelfox.settings['maxUsedSpace'])
                )


                # Stop a finished torrent
                finishedTorrent = finishedTorrents[0]

                torrentClient.deleteTorrent(hashString=finishedTorrent["hashString"],reason='Freespace Needed (maxUsedSpace)')

                torrentClient.updateQueue()



        # Ensure there are not too many torrents running
        while len(torrentClient.getQueue()) > flannelfox.settings['queueManagement']['maxTorrents']:

            finishedTorrents = torrentClient.getFinishedSeeding()

            if len(finishedTorrents) <= 0:
                break

            logger.info("Too many torrents are running, trying to remove one {0}/{1}".format(
                flannelfox.settings['queueManagement']['maxTorrents'],
                len(torrentClient.getQueue())
            ))

            # Stop a finished torrent
            finishedTorrent = finishedTorrents[0]

            torrentClient.deleteTorrent(hashString=finishedTorrent["hashString"],reason='Too Many Torrents Running')

            torrentClient.updateQueue()

        # Remove Finished torrents is strict queue management is enabled
        while flannelfox.settings['queueManagement']['strictQueueManagement'] and len(torrentClient.getFinishedSeeding()) > 0:
            finishedTorrents = torrentClient.getFinishedSeeding()

            if len(finishedTorrents) <= 0:
                break

            logger.info('Strict Queue Management is enabled, stopping {0} finished torrents.'.format(len(finishedTorrents)))

            deleteCount = 0

            for finishedTorrent in finishedTorrents:
                torrentClient.deleteTorrent(hashString=finishedTorrent["hashString"], reason='Strict Queue Management Enabled and Torrent Finished')
                deleteCount += 1

            torrentClient.updateQueue()

        # Add torrents if there is room
        while ( len(torrentClient.getQueue()) < flannelfox.settings['queueManagement']['maxTorrents'] and
                len(TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'],num=1)) > 0 and
                len(torrentClient.getDownloading()) < flannelfox.settings['queueManagement']['maxDownloadingTorrents'] and
                (
                    int(UsedSpace.check(flannelfox.settings['files']['maxUsedSpaceDir'],u'G')) < int(flannelfox.settings['maxUsedSpace']) or
                    int(flannelfox.settings['maxUsedSpace']) == 0
                )
               ):


            serverQueue = torrentClient.getQueue()
            queuedTorrents = TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'])
            downloadingTorrents = torrentClient.getDownloading()

            logger.info("There {0} queued torrents, let's add them".format(
                len(queuedTorrents)
            ))

            # Get a new torrent
            newTorrent = queuedTorrents[0]

            # Add new torrent
            # If a destination was not specified then don't pass one
            logger.info("Adding: {0}".format(newTorrent))
            if newTorrent.get("feedDestination", None) is None:
                torrentClient.addTorrentURL(newTorrent["url"])
            else:
                torrentClient.addTorrentURL(newTorrent["url"],newTorrent["feedDestination"])

            torrentClient.updateQueue()



        # Remove a finished torrent if room is needed to add a torrent
        while ( len(torrentClient.getQueue()) >= flannelfox.settings['queueManagement']['maxTorrents'] and
                len(TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'],num=1)) > 0 and
                len(torrentClient.getDownloading()) < flannelfox.settings['queueManagement']['maxDownloadingTorrents'] and
                (
                    int(UsedSpace.check(flannelfox.settings['files']['maxUsedSpaceDir'],u'G')) < int(flannelfox.settings['maxUsedSpace']) or
                    int(flannelfox.settings['maxUsedSpace']) == 0
                )
               ):

            finishedTorrents = torrentClient.getFinishedSeeding()
            serverQueue = torrentClient.getQueue()
            queuedTorrents = TorrentDB.getQueuedTorrents(fields=['url', 'feedDestination'])
            downloadingTorrents = torrentClient.getDownloading()
            dormantSeeds = torrentClient.getDormantSeeds()

            if len(finishedTorrents) <= 0:
                break

            logger.info("There {0} queued torrents, let's make room and add them".format(
                len(queuedTorrents)
            ))

            # Try to grab an old dormant seed
            if len(dormantSeeds) > 0:
                slowestFinishedSeed = dormantSeeds
            # Else get a slow seed
            else:
                slowestFinishedSeed = torrentClient.getSlowestSeeds(num=1)

            slowestFinishedSeed = slowestFinishedSeed[0]

            # Remove slow seed
            if torrentClient.deleteTorrent(hashString=slowestFinishedSeed['hashString'], reason='Making Room For a New Torrent'):

                # Get a new torrent
                newTorrent = queuedTorrents[0]


                # Add new torrent
                # If a destination was not specified then don't pass one
                if newTorrent.get("feedDestination", None) is None:
                    torrentClient.addTorrentURL(newTorrent["url"])
                else:
                    torrentClient.addTorrentURL(newTorrent["url"],newTorrent["feedDestination"])

            torrentClient.updateQueue()


        logger.debug(u"HttpCode: {0} | TransmissionCode: {1} | Downloading: {2} | Seeding: {3} | Total: {4}".format(httpResponseCode,transmissionResponseCode,len(torrentClient.getDownloading()),len(torrentClient.getSeeding()),len(torrentClient.getQueue())).encode("utf-8"))

        logger.info("Loop Stopped {0}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))

        # Put the app to sleep
        time.sleep(flannelfox.settings['queueDaemonThreadSleep'])

def main():
    '''
    Main entry point for the Application
    TODO: Implement threading or multiprocessing
    '''

    with daemon.DaemonContext(
        files_preserve = [
            logging.getFileHandle(__name__).stream
        ]
    ):
        while True:
        
            try:
                __queueReader()

            except KeyboardInterrupt as e:
                logger.warning("Application Aborted")
                break

            except Exception as e:
                logger.error(u"Application Stopped {0}\nTrace: {1}".format(e, traceback.format_exc() ))
                
                # Sleep for 10 seconds to give a bit of time for the error to try and resolve itself
                # This is mainly related to the occurance of an error that can be generated randomly
                #   [Errno 11] Resource temporarily unavailable
                time.sleep(10)

    logger.info("Application Exited")


if __name__ == '__main__':
    main()
