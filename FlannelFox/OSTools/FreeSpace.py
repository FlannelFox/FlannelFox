#-------------------------------------------------------------------------------
# Name:        FreeSpace Module
# Purpose:     Returns the free space in a folder/drive in bytes
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import ctypes, os, platform, sys

def check(folder,size=u'G'):
    ''' Return folder/drive free space (in bytes) '''

    # format the response in the desired size
    if size == u'B': #Byte
        divisor = 1.0
    if size == u'K': #KiloByte
        divisor = 1024.0
    if size == u'M': #MegaByte
        divisor = 1024.0**2
    if size == u'G': #GigaByte
        divisor = 1024.0**3
    if size == u'T': #TeraByte
        divisor = 1024.0**4


    try:
        if platform.system() == u'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value/divisor
        else:
            st = os.statvfs(folder)
            return st.f_bavail * st.f_frsize/divisor
    except OSError:
        print 'The Folder [%s] does not exist.' % (folder)

        # Let's return a really large value so this folder is not considered for removal
        return 9*(1024**4)
