# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
import os

from flannelfox.torrenttools.TorrentQueue import Queue
from flannelfox.torrenttools import Torrents

class TestTorrentQueue(unittest.TestCase):

	testDatabaseFile = 'ff.db'

	def removeDatabase(self):
		try:
			os.remove(self.testDatabaseFile)
		except Exception:
			pass

	@patch.object(Queue, 'databaseTorrentBlacklisted')
	@patch.object(Queue, 'databaseTorrentExists')
	def test_Queue(self, mockDatabaseTorrentExists, mockDatabaseTorrentBlacklisted):

		self.removeDatabase()

		torrentQueue = Queue()

		mockDatabaseTorrentBlacklisted.return_value = False
		mockDatabaseTorrentExists.return_value = False

		# Ensure len returns a valid answer
		self.assertEqual(len(torrentQueue), 0)

		# Make sure appending an item works
		torrentQueue.append(Torrents.TV(torrentTitle='some.show.s01e01.720p.junk.here'))
		self.assertEqual(len(torrentQueue), 1)

		# Make sure appending a duplicate item does not work
		torrentQueue.append(Torrents.TV(torrentTitle='some.show.s01e01.720p.junk.here'))
		self.assertEqual(len(torrentQueue), 1)

		# Add a different item and make sure it works
		torrentQueue.append(Torrents.TV(torrentTitle='some.show.s01e02.720p.junk.here2'))
		self.assertEqual(len(torrentQueue), 2)

		mockDatabaseTorrentBlacklisted.return_value = True
		mockDatabaseTorrentExists.return_value = False

		# Check if Blacklisted torrent gets blocked
		torrentQueue.append(Torrents.TV(torrentTitle='some.show.s01e02.720p.junk.here3'))
		self.assertEqual(len(torrentQueue), 2)


		mockDatabaseTorrentBlacklisted.return_value = False
		mockDatabaseTorrentExists.return_value = True

		# Check if Existing Torrent in Database gets blocked
		torrentQueue.append(Torrents.TV(torrentTitle='some.show.s01e02.720p.junk.here3'))
		self.assertEqual(len(torrentQueue), 2)

		mockDatabaseTorrentBlacklisted.return_value = False
		mockDatabaseTorrentExists.return_value = False

if __name__ == '__main__':
	unittest.main()
