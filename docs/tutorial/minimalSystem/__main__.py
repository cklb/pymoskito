# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

import model
import controller

if __name__ == '__main__':

    app = QApplication([])
    prog = pm.SimulationGui()
    prog.show()
    app.exec_()