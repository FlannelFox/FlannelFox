# -*- coding: utf-8 -*-

import unittest
from flannelfox.tools import dictMerge, changeCharset

class TestTools(unittest.TestCase):

	def test_dictMerge(self):
		dictA = {
			'a': None,
			'c': None,
			'g': {},
			'l':None,
			'm':None
		}

		dictB = {
			'a': 'b',
			'c': ['d', 'e', 'f'],
			'g': {
				'h': 'i',
				'j': 'k'
			},
			'l':0,
			'm':True
		}

		dictC = dictMerge(dictA, dictB)

		self.assertEqual(dictB, dictC)


	def test_dictMergeDetectsInvalidParameters(self):
		with self.assertRaises(TypeError):
			dictMerge(True, {})

		with self.assertRaises(TypeError):
			dictMerge({}, True)


	def test_changeCharset(self):

		convertedText = changeCharset(u'testing')
		self.assertIsInstance(convertedText, bytes)


if __name__ == '__main__':
	unittest.main()