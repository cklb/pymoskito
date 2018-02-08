# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication

import pymoskito as pm

import model
import controller

if __name__ == '__main__':

    pm.register_simulation_module(pm.Model, model.PendulumModel)
    pm.register_simulation_module(pm.Controller, controller.BasicController)

    pm.run()
