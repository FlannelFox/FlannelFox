#-------------------------------------------------------------------------------
# Name:        TransmissionRemote
# Purpose:     Interacts with transmission daemon
#
# TODO: 
#           Modify torrent using funcs to use the torrent class
#           List out the actual generic calls
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

# System Includes
import re, json, time

# flannelfox Includes
import flannelfox
import Trackers
from flannelfox import Settings
from Torrent import Status as TorrentStatus
from Torrent import Torrent
from flannelfox.databases import Databases


import requests

# Needed to fix an SSL issue
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

TRANSMISSION_MAX_RETRIES = 3

# Setup the database object
TorrentDB = Databases(flannelfox.settings['database']['defaultDatabaseEngine'])

class Responses(object):
    success = u'success'
    invalid_argument = u'invalid argument'
    duplicate = u'duplicate torrent'
    bad_torrent = u'invalid or corrupt torrent file'
    torrent_not_found = u'gotMetadataFromURL: http error 404: Not Found'
    torrent_bad_request = u'gotMetadataFromURL: http error 400: Bad Request'
    torrent_service_unavailable = u'gotMetadataFromURL: http error 503: Service Unavailable'
    torrent_no_response = u"gotMetadataFromURL: http error 0: No Response"


class Client(object):

    def __init__(self, host=u"localhost", port=u"9091", user=None, password=None, rpcLocation=None, https=False):

        self.elements = {}
        self.elements["host"] = host
        self.elements["port"] = port
        self.elements["user"] = user
        self.elements["password"] = password
        self.elements["rpcLocation"] = rpcLocation.lstrip('/')
        self.elements["sessionId"] = None
        self.elements["queue"] = []
        self.tagGenerator = self.__generateTag()

        # Build the server URI
        self.elements["uri"] = u"http"

        if https:
            self.elements["uri"] += u"s"

        self.elements["uri"] += u"://{0}:{1}".format(host,port)

            
    def __transmissionInit(self, action=u'restart'):
        '''
        Used to restart the transmission daemon
        '''

        response,error = subprocess.Popen([TORRENT_DAEMON_INIT,action], stdout=subprocess.PIPE).communicate()

        if error is not None:
            raise ValueError


    def __generateTag(self):
        '''
        Generates an int to be used for tag numbers in the transmission-rpc
        calls
        '''
        while True:
            for n in xrange(65535):
                yield n


    def __sendRequest(self,queryString=None,postData=None):
        '''
        Handles making calls to the transmission-rpc interface

        Takes:
            queryString - GET data
            postData - PostData

        Returns:
            Tuple (response and httpCode)
        '''

        response = u''
        httpCode = None
        encoding = u"utf-8"
        authHandler = None
        headers = {}
        uri = None
        auth = None

        # Check if authentication should be used
        if self.elements["user"] is not None:
            auth=(self.elements["user"], self.elements["password"])

        if self.elements["sessionId"] is not None:
            headers.update({"X-Transmission-Session-Id":self.elements["sessionId"]})

        if postData is not None:
            headers.update({"Content-type":"application/json"})

        # Add RPC path to the URI
        if queryString is not None:
            uri = "{0}/{1}?{2}".format(self.elements["uri"],self.elements["rpcLocation"],queryString)
        else:
            uri = "{0}/{1}".format(self.elements["uri"],self.elements["rpcLocation"])

        if flannelfox.settings['debugLevel'] >= 10: print "Trying to communicate with the Transmission Server"
        try:
            # Connect to the RPC server
            if postData is None:
                if auth is not None:
                    r = requests.get(uri, auth=auth, headers=headers)
                else:
                    r = requests.get(uri, headers=headers)
            else:
                if auth is not None:
                    r = requests.post(uri, auth=auth, headers=headers, data=postData)
                else:
                    r = requests.post(uri, headers=headers, data=postData)

            response = r.content
            httpCode = r.status_code
            encoding = r.encoding

            # Look for the X-Transmission-Session-Id header and save it, then
            # make the request again
            if httpCode == 409:
                #print "Trying to get Session-Id Header: [{0}]".format(r.headers.get("X-Transmission-Session-Id"))
                self.elements["sessionId"] = r.headers.get("X-Transmission-Session-Id")
                if flannelfox.settings['debugLevel'] >= 10: print "X-Transmission-Session-Id Error"

                response, httpCode, encoding = self.__sendRequest(queryString,postData)

            if flannelfox.settings['debugLevel'] >= 10: print "Transmission call completed"
        except Exception as e:
            if flannelfox.settings['debugLevel'] >= 1: print "There was a problem communicating with Transmission:\n{0}".format(e)
            try:
                httpCode = e.code
            except (AttributeError):
                httpCode = -1

        return (response, httpCode, encoding)


    def __parseTransmissionResponse(self,postData,tries=0):
        '''
        Parse a transmission response

        Takes:
            tries - Limits the recursion of this call when tags do not match
            postData - The data posted to transmission-rpc

        Returns:
            Tuple (torrents,httpResponseCode,transmissionResponseCode)
        '''

        response = None
        httpResponseCode = -1
        encoding = None
        transmissionResponseCode = u"failed"

        if tries >= TRANSMISSION_MAX_RETRIES:
            return (response,httpResponseCode,transmissionResponseCode)

        # Make the call
        response, httpResponseCode, encoding = self.__sendRequest(postData = postData.encode("utf-8"))

        # Ensure httpResponseCode is unicode
        httpResponseCode = unicode(httpResponseCode)

        # Ensure the result is in utf-8
        response = Settings.changeCharset(response,"utf-8","html.parser")

        torrents = []

        # parse the json if it exists
        if response is not None:
            try:
                response = json.loads(response)

            # If there is a problem parsing the response then return an empty set
            except (ValueError) as e:
                pass

        # Make sure we got a result
        if isinstance(response,dict):

            # Get Tag, if tag is available and ensure the response matches
            posted = json.loads(postData)
            if isinstance(posted,dict) and "tag" in posted:
                if isinstance(response,dict) and "tag" in response:
                    if posted["tag"] != response["tag"]:
                        time.sleep(5)
                        response,httpResponseCode = self.__parseTransmissionResponse(self,postData,tries=tries+1)


            # Get Transmission Response Code
            if isinstance(response,dict) and "result" in response:
                transmissionResponseCode = unicode(response["result"])

        return (response,httpResponseCode,transmissionResponseCode)


    def __getTorrents(self,fields=[u"hashString",u"id",u"error",u"errorString",u"uploadRatio",u"percentDone",u"doneDate",u"activityDate",u"rateUpload",u"status",u"downloadDir",u'trackerStats']):
        '''
        Fetch a set of torrents with the provided information

        Takes:
            fields - Fields to be returned in the transmission-rpc

        Returns:
            Tuple (torrents,httpResponseCode,transmissionResponseCode)
        '''

        # Method
        commandJson = u'{"method":"torrent-get",'

        # Arguments
        commandJson += u'"arguments":{'

        # Fields
        commandJson += u'"fields":["'
        commandJson += u'","'.join(fields)
        commandJson += u'"]'

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Extract the values so we can replace the response with only torrents
        response,httpResponseCode,transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        # Get Torrents
        torrents = []

        if isinstance(response,dict) and "arguments" in response:
            if isinstance(response["arguments"],dict) and "torrents" in response["arguments"]:
                if isinstance(response["arguments"]["torrents"],list):
                    torrents = response["arguments"]["torrents"]

        return (torrents,httpResponseCode,transmissionResponseCode)


    def __updateHashString(self,using=None,update=None):
        '''
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
            Tuple (transmissionResponseCode,httpResponseCode)
        '''

        # Initial attempt at fetching data
        torrents,httpResponseCode,transmissionResponseCode = self.__getTorrents()

        # Incase we get an incomplete answer or fail let's retry
        tries = 0
        while transmissionResponseCode != Responses.success and tries < TRANSMISSION_MAX_RETRIES:
            torrents,httpResponseCode,transmissionResponseCode = self.__getTorrents()
            tries += 1

        if isinstance(torrents,list):
            self.elements["queue"] = []

            for torrent in torrents:

                trackers = torrent['trackerStats']
                
                # Look to make sure at least one tracker is working
                # This is due to bug #5775
                # https://trac.transmissionbt.com/ticket/5775
                if torrent['status'] == TorrentStatus.Downloading and torrent['percentDone'] == 0.0 and torrent['errorString'] == u'':

                    workingTrackerExists = False

                    for tracker in trackers:
                        #print tracker
                        #print 'Error: {0}'.format(torrent['errorString'])
                        #print 'Announce {0}:{1}'.format(tracker['host'], tracker['lastAnnounceSucceeded'])
                        #print 'Status: {0}'.format(torrent['status'])
                        if not workingTrackerExists:
                            
                            if tracker['lastAnnounceResult'] != '' and tracker['lastAnnounceResult'] != None:
                                workingTrackerExists = True
                                if flannelfox.settings['debugLevel'] >= 5: print 'Rewriting errorString: {0}'.format(tracker['lastAnnounceResult'])
                                torrent['errorString'] = tracker['lastAnnounceResult']

                            elif tracker['lastAnnounceSucceeded']:
                                workingTrackerExists = True

                    if not workingTrackerExists and torrent['errorString'] == u'':
                        torrent['error'] = -1
                        torrent['errorString'] = u'No Connectable Trackers Found'
                        #print '{0}: No Connectable Trackers Found'.format(torrent['hashString'])
                        #print 'Announce {0}:{1}'.format(tracker['announce'], tracker['lastAnnounceSucceeded'])
                        torrent['error'] = 99
                        torrent['errorString'] = 'No Connectable Trackers Found'

                # Check for torrents that should be removed
                for error in Trackers.Responses.Remove:
                    if error in torrent['errorString']:
                        if flannelfox.settings['debugLevel'] >= 5: print 'Removing torrent do to errorString: {0}'.format(torrent['errorString'])
                        self.removeBadTorrent(hashString=torrent['hashString'])
                        continue

                # Check if the torrent is corrupted
                if 'please verify local data' in torrent['errorString']:

                    # Ensure a Check is not already in place
                    if (torrent["status"] not in [TorrentStatus.Paused, TorrentStatus.QueuedForVerification, TorrentStatus.Verifying]):
                        self.verifyTorrent(hashString=torrent["hashString"])
                        continue

                    elif torrent["status"] == TorrentStatus.Paused:
                        self.StartTorrent(hashString=torrent["hashString"])
                        continue

                    if flannelfox.settings['debugLevel'] >= 5: print "Corrupted torrent: {1} STAT: {0}".format(torrent["status"], torrent["hashString"])

                elif torrent["errorString"] != u'':
                    if flannelfox.settings['debugLevel'] >= 5: print "Error encountered: {0} {1}".format(torrent["hashString"],torrent["errorString"])


                t = Torrent(hashString=torrent["hashString"],
                            id=torrent["id"],
                            error=torrent["error"],
                            errorString=torrent["errorString"],
                            uploadRatio=torrent["uploadRatio"],
                            percentDone=torrent["percentDone"],
                            doneDate=torrent["doneDate"],
                            activityDate=torrent["activityDate"],
                            rateUpload=torrent["rateUpload"],
                            downloadDir=torrent["downloadDir"],
                            status=torrent["status"]
                )

                self.elements["queue"].append(t)

        return (transmissionResponseCode,httpResponseCode)


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
        print "Verify Requested"
        time.sleep(5)

        if hashString is None:
            return False

        # Method
        commandJson = u'{"method":"torrent-verify",'

        # Arguments
        commandJson += u'"arguments":{'

        # Ids
        commandJson += u'"ids":"{0}"'.format(hashString)

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Stop the torrent first
        if not self.StopTorrent(hashString=hashString):
            print "Could not stop the torrent... This should not happen"

        # Make sure the call worked
        response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        if transmissionResponseCode == Responses.success:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Verification Succeeded"
            return True
        else:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Verification Failed"

            return False


    def StopTorrent(self,hashString=None):
        '''
        Stops a torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        print "Stop Requested"
        time.sleep(5)

        if hashString is None:
            return False

        # Method
        commandJson = u'{"method":"torrent-stop",'

        # Arguments
        commandJson += u'"arguments":{'

        # Ids
        commandJson += u'"ids":"{0}"'.format(hashString)

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Make sure the call worked
        response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        if transmissionResponseCode == Responses.success:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Stop Succeeded"
            return True
        else:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Stop Failed"

            return False


    def StartTorrent(self,hashString=None):
        '''
        Starts a torrent

        Takes:
            hashString - Hash of the specific torrent to remove

        Returns:
            bool True is action completed
        '''
        print "Start Requested"
        time.sleep(10)

        if hashString is None:
            return False

        # Method
        commandJson = u'{"method":"torrent-start",'

        # Arguments
        commandJson += u'"arguments":{'

        # Ids
        commandJson += u'"ids":"{0}"'.format(hashString)

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Make sure the call worked
        response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        if transmissionResponseCode == Responses.success:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Start Succeeded"
            return True
        else:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Start Failed"

            return False


    def removeBadTorrent(self,hashString=None):
        '''
        Removes a torrent from both transmission and the database
        this should be called when there is a bad torrent.

        Takes:
            hashString - Hash of the specific torrent to remove
        '''

        # Remove the torrent from the client
        self.removeTorrent(hashString=hashString,deleteData=True)

        # Remove the torrent from the DB
        TorrentDB.deleteTorrent(hashString=hashString)

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
            self.removeTorrent(hashString=hashString,deleteData=False)

            return True
        else:
            # Remove the torrent from the DB
            TorrentDB.deleteTorrent(url=url)

            return True

    def removeTorrent(self,hashString=None,deleteData=False):
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
        print "Delete Requested"
        time.sleep(5)

        if hashString is None:
            return False

        # Method
        commandJson = u'{"method":"torrent-remove",'

        # Arguments
        commandJson += u'"arguments":{'

        # Ids
        commandJson += u'"ids":"{0}",'.format(hashString)

        # Delete Option
        commandJson += u'"delete-local-data":{0}'.format(str(deleteData).lower())

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Make sure the call worked
        response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        if transmissionResponseCode == Responses.success:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Torrent Removal Succeeded"
            return True
        else:
            if flannelfox.settings['debugLevel'] >= 5:
                print "Torrent Removal Failed"

            return False


    def deleteTorrent(self,hashString=None):
        '''
        Removes a torrent from transmission and deletes the associated data

        Takes:
            hashString - Hash of the specific torrent to remove

            TODO: if hashString is not specified then we should remove the torrent
            that has the longest time since active.

        Returns:
            bool True is action completed
        '''
        return self.removeTorrent(hashString=hashString,deleteData=True)


    def removeExtraTrackers(self,hashString=None):
        '''
        Attempts to remove extra trackers from torrents that can cause automation issues.
        '''
        # Method
        commandJson = u'{"method":"torrent-set",'

        # Arguments
        commandJson += u'"arguments":{'
        
        # Tracker remove
        commandJson += u'"trackerRemove":[1],'
        
        # Torrent Id
        commandJson += u'"ids":"{0}"'.format(hashString)

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        if flannelfox.settings['debugLevel'] >= 10: print "Trying to remove extra trackers"
        while (True):

        # Remove a tracker
            response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)
            
            # If the call did not work then we are down to 
            # the last tracker so break out of the loop
            if transmissionResponseCode == Responses.invalid_argument:
                break

            if flannelfox.settings['debugLevel'] >= 10: print "Tracker removed"
            
            # Wait 3 seconds before removing the next tracker
            time.sleep(5)

        return True


    def addTorrentURL(self,url=None,destination=flannelfox.settings['files']['defaultTorrentLocation']):
        '''
        Attempts to load the torrent at the given url into transmission

        Takes:
            url - url of the torrent file to be added

            destination - where the torrent should be saved

        Returns:
            bool True is action completed successfully
        '''

        # Make sure a URL was passed
        if url is None:
            raise ValueError(u"A url must be provided to add a torrent")

        if flannelfox.settings['debugLevel'] >= 5:
            print "Trying to add a new torrent:\n{0}".format(url)

        # Method
        commandJson = u'{"method":"torrent-add",'

        # Arguments
        commandJson += u'"arguments":{'

        # Download Dir
        if destination is not None:
            commandJson += u'"download-dir":"{0}",'.format(destination)

        # Filename
        commandJson += u'"filename":"{0}"'.format(url)

        # Close Arguments
        commandJson += u'},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Make sure the call worked
        response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        # Get Duplicated Torrents
        if isinstance(response,dict) and "arguments" in response:
            if isinstance(response["arguments"],dict) and u"torrent-duplicate" in response["arguments"]:

                # Duplicate Torrent
                duplicateTorrent = response["arguments"]["torrent-duplicate"]

                # Torrent is broken so lets delete it from the DB, this leaves the opportunity
                # for the torrent to later be added again
                self.removeDupeTorrent(url=url, hashString=duplicateTorrent["hashString"])

                if flannelfox.settings['debugLevel'] >= 5:
                    print "Duplicate torrent encountered: {0}".format(transmissionResponseCode)
                    print "Duplicate info {0}".format(response["arguments"])

                return False

        # Get Added Torrents
        if isinstance(response,dict) and "arguments" in response:
            if isinstance(response["arguments"],dict) and "torrent-added" in response["arguments"]:
                torrentAdded = response["arguments"]["torrent-added"]

                # Get Current Time
                sinceEpoch = int(time.time())

                # update hash, addedOn, added in DB
                self.__updateHashString(using={u"url":url}, update={u"hashString":torrentAdded["hashString"],u"addedOn":sinceEpoch,u"added":1})

                if flannelfox.settings['debugLevel'] >= 5:
                    print "Torrent Added: {0}".format(transmissionResponseCode)


        if transmissionResponseCode == Responses.success:
            # TODO: Remove extra trackers, this is needed due to a bug in
            # transmission that prevents non-communication related errors
            # from being seen when there is a back tracker.
            pass
            ###self.removeExtraTrackers(hashString=torrentAdded["hashString"])

            ###time.sleep(10)
            ###return True

        else:
            # Here we need to handle any special errors encountered when
            # trying to add a torrent

            if flannelfox.settings['debugLevel'] >= 5:
                print "Torrent Add Failed: {0}".format(transmissionResponseCode)

            # Get Current Time
            sinceEpoch = int(time.time())

            if (transmissionResponseCode == Responses.bad_torrent or
#                transmissionResponseCode == Responses.duplicate or
                transmissionResponseCode == Responses.torrent_not_found or
                transmissionResponseCode == Responses.torrent_bad_request or
                transmissionResponseCode == Responses.torrent_service_unavailable or
                transmissionResponseCode == Responses.torrent_no_response):
                # Torrent is broken so lets delete it from the DB, this leaves the opportunity
                # for the torrent to later be added again
                TorrentDB.deleteTorrent(url=url)

            time.sleep(10)
            return False

            
    def getSlowestSeeds(self,num=None):
        '''
        Look for the slowest seeding torrents, slowest first

        Takes:
            num - Int, the number of torrent objects to return
        '''
        slowestSeeds = []

        torrents = self.getFinishedSeeding()

        for torrent in torrents:
            if torrent.isSeeding():
                slowestSeeds.append(torrent)

        # Sort torrents if we have any
        if len(slowestSeeds) > 0:
            slowestSeeds.sort(key=lambda torrent: torrent["rateUpload"])

        if num is None or len(slowestSeeds) <= num:
            return slowestSeeds
        return slowestSeeds[:num]


    def getDormantSeeds(self,num=None):
        '''
        Looks for a seeding torrent with the longest time since active, returns
        torrents, oldest first
        '''
        dormantSeeds = []


        torrents = self.getFinishedSeeding()

        for torrent in torrents:
            if torrent.isDormant():
                dormantSeeds.append(torrent)

        # Sort torrents if we have any
        if len(dormantSeeds) > 0:
            dormantSeeds.sort(key=lambda torrent: torrent["activityDate"], reverse=True)

        if dormantSeeds is None or len(dormantSeeds) <= num:
            return dormantSeeds
        return dormantSeeds[:num]


    def getDownloading(self,num=None):
        '''
        Returns a list of torrents that are downloading

        Takes:
            num - Int, the number of torrents to return
        '''
        downloadingTorrents = []

        torrents = self.elements["queue"]

        for torrent in torrents:
            if torrent.isDownloading():
                downloadingTorrents.append(torrent)

        if downloadingTorrents is None or len(downloadingTorrents) <= num:
            return downloadingTorrents
        return downloadingTorrents[:num]


    def getSeeding(self,num=None):
        '''
        Returns a list of torrents that are Seeding

        Takes:
            num - Int, the number of torrents to return
        '''
        seedingTorrents = []

        torrents = self.elements["queue"]

        for torrent in torrents:
            if torrent.isSeeding():
                seedingTorrents.append(torrent)

        if seedingTorrents is None or len(seedingTorrents) <= num:
            return seedingTorrents
        return seedingTorrents[:num]

        
    def getFinishedSeeding(self, num=None):
        '''
        Returns a list of torrents that are finished seeding

        Takes:
            num - Int, the number of torrents to return
        '''
        torrents = self.getSeeding()
        finishedSeeding = []

        for torrent in torrents:
            if torrent.isFinished():
                finishedSeeding.append(torrent)

        if num is None or len(finishedSeeding) <= num:
            return finishedSeeding
        return finishedSeeding[:num]


    def setAltSpeed(self,enabled=False):
        '''
        Enables/Disables the altSpeed setting in transmission

        Takes:
            enabled - bool, True is ON, False is OFF

        Returns:
            bool, True if action completed
        '''

        # Method
        commandJson = u'{"method":"session-set",'

        # Arguments
        commandJson += u'"arguments":{'

        # Ids
        commandJson += u'"alt-speed-time-enabled":{0}'.format(str(enabled).lower())

        # Close Arguments
        commandJson += u'"},'

        # Tag (not strictly needed)
        commandJson += u'"tag":{0}'.format(self.tagGenerator.next())+u'}'

        # Make sure the call worked
        response, httpResponseCode, transmissionResponseCode = self.__parseTransmissionResponse(commandJson)

        if transmissionResponseCode == Responses.success:
            return True
        else:
            return False

            
    def restart(self):
        self.__transmissionInit(action=u'restart')

        
    def start(self):
        self.__transmissionInit(action=u'restart')

        
    def stop(self):
        self.__transmissionInit(action=u'restart')
