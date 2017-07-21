# -*- coding: utf-8 -*-

import flannelfox.settings

levels = {
	"CRITICAL": 50,
	"ERROR": 40,
	"WARNING": 30,
	"INFO": 20,
	"THREADINGINFO": 15,
	"DEBUG": 10,
	"THREADINGDEBUG": 5,
	"NOTSET": 0,
	"50": 50,
	"40": 40,
	"30": 30,
	"20": 20,
	"15": 15,
	"10": 10,
	"5": 5,
	"0": 0
}

def __sanitizeLevel(lvl="NOTSET"):
	'''
	Makes sure the level returned is consistent
	'''
	if lvl == "":
		lvl="NOTSET"
	return lvl.upper()

def getLevel():
	lvl = flannelfox.settings.getSettings()["debugLevel"]
	lvl = __sanitizeLevel(lvl)
	return levels[lvl]