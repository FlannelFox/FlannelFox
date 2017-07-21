#-------------------------------------------------------------------------------
# Name:		UsedSpace
# Purpose:	Returns the used space in a folder/drive in bytes
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import ctypes, platform, subprocess, re, math

# Logging
from flannelfox import logging

def check(folder,size='G'):
	''' Return folder/drive used space (in bytes) '''

	logger = logging.getLogger(__name__)

	# format the response in the desired size
	if size == 'B': #Byte
		divisor = 1/1024.0
	if size == 'K': #KiloByte
		divisor = 1024.0
	if size == 'M': #MegaByte
		divisor = 1024.0**1
	if size == 'G': #GigaByte
		divisor = 1024.0**2
	if size == 'T': #TeraByte
		divisor = 1024.0**3


	logger.debug('Checking Space on: {0}'.format(folder))

	try:

		# TODO: figure out how to measure used space in windows, This does not work
		if platform.system() == u'Windows':
			return 2000
			freeBytes = ctypes.c_ulonglong(0)
			ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(freeBytes))
			ctypes.windll.kernel32.GetDisk
			GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(freeBytes))
			return freeBytes.value/divisor
		else:
		# TODO: Change this to walk the directory and add up the sizes, we want
		# this to be all python after all

			response, error = subprocess.Popen(['du','-s',folder], stdout=subprocess.PIPE).communicate()

			response = response.decode('utf-8')

			if error is not None:
				raise ValueError

			usedspace = re.match(r'^(?P<size>\d+)', response)
			usedspace = int(usedspace.group('size'))/divisor
			usedspace = int(math.ceil(usedspace))

			return usedspace

	except ValueError as e:
		# TODO: This should not happen, but if it does let's alert someone that
		# it did. We will return 0 since we did not get a number
		return 0
