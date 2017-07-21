# -*- coding: utf-8 -*-

import unittest, os
from unittest.mock import patch

from flannelfox.queuedaemon import QueueReader

class TestQueueDaemon(unittest.TestCase):

	def test_queueReader(self):

		queueReader = QueueReader()
