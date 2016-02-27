#!/usr/bin/python2.7
#-------------------------------------------------------------------------------
# Name:        rssdaemon
# Purpose:     Run in the background and get new torrents from RSS
#              This app will read torrent RSS feeds and pull out the title and
#              other needed data. It will then create a list of torrents that
#              can be returned and write it to the DB.
#
# TODO:        Migrate this to a class so multiple daemons could be run (LOW)
#              Implement multiprocessing for web fetches
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-


# System Includes
import time, re, signal, os
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from time import gmtime, strftime

# Third party modules
import requests
import daemon
# Needed to fix an SSL issue with requests
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# flannelfox Includes
import flannelfox
from flannelfox import logging
from flannelfox import Settings

# rssdaemon Includes
from flannelfox.torrenttools import Torrents, TorrentQueue
from flannelfox.torrenttools.Torrents import TORRENT_TYPES


# TODO: can this be moved?
httpRegex = re.compile(r"https?://([^/]+)(?:/.*)?")

# Setup the logging agent
logger = logging.getLogger(__name__)


def __readRSSFeed(url):

    response = u''
    xmlData = None
    httpCode = None
    encoding = "utf-8"

    try:

        # initialize the responses
        response = None

        # Setup the headers
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'}

        # Open the URL and get the data
        r = requests.get(url, headers=headers, timeout=10)
        response = r.content
        httpCode = r.status_code
        encoding = r.encoding
        logger.debug("RSS fetch OK URL: [{0}]|[{1}]".format(httpRegex.match(url).group(1),r.status_code))

    except Exception as e:
        logger.error("There was a problem fetching the URL: [{0}]\n{1}".format(url,e))
        
    return (response, httpCode, encoding)


def __rssToTorrents(xmlData,feedType=u"none",feedDestination=None,minRatio=0.0,minTime=0,comparison=u"or"):
    '''
    Read the RSS Feed and return a list of torrent items
    '''

    rssTorrents = []

    try:
        if not isinstance(xmlData,(str,unicode)):
            raise ValueError("RSS Feed Data is not valid")

        # Parse the RSS XML
        rssItems = ET.fromstring(xmlData)

        # Check for a Channel container
        channel = rssItems.find("channel")
        if channel is not None:
            rssItems = channel

        for rssItem in rssItems.iter("item"):

            title = rssItem.find("title").text

            if title is not None and title != "":
                title = unicode(title.strip())
                title = title.replace(u" & ",u" and ")
            else:
                continue

            link = unicode(rssItem.find("link").text.strip())
            link = link.replace(u' ', u"%20")

            # If the torrent does not have a url then skip it,
            if link is None or link == u'':
                continue

            # Try to create a torrent from the title
            try:

                torrentItem = TORRENT_TYPES[feedType](torrentTitle=title,url=link,minTime=minTime,minRatio=minRatio,comparison=comparison,feedDestination=feedDestination)

                if torrentItem is not None:
                    rssTorrents.append(torrentItem)
                else:
                    raise TypeError("The Title given does not appear to be of type: {0}\n{1}".format(feedType,title))


            except (KeyError) as e:
                logger.debug("A valid Feed Type was not specified:\n{0}".format(e))

            except (TypeError, ValueError) as e:
                logger.debug("There was a problem creating a torrent:\n{0}".format(e))

        rssItems = None

    except (IOError,ValueError,ET.ParseError) as e:
        logger.error("There was a problem reading the RSS Feed:\n{0}".format(e))


    return rssTorrents


def __rssThread(majorFeed):

    # This is needed to ensure Keyboard driven interruptions are handled correctly
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    rssTorrents = []

    try:

        # Check each feed for a list of possible torrents
        # Set the default type for untyped feeds
        if isinstance(majorFeed["feedType"],unicode) and majorFeed["feedType"] != "":
            majorFeed["feedType"] = majorFeed["feedType"]
        else:
            majorFeed["feedType"] = u"none"

        # Aggregate all the minorFeed items
        for minorFeed in majorFeed["minorFeeds"]:
            # Read URL
            rssData, httpCode, encoding = __readRSSFeed(minorFeed["url"])

            logger.info("Checking URL: {0} [{1}]".format(httpRegex.match(minorFeed["url"]).group(1), httpCode))

            # If we did not get any data or there was an error then skip to the next feed
            if rssData is None or httpCode != 200:
                continue

            # Ensure data is utf-8
            rssData = Settings.changeCharset(rssData, "utf-8", "xml")

            # Create a list of torrents from the RSS Feed
            torrents = __rssToTorrents(rssData, feedType=majorFeed["feedType"], feedDestination=majorFeed["feedDestination"],minRatio=minorFeed["minRatio"],comparison=minorFeed["comparison"],minTime=minorFeed["minTime"])
            for torrent in torrents:

                # Check the filters and see if anything should be excluded
                if torrent.filterMatch(majorFeed["feedFilters"]):
                    rssTorrents.append(torrent)

        # Garbage Collection
        minorFeed = rssData = torrents = None

    except Exception as e:
        logger.error("Thread ERROR: {0} Exception: {1}".format(minorFeed["url"]),e)
        rssTorrents = []

    return rssTorrents


def rssReader():
    '''
    This thread will take care of Processing RSS Feeds
    '''

    logger.info('RSSDaemon Started')

    while True:

        # Reads the RSSFeedConfig file each loop to ensure new entries are picked up
        # rssFeeds
        majorFeeds = {}
        majorFeeds.update(Settings.readLastfmArtists())
        majorFeeds.update(Settings.readTraktTV())
        majorFeeds.update(Settings.readRSS())

        # Holds all the torrents that are in the feeds, filtered, and new
        rssTorrents = TorrentQueue.Queue()

        # If single thread is specified then do not fork
        # TODO: this should not happen and will be removed
        if flannelfox.settings['maxRssThreads'] == 1:
            for majorFeed in majorFeeds.itervalues():
                logger.info("Feed Name: {0}".format(majorFeed["feedName"]))

                result = __rssThread(majorFeed)

                for r in result:
                    rssTorrents.append(r)

        # If multiple cores are allowed then for http calls
        else:
            rssPool = Pool(processes=flannelfox.settings['maxRssThreads'])

            try:
                logger.info("Pool fetch of RSS Started {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                results = [rssPool.apply_async(__rssThread, (f,)) for f in majorFeeds.itervalues()]
                rssPool.close()

            except Exception as e:
                logger.error("There was an error fetching the RSS Feeds.\n{0}".format(e))
                rssPool.terminate()

            finally:
                rssPool.join()


            # Try to get the rssFeeds and return the resutls
            logger.info('Appending items to the queue')
            
            try:
                

                for result in results:

                    try:
                        result = result.get(timeout=1)
                    except Exception as e:
                        logger.warning("There was a problem with reading one of the result sets.\n{0}".format(e))
                        continue

                    #Take each item in the result and append it to the Queue
                    for r in result:
                        rssTorrents.append(r)

            except Exception as e:
                logger.error("There was a problem appending data to the queue.\n{0}".format(e))

        logger.info("Pool fetch of RSS Done {0} {1} records loaded".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), len(rssTorrents)))

        # Write matching filters to database
        rssTorrents.writeToDB()

        # Garbage collection
        majorFeeds = rssTorrents = results = result = rssPool = None

        #Settings.showHeap()

        # Put the app to sleep
        time.sleep(flannelfox.settings['rssDaemonThreadSleep'])


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
        try:
            rssReader()

        except KeyboardInterrupt as e:
            logger.error("Application Aborted")

        finally:
            logger.info("Application Exited")

        
if __name__ == '__main__':
    main()
