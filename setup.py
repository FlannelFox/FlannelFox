import os.path as osPath
from setuptools import setup, find_packages
setup(name = 'flannelfox',
      version = '0.1.9',
      packages = find_packages(),
      package_data={'flannelfox': ['flannelfox/data/*', 'flannelfox/data/config/*']},
      data_files = [
        (osPath.join(osPath.expanduser('~'),'.flannelfox/'), ['flannelfox/data/flannelfox.db']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/rssfeeds'), ['flannelfox/data/config/feeds/rssfeeds/rss.json']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/lastfmfeeds'), ['flannelfox/data/config/feeds/lastfmfeeds/LastfmArtistsConfig.json']),
        #(osPath.join(osPath.expanduser('~'),'.flannelfox/config'), ['flannelfox/data/config/python.inc']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config'), ['flannelfox/data/config/settings.json']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/traktfeeds'), ['flannelfox/data/config/feeds/traktfeeds/TraktConfig.json'])
      ],
      entry_points = {
        'console_scripts': [
          'RSSDaemon = flannelfox.rssdaemon:main',
          'QueueDaemon = flannelfox.queuedaemon:main',
        ],              
      },
      install_requires = [
        "requests",
        "beautifulsoup4",
        "chardet",
        "pyOpenSSL",
        "ndg-httpsclient",
        "pyasn1",
        "python-daemon"
	    ]
)