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
import time, re, zlib, sys, platform

import xml.etree.ElementTree as ET
from multiprocessing import Pool
from time import gmtime, strftime
import os.path as OsPath

# Third party modules
import requests

# Needed to fix an SSL issue
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# flannelfox Includes
import flannelfox
from flannelfox import Settings

# rssdaemon Includes
from flannelfox.torrenttools import Torrents, TorrentQueue
from flannelfox.torrenttools.Torrents import TORRENT_TYPES


httpRegex = re.compile(r"https?://([^/]+)(?:/.*)?")

def __readRSSFeed(url):

    response = u''
    xmlData = None
    httpCode = None
    encoding = "utf-8"

    try:
        #if flannelfox.settings['debugLevel'] >= 5: print "Fetching URL: [{0}]".format(url)
        # Open the URL and get the data
        #opener = urllib2.build_opener()
        #opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0')]
        #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        #opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36')]
        
        response = None

        try:
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'}
            r = requests.get(url, headers=headers, timeout=60)
            response = r.content
            httpCode = r.status_code
            encoding = r.encoding
            # print "RSS fetch OK URL: [{0}]\n[{1}]".format(url,r.status_code)
        except Exception as e:
            print "There was a problem opening the URL: [{0}]\n[{1}]".format(url,e)

    except Exception as e:
        if flannelfox.settings['debugLevel'] >= 1: print "There was a problem fetching the URL: [{0}]\n{1}".format(url,e)
        
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
                if flannelfox.settings['debugLevel'] >= 10: print "A valid Feed Type was not specified:\n{0}".format(e)

            except (TypeError, ValueError) as e:
                if flannelfox.settings['debugLevel'] >= 10: print "There was a problem creating a torrent:\n{0}".format(e)

        rssItems = None

    except (IOError,ValueError,ET.ParseError) as e:
        if flannelfox.settings['debugLevel'] >= 1:
            print "There was a problem reading the RSS Feed:\n{0}".format(e)
            print xmlData[:300]
       
        return rssTorrents

    return rssTorrents


def __rssThread(majorFeed):

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

            if flannelfox.settings['debugLevel'] >= 5: print "Checking URL: {0} [{1}]".format(httpRegex.match(minorFeed["url"]).group(1), httpCode)

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

        #for torrent in rssTorrents:
        #    print "__rssThread Results: {0}".format(torrent["torrentTitle"])

    except Exception as e:
        print "Thread ERROR: {0}".format(minorFeed["url"])
        print "Exception: {0}".format(e)
        rssTorrents = []

    return rssTorrents


def rssReader():
    '''
    This thread will take care of Processing RSS Feeds
    '''

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
        if Settings.CPU_COUNT == 1:
            for majorFeed in majorFeeds.itervalues():
                if flannelfox.settings['debugLevel'] >= 5: 
                    print "#########################"
                    print "Feed Name: {0}".format(majorFeed["feedName"])
                    print "#########################"

                result = __rssThread(majorFeed)

                for r in result:
                    rssTorrents.append(r)

        # If multiple cores are allowed then for http calls
        else:
            rssPool = Pool(processes=(Settings.CPU_COUNT)*4)

            print "Pool fetch of RSS Started {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            results = [rssPool.apply_async(__rssThread, (f,)) for f in majorFeeds.itervalues()]

            rssPool.close()
            rssPool.join()


            # Try to get the rssFeeds and return the resutls
            try:
                for result in results:

                    try:
                        result = result.get(timeout=1)
                    except Exception as e:
                        if flannelfox.settings['debugLevel'] >= 10: print "TEST ERROR\n{0}".format(e)
                        continue

                    if flannelfox.settings['debugLevel'] >= 10:
                        print 'Appending items to the torrent queue'

                    #Take each item in the result and append it to the Queue
                    for r in result:
                        rssTorrents.append(r)

            except Exception as e:
                if flannelfox.settings['debugLevel'] >= 10: print "There was a problem getting the data from the result pool\n{0}".format(e)

            print "###################################"
            print "Pool fetch of RSS Done {0}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            print "###################################"

        if flannelfox.settings['debugLevel'] >= 1:
            print "###################################"
            print "# {0} records loaded from RSS Feeds".format(len(rssTorrents))
            print "###################################"

        # Write matching filters to database
        #if flannelfox.settings['debugLevel'] >= 1: print "RSSQUEUE:\n {0}".format(rssTorrents)
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

    try:
        rssReader()

    except KeyboardInterrupt as e:
        if flannelfox.settings['debugLevel'] >= 1: print "Application Aborted"

    finally:
        if flannelfox.settings['debugLevel'] >= 1: print "Application Exited"

        
if __name__ == '__main__':
    main()
