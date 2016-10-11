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
import time, re, signal, os, traceback
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
httpRegex = re.compile(ur"https?://([^/]+)(?:/.*)?")

# Setup the logging agent
logger = logging.getLogger(__name__)


def __readRSSFeed(url):

    response = u''
    xmlData = None
    httpCode = None
    encoding = "utf-8"
    pid = os.getpid()

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
        logger.threadingDebug(u"[T:{0}] RSS fetch OK URL: [{1}]|[{2}]".format(pid, httpRegex.match(url).group(1), r.status_code))

    except Exception as e:
        logger.threadingInfo(u"[T:{0}] There was a problem fetching the URL: [{1}]\n-  {2}".format(pid, httpRegex.match(url).group(1), e))
        pass
        
    return (response, httpCode, encoding)


def __rssToTorrents(xmlData, feedType=u"none", feedDestination=None, minRatio=0.0, minTime=0, comparison=u"or"):
    '''
    Read the RSS Feed and return a list of torrent items
    '''

    rssTorrents = []
    pid = os.getpid()

    try:
        if not isinstance(xmlData,(str,unicode)):
            raise ValueError(u"RSS Feed Data is not valid")

        # Parse the RSS XML
        rssItems = ET.fromstring(xmlData)

        # Check for a Channel container
        channel = rssItems.find("channel")
        if channel is not None:
            rssItems = channel

        for rssItem in rssItems.iter("item"):

            # Try to get a title property, if we can't then skip this item
            try:
                title = rssItem.find("title").text

                if title is not None and title != u"":
                    title = unicode(title.strip())
                    title = title.replace(u" & ",u" and ")
                else:
                    continue
            except:
                continue

            # Try to get a link property, if we can't then skip this item
            try:
                link = unicode(rssItem.find("link").text.strip())
                link = link.replace(u' ', u"%20")

                if link is None or link == u'':
                    continue
            except:
                continue

            # Try to create a torrent from the title
            try:

                torrentItem = TORRENT_TYPES[feedType](torrentTitle=title, url=link, minTime=minTime, minRatio=minRatio, comparison=comparison, feedDestination=feedDestination)

                if torrentItem is not None:
                    rssTorrents.append(torrentItem)
                else:
                    raise TypeError(u"The Title given does not appear to be of type: {0}\n-  {1}".format(feedType, title))


            except (KeyError) as e:
                logger.threadingInfo(u"[T:{0}] A valid Feed Type was not specified:\n-  {1}".format(pid, e))
                pass

            except (TypeError, ValueError) as e:
                logger.threadingDebug(u"There was a problem creating a torrent:\n-  {0}".format(e))
                pass

        rssItems = None

    except (IOError,ValueError,ET.ParseError) as e:
        logger.threadingInfo(u"[T:{0}]  There was a problem reading the RSS Feed:\n-  {1}".format(pid, e))
        pass


    return rssTorrents


def __rssThread(majorFeed):

    error = None
    processed = 0
    pid = os.getpid()

    try:

        rssTorrents = []

        logger.threadingInfo("[T:{0}] Thread Started".format(pid))
        
        # This is needed to ensure Keyboard driven interruptions are handled correctly
        # signal.signal(signal.SIGINT, signal.SIG_IGN)

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

            logger.threadingDebug(u"[T:{0}] Checking URL: {1} [{2}]".format(pid, httpRegex.match(minorFeed["url"]).group(1), httpCode))

            # If we did not get any data or there was an error then skip to the next feed
            if rssData is None or httpCode != 200:
                continue

            # Ensure data is utf-8
            rssData = Settings.changeCharset(rssData, "utf-8", "xml")

            # Create a list of torrents from the RSS Feed
            torrents = __rssToTorrents(rssData, feedType=majorFeed["feedType"], feedDestination=majorFeed["feedDestination"],minRatio=minorFeed["minRatio"],comparison=minorFeed["comparison"],minTime=minorFeed["minTime"])

            # Update the processed count
            processed += len(torrents)

            for torrent in torrents:

                # Check the filters and see if anything should be excluded
                if torrent.filterMatch(majorFeed["feedFilters"]):
                    rssTorrents.append(torrent)
                '''
                    logger.debug("Matched Torrent: ")
                    logger.debug("======================")
                    logger.debug(u"{0}".format(torrent))
                    logger.debug("======================")
                else:
                    logger.debug("UnMatched Torrent: ")
                    logger.debug("======================")
                    logger.debug(u"{0}".format(torrent))
                    logger.debug("======================")
                '''

        # Garbage Collection
        minorFeed = rssData = torrents = None

    except Exception as e:
        error = u"ERROR: [T:{0}]: {0}\nException: {1}\nTraceback: {2}".format(minorFeed["url"],e, traceback.format_exc())
        rssTorrents = []

    except:
        error = u'ERROR: [T:{0}]: {0}'.format(traceback.format_exc())
        rssTorrents = []

    logger.threadingInfo("[T:{0}] Thread Done".format(pid))
    return (pid, rssTorrents, error, processed)


