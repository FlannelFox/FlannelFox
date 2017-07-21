# -*- coding: utf-8 -*-

import unittest, os
from unittest.mock import patch, PropertyMock

import flannelfox
from flannelfox.settings import settings
from flannelfox.torrentclients import Transmission, Torrent
from flannelfox.torrentclients.Transmission import Responses

class TestTransmission(unittest.TestCase):

	def getTestTorrents(self):
		return [
			Torrent(
				hashString='hashstring',
				id=123,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=0,
				downloadDir=None,
				status=0,
			),
			Torrent(
				hashString='hashstring',
				id=123,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=1,
				downloadDir=None,
				status=1,
			),
			Torrent(
				hashString='hashstring',
				id=123,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=2,
				downloadDir=None,
				status=2,
			),
			Torrent(
				hashString='hashstring',
				id=123,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=3,
				downloadDir=None,
				status=3,
			),
			Torrent(
				hashString='hashstring',
				id=123,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=4,
				downloadDir=None,
				status=4,
			),
			Torrent(
				hashString='hashstring',
				id=51,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419654, #Wednesday, June 14, 2017 5:54:14 AM
				rateUpload=0,
				downloadDir=None,
				status=5,
			),
			Torrent(
				hashString='hashstring',
				id=52,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=0,
				downloadDir=None,
				status=5,
			),
			Torrent(
				hashString='hashstring',
				id=123,
				error=None,
				errorString=None,
				uploadRatio=1.2,
				percentDone=100,
				doneDate=1494741255, #Sunday, May 14, 2017 5:54:15 AM
				activityDate=1497419655, #Wednesday, June 14, 2017 5:54:15 AM
				rateUpload=6,
				downloadDir=None,
				status=6,
			)
		]

	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_getQueue(self, SLEEP_SHORT, SLEEP_LONG):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		self.assertIsInstance(client.getQueue(), list)


	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_updateQueue(self, SLEEP_SHORT, SLEEP_LONG):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		self.assertIsInstance(client.updateQueue(), tuple)


	@patch.object(flannelfox.torrentclients.Transmission.Client, '_Client__parseTransmissionResponse')
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_verifyTorrent(self, SLEEP_SHORT, SLEEP_LONG, mock_parseTransmissionResponse):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		mock_parseTransmissionResponse.return_value = ('data', Responses.invalidArgument)
		self.assertIsInstance(client.verifyTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.verifyTorrent(hashString='test_hash'), False)

		mock_parseTransmissionResponse.return_value = ('data', Responses.success)
		self.assertIsInstance(client.verifyTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.verifyTorrent(hashString='test_hash'), True)


	@patch.object(flannelfox.torrentclients.Transmission.Client, '_Client__parseTransmissionResponse')
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_stopTorrent(self, SLEEP_SHORT, SLEEP_LONG, mock_parseTransmissionResponse):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		mock_parseTransmissionResponse.return_value = ('data', Responses.invalidArgument)
		self.assertIsInstance(client.stopTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.stopTorrent(hashString='test_hash'), False)

		mock_parseTransmissionResponse.return_value = ('data', Responses.success)
		self.assertIsInstance(client.stopTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.stopTorrent(hashString='test_hash'), True)


	@patch.object(flannelfox.torrentclients.Transmission.Client, '_Client__parseTransmissionResponse')
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_startTorrent(self, SLEEP_SHORT, SLEEP_LONG, mock_parseTransmissionResponse):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		mock_parseTransmissionResponse.return_value = ('data', '200', Responses.invalidArgument)
		self.assertIsInstance(client.startTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.startTorrent(hashString='test_hash'), False)

		mock_parseTransmissionResponse.return_value = ('data', '200', Responses.success)
		self.assertIsInstance(client.startTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.startTorrent(hashString='test_hash'), True)


	@patch.object(flannelfox.torrentclients.Transmission.Client, '_Client__parseTransmissionResponse')
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_removeTorrent(self, SLEEP_SHORT, SLEEP_LONG, mock_parseTransmissionResponse):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		mock_parseTransmissionResponse.return_value = ('data', '200', Responses.invalidArgument)
		self.assertIsInstance(client.removeTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.removeTorrent(hashString='test_hash'), False)

		mock_parseTransmissionResponse.return_value = ('data', '200', Responses.success)
		self.assertIsInstance(client.removeTorrent(hashString='test_hash'), bool)
		self.assertEqual(client.removeTorrent(hashString='test_hash'), True)


	@patch.object(flannelfox.torrentclients.Transmission.Client, '_Client__parseTransmissionResponse')
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_removeExtraTrackers(self, SLEEP_SHORT, SLEEP_LONG, mock_parseTransmissionResponse):

		SLEEP_LONG.return_value = 0
		SLEEP_SHORT.return_value = 0

		client = Transmission.Client()
		mock_parseTransmissionResponse.return_value = ('data', '200', Responses.invalidArgument)
		self.assertIsInstance(client.removeExtraTrackers(hashString='test_hash'), bool)
		self.assertEqual(client.removeExtraTrackers(hashString='test_hash'), True)


	@patch.object(flannelfox.torrentclients.Transmission.Client, '_Client__parseTransmissionResponse')
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_LONG', new_callable=PropertyMock)
	@patch('flannelfox.torrentclients.Transmission.Client.SLEEP_SHORT', new_callable=PropertyMock)
	def test_addTorrentURL(self, SLEEP_SHORT, SLEEP_LONG, mock_parseTransmissionResponse):

		client = Transmission.Client()

		#test duplicate torrent
		testData = [
			{
				'data':{
					'arguments':{
						'torrent-duplicate':{
							'hashString':'test_hash'
						}
					}
				},
				'validResult':(1, 'test_hash'),
				'response':	Responses.duplicate
			},
			{
				'data':{
					'arguments':{
						'torrent-added':{
							'hashString':'test_hash'
						}
					}
				},
				'validResult':(0, 'test_hash'),
				'response':	Responses.success
			},
			{
				'data':{},
				'validResult':(2, Responses.torrentBadRequest),
				'response':	Responses.torrentBadRequest
			},
			{
				'data':{},
				'validResult':(2, Responses.torrentServiceUnavailable),
				'response':	Responses.torrentServiceUnavailable
			},
			{
				'data':{},
				'validResult':(2, Responses.torrentNoResponse),
				'response':	Responses.torrentNoResponse
			},
			{
				'data':{},
				'validResult':(3, Responses.badTorrent),
				'response':	Responses.badTorrent
			},
			{
				'data':{},
				'validResult':(3, Responses.torrentNotFound),
				'response':	Responses.torrentNotFound
			},
			{
				'data':{},
				'validResult':(4, 'Unknown Error/Failed'),
				'response':	'xyz'
			}
		]


		for test in testData:
			mock_parseTransmissionResponse.return_value = (test['data'], 200, test['response'])
			result = client.addTorrentURL(url='localhost')
			self.assertEqual(result, test['validResult'])


	def test_getSeeding(self):

		client = Transmission.Client()

		torrents = self.getTestTorrents()

		client.elements['queue'] = torrents
		result = client.getSeeding(num=50)
		self.assertEqual(3, len(result))


	def test_getDownloading(self):

		client = Transmission.Client()

		torrents = self.getTestTorrents()

		client.elements['queue'] = torrents
		result = client.getDownloading(num=50)
		self.assertEqual(2, len(result))


	@patch.object(flannelfox.databases.Databases, 'getTorrentInfo')
	def test_getSlowestSeeds(self, mock_getTorrentInfo):

		mock_getTorrentInfo.return_value = [{
			'minTime':1,
			'minRatio':1,
			'comparison':'or'
		}]

		client = Transmission.Client()

		torrents = self.getTestTorrents()

		client.elements['queue'] = torrents
		result = client.getSlowestSeeds(num=50)
		self.assertEqual(3, len(result))

		result = client.getSlowestSeeds()
		self.assertEqual(5, result[0]['status'])


	@patch.object(flannelfox.databases.Databases, 'getTorrentInfo')
	def test_getDormantSeeds(self, mock_getTorrentInfo):

		mock_getTorrentInfo.return_value = [{
			'minTime':1,
			'minRatio':1,
			'comparison':'or'
		}]

		client = Transmission.Client()

		torrents = self.getTestTorrents()

		client.elements['queue'] = torrents
		result = client.getDormantSeeds(num=50)
		self.assertEqual(2, len(result))

		result = client.getDormantSeeds()
		self.assertEqual(51, result[0]['id'])


	@patch.object(flannelfox.databases.Databases, 'getTorrentInfo')
	def test_getFinishedSeeding(self, mock_getTorrentInfo):

		mock_getTorrentInfo.return_value = [{
			'minTime':1,
			'minRatio':1,
			'comparison':'or'
		}]

		client = Transmission.Client()

		torrents = self.getTestTorrents()

		client.elements['queue'] = torrents
		result = client.getFinishedSeeding(num=50)
		self.assertEqual(3, len(result))


	@patch.object(flannelfox.databases.Databases, 'getTorrentInfo')
	def test_getDownloading(self, mock_getTorrentInfo):

		mock_getTorrentInfo.return_value = [{
			'minTime':1,
			'minRatio':1,
			'comparison':'or'
		}]

		client = Transmission.Client()

		torrents = self.getTestTorrents()

		client.elements['queue'] = torrents
		result = client.getDownloading(num=50)
		self.assertEqual(2, len(result))


	def test_client(self):

		mock_settings = {
			'client':{
				'host': '127.0.0.1',
				'port': '9000',
				'user': 'admin',
				'password': 'pass',
				'rpcLocation': 'trans',
				'https': True,
				'queue': [],
				'sessionId': None
			}
		}

		client = None

		with patch.dict(
			'flannelfox.settings.settings',
			mock_settings
		):

			client = Transmission.Client()

		for key, val in mock_settings['client'].items():
			self.assertEqual(val, client.elements[key])


if __name__ == '__main__':
	unittest.main()

