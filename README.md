#FlannelFox
FlannelFox is a Python application that can monitor a torrent client and perform regular management tasks such as:
* Ensuring torrents seed an appropriate amount of time after they complete
* Ensuring torrents seed an to an appropriate ration after they complete
* Manage how many torrents are running at a time
* Automatically load torrents from RSS feeds based of user defined filters


##What will it download and how does it know what I want?
FlannelFox uses set of JSON files that allow you to let it know what you want in three (3) ways:

* **Trakt.tv list monitoring** - You can create rule sets in the `~/.flannelfox/config/feeds/traktfeeds` folder that will monitor [Trakt.TV](http://trakt.tv) lists (public lists only at the moment) you specify for things you want. For best results make sure to only add movies OR tv series entries to your lists, episodes can cause issues in some instances

* **Last.fm Library monitoring** - You can create rule sets in the `~/.flannelfox/config/feeds/lastfmfeeds` folder that will monitor your library on [Last.FM](http://last.fm) and automatically grab releases from artists in your library.

* **Plain text matching** - Create rule sets in the `~/.flannelfox/config/feeds/rssfeeds` folder and they will be used to match the text entered against the feeds you specify. This is the most basic form of matching and can be a bit tedious. It is needed however, for those odd names that can not be pulled from Trakt or LastFM in a form the trackers use.


##How do I edit these files and what type of filtering can I do?
*Soon to come*


##Requirements/Dependencies
Python 2.7
* requests
* beautifulsoup4
* chardet
* pyOpenSSL
* ndg-httpsclient
* pyasn1


##Setup information


###Create .local to install as a user
```mkdir -p ~/.local/lib/python2.7/site-packages```


###Add ~/.local/bin to your path
```echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc```


###Compile FlannelFox
```python setup.py install --prefix=~/.local```

##Submissions
I am open for help and changes on this project, just make sure it is submitted in the form of a pullrequest and that it has been squashed/flattened into a single commit. To see the features that are needing a bit of love check the [help wanted](https://github.com/FlannelFox/FlannelFox/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) page.