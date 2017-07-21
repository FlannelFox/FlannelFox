# -*- coding: utf-8 -*-

import unittest
from flannelfox.datasources import rss

class TestRssConfig(unittest.TestCase):

	def test_rss(self):

		# This needs to match the combined contents files in temp/rssfeeds
		# after being processed by readRssConfigs
		convertedTestList = {
			"./.flannelfox/config/feeds/rssfeeds/rss1.json.somesite tv":{
			"feedName":"somesite tv",
			"feedFilters":[
				[
					{
						"exclude":True,
						"val":"xvid",
						"key":"codec"
					},
					{
						"exclude":True,
						"val":"x264-hi10p",
						"key":"codec"
					},
					{
						"exclude":False,
						"val":"some title",
						"key":"title"
					},
					{
						"exclude":False,
						"val":"720p",
						"key":"quality"
					},
					{
						"exclude":False,
						"val":"mkv",
						"key":"container"
					}
				]
			],
			"feedDestination":"finished/tv",
			"minorFeeds":[
				{
				"comparison":"or",
				"minTime":24,
				"minRatio":1.5,
				"url":"http://somesite.com/rss"
				}
			],
			"feedType":"tv"
			},
			"./.flannelfox/config/feeds/rssfeeds/rss1.json.somesite tv2":{
			"feedName":"somesite tv2",
			"feedFilters":[
				[
					{
						"exclude":True,
						"val":"xvid",
						"key":"codec"
					},
					{
						"exclude":True,
						"val":"x264-hi10p",
						"key":"codec"
					},
					{
						"exclude":False,
						"val":"some title",
						"key":"title"
					},
					{
						"exclude":False,
						"val":"720p",
						"key":"quality"
					},
					{
						"exclude":False,
						"val":"mkv",
						"key":"container"
					}
				]
			],
			"feedDestination":"finished/tv",
			"minorFeeds":[
				{
				"comparison":"or",
				"minTime":24,
				"minRatio":1.5,
				"url":"http://somesite.com/rss"
				}
			],
			"feedType":"tv"
			},
			"./.flannelfox/config/feeds/rssfeeds/rss2.json.somesite tv3":{
			"feedName":"somesite tv3",
			"feedFilters":[
				[
					{
						"exclude":True,
						"val":"xvid",
						"key":"codec"
					},
					{
						"exclude":True,
						"val":"x264-hi10p",
						"key":"codec"
					},
					{
						"exclude":False,
						"val":"some title",
						"key":"title"
					},
					{
						"exclude":False,
						"val":"720p",
						"key":"quality"
					},
					{
						"exclude":False,
						"val":"mkv",
						"key":"container"
					}
				]
			],
			"feedDestination":"finished/tv",
			"minorFeeds":[
				{
				"comparison":"or",
				"minTime":24,
				"minRatio":1.5,
				"url":"http://somesite.com/rss"
				}
			],
			"feedType":"tv"
			},
			"./.flannelfox/config/feeds/rssfeeds/rss2.json.somesite tv4":{
			"feedName":"somesite tv4",
			"feedFilters":[
				[
					{
						"exclude":True,
						"val":"xvid",
						"key":"codec"
					},
					{
						"exclude":True,
						"val":"x264-hi10p",
						"key":"codec"
					},
					{
						"exclude":False,
						"val":"some title",
						"key":"title"
					},
					{
						"exclude":False,
						"val":"720p",
						"key":"quality"
					},
					{
						"exclude":False,
						"val":"mkv",
						"key":"container"
					}
				]
			],
			"feedDestination":"finished/tv",
			"minorFeeds":[
				{
				"comparison":"or",
				"minTime":24,
				"minRatio":1.5,
				"url":"http://somesite.com/rss"
				}
			],
			"feedType":"tv"
			},
		}

		rssResults = rss.readRssConfigs()

		self.assertTrue(len(rssResults) > 0)
		self.assertEqual(rssResults, convertedTestList)


if __name__ == '__main__':
	unittest.main()