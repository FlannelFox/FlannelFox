#-------------------------------------------------------------------------------
# Name:		FreeSpace Module
# Purpose:	Returns the free space in a folder/drive in bytes
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import ctypes, os, platform

def check(folder,size='G'):
	''' Return folder/drive free space (in bytes) '''

	# format the response in the desired size
	if size == 'B': #Byte
		divisor = 1.0
	if size == 'K': #KiloByte
		divisor = 1024.0
	if size == 'M': #MegaByte
		divisor = 1024.0**2
	if size == 'G': #GigaByte
		divisor = 1024.0**3
	if size == 'T': #TeraByte
		divisor = 1024.0**4


	try:
		if platform.system() == u'Windows':
			freeBytes = ctypes.c_ulonglong(0)
			ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(freeBytes))
			return freeBytes.value/divisor
		else:
			st = os.statvfs(folder)
			return st.f_bavail * st.f_frsize/divisor
	except OSError:

		# Let's return a really large value so this folder is not considered for removal
		return 9*(1024**4)
