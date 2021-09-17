"""
test_simulation_gui
----------------------------------

Tests for `simulation_gui` module.
"""

import sys
import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy, QTest
from PyQt5.QtWidgets import QApplication

from pymoskito import SimulationGui

app = QApplication([])


class TestGUIBasics(unittest.TestCase):

    def setUp(self):
        self.gui = SimulationGui()
        # self.gui.show()

    def test_defaults(self):
        # actions - enable at start
        self.assertTrue(self.gui.actLoadRegimes.isEnabled())
        # self.assertTrue(self.gui.actLoadStandardState.isEnabled())
        self.assertTrue(self.gui.actSimulateCurrent.isEnabled())
        self.assertTrue(self.gui.actSlow.isEnabled())
        self.assertTrue(self.gui.actFast.isEnabled())

        # actions - disabled at start
        self.assertFalse(self.gui.actSave.isEnabled())
        self.assertFalse(self.gui.actSimulateAll.isEnabled())
        self.assertFalse(self.gui.actPlayPause.isEnabled())
        self.assertFalse(self.gui.actStop.isEnabled())
        try:
            import vtk
            self.assertTrue(self.gui.actResetCamera.isEnabled())
        except ImportError:
            self.assertFalse(self.gui.actResetCamera.isEnabled())

        # timeline
        self.assertFalse(self.gui.timeSlider.isEnabled())

        # playback speed
        self.assertTrue(self.gui.speedControl.isEnabled())
        self.assertEqual(self.gui.speedControl.value(), 6)

    def tearDown(self):
        self.gui.close()


if __name__ == '__main__':
    unittest.main()
