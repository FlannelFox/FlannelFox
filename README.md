FlannelFox is a Python application that can monitor a torrent client and perform regular management tasks such as:
* Ensuring torrents seed an appropriate amount of time after they complete
* Ensuring torrents seed to an appropriate ratio after they complete
* Manage how many torrents are running at a time
* Automatically load torrents from RSS feeds based on user defined filters

[![GitHub license](https://img.shields.io/github/license/FlannelFox/FlannelFox.svg?style=flat-square)](https://github.com/FlannelFox/FlannelFox/blob/master/License.md)
[![Github All Releases](https://img.shields.io/github/downloads/FlannelFox/FlannelFox/total.svg?style=flat-square)](https://github.com/FlannelFox/FlannelFox)


#What will it download and how does it know what I want?
FlannelFox uses a set of JSON files (.json) that allow you to let it know what you want in three (3) ways:

* **Trakt.TV list monitoring** - You can create rule sets in the `~/.flannelfox/config/feeds/traktfeeds` folder that will monitor [Trakt.TV](http://Trakt.TV) lists (public lists only at the moment) you specify for things you want. For best results make sure to only add movies OR tv series entries to your lists, episodes can cause issues in some instances. Make sure you register for an API key to use.

* **Last.FM Library monitoring** - You can create rule sets in the `~/.flannelfox/config/feeds/lastfmfeeds` folder that will monitor your library on [Last.FM](http://Last.FM) and automatically grab releases from artists in your library. Make sure you register for an API key to use.

* **Plain text matching** - Create rule sets in the `~/.flannelfox/config/feeds/rssfeeds` folder and they will be used to match the text entered against the feeds you specify. This is the most basic form of matching and can be a bit tedious. It is needed however, for those odd names that can not be pulled from Trakt or LastFM in a form the trackers use.

[Example config files](#example-config-files)


#How do I edit these files and what type of filtering can I do?
The filtering engine is fairly robust and as such can take a number of different items depending on the feed type chosen. The feed types and keywords each uses are:
* [tv](#tv)
* [movie](#movie)
* [music](#music)
* [other](#other)


#Where does all the torrent information get stored?
This is something that can be configured, but by default a sqlite3 database is used to track all the data. The database can be found at ```~/.flannelfox/flannelfox.db```


#Requirements/Dependencies
Python 2.7
* requests
* beautifulsoup4
* chardet
* pyOpenSSL
* ndg-httpsclient
* pyasn1
* python-daemon


#Setup information
---------------
##Create .local to install as a user
```$> mkdir -p ~/.local/lib/python2.7/site-packages```


##Add ~/.local/bin to your path
```$> echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc```


##Build/Install FlannelFox
```$> python setup.py install --prefix=~/.local```


##Starting FlannelFox
```$> flannelfox-init start```


#Submissions
---------------
I am open for help and changes on this project, just make sure it is submitted in the form of a pull request and that it has been squashed/flattened into a single commit. To see the features that are needing a bit of love check the [help wanted](https://github.com/FlannelFox/FlannelFox/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) page.


#Matching Keywords
---------------
Keywords are how the application knows what you want it to grab for you. You can mix and match keywords in both the include and exclude areas of the config files.

##TV
* wordMatch - matches an exact word/phrase in the torrent name.
* wordMatchStrict - matches an exact word/phrase in the torrent name while taking letter case into consideration.
* title - matches an exact title to the data extracted from the torrent name.
* titleLike - performs a partial match to the data extracted from the torrent name.
* season - matches a season number to the data extracted from the torrent name.
* episode - matches an episode number to the data extracted from the torrent name.
* quality - matches a specific quality to the data extracted from the torrent name.
    * 480p
    * 480i
    * 576p
    * 576i
    * 720p
    * 720i
    * 1080p
    * 1080i
    * sd
* codec - matches a specific codec to the data extracted from the torrent name.
    * xvid
    * divx
    * dvdr
    * h264
    * vc-1
    * wmv
    * x264-hi10p
    * x264
    * bd
    * mpeg2
* container - matches a specific container to the data extracted from the torrent name.
    * mp4
    * vob
    * mpeg
    * iso
    * wmv
    * m4v
    * m2ts
    * avi
    * ts
    * mkv
* source - matches a specific source type to the data extracted from the torrent name.
    * dsr
    * dvdrip
    * tvrip
    * vhsrip
    * bluray
    * bdrip
    * brrip
    * dvd5
    * dvd9
    * hddvd
    * webdl
    * webrip
    * bd5
    * bd9
    * bd25
    * bd50
    * hdtv
    * pdtv


##Movie
Movies have many of the same filters as TV with a couple of exceptions; episode and season flags are not valid and a new flag called year is added.
    * year - matches a specific year to the data extracted from the torrent name.


##Music
* wordMatch - matches an exact word/phrase in the torrent name.
* wordMatchStrict - matches an exact word/phrase in the torrent name while taking letter case into consideration.
* title - matches an exact title to the data extracted from the torrent name.
* titleLike - performs a partial match to the data extracted from the torrent name.
* quality
    * apsvbr
    * apxvbr
    * v0vbr
    * v1vbr
    * v2vbr
    * v8vbr
    * 128
    * 192
    * 256
    * 320
    * 24bit lossless
    * lossless
* releaseType
    * album
    * soundtrack
    * ep
    * anthology
    * compilation
    * dj mix
    * single
    * live album
    * remix
    * bootleg
    * interview
    * mixtape
    * unknown
    * concert recording
    * demo
* codec
    * aac
    * ac3
    * dts
    * mp3
    * flac
* source
    * cd
    * dvd
    * vinyl
    * soundboard
    * sacd
    * dat
    * cassette
    * web-dl
    * blu-ray


##Other
This is achieved by leaving the type section empty ""

* wordMatch - matches an exact word/phrase in the torrent name.
* wordMatchStrict - matches an exact word/phrase in the torrent name while taking letter case into consideration.


##Example config files
---------------
* Custom Config
    * [Get only the first five (5) episodes of a new series' first season.](#get-only-the-first-five-5-episodes-of-a-new-series-first-season)
    * [Get only shows with the word "Boogieman" in the title that are 720p quality and mkv container](#get-only-shows-with-the-word-boogieman-in-the-title-that-are-720p-quality-and-mkv-container)
    * [Get a show called fakeworld but do not match the aftershow episode](#get-a-show-called-fakeworld-but-do-not-match-the-aftershow-episode)
* Trakt.TV
    * [List monitoring config file to monitor a list called "your-list-name" and auto pull shows that are 720p quality and match the titles in the list.](#list-monitoring-config-file-to-monitor-a-list-called-your-list-name-and-auto-pull-shows-that-are-720p-quality-and-match-the-titles-in-the-list)
    * [List monitoring config file to monitor a list called "your-list-name-partial" and auto pull shows that are 720p quality and paritally match the title.](#list-monitoring-config-file-to-monitor-a-list-called-your-list-name-partial-and-auto-pull-shows-that-are-720p-quality-and-paritally-match-the-title)
* Last.FM
    * [Library monitoring config file to grab all releases that match your library that are mp3/v0vbr and the source is a cd.](#library-monitoring-config-file-to-grab-all-releases-that-match-your-library-that-are-mp3v0vbr-and-the-source-is-a-cd)


###Custom Config
####Get only the first five (5) episodes of a new series' first season.
```
[
    {
        "majorFeed": {
            "list_name":"Somesite TV",
            "type": "tv",
            "feedDestination": "###DOWNLOAD_DIR###/finished/tv",
            "minorFeeds": [
                {
                    "url":"http://somesite.com/rss",
                    "minRatio": "1.5",
                    "minTime": "24"
                }
            ],
            "filters":[
                {
                    "include":[
                        {"season": "1"},
                        {"episode": "1"}
                    ]
                },
                {
                    "include":[
                        {"season": "1"},
                        {"episode": "2"}
                    ]
                },
                {
                    "include":[
                        {"season": "1"},
                        {"episode": "3"}
                    ]
                },
                {
                    "include":[
                        {"season": "1"},
                        {"episode": "4"}
                    ]
                },
                {
                    "include":[
                        {"season": "1"},
                        {"episode": "5"}
                    ]
                }
            ]
        }
    }
]

```


####Get only shows with the word "Boogieman" in the title that are 720p quality and mkv container
```
[
    {
        "majorFeed": {
            "list_name":"Somesite TV",
            "type": "tv",
            "feedDestination": "###DOWNLOAD_DIR###/finished/tv",
            "minorFeeds": [
                {
                    "url":"http://somesite.com/rss",
                    "minRatio": "1.5",
                    "minTime": "24"
                }
            ],
            "filters":[
                {
                    "include":[
                        {"title": "Boogieman"},
                        {"quality": "720p"},
                        {"container": "mkv"}
                    ]
                }
            ]
        }
    }
]

```


####Get a show called fakeworld but do not match the aftershow episode
```
[
    {
        "majorFeed": {
            "list_name":"Somesite TV",
            "type": "tv",
            "feedDestination": "###DOWNLOAD_DIR###/finished/tv",
            "minorFeeds": [
                {
                    "url":"http://somesite.com/rss",
                    "minRatio": "1.5",
                    "minTime": "24"
                }
            ],
            "filters":[
                {
                    "exclude":[
                        {"wordMatch": "aftershow"}
                    ],
                    "include":[
                        {"title": "fakeworld"},
                        {"quality": "720p"},
                        {"container": "mkv"}
                    ]
                }
            ]
        }
    }
]

```

###Trakt.TV
####List monitoring config file to monitor a list called "your-list-name" and auto pull shows that are 720p quality and match the titles in the list.
```
[
  {
    "username": "trakt-user-name",
    "api_key": "",
    "list_name": "your-list-name",
    "type": "tv",
    "feedDestination": "###DOWNLOAD_DIR###/finished/tv",
    "minorFeeds": [
      {
        "url": "http://site.com/rss",
        "minTime": "24",
        "minRatio": "1.5"
      },
      {
        "url": "http://site2.com/rss",
        "minTime": "72",
        "minRatio": "1.5"
      },
      {
        "url": "http://site2.com/rss?somefiler=1",
        "minTime": "24",
        "minRatio": "1.5"
      }
    ],
    "filters": {
      "include": [
        {
          "quality": "720p"
        }
      ]
    }
  }
```


####List monitoring config file to monitor a list called "your-list-name-partial" and auto pull shows that are 720p quality and paritally match the title.
```
[
  {
    "username": "trakt-user-name",
    "api_key": "",
    "list_name": "your-list-name",
    "type": "tv",
    "feedDestination": "###DOWNLOAD_DIR###/finished/tv",
    "like": true,
    "minorFeeds": [
      {
        "url": "http://site.com/rss",
        "minTime": "24",
        "minRatio": "1.5"
      },
      {
        "url": "http://site2.com/rss",
        "minTime": "72",
        "minRatio": "1.5"
      },
      {
        "url": "http://site2.com/rss?somefiler=1",
        "minTime": "24",
        "minRatio": "1.5"
      }
    ],
    "filters": {
      "include": [
        {
          "quality": "720p"
        }
      ]
    }
  }
]
```


###Last.FM Config
####Library monitoring config file to grab all releases that match your library that are mp3/v0vbr and the source is a cd.
```
[
  {
    "username": "last-fm-user-name",
    "api_key": "",
    "list_name": "your-list-name",
    "type": "music",
    "feedDestination": "###DOWNLOAD_DIR###/finished/music",
    "minorFeeds": [
      {
        "url": "http://site.com/rss",
        "minTime": "24",
        "minRatio": "1.5"
      },
      {
        "url": "http://site2.com/rss",
        "minTime": "72",
        "minRatio": "1.5"
      },
      {
        "url": "http://site2.com/rss?somefiler=1",
        "minTime": "24",
        "minRatio": "1.5"
      }
    ],
    "filters": {
      "exclude": [
        {"wordMatch": "scene"}
      ],
      "include": [
        {"source": "cd"},
        {"quality": "v0vbr"},
        {"codec": "mp3"}
      ]
    }
  }
]
```
