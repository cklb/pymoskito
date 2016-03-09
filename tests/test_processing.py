#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_processing
----------------------------------

Tests for `processing` module.
"""

import unittest
from PyQt4.QtGui import QApplication

from pymoskito import registry as pm
import pymoskito.generic_processing_modules as post_modules
from pymoskito.processing_gui import PostProcessor

class TestProcessing(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.post = PostProcessor()

        # load some test data sets
        self.post._load_result_file("data/step_response.pmr")

    def test_postprocessor(self):
        self.post.run_processor("StepResponse")

    def tearDown(self):
        del self.post

if __name__ == '__main__':
    unittest.main()
