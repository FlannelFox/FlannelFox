# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from flannelfox import logging

class TestLogging(unittest.TestCase):

	@classmethod
	def __resetHandles(self):
		logging.handles = {}


	def test_getLogger(self):
		self.__resetHandles()

		logging.getLogger()


	def test_getFileHandleReturnsHandle(self):
		self.__resetHandles()

		logging.getLogger()

		handle = logging.getFileHandle()
		self.assertIsInstance(handle, logging.logging.handlers.TimedRotatingFileHandler)


	def test_getFileHandleDetectsMissingKey(self):
		self.__resetHandles()

		with self.assertRaises(KeyError):
			logging.getFileHandle('')


if __name__ == '__main__':
	unittest.main()
