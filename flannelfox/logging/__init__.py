#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# Name:		logging
# Purpose:	Used to uniformly creat logs for our modules
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import logging, logging.handlers
import flannelfox.debuglevels, flannelfox.settings
import os

handles = {};

def __init():
	# Add some custom log levels
	THREADINGINFO = flannelfox.debuglevels.levels["THREADINGINFO"]
	THREADINGDEBUG = flannelfox.debuglevels.levels["THREADINGDEBUG"]

	def threadingInfo(self, msg, *args, **kws):
		if self.isEnabledFor(THREADINGINFO):
			self._log(THREADINGINFO, msg, args, **kws)

	def threadingDebug(self, msg, *args, **kws):
		if self.isEnabledFor(THREADINGDEBUG):
			self._log(THREADINGDEBUG, msg, args, **kws)

	logging.addLevelName(THREADINGINFO, "THREADINGINFO")
	logging.addLevelName(THREADINGDEBUG, "THREADINGDEBUG")
	logging.Logger.threadingInfo = threadingInfo
	logging.Logger.threadingDebug = threadingDebug


def __getLogDir():
	return flannelfox.settings.getSettings()['files']['logDir']


def getLogger(name='flannelfox'):

	try:

		logger = logging.getLogger(name)
		logger.propagate = False

		# Setup the logging agent that will rotate each day
		if name not in handles:

			# Format the logs like this
			logFormatting = logging.Formatter("[{0}][%(asctime)s.%(msecs)03d] %(message)s".format(name), "%H%M%S")

			# Setup a filter to limit the scope of the logs
			logFilter = logging.Filter(name)

			logger.setLevel(flannelfox.debuglevels.getLevel())

			logFile = os.path.join(
				__getLogDir(),
				name+'.log'
			)

			logDir = os.path.join(
				__getLogDir()
			)

			if not os.path.exists(logDir):
				os.makedirs(logDir)

			handles[name] = logging.handlers.TimedRotatingFileHandler(
				logFile,
				when='d',
				interval=1,
				backupCount=1
			)

			handles[name].setFormatter(logFormatting)

			handles[name].addFilter(logFilter)

			logger.addHandler(handles[name])

		return logger

	except Exception:
		raise ValueError('Could not create a logging instance')

def getFileHandle(name='flannelfox'):
	if name not in handles.keys():
		raise KeyError

	return handles[name]

__init()