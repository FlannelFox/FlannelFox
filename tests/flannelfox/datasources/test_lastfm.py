# -*- coding: utf-8 -*-

import unittest, shutil
from unittest.mock import patch

import flannelfox

from flannelfox.datasources import lastfm

class TestLastFmConfig(unittest.TestCase):


	# This needs to match the combined contents files in temp/traktfeeds
	# after being processed by readRssConfigs
	convertedTestList = {
		'./.flannelfox/config/feeds/lastfmfeeds/lastfmconfig1.json.albums-cd': {
			'feedFilters': [
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 1'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2018'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 1'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2017'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 2'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2018'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 2'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2017'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 3'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2018'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 3'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2017'
					}
				]
			],
			'feedType': 'music',
			'minorFeeds': [
				{
					'minRatio': 1.5,
					'comparison': 'or',
					'url': 'http://site.com/rss',
					'minTime': 24
				},
				{
					'minRatio': 1.5,
					'comparison': 'or',
					'url': 'http://site2.com/rss',
					'minTime': 72
				},
				{
					'minRatio': 1.5,
					'comparison': 'or',
					'url': 'http://site2.com/rss?somefiler=1',
					'minTime': 24
				}
			],
			'feedDestination': 'finished/music',
			'feedName': 'albums-cd'
		},
		'./.flannelfox/config/feeds/lastfmfeeds/lastfmconfig2.json.albums-cd': {
			'feedFilters': [
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 1'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2016'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 1'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2015'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 2'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2016'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 2'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2015'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 3'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2016'
					}
				],
				[
					{
						'key': 'artist',
						'exclude': False,
						'val': 'artist 3'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various artists'
					},
					{
						'key': 'artist',
						'exclude': True,
						'val': 'various'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'vinyl'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'soundboard'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'sacd'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'dat'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'cassette'
					},
					{
						'key': 'source',
						'exclude': True,
						'val': 'bluray'
					},
					{
						'key': 'quality',
						'exclude': False,
						'val': 'v0vbr'
					},
					{
						'key': 'codec',
						'exclude': False,
						'val': 'mp3'
					},
					{
						'key': 'releaseType',
						'exclude': False,
						'val': 'album'
					},
					{
						'key': 'wordMatch',
						'exclude': False,
						'val': '2015'
					}
				]
			],
			'feedType': 'music',
			'minorFeeds': [
				{
					'minRatio': 1.5,
					'comparison': 'or',
					'url': 'http://site.com/rss',
					'minTime': 24
				},
				{
					'minRatio': 1.5,
					'comparison': 'or',
					'url': 'http://site2.com/rss',
					'minTime': 72
				},
				{
					'minRatio': 1.5,
					'comparison': 'or',
					'url': 'http://site2.com/rss?somefiler=1',
					'minTime': 24
				}
			],
			'feedDestination': 'finished/music',
			'feedName': 'albums-cd'
		}
	}



	sampleLastFmApiData = [
		'artist 1',
		'artist 2',
		'artist 3'
	]

	@classmethod
	def deleteCache(self):
		try:
			shutil.rmtree(lastfm.getCacheDir())
		except Exception:
			pass


	@patch.object(flannelfox.datasources.lastfm.lastfmApi, '_lastfmApi__getLibraryArtistsFeed')
	def test_lastfm(self, getLibraryArtistsFeed):

		lastfmapi = lastfm.lastfmApi()

		getLibraryArtistsFeed.return_value = ( 200, self.sampleLastFmApiData )

		publicList = lastfmapi.getLibraryArtists(
			apiKey='apikey',
			username='username',
		)

		getLibraryArtistsFeed.assert_called_once_with(
			apiKey='apikey',
			username='username'
		)

		with patch.object(flannelfox.datasources.common, 'isCacheStillValid') as isCacheStillValid:
			isCacheStillValid.return_value = False

			lastfmResults = lastfm.readLastfmArtistsConfigs()

			self.assertTrue( isinstance( lastfmResults, dict ) )
			self.assertTrue( len( lastfmResults ) > 0 )
			self.assertEqual( lastfmResults, self.convertedTestList )

		self.deleteCache()


if __name__ == '__main__':
	unittest.main()