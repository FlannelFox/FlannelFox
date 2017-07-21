# -*- coding: utf-8 -*-

import unittest, os
from unittest.mock import patch

from flannelfox.torrentclients import Torrent

class TestTorrentClientTorrent(unittest.TestCase):

	@patch.object(Torrent, 'getDatabaseData')
	def test_torrent(self, mockDatabases):

		testTorrent = Torrent(
			hashString='123123123',
			doneDate=1,
			uploadRatio='1.0'
		)

		mockDatabases.return_value = [{
			'title': 'some title',
			'minTime': '1',
			'minRatio': '1.0',
			'comparison': 'and',
			'doneDate': 1
		}]

		self.assertTrue(testTorrent.isFinished())

		mockDatabases.return_value = [{
			'title': 'some title',
			'minTime': '1',
			'minRatio': '2.0',
			'comparison': 'and',
			'doneDate': 9999999999
		}]

		self.assertFalse(testTorrent.isFinished())

		mockDatabases.return_value = [{
			'title': 'some title',
			'minTime': '0',
			'minRatio': '1.0',
			'comparison': 'or',
			'doneDate': 1
		}]

		self.assertTrue(testTorrent.isFinished())

		mockDatabases.return_value = [{
			'title': 'some title',
			'minTime': '1',
			'minRatio': '2.0',
			'comparison': 'and',
			'doneDate': 9999999999
		}]

		self.assertFalse(testTorrent.isFinished())

if __name__ == '__main__':
	unittest.main()
