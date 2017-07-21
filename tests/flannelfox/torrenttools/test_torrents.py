# -*- coding: utf-8 -*-

import unittest
from flannelfox.torrenttools.Torrents import Generic, TV, Movie, Music

class TestTorrents(unittest.TestCase):

    def test_GenericTorrent(self):
        testCases = [
            (
                {'title': 'some show s01e01 720p junk here'},
                Generic(torrentTitle='some.show.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some and show s01e01 720p junk here'},
                Generic(torrentTitle='some.&.show.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some show first edition s01e01 720p junk here'},
                Generic(torrentTitle='some.show:.first.edition.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some shows day s01e01 720p junk here'},
                Generic(torrentTitle='some.show\'s.day.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some show the first time s01e01 720p junk here'},
                Generic(torrentTitle='some.show,.the.first.time.s01e01.720p.junk.here')
            ),
            (
                {'title': 'somethat show s01e01 720p junk here'},
                Generic(torrentTitle='some\\that.show.s01e01.720p.junk.here')
            )
        ]

        for test in testCases:
            self.assertTrue(test[1] == test[0])

    def test_TVTorrent(self):
        testCases = [
            (
                {'title': 'some show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.s01.e01.720p.junk.here')
            ),
            (
                {'title': 'some show', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.ep01.720p.junk.here')
            ),
            (
                {'title': 'some show', 'episode': '1', 'quality': '720p', 'proper':True},
                TV(torrentTitle='some.show.e01.720p.proper.junk.here')
            ),
            (
                {'title': 'some show', 'year': '2016', 'month': '12', 'day': '1', 'quality': '720p', 'proper':True},
                TV(torrentTitle='some.show.2016.12.01.720p.dirfix.junk.here')
            ),
            (
                {'title': 'some show', 'year': '2016', 'month': '12', 'day': '1', 'quality': '720p', 'proper':True},
                TV(torrentTitle='some.show.01.12.2016.720p.repack.junk.here')
            ),
            (
                {'title': 'some show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.1x01.720p.junk.here')
            ),
            (
                {'title': 'some show', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.pt01.720p.junk.here')
            ),
            (
                {'title': 'some show', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.part01.720p.junk.here')
            ),
            (
                {'title': 'some show', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.001.720p.junk.here')
            ),
            (
                {'title': 'some and show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.&.show.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some show first edition', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show:.first.edition.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some shows day', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show\'s.day.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some show the first time', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show,.the.first.time.s01e01.720p.junk.here')
            ),
            (
                {'title': 'somethat show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some\\that.show.s01e01.720p.junk.here')
            ),
            (
                {'title': 'some show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.s01e01.[720p].junk.here')
            ),
            (
                {'title': 'some show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.s01e01.(720p).junk.here')
            ),
            (
                {'title': 'some show', 'season': '1', 'episode': '1', 'quality': '720p'},
                TV(torrentTitle='some.show.s01e01.{720p}.junk.here')
            ),
            (
                {'title': 'some show', 'season': '1', 'episode': '1', 'quality': '720p', 'codec': 'x264'},
                TV(torrentTitle='some.show.s01e01.720p.x264.junk.here')
            )
        ]

        for test in testCases:
            self.assertTrue(test[1] == test[0])

    def test_MovieTorrent(self):
        testCases = [
            (
                {'title': 'some show', 'year': '2009', 'codec':'x264', 'quality':'720p'},
                Movie(torrentTitle='some.show.2009.x264.720p')
            ),
            (
                {'title': 'some show', 'year': '2009', 'codec':'x264', 'quality':'720p'},
                Movie(torrentTitle='some.show.(2009).x264.720p')
            )
        ]

        for test in testCases:
            self.assertTrue(test[1] == test[0])


    def test_MusicTorrent(self):
        testCases = [
            (
                {'artist':'some artist', 'album':'album name', 'codec':'mp3', 'quality':'v0vbr'},
                Music(torrentTitle='some.artist.-.album.name.[2008-mp3-v0(vbr)]')
            ),
            (
                {'artist':'some artist', 'album':'album name', 'source':'cd', 'codec':'mp3', 'quality':'v0vbr'},
                Music(torrentTitle='some artist - album name [1997] [Single] - MP3 / V0 (VBR) / CD')
            ),
            (
                {'artist':'some artist', 'album':'album name'},
                Music(torrentTitle='some.artist.-.album.name')
            )
        ]

        for test in testCases:
            self.assertTrue(test[1] == test[0])


    def test_GenericTorrentMethods(self):
        torrent = TV(torrentTitle='some.show.s01e01.720p.junk.here')

        # Test that the title can be accessed
        self.assertEqual(torrent.get('title'), 'some show')

        self.assertEqual(torrent.get('invalidThing'), None)

        with self.assertRaises(KeyError):
            torrent.__getitem__('invalidThing')


        # Test to make sure a simple filter rule matches
        self.assertTrue(
            torrent.filterMatch([
                [
                    {
                        'key':'title',
                        'val':'some show',
                        'exclude': False
                    }
                ]
            ])
        )


        # Test to make sure an exclusion rule forces a mismatch
        self.assertTrue(
            not torrent.filterMatch([
                [
                    {
                        'key':'title',
                        'val':'some show',
                        'exclude': True
                    }
                ]
            ])
        )


        # Test to make sure an exclusion rule creates a match
        self.assertTrue(
            torrent.filterMatch([
                [
                    {
                        'key':'quality',
                        'val':'1080p',
                        'exclude': True
                    }
                ]
            ])
        )


        # Test to make sure match does not have to be the first filter in list
        self.assertTrue(
            torrent.filterMatch([
                [
                    {
                        'key':'title',
                        'val':'some show2',
                        'exclude': False
                    },
                ],
                [
                    {
                        'key':'title',
                        'val':'some show',
                        'exclude': False
                    },
                ]
            ])
        )


        # Test to make sure a complex match works
        self.assertTrue(
            torrent.filterMatch([
                [
                    {
                        'key':'title',
                        'val':'some show',
                        'exclude': False
                    },
                    {
                        'key':'season',
                        'val': '1',
                        'exclude': False
                    },
                    {
                        'key':'episode',
                        'val': '1',
                        'exclude': False
                    },
                    {
                        'key':'quality',
                        'val': '720p',
                        'exclude': False
                    }
                ]
            ])
        )


if __name__ == '__main__':
    unittest.main()