# -*- coding: utf-8 -*-

import unittest
from flannelfox.scenetools import Music

class TestMusic(unittest.TestCase):

	def test_parseTitle(self):

		testCases = [
			({'quality':'apsvbr', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [apsvbr]'),
			({'quality':'apxvbr', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [apxvbr]'),
			({'quality':'v0vbr', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [v0vbr]'),
			({'quality':'v1vbr', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [v1vbr]'),
			({'quality':'v2vbr', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [v2vbr]'),
			({'quality':'v8vbr', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [v8vbr]'),
			({'quality':'128', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [128]'),
			({'quality':'192', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [192]'),
			({'quality':'256', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [256]'),
			({'quality':'320', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [320]'),
			({'quality':'24bit lossless', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [24bit lossless]'),
			({'quality':'lossless', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [lossless]'),
			({'releaseType':'album', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [album]'),
			({'releaseType':'soundtrack', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [soundtrack]'),
			({'releaseType':'ep', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [ep]'),
			({'releaseType':'anthology', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [anthology]'),
			({'releaseType':'compilation', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [compilation]'),
			({'releaseType':'dj mix', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [dj mix]'),
			({'releaseType':'single', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [single]'),
			({'releaseType':'live', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [live]'),
			({'releaseType':'remix', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [remix]'),
			({'releaseType':'bootleg', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [bootleg]'),
			({'releaseType':'interview', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [interview]'),
			({'releaseType':'mixtape', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [mixtape]'),
			({'releaseType':'unknown', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [unknown]'),
			({'releaseType':'concert recording', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [concert recording]'),
			({'releaseType':'demo', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [demo]'),
			({'codec':'aac', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [aac]'),
			({'codec':'ac3', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [ac3]'),
			({'codec':'dts', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [dts]'),
			({'codec':'mp3', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [mp3]'),
			({'codec':'flac', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [flac]'),
			({'source':'cd', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [cd]'),
			({'source':'dvd', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [dvd]'),
			({'source':'vinyl', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [vinyl]'),
			({'source':'soundboard', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [soundboard]'),
			({'source':'dat', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [dat]'),
			({'source':'cassette', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [cassette]'),
			({'source':'webdl', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [web-dl]'),
			({'source':'bluray', 'artist': 'some band', 'album': 'album name'} ,'some.band - album.name [blu-ray]'),
			({'artist': 'some band', 'album': 'album name'} ,'some.band - album.name')

		]

		for test in testCases:
			self.assertEqual(test[0], Music.parseTitle(test[1]))


if __name__ == '__main__':
	unittest.main()