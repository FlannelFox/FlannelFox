#-------------------------------------------------------------------------------
# Name:        Trackers
# Purpose:     Collection of tracker related settings and funcs
#
# TODO: Perhaps we should all for extending of this via config
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

class Responses(object):
    '''
    Tracker responses we can get and if we should consider them for torernt
        removal or not. It is important to not that these are partial matches;
        this means if the phrase is found anywhere in the tracker reply it
        will be labeled as such.


    Remove is a list of messages that should cause the torrent to be removed

    OK is a list of messages that are ok and should not result in the torrent
        being removed. (Not used as of yet, but could be in the future)
    '''
    Remove = [
        'unregistered torrent',
        'Unregistered torrent',
        'torrent not registered with this tracker',
        'invalid torrent'
    ]
    
    Ok = [
        'tracker down for scheduled maintenance'
    ]

