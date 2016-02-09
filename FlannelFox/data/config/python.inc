#Variables that are needed by the python scripts to function


print "Loaded"
# #############################################################################
# Files and other path related variables
#
# Default torrent location, this is the top level folder that should contain all
# folders that torrents are stored in
# #############################################################################
DEFAULT_TORRENT_LOCATION = ur"###DOWNLOAD_DIR###"
# #############################################################################



# #############################################################################
# Debug Level, set to 0 to disable messages
# #############################################################################
# True: Show Debug Message; False: Hide Debug Messages
# 1 - Show only needed Status messages
# 5 - Show informational logging
# 10 - Show all debug info
DEBUG_LEVEL = 1
# #############################################################################



# #############################################################################
# Minimum free space to keep on paths, this is a one size fits all directive
# measured in MB. Ex. 1024 = 1GB
#
# Set to 0 to disable
# #############################################################################
MINIMUM_FREE_SPACE = 0
# #############################################################################



# #############################################################################
# Max used space in root folder of storage
# This is handy for people who have many subfolders of torrents under one main
# directory
# Use this to ensure the total size of the files in the root folder does not
# fill the drive.
# Measured in GB. Ex. 1 = 1GB
#
# Set to 0 to disable
# #############################################################################
MAX_USED_SPACE = ###MAX_USED_SPACE###
MAX_USED_SPACE_DIR = DEFAULT_TORRENT_LOCATION
# #############################################################################



# #############################################################################
# Thread timers, this controls how often each application should run
# #############################################################################
# QueueDaemon Thread Sleep
QUEUEDAEMON_THREAD_SLEEP = 60 #SECONDS

# RSSDaemon Thread Sleep
RSSDAEMON_THREAD_SLEEP = 60 #SECONDS
# #############################################################################



# #############################################################################
# Transmission RPC Info, this is needed to communicate with the server
# #############################################################################
TRANSMISSION_RPC_INFO = {
    u"host":u"###TC_ADDR###",
    u"https":False,
    u"port":u"###TC_PORT###",
    u"rpcLocation":u"transmission/rpc",
    u"user":u"###TC_USER###",
    u"password":u"###TC_PASS###",
}
# #############################################################################



# #############################################################################
# Torrent Queue Limits
# #############################################################################
# Max total torrents
MAX_TORRENTS = ###MAX_TORRENTS###

# Max Downloading Torrents
MAX_DOWNLOADING_TORRENTS = ###MAX_DOWNLOADING_TORRENTS###
# #############################################################################



# #############################################################################
# Queue Management Style
#   This controls whether torrents should be removed only when queue space is needed
#   or if they should be removed as soon as they meet their seeding requirements
#   Both settings will ensure seeding limits are met
#
# 0 = OFF, 1 = ON
# #############################################################################
STRICT_QUEUE_MANAGEMENT = ###STRICT_QUEUE_MANAGEMENT###
# #############################################################################
