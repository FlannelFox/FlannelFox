# -*- coding: utf-8 -*-

import unittest
import os


from flannelfox.torrenttools import Torrents
from flannelfox.databases import Databases
from flannelfox.torrenttools.TorrentQueue import Queue
from flannelfox.settings import settings

class TestDatabases(unittest.TestCase):

	testDatabaseFile = os.path.join(settings['files']['privateDir'],'flannelfox.db')


	def removeDatabase(self):
		try:
			os.remove(self.testDatabaseFile)
		except Exception:
			pass


	def test_AddBlacklistedTorrent(self):

		self.removeDatabase()

		dbObject = Databases(
			dbType = "SQLITE3",
			databaseSettings = {
				'databaseLocation': self.testDatabaseFile
			}
		)

		dbObject.addBlacklistedTorrent(url='http://testurl.com/test')

		self.assertTrue(dbObject.torrentBlacklisted(url='http://testurl.com/test'))

		self.removeDatabase()


	def test_addTorrentsToQueue_torrentExists_deleteTorrent(self):

		self.removeDatabase()

		testTorrent = Torrents.TV(torrentTitle='some.show.s01e01.720p.junk.here', url='http://testurl.com/test')
		testTorrent2 = Torrents.TV(torrentTitle='some.show.s01e02.720p.junk.here', url='http://testurl.com/test2')

		torrentQueue = Queue()
		torrentQueue.append(testTorrent)

		dbObject = Databases(
			dbType = "SQLITE3",
			databaseSettings = {
				'databaseLocation': self.testDatabaseFile
			}
		)

		dbObject.addTorrentsToQueue(torrentQueue)
		self.assertTrue(dbObject.torrentExists(testTorrent))

		dbObject.updateHashString(
			{
				'hashString': 'abc123'
			},
			{
				'url':'http://testurl.com/test'
			}
		)

		self.assertTrue(
			len(dbObject.getTorrentInfo(hashString='abc123', selectors=['torrentTitle','url'])) == 1
		)


		torrentQueue = Queue()
		torrentQueue.append(testTorrent2)

		dbObject.addTorrentsToQueue(torrentQueue)

		self.assertTrue(
			dbObject.getQueuedTorrentsCount() == 2
		)

		self.assertTrue(
			len(dbObject.getQueuedTorrents()) == 2
		)

		dbObject.deleteTorrent(url='http://testurl.com/test')
		self.assertFalse(dbObject.torrentExists(testTorrent))

		self.assertTrue(
			dbObject.getQueuedTorrentsCount() == 1
		)

		dbObject.deleteTorrent(url='http://testurl.com/test2')
		self.assertFalse(dbObject.torrentExists(testTorrent))

		self.assertTrue(
			dbObject.getQueuedTorrentsCount() == 0
		)

		self.removeDatabase()


if __name__ == '__main__':
	unittest.main()