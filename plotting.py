#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView

from logging import DataLogger

#--------------------------------------------------------------------- 
# data plotting helper
#--------------------------------------------------------------------- 
class Plotter:
    """ 
    """
    def __init__(self, dataNames, logger):
        self.keys = [i for i in dataNames]
        self.keys.append('t')
        self.logger = logger
        self.logger.subscribe(self.keys, self.update)

    def update(self, data):
        """ update routine
        will get called, whenever there is new data. Has to be implemented
        """
        return

class PyQtGraphPlotter(Plotter):
    ''' Plotting Helper using PyQtgraph
    '''

    #for several plots in the same window
    colors = ['b', 'g', 'r', 'w']
    
    def __init__(self, dataNames, logger):
        Plotter.__init__(self, dataNames, logger)

        #create own QGraphicsWidget
        self.view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
        self.view.pg.setConfigOptions(antialies=True)
        self.view.setWindowTitle('Data')
        self.plt = self.view.pg.PlotItem()
        self.plt._setProxyOptions(deferGetattr=True)
        self.view.setCentralItem(self.plt)

        #create curves
        self.curves = {}
        for entry in dataNames:
            self.curves.update({entry: self.plt.plot()})


    def getWidget(self):
        return self.view

    def update(self, data):
        """ update routine
        updates data in plot window
        """
        for key, val in data.iteritems():
            if key == 't':
                pass
            else:
                self.curves[key].setData(val)


