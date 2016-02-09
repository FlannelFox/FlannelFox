#-------------------------------------------------------------------------------
# Name:        TorrentDB
# Purpose:     These functions handle writing/reading torrent information
#              to/from the sqlite database
#
# TODO: Turn this into a class that can be instantiated as various
#       database types.
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-


# System Includes
import sqlite3 as sql
import time

# FlannelFox Includes
from FlannelFox import Settings
from FlannelFox.TorrentTools import Torrents

# Import the Torrent Types
from FlannelFox.TorrentTools.Torrents import TORRENT_TYPES

def dictFactory(cursor, row, ignore=None):
    '''
    Used to return an actual dict of values instead of Row
    '''
    if ignore is None:
        ignore=[]

    d = {}
    for idx, col in enumerate(cursor.description):

        # If the column is empty then skip it
        # If the column is queue management related then skip it

        if row[idx] is None or unicode(col[0]) in ignore:
            pass    # Ignore these fields during conversion
        else:
            d[unicode(col[0])] = unicode(row[idx])

    return d


def addTorrentsToQueue(queue):
    '''
    Write the Current Torrent Queue to the database

    Takes a queue of torrents as a parameter
    '''

    try:

        # Populate the insert list, this should be a list of sql statements
        insertStatements = []

        # Get current time, used for queuedOn field in DB
        sinceEpoch = int(time.time())

        for torrent in queue:
            keys = [u"queuedOn",u"added"]
            vals = [unicode(sinceEpoch),unicode(0)]

            notExistsWhereClause = u""

            for key, val in torrent.iteritems():
                if notExistsWhereClause != "":
                     notExistsWhereClause += u" AND "

                if isinstance(val, (unicode)):
                    keys.append(key)
                    vals.append(u"'{0}'".format(val.replace('\'','\'\'')))
                    notExistsWhereClause += u"`{0}` = '{1}'".format(key, val.replace('\'','\'\''))
                elif val is None:
                    keys.append(key)
                    vals.append(u'')
                    notExistsWhereClause += u"`{0}` = u''".format(key)
                elif isinstance(val, (int,float)):
                    keys.append(unicode(key))
                    vals.append(unicode(val))
                    notExistsWhereClause += u"`{0}` = {1}".format(key, val)

            query = u"INSERT INTO {0} ({1}) VALUES ({2})".format(Settings.QUEUED_TORRENTS_TABLE, ",".join(keys), ",".join(vals))
            insertStatements.append(query)


        # Insert each torrent into the DB
        for statement in insertStatements:
            execDB(statement)

    except sql.Error as e:
        ''' TODO do something smart when this happens '''
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, statement)
        return False
    
    except Exception as e:
        ''' TODO do something smart when this happens '''
        return False

    return True


def deleteTorrent(hashString=None,url=None):
    '''
    Removes a torrent from the database
    
    Takes a torrent as a parameter
    '''
    
    try:
        print "Torrent delete called"
    
        # The view the query should use
        currentView = Settings.QUEUED_TORRENTS_TABLE
        
        # Build the Where Clause for the query
        if hashString is not None:
            whereClause = u"`hashString` = '{0}'".format(hashString)
        elif url is not None:
            whereClause = u"`url` = '{0}'".format(url)
        else:
            return
            
        query = u"DELETE FROM {0} WHERE {1}".format(currentView, whereClause)

        execDB(query)

    except sql.Error as e:
        ''' TODO do something smart when this happens '''
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, statement)
    except Exception as e:
        ''' TODO do something smart when this happens '''
        pass


def torrentExists(torrent=None, url=None, hashString=None):
    '''
    Checks to see if the torrent is already in the database

    Takes:
        A torrent as a parameter OR
        A hashString and url 

    Returns True if it exists or False if it does not
    '''
   
    try:

        # Default for exists
        exists = None

        # The view the query should use
        currentView = Settings.GENERIC_TORRENTS_VIEW
        
        # Build the Where Clause for the query
        whereClause = u''
        
        if torrent is not None:
            for key, val in torrent.iteritems():

                if isinstance(val, unicode) and key not in Settings.FUZZY_PROPERTIES:
                    if whereClause != u'':
                        whereClause += u" AND "
                    whereClause += u"`{0}` = '{1}'".format(key,val.replace('\'','\'\''))


            # Decide what View to use
            if torrent["torrentType"] == u"tv":
                currentView = Settings.TV_TORRENTS_VIEW
            elif torrent["torrentType"] == u"movie":
                currentView = Settings.MOVIE_TORRENTS_VIEW
            elif torrent["torrentType"] == u"music":
                currentView = Settings.MUSIC_TORRENTS_VIEW
        
        
            query = u"SELECT torrentTitle FROM `{0}` WHERE ".format(currentView)
            query += whereClause

            #print "Check Exists: {0}".format(query)

            # Query to see if the torrent is already in the DB
            exists = queryDB(query)

        elif url is not None and hashString is not None:

            # The view the query should use
            currentView = Settings.QUEUED_TORRENTS_TABLE

            # Build the Where Clause for the query
            whereClause = u"`hashString` = '{0}' AND `url` = '{0}'".format(hashString, url)

            query = u"SELECT torrentTitle FROM `{0}` WHERE {1}".format(currentView, whereClause)

            exists = queryDB(query)

        if exists is None:
            pass

        elif len(exists) > 0:
            return True
        else:
            return False

    except sql.Error as e:
        ''' TODO do something smart when this happens '''
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, statement)

        # This is false because we were not able to get an answer back
        return False
    
    except Exception as e:
        ''' TODO do something smart when this happens '''
        # This is false because we were not able to get an answer back
        return False


