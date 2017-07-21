# -*- coding: utf-8 -*-

import unittest
from json import JSONDecodeError
from unittest.mock import patch
import flannelfox.settings

class TestSettings(unittest.TestCase):

	@patch('flannelfox.settings.readSettingsFile')
	def test_updateSettings(self, mockData):

		mockData.return_value = '{"unittest": true}'

		flannelfox.settings.updateSettings()

		self.assertTrue('unittest' in flannelfox.settings.getSettings().keys())


	@patch('flannelfox.settings.readSettingsFile')
	def test_updateSettingsCatchesBadJson(self, mockData):

		mockData.return_value = 'string'

		with self.assertRaises(JSONDecodeError):
			flannelfox.settings.updateSettings()


if __name__ == '__main__':
	unittest.main()
