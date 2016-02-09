import os.path as osPath
from setuptools import setup, find_packages
setup(name = 'FlannelFox',
      version = '0.1.6',
      packages = find_packages(),
      package_data={'FlannelFox': ['FlannelFox/data/*', 'FlannelFox/data/config/*']},
      data_files = [
        (osPath.join(osPath.expanduser('~'),'.FlannelFox/'), ['FlannelFox/data/FlannelFox.db']),
        (osPath.join(osPath.expanduser('~'),'.FlannelFox/config/feeds/rssfeeds'), ['FlannelFox/data/config/feeds/rssfeeds/rss.json']),
        (osPath.join(osPath.expanduser('~'),'.FlannelFox/config/feeds/lastfmfeeds'), ['FlannelFox/data/config/feeds/lastfmfeeds/LastfmArtistsConfig.json']),
        (osPath.join(osPath.expanduser('~'),'.FlannelFox/config'), ['FlannelFox/data/config/python.inc']),
        (osPath.join(osPath.expanduser('~'),'.FlannelFox/config'), ['FlannelFox/data/config/settings.json']),
        (osPath.join(osPath.expanduser('~'),'.FlannelFox/config/feeds/traktfeeds'), ['FlannelFox/data/config/feeds/traktfeeds/TraktConfig.json'])
      ],
      entry_points = {
        'console_scripts': [
          'RSSDaemon = FlannelFox.RSSDaemon:main',
          'QueueDaemon = FlannelFox.QueueDaemon:main',
        ],              
      },
      install_requires = [
        "requests",
        "beautifulsoup4",
        "chardet"
	    ]
)