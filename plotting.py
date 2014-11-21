#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyqtplot as pt

from logging import Logger

#--------------------------------------------------------------------- 
# data plotting helper
#--------------------------------------------------------------------- 
class Plotter:
    """ 
    """

    #for several plots in the same window
    self.colors = ['b', 'g', 'r', 'w']

    def __init__(self, dataNames):
        self.keys = dataNames
        self.keys.append('t')

    def connect(self, logger):
        ''' registration routine
        this routine registers at the logger to get called whenever there is new data
        '''
        self.logger = logger
        self.logger.register(self.keys, self.update)

class PyQtGraphPlotter(Plotter):
    ''' Plotting Helper using PyQtgraph
    '''
    def __init__(self, dataNames):
        Plotter.__init__(dataNames)
        #create own QGraphicsWidget
        self.win = plt.plot([], [])
#        self.lines = ...

    def update(self, data):
        """ update routine
        will get called, whenever there is new data. Has to be implemented
        """
        for key, val in data.iteritems():
            self.lines[key].setData(val)



