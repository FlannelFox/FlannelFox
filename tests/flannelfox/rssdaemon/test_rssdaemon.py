# -*- coding: utf-8 -*-

import unittest, os
from unittest.mock import patch

from flannelfox import rssdaemon
from flannelfox.databases import Databases
from flannelfox.settings import settings

class TestRssDaemon(unittest.TestCase):


	testRssDataTv = b'''<?xml version="1.0" encoding="utf-8"?>
		<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
			<channel>
				<title>Somesite</title>
				<link>https://somesite.com/</link>
				<description>RSS feed</description>
				<language>en-us</language>
				<lastBuildDate>Fri, 27 Jan 2017 04:38:03 +0000</lastBuildDate>
				<docs>http://blogs.law.harvard.edu/tech/rss</docs>
				<generator>RSS Gen</generator>
				<item>
					<title><![CDATA[Some Title - S02E03 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ] ]]></title>
					<description>TEST Description</description>
					<pubDate>Fri, 27 Jan 2017 04:37:49 +0000</pubDate>
					<link>https://somesite.com/link1</link>
					<guid>https://somesite.com/link1</guid>
					<comments>, Drama, sciencefiction, </comments>
					<dc:creator>Anonymous</dc:creator>
				</item>
				<item>
					<title><![CDATA[Some Title - S01E04 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ] ]]></title>
					<description>TEST Description</description>
					<pubDate>Fri, 27 Jan 2017 04:37:49 +0000</pubDate>
					<link>https://somesite.com/link1</link>
					<guid>https://somesite.com/link1</guid>
					<comments>, Drama, sciencefiction, </comments>
					<dc:creator>Anonymous</dc:creator>
				</item>
			</channel>
		</rss>'''


	testRssDataEbook = b'''<?xml version="1.0" encoding="utf-8"?>
		<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
			<channel>
				<title>Somesite</title>
				<link>https://somesite.com/</link>
				<description>RSS feed</description>
				<language>en-us</language>
				<lastBuildDate>Fri, 27 Jan 2017 04:38:03 +0000</lastBuildDate>
				<docs>http://blogs.law.harvard.edu/tech/rss</docs>
				<generator>RSS Gen</generator>
				<item>
					<title>Author 1: The Title Of This Book [Nonfiction Biography]</title>
					<description>TEST Description</description>
					<pubDate>Fri, 27 Jan 2017 04:37:49 +0000</pubDate>
					<link>https://somesite.com/link1</link>
					<guid>https://somesite.com/link1</guid>
					<comments>, Drama, sciencefiction, </comments>
					<dc:creator>Anonymous</dc:creator>
				</item>
				<item>
					<title>Author 2: The Title Of This Other Book [Fiction]</title>
					<description>TEST Description</description>
					<pubDate>Fri, 27 Jan 2017 04:37:49 +0000</pubDate>
					<link>https://somesite.com/link1</link>
					<guid>https://somesite.com/link1</guid>
					<comments>, Drama, sciencefiction, </comments>
					<dc:creator>Anonymous</dc:creator>
				</item>
			</channel>
		</rss>'''


	testRssDataMusic = b'''<?xml version="1.0" encoding="utf-8"?>
		<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
			<channel>
				<title>Somesite</title>
				<link>https://somesite.com/</link>
				<description>RSS feed</description>
				<language>en-us</language>
				<lastBuildDate>Fri, 27 Jan 2017 04:38:03 +0000</lastBuildDate>
				<docs>http://blogs.law.harvard.edu/tech/rss</docs>
				<generator>RSS Gen</generator>
				<item>
					<title><![CDATA[artist 1 - some album [2017] [Album] - MP3 / V0 VBR / CD]]></title>
					<description>TEST Description</description>
					<pubDate>Fri, 27 Jan 2017 04:37:49 +0000</pubDate>
					<link>https://somesite.com/link1</link>
					<guid>https://somesite.com/link1</guid>
					<comments>, Drama, sciencefiction, </comments>
					<dc:creator>Anonymous</dc:creator>
				</item>
				<item>
					<title><![CDATA[artist 2 - some other album [2018] [Album] - MP3 / V0 VBR / CD]]></title>
					<description>TEST Description</description>
					<pubDate>Fri, 27 Jan 2017 04:37:49 +0000</pubDate>
					<link>https://somesite.com/link1</link>
					<guid>https://somesite.com/link1</guid>
					<comments>, Drama, sciencefiction, </comments>
					<dc:creator>Anonymous</dc:creator>
				</item>
			</channel>
		</rss>
		'''


	testTrakttvConfig = {
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


	testLastfmConfig = {
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


	testRssConfig = {
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


	testGoodreadsConfig = {
		'./.flannelfox/config/feeds/goodreadsfeeds/goodreadsconfig2.json.my-fav-authors2': {
			'feedType': 'ebook',
			'feedFilters': [
				[
					{
						'exclude': False,
						'val': 'author 1',
						'key': 'wordMatch'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 2',
						'key': 'wordMatch'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 3',
						'key': 'wordMatch'
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
						'key': 'wordMatch'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 2',
						'key': 'wordMatch'
					}
				],
				[
					{
						'exclude': False,
						'val': 'author 3',
						'key': 'wordMatch'
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


	testDatabaseFile = os.path.join(settings['files']['privateDir'],'flannelfox.db')


	def getQueuedTorrentsCount(self):

		dbObject = Databases(
			dbType = "SQLITE3",
			databaseSettings = {
				'databaseLocation': self.testDatabaseFile
			}
		)

		return dbObject.getQueuedTorrentsCount()


	def removeDatabase(self):
		try:
			os.remove(self.testDatabaseFile)
		except Exception:
			pass


	def test_readRSSFeed(self):

		testRssFeed = 'https://github.com/FlannelFox/FlannelFox/commits/master.atom'

		response, httpCode, encoding = rssdaemon.readRSSFeed(testRssFeed)

		self.assertEqual(httpCode, 200)
		self.assertIsInstance(response, bytes)
		self.assertEqual(encoding, 'utf-8')


	def test_rssToTorrents(self):


		parsedResponse=[
			{'minRatio': 0.0, 'minTime': 0, 'torrentType': 'tv', 'episode': '3', 'quality': '720p', 'title': 'some title', 'container': 'mkv', 'source': 'hdtv', 'torrentTitle': 'Some Title - S02E03 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ]', 'codec': 'h264', 'comparison': 'or', 'url': 'https://somesite.com/link1', 'feedDestination': None, 'season': '2'},
			{'minRatio': 0.0, 'minTime': 0, 'torrentType': 'tv', 'episode': '4', 'quality': '720p', 'title': 'some title', 'container': 'mkv', 'source': 'hdtv', 'torrentTitle': 'Some Title - S01E04 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ]', 'codec': 'h264', 'comparison': 'or', 'url': 'https://somesite.com/link1', 'feedDestination': None, 'season': '1'}
		]

		results = rssdaemon.rssToTorrents(self.testRssDataTv, feedType='tv')

		count = 0
		for result in results:
			self.assertEqual(result, parsedResponse[count])
			count = count+1



	@patch('flannelfox.rssdaemon.readRSSFeed')
	def test_rssThread(self,mock_readRSSFeed):

		majorFeed = {
			'feedType':'tv',
			'feedDestination':'finished/files',
			'minorFeeds':[
				{
					'url':'http://somesite.com',
					'minRatio':1.0,
					'minTime':72,
					'comparison':'or'
				},
				{
					'url':'http://somesite.com',
					'minRatio':1.0,
					'minTime':72,
					'comparison':'or'
				}
			],
			'feedFilters':[
				[
					{
						'key':'title',
						'val':'some title',
						'exclude':False
					}
				]
			]
		}

		processedResponse = [
			{'torrentTitle': 'Some Title - S02E03 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ]', 'torrentType': 'tv', 'url': 'https://somesite.com/link1', 'minRatio': 1.0, 'feedDestination': 'finished/files', 'title': 'some title', 'episode': '3', 'minTime': 72, 'season': '2', 'container': 'mkv', 'source': 'hdtv', 'codec': 'h264', 'quality': '720p', 'comparison': 'or'},
			{'torrentTitle': 'Some Title - S01E04 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ]', 'torrentType': 'tv', 'url': 'https://somesite.com/link1', 'minRatio': 1.0, 'feedDestination': 'finished/files', 'title': 'some title', 'episode': '4', 'minTime': 72, 'season': '1', 'container': 'mkv', 'source': 'hdtv', 'codec': 'h264', 'quality': '720p', 'comparison': 'or'},
			{'torrentTitle': 'Some Title - S02E03 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ]', 'torrentType': 'tv', 'url': 'https://somesite.com/link1', 'minRatio': 1.0, 'feedDestination': 'finished/files', 'title': 'some title', 'episode': '3', 'minTime': 72, 'season': '2', 'container': 'mkv', 'source': 'hdtv', 'codec': 'h264', 'quality': '720p', 'comparison': 'or'},
			{'torrentTitle': 'Some Title - S01E04 [ 2017 ] [ MKV | H.264 | HDTV | 720p | Scene | FastTorrent ] [ Uploader: Anonymous ]  [ Some.Title.S02E03.INTERNAL.720p.HDTV.x264 ]', 'torrentType': 'tv', 'url': 'https://somesite.com/link1', 'minRatio': 1.0, 'feedDestination': 'finished/files', 'title': 'some title', 'episode': '4', 'minTime': 72, 'season': '1', 'container': 'mkv', 'source': 'hdtv', 'codec': 'h264', 'quality': '720p', 'comparison': 'or'}
		]

		mock_readRSSFeed.return_value = (self.testRssDataTv, 200, 'utf-8')

		results = rssdaemon.rssThread(majorFeed)

		self.assertEqual(processedResponse, results[1])


	@patch('flannelfox.datasources.rss.readRssConfigs')
	@patch('flannelfox.datasources.lastfm.readLastfmArtistsConfigs')
	@patch('flannelfox.datasources.goodreads.readGoodreadsConfigs')
	@patch('flannelfox.datasources.trakttv.readTraktTvConfigs')
	@patch('flannelfox.rssdaemon.readRSSFeed')
	def test_rssReader_rss_sources(self, mock_readRSSFeed, mock_trakttv, mock_goodreads, mock_lastfm, mock_rss):

		self.removeDatabase()

		mock_rss.return_value = self.testRssConfig
		mock_lastfm.return_value = {}
		mock_goodreads.return_value = {}
		mock_trakttv.return_value = {}

		mock_readRSSFeed.return_value = (self.testRssDataTv, 200, 'utf-8')
		rssdaemon.rssReader()

		self.assertEqual(self.getQueuedTorrentsCount(), 2)


	@patch('flannelfox.datasources.rss.readRssConfigs')
	@patch('flannelfox.datasources.lastfm.readLastfmArtistsConfigs')
	@patch('flannelfox.datasources.goodreads.readGoodreadsConfigs')
	@patch('flannelfox.datasources.trakttv.readTraktTvConfigs')
	@patch('flannelfox.rssdaemon.readRSSFeed')
	def test_rssReader_trakt_sources(self, mock_readRSSFeed, mock_trakttv, mock_goodreads, mock_lastfm, mock_rss):

		self.removeDatabase()

		mock_rss.return_value = {}
		mock_lastfm.return_value = {}
		mock_goodreads.return_value = {}
		mock_trakttv.return_value = self.testTrakttvConfig

		mock_readRSSFeed.return_value = (self.testRssDataTv, 200, 'utf-8')
		rssdaemon.rssReader()

		self.assertEqual(self.getQueuedTorrentsCount(), 2)


	@patch('flannelfox.datasources.rss.readRssConfigs')
	@patch('flannelfox.datasources.lastfm.readLastfmArtistsConfigs')
	@patch('flannelfox.datasources.goodreads.readGoodreadsConfigs')
	@patch('flannelfox.datasources.trakttv.readTraktTvConfigs')
	@patch('flannelfox.rssdaemon.readRSSFeed')
	def test_rssReader_lastfm_sources(self, mock_readRSSFeed, mock_trakttv, mock_goodreads, mock_lastfm, mock_rss):

		self.removeDatabase()

		mock_rss.return_value = {}
		mock_lastfm.return_value = self.testLastfmConfig
		mock_goodreads.return_value = {}
		mock_trakttv.return_value = {}

		mock_readRSSFeed.return_value = (self.testRssDataMusic, 200, 'utf-8')
		rssdaemon.rssReader()

		self.assertEqual(self.getQueuedTorrentsCount(), 2)


	@patch('flannelfox.datasources.rss.readRssConfigs')
	@patch('flannelfox.datasources.lastfm.readLastfmArtistsConfigs')
	@patch('flannelfox.datasources.goodreads.readGoodreadsConfigs')
	@patch('flannelfox.datasources.trakttv.readTraktTvConfigs')
	@patch('flannelfox.rssdaemon.readRSSFeed')
	def test_rssReader_goodreads_sources(self, mock_readRSSFeed, mock_trakttv, mock_goodreads, mock_lastfm, mock_rss):

		self.removeDatabase()

		mock_rss.return_value = {}
		mock_lastfm.return_value = {}
		mock_goodreads.return_value = {}
		mock_trakttv.return_value = self.testGoodreadsConfig

		mock_readRSSFeed.return_value = (self.testRssDataEbook, 200, 'utf-8')
		rssdaemon.rssReader()

		self.assertEqual(self.getQueuedTorrentsCount(), 2)



if __name__ == '__main__':
	unittest.main()
