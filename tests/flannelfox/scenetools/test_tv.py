# -*- coding: utf-8 -*-

import unittest
from flannelfox.scenetools import TV

class TestTv(unittest.TestCase):

	def test_parseTitle(self):

		testCases = [
			({'quality':'480p', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.480p.junk.here'),
			({'quality':'480i', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.480i.junk.here'),
			({'quality':'576p', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.576p.junk.here'),
			({'quality':'576i', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.576i.junk.here'),
			({'quality':'720p', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.720p.junk.here'),
			({'quality':'720i', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.720i.junk.here'),
			({'quality':'1080p', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.1080p.junk.here'),
			({'quality':'1080i', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.1080i.junk.here'),
			({'quality':'sd', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.sd.junk.here'),
			({'container':'mp4', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.mp4.junk.here'),
			({'container':'vob', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.vob.junk.here'),
			({'container':'iso', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.iso.junk.here'),
			({'container':'m4v', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.m4v.junk.here'),
			({'container':'m2ts', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.m2ts.junk.here'),
			({'container':'avi', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.avi.junk.here'),
			({'container':'ts', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.ts.junk.here'),
			({'container':'mkv', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.mkv.junk.here'),
			({'container':'wmv', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.wmv.junk.here'),
			({'container':'mpeg', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.mpeg.junk.here'),
			({'codec':'xvid', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.xvid.junk.here'),
			({'codec':'divx', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.divx.junk.here'),
			({'codec':'h264', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.h264.junk.here'),
			({'codec':'vc1', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.vc-1.junk.here'),
			({'codec':'asf', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.asf.junk.here'),
			({'codec':'h264hi10p', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.x264-hi10p.junk.here'),
			({'codec':'h264', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.x264.junk.here'),
			({'codec':'mpeg2', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.mpeg2.junk.here'),
			({'source':'dsr','episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.dsr.junk.here'),
			({'source':'dvdrip', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.dvdrip.junk.here'),
			({'source':'tvrip', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.tvrip.junk.here'),
			({'source':'vhsrip', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.vhsrip.junk.here'),
			({'source':'bluray', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.bluray.junk.here'),
			({'source':'bluray', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.bdrip.junk.here'),
			({'source':'bluray', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.brrip.junk.here'),
			({'source':'dvd5', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.dvd5.junk.here'),
			({'source':'dvd9', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.dvd9.junk.here'),
			({'source':'hddvd', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.hddvd.junk.here'),
			({'source':'webdl', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.webdl.junk.here'),
			({'source':'webrip', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.webrip.junk.here'),
			({'source':'bd25', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.bd25.junk.here'),
			({'source':'bd50', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.bd50.junk.here'),
			({'source':'hdtv', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.hdtv.junk.here'),
			({'source':'pdtv', 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01e01.pdtv.junk.here'),
			({'proper':True, 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01E01.proper.junk.here'),
			({'proper':True, 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01E01.repack.junk.here'),
			({'proper':True, 'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01E01.dirfix.junk.here'),
			({'episode': '1', 'season': '1', 'title': 'some show'} ,'some.show.s01E01.junk.here')
		]

		for test in testCases:
			self.assertEqual(test[0], TV.parseTitle(test[1]))

if __name__ == '__main__':
	unittest.main()