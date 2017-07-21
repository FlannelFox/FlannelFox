# -*- coding: utf-8 -*-

import unittest, shutil
from unittest.mock import patch

import flannelfox

from flannelfox.datasources import trakttv

class TestTraktTvConfig(unittest.TestCase):


	# This needs to match the combined contents files in temp/traktfeeds
	# after being processed by readRssConfigs
	convertedTestList = {
		'./.flannelfox/config/feeds/traktfeeds/traktconfig1.json.your-list-name': {
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
			'feedType': 'tv',
			'feedFilters': [
				[
					{
						'val': 'some title',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				],
				[
					{
						'val': 'billions',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				]
			],
			'feedDestination': 'finished/tv',
			'feedName': 'your-list-name'
		},
		'./.flannelfox/config/feeds/traktfeeds/traktconfig1.json.your-list-name2': {
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
			'feedType': 'tv',
			'feedFilters': [
				[
					{
						'val': 'some title',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				],
				[
					{
						'val': 'billions',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				]
			],
			'feedDestination': 'finished/tv',
			'feedName': 'your-list-name2'
		},
		'./.flannelfox/config/feeds/traktfeeds/traktconfig2.json.your-list-name3': {
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
			'feedType': 'tv',
			'feedFilters': [
				[
					{
						'val': 'some title',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				],
				[
					{
						'val': 'billions',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				]
			],
			'feedDestination': 'finished/tv',
			'feedName': 'your-list-name3'
		},
		'./.flannelfox/config/feeds/traktfeeds/traktconfig2.json.your-list-name4': {
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
			'feedType': 'tv',
			'feedFilters': [
				[
					{
						'val': 'some title',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				],
				[
					{
						'val': 'billions',
						'exclude': False,
						'key': 'title'
					},
					{
						'val': 'bluray',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'brrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'bdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'dvdrip',
						'exclude': True,
						'key': 'source'
					},
					{
						'val': 'x264-hi10p',
						'exclude': True,
						'key': 'codec'
					},
					{
						'val': '720p',
						'exclude': False,
						'key': 'quality'
					}
				]
			],
			'feedDestination': 'finished/tv',
			'feedName': 'your-list-name4'
		}
	}


	sampleTrakttvApiData = [
		{
			"type": "show",
			"show": {
				"ids": {
					"tvdb": 291517,
					"tmdb": 63645,
					"trakt": 95646,
					"imdb": "tt3499120",
					"slug": "agent-x-2015",
					"tvrage": None
				},
				"year": 2015,
				"title": "some title"
			},
			"rank": 1,
			"listed_at": "2015-12-08T02:21:17.000Z"
		},
		{
			"type": "show",
			"show": {
				"ids": {
					"tvdb": 279536,
					"tmdb": 62852,
					"trakt": 77692,
					"imdb": "tt4270492",
					"slug": "billions",
					"tvrage": 41376
				},
				"year": 2016,
				"title": "Billions"
			},
			"rank": 2,
			"listed_at": "2016-01-02T03:49:44.000Z"
		}
	]


	@classmethod
	def deleteCache(self):
		try:
			shutil.rmtree(trakttv.getCacheDir())
		except Exception:
			pass


	@patch.object(flannelfox.datasources.trakttv.trakttvApi, '_trakttvApi__getFeed')
	def test_publicList(self, getFeed):

		trakttvapi = trakttv.trakttvApi()

		getFeed.return_value = ( 200, self.sampleTrakttvApiData )

		publicList = trakttvapi.getPublicList(
			'apikey',
			'username',
			'listname'
		)

		self.assertTrue(isinstance(publicList, list))

		getFeed.assert_called_once_with(
			apiKey='apikey',
			url='https://api-v2launch.trakt.tv/users/username/lists/listname/items'
		)

		with patch.object(flannelfox.datasources.common, 'isCacheStillValid') as isCacheStillValid:
			isCacheStillValid.return_value = False

			trakttvResults = trakttv.readTraktTvConfigs()

			self.assertTrue(isinstance(trakttvResults, dict))
			self.assertTrue(len(trakttvResults) > 0)
			self.assertEqual(trakttvResults, self.convertedTestList)

		self.deleteCache()


if __name__ == '__main__':
	unittest.main()