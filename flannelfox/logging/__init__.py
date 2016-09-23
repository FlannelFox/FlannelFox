#!/usr/bin/python2.7
#-------------------------------------------------------------------------------
# Name:        logging
# Purpose:     Used to uniformly creat logs for our modules
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import logging, logging.handlers, os
import flannelfox

# Add some custom log levels
THREADINGINFO = 15
THREADINGDEBUG = 5
logging.addLevelName(THREADINGINFO, "THREADINGINFO")
logging.addLevelName(THREADINGDEBUG, "THREADINGDEBUG")

def threadingInfo(self, msg, *args, **kws):
    if self.isEnabledFor(THREADINGINFO):
        self._log(THREADINGINFO, msg, args, **kws)

def threadingDebug(self, msg, *args, **kws):
    if self.isEnabledFor(THREADINGDEBUG):
        self._log(THREADINGDEBUG, msg, args, **kws)

logging.Logger.threadingInfo = threadingInfo
logging.Logger.threadingDebug = threadingDebug

handles = {};

def getLogger(name=''):

    logger = logging.getLogger(name)
    logger.propagate = False

    # Setup the logging agent that will rotate each day
    if name not in handles:

        # Format the logs like this
        logFormatting = logging.Formatter("[{0}][%(asctime)s.%(msecs)03d] %(message)s".format(name), "%H%M%S")

        # Setup a filter to limit the scope of the logs
        logFilter = logging.Filter(name)

        logger.setLevel(flannelfox.debuglevels.getLevel())
        
        handles[name] = logging.handlers.TimedRotatingFileHandler(
            os.path.join(
                flannelfox.settings['files']['privateDir'],
                name+'.log'
            ),
            when='d',
            interval=1,
            backupCount=1
        )


        handles[name].setFormatter(logFormatting)

        handles[name].addFilter(logFilter)

        logger.addHandler(handles[name])

    return logger

def getFileHandle(name=''):
    return handles[name]

