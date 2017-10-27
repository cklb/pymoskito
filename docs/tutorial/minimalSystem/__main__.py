# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

import model
import controller

if __name__ == '__main__':

    # create an Application instance
    app = QApplication([])
    
    # launch gui
    prog = pm.SimulationGui()

    # show gui
    prog.show()

    # execute gui
    app.exec_()
