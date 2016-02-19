#!/usr/bin/python2.7
#-------------------------------------------------------------------------------
# Name:        logging
# Purpose:     Used to uniformly creat logs for our modules
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import logging, logging.handlers, os
import flannelfox

_handles = {};

def getLogger(name=''):
    # Setup the logging agent that will rotate each day
    _logger = logging.getLogger(name)
    _logger.setLevel(flannelfox.debuglevels.getLevel())
    _handles[name] = logging.handlers.TimedRotatingFileHandler(
        os.path.join(
            flannelfox.settings['files']['privateDir'],
            name+'.log'
        ),
        when='d',
        interval=1,
        backupCount=1
    )
    _logger.addHandler(_handles[name])
    return _logger

def getFileHandle(name=''):
    return _handles[name]