def __rssReader():
    '''
    This thread will take care of Processing RSS Feeds
    '''

    logger.info(u'RSSDaemon Started')

    logger.debug("Pool Created")

    try:
        while True:

            totalProcessed = 0
            startTime = time.time()

            rssPool = Pool(processes=flannelfox.settings['maxRssThreads'], maxtasksperchild=10)

            # Reads the RSSFeedConfig file each loop to ensure new entries are picked up
            # rssFeeds
            majorFeeds = {}
            results = []
            majorFeeds.update(Settings.readLastfmArtists())
            majorFeeds.update(Settings.readTraktTV())
            majorFeeds.update(Settings.readGoodreads())
            majorFeeds.update(Settings.readRSS())

            # Holds all the torrents that are in the feeds, filtered, and new
            rssTorrents = TorrentQueue.Queue()

            # If single thread is specified then do not fork
            # TODO: this should not happen and will be removed
            if flannelfox.settings['maxRssThreads'] == 1:
                for majorFeed in majorFeeds.itervalues():
                    logger.info(u"Feed Name: {0}".format(majorFeed["feedName"]))

                    torrents, error, processed = __rssThread(majorFeed)

                    for t in torrents:
                        rssTorrents.append(t)

            # If multiple cores are allowed then for http calls
            else:

                try:
                    logger.info(u"Pool fetch of RSS Started {0}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))


                    #for f in majorFeeds.itervalues():
                    #    results.append(rssPool.apply_async(__rssThread, (f,)))
                 
                    results = rssPool.imap_unordered(__rssThread, majorFeeds.itervalues())

                except Exception as e:
                    logger.error(u"ERROR: There was an error fetching the RSS Feeds.\n-  {0}".format(e))


                # Try to get the rssFeeds and return the resutls
                logger.info(u'Appending items to the queue')
                
                try:
                    
                    for result in results:
                        
                        #Take each item in the result and append it to the Queue
                        pid, torrents, error, processed = result

                        if error is not None:
                            logger.error('ERROR: There was a problem processing a rss feed:\n-  {0}'.format(error))

                        totalProcessed += processed

                        currentTorrent = 0
                        for t in torrents:

                            currentTorrent += 1

                            logger.debug(u'Processing: T[{0}]I[{1}]'.format(pid, currentTorrent))
                            try:
                                rssTorrents.append(t)
                            except Exception as e:
                                logger.error(u"ERROR: There was a problem appending data to the queue.\n-  {0}".format(e))

                    try:

                        logger.debug(u"Closing RSS Pool")
                        rssPool.close()
                    
                        logger.debug(u"Joining RSS Pool Workers")
                        rssPool.join()
                    except:
                        logger.error(u"ERROR: There was a problem clearing the pool.\n-  {0}".format(traceback.format_exc()))    

                except Exception as e:
                    logger.error(u"ERROR: There was a problem iterating the results.\n-  {0}".format(e))

                    try:
                        logger.debug(u"Closing RSS Pool")
                        rssPool.close()

                        logger.debug(u"Terminating RSS Pool Workers")
                        rssPool.terminate()

                        logger.debug(u"Joining RSS Pool Workers")
                        rssPool.join()
                    except:
                        logger.error(u"ERROR: There was a problem clearing the pool after an error.\n-  {0}".format(traceback.format_exc()))    

            logger.info(u"Pool fetch of RSS Done {0} {1} records loaded".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), len(rssTorrents)))
            
            # Log the number of records processed
            logger.info("Processed {0} items in {1:.2f} second(s)".format(totalProcessed, time.time() - startTime))

            # Write matching filters to database
            logger.debug("Writing {0} Torrents to DB".format(len(rssTorrents)))
            rssTorrents.writeToDB()

            # Garbage collection
            logger.debug("Garbage Collection")
            majorFeeds = rssTorrents = results = result = rssPool = None

            #Settings.showHeap()

            # Put the app to sleep
            logger.info("Sleep for a bit")
            time.sleep(flannelfox.settings['rssDaemonThreadSleep'])

    except Exception as e:
        logger.error(u"ERROR: __rssReader Failed {0} {1}\n-  {2}".format(
            strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            e, 
            traceback.format_exc())
        )

    except:
        logger.error(u"ERROR: __rssReader Failed {0}\n-  {1}".format(
            strftime("%Y-%m-%d %H:%M:%S", gmtime()), 
            traceback.format_exc())
        )
        


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
                logger.critical("__rssReader Started")
                __rssReader()

            except KeyboardInterrupt as e:
                logger.critical(u"Application Aborted")
                break

            except Exception as e:
                logger.critical(u"Application Stopped {0}".format(e))

                # Sleep for 10 seconds to give a bit of time for the error to try and resolve itself
                # This is mainly related to the occurance of an error that can be generated randomly
                #   [Errno 11] Resource temporarily unavailable
                time.sleep(10)


    logger.critical(u"Application Exited")

        
if __name__ == '__main__':
    main()
