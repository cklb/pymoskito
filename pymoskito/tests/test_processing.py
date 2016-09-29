#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_processing
----------------------------------

Tests for `processing` module.
"""

import unittest

from PyQt5.QtWidgets import QApplication

from pymoskito.processing_gui import PostProcessor


class TestProcessing(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.post = PostProcessor()

        # load some test data sets
        self.post._load_result_file("data/step_response.pmr")

    def test_postprocessor(self):
        self.post.run_processor("StepResponse", processor_type="post")

    def tearDown(self):
        del self.post

if __name__ == '__main__':
    unittest.main()
