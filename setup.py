import os.path as osPath
import sys
from setuptools import setup, find_packages
setup(name = 'flannelfox',
	version = '1.1.5',
	packages = find_packages(),
	package_data={'flannelfox': ['.flannelfox/config/*']},
	data_files = [
		(sys.prefix, ['.flannelfox/bin/flannelfox-init']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config'), ['.flannelfox/config/settings.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/rssfeeds'), ['.flannelfox/config/feeds/rssfeeds/rss1.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/rssfeeds'), ['.flannelfox/config/feeds/rssfeeds/rss2.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/lastfmfeeds'), ['.flannelfox/config/feeds/lastfmfeeds/lastfmconfig1.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/lastfmfeeds'), ['.flannelfox/config/feeds/lastfmfeeds/lastfmconfig2.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/goodreadsfeeds'), ['.flannelfox/config/feeds/goodreadsfeeds/goodreadsconfig1.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/goodreadsfeeds'), ['.flannelfox/config/feeds/goodreadsfeeds/goodreadsconfig2.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/traktfeeds'), ['.flannelfox/config/feeds/traktfeeds/traktconfig1.json']),
		(osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/traktfeeds'), ['.flannelfox/config/feeds/traktfeeds/traktconfig2.json'])
	],
	entry_points = {
		'console_scripts': [
		'RSSDaemon = flannelfox.rssdaemon:main',
		'QueueDaemon = flannelfox.queuedaemon:main',
		],
	},
	install_requires = [
		"requests",
		"bs4",
		"lxml",
		"python-daemon-3K",
		"defusedxml"
	]
)