def execDB(query):
    '''
    Executes a query and tries to do any cleanup if there is an issue


    '''

    try:
        # SQL Connection
        sqlConnection = sql.connect(Settings.TORRENT_DB)

        with sqlConnection:

            # Set the results to be in dictionary form
            sqlConnection.row_factory = dictFactory

            # Establish a cursor and then make the query
            sqlCursor = sqlConnection.cursor()

            sqlCursor.execute(query)

            return sqlCursor.rowcount

    except sql.Error as e:
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, query)
        return 0
    
    except Exception as e:
        ''' TODO do something smart when this happens '''
        pass


def queryDB(query):
    '''
    Perform a query on the database, this should not be called directly

    Takes:
        a SQL statement as a parameter
    
    Returns:
        a list of dicts, each dict holding the row information
    '''

    try:
        # SQL Connection
        sqlConnection = sql.connect(Settings.TORRENT_DB)

        with sqlConnection:

            # Set the results to be in dictionary form
            sqlConnection.row_factory = dictFactory

            # Establish a cursor and then make the query
            sqlCursor = sqlConnection.cursor()
            sqlCursor.execute(query)

            rows = sqlCursor.fetchall()

            # Check for None, this might happen and should return an empty dict
            if rows is None:
                rows = {}

        return rows

    except sql.Error as e:
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, query)
        return {}

    except Exception as e:
        ''' TODO do something smart when this happens '''
        return {}


def getTorrentInfo(hashString=None,fields=[]):
    '''
    Returns the desired information about a torrent

    Takes:
        hashString - The hash of the desired torrent
        fields - List of fields that you want returned

    Returns:
        Dict of key,val
    '''

    try:

        # Build the field selectors
        selectors = u"`{0}`".format("`,`".join(fields))

        # Replace empty set with *
        if isinstance(fields,list) and len(fields) <= 0:
            selectors = u'*'

        # If just a single selector is given then use it
        if isinstance(fields,(unicode,str)):
            selectors = u"`{0}`".format(fields)


        # Build the query
        query = u"SELECT {0} FROM {1} WHERE `hashString` = '{2}'".format(selectors,Settings.QUEUED_TORRENTS_TABLE,hashString)

        # Query DB
        results = queryDB(query)

        if results is None:
           results = {}

        return results

    except sql.Error as e:
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, query)
        return {}

    except Exception as e:
        ''' TODO do something smart when this happens '''
        return {}


def getDestinations():
    '''
    Returns a List of torrentDestinations

    DEPRECIATED
    '''
    print "This command is depreciated and should not be used"
    locations = [Settings.DEFAULT_TORRENT_LOCATION]

    query = u"SELECT `feedDestination` from {0} Group By `feedDestination`".format(Settings.QUEUED_TORRENTS_TABLE)

    responses = queryDB(query)

    for response in responses:
        locations.append(response[u"feedDestination"])

    return locations


def getQueuedTorrents(fields=[],num=None):
    '''
    Returns the desired information about the torrent queue

    Takes:
        fields - List of fields that you want returned
        num - Number of rows to return

    Returns:
        Dict of key,val
    '''

    try:

        # Build the field selectors
        selectors = u"`"+"`,`".join(fields)+"`"

        # Replace empty set with *
        if isinstance(fields,list) and len(fields) <= 0:
            selectors = u"*"

        # If just a single selector is given then use it
        if isinstance(fields,(unicode,str)):
            selectors = u"`"+fields+"`"

        # Build the query
        query = u"SELECT {0} FROM {1}".format(selectors,Settings.QUEUED_TORRENTS_VIEW)

        if num is not None:
            query += u" LIMIT {0}".format(num)

        # Query DB
        results = queryDB(query)

        if results is None:
            return []
        else:
            return results

    except sql.Error as e:
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, query)
        return []

    except Exception as e:
        ''' TODO do something smart when this happens '''
        return []


def getQueuedTorrentsCount():
    '''
    Returns the total number of torrents waiting in queue

    Returns:
        int
    '''

    try:

        # Build the query
        query = u"SELECT count(added) AS downloadsQueued FROM {0} WHERE added=0".format(Settings.QUEUED_TORRENTS_VIEW)

        # Query DB
        results = queryDB(query)
        
        return results[0][u"downloadsQueued"]
    
    except sql.Error as e:
        if Settings.DEBUG_LEVEL >= 10: print "There was a problem executing the SQL query:\n{0}\n{1}".format(e, query)
        return -1

    except Exception as e:
        ''' TODO do something smart when this happens '''
        return -1
