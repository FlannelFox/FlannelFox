# -*- coding: utf-8 -*-

import unittest, shutil
from unittest.mock import patch

import flannelfox

from flannelfox.datasources import goodreads

class TestGoodreadsConfig(unittest.TestCase):


	# This needs to match the combined contents files in temp/traktfeeds
	# after being processed by readRssConfigs
	convertedTestList = {
		'./.flannelfox/config/feeds/goodreadsfeeds/goodreadsconfig2.json.my-fav-authors2': {
			'feedType': 'ebook',
			'feedFilters': [
				[
					{
						'exclude': False,
						'val': 'author 1',
						'key': 'titleLike'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 2',
						'key': 'titleLike'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 3',
						'key': 'titleLike'
					}
				]
			],
			'feedDestination': 'finished/ebooks',
			'feedName': 'my-fav-authors2',
			'minorFeeds': [
				{
					'minRatio': 1.5,
					'url': 'http://site.com/rss',
					'minTime': 24,
					'comparison': 'or'
				},
				{
					'minRatio': 1.5,
					'url': 'http://site2.com/rss',
					'minTime': 72,
					'comparison': 'or'
				},
				{
					'minRatio': 1.5,
					'url': 'http://site2.com/rss?somefiler=1',
					'minTime': 24,
					'comparison': 'or'
				}
			]
		},
		'./.flannelfox/config/feeds/goodreadsfeeds/goodreadsconfig1.json.my-fav-authors': {
			'feedType': 'ebook',
			'feedFilters': [
				[
					{
						'exclude': False,
						'val': 'author 1',
						'key': 'titleLike'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 2',
						'key': 'titleLike'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 3',
						'key': 'titleLike'
					}
				]
			],
			'feedDestination': 'finished/ebooks',
			'feedName': 'my-fav-authors',
			'minorFeeds': [
				{
					'minRatio': 1.5,
					'url': 'http://site.com/rss',
					'minTime': 24,
					'comparison': 'or'
				},
				{
					'minRatio': 1.5,
					'url': 'http://site2.com/rss',
					'minTime': 72,
					'comparison': 'or'
				},
				{
					'minRatio': 1.5,
					'url': 'http://site2.com/rss?somefiler=1',
					'minTime': 24,
					'comparison': 'or'
				}
			]
		}
	}


	sampleGoodreadsApiData = [
		'author 1',
		'author 2',
		'author 3'
	]

	@classmethod
	def deleteCache(self):
		try:
			shutil.rmtree(goodreads.getCacheDir())
		except Exception:
			pass

	@patch.object(flannelfox.datasources.goodreads.goodreadsApi, '_goodreadsApi__getFeed')
	def test_goodreads(self, getFeed):

		goodreadsapi = goodreads.goodreadsApi()

		getFeed.return_value = ( 200, self.sampleGoodreadsApiData )

		publicList = goodreadsapi.getFavouriteAuthors(
			apiKey='apikey',
			username='username',
		)

		getFeed.assert_called_once_with(
			apiKey='apikey',
			url='https://www.goodreads.com/user/show/username.xml',
		)

		with patch.object(flannelfox.datasources.common, 'isCacheStillValid') as isCacheStillValid:
			isCacheStillValid.return_value = False

			goodreadsResults = goodreads.readGoodreadsConfigs()

			self.assertTrue( isinstance( goodreadsResults, dict ) )
			self.assertTrue( len( goodreadsResults ) > 0 )
			self.assertEqual( goodreadsResults, self.convertedTestList )

		self.deleteCache()


if __name__ == '__main__':
	unittest.main()