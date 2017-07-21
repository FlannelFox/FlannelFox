# -*- coding: utf-8 -*-

import unittest
from flannelfox.scenetools import Movie

class TestMovie(unittest.TestCase):

	def test_parseTitle(self):

		testCases = [
			({'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016'),
			({'quality':'480p', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.480p'),
			({'quality':'480i', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.480i'),
			({'quality':'576p', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.576p'),
			({'quality':'576i', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.576i'),
			({'quality':'720p', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.720p'),
			({'quality':'720i', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.720i'),
			({'quality':'1080p', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.1080p'),
			({'quality':'1080i', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.1080i'),
			({'quality':'sd', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.sd'),
			({'container':'mp4', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.mp4'),
			({'container':'vob', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.vob'),
			({'container':'mpeg', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.mpeg'),
			({'container':'iso', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.iso'),
			({'container':'wmv', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.wmv'),
			({'container':'m4v', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.m4v'),
			({'container':'m2ts', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.m2ts'),
			({'container':'avi', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.avi'),
			({'container':'ts', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.ts'),
			({'container':'mkv', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.mkv'),
			({'container':'wmv', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.wmv'),
			({'codec':'xvid', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.xvid'),
			({'codec':'divx', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.divx'),
			({'codec':'h264', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.h264'),
			({'codec':'vc1', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.vc-1'),
			({'codec':'asf', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.asf'),
			({'codec':'h264hi10p', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.x264-hi10p'),
			({'codec':'h264', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.x264'),
			({'codec':'mpeg2', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.mpeg2'),
			({'source':'dsr', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.dsr'),
			({'source':'dvdrip', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.dvdrip'),
			({'source':'tvrip', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.tvrip'),
			({'source':'vhsrip', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.vhsrip'),
			({'source':'bluray', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.bluray'),
			({'source':'bluray', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.bdrip'),
			({'source':'bluray', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.brrip'),
			({'source':'dvd5', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.dvd5'),
			({'source':'dvd9', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.dvd9'),
			({'source':'hddvd', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.hddvd'),
			({'source':'webdl', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.webdl'),
			({'source':'webrip', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.webrip'),
			({'source':'bd25', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.bd25'),
			({'source':'bd50', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.bd50'),
			({'source':'hdtv', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.hdtv'),
			({'source':'pdtv', 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.pdtv'),
			({'proper':True, 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.proper'),
			({'proper':True, 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.repack'),
			({'proper':True, 'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016.dirfix'),
			({'year':'2016', 'title': 'some movie title'} ,'some.movie.title.2016')
		]

		for test in testCases:
			self.assertEqual(test[0], Movie.parseTitle(test[1]))

if __name__ == '__main__':
	unittest.main()
