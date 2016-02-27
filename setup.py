import os.path as osPath
from setuptools import setup, find_packages
setup(name = 'flannelfox',
      version = '0.1.9',
      packages = find_packages(),
      package_data={'flannelfox': ['flannelfox/data/*']},
      data_files = [
        ('bin', ['flannelfox/data/bin/flannelfox-init']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config'), ['flannelfox/data/config/settings.json.example']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/rssfeeds'), ['flannelfox/data/config/feeds/rssfeeds/rss.json.example']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/lastfmfeeds'), ['flannelfox/data/config/feeds/lastfmfeeds/lastfmartists.json.example']),
        (osPath.join(osPath.expanduser('~'),'.flannelfox/config/feeds/traktfeeds'), ['flannelfox/data/config/feeds/traktfeeds/traktconfig.json.example'])
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
        "python-daemon",
        "lxml",
        "urllib3"
	    ]
)