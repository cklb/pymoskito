#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt 
plt.ion()
from settings import *

#--------------------------------------------------------------------- 
# data logging helper
#--------------------------------------------------------------------- 
class Logger:
    """ base class for data logger
    """


    def __init__(self):
        self.data = {}
        self.data['t'] = []
        #TODO respect dimensions
        self.data['x'] = [[], [], [], []]

    def log(self, inputData):
        '''
        expects 1 value for time axis + list of x values
        '''

        if len(inputData) < 2:
            print 'Error: Data Set to small!'
            return


        self.data['t'].append(inputData[0])
        for index, val in enumerate(inputData[1]):
            self.data['x'][index].append(val)
        
        self.takeAction()

    def finalize(self):
        ''' dump data to disk
        '''
        #TODO
    
class GraphLogger(Logger):

    def __init__(self, name='Untitled', dim=2, x_range=[0, 10]):
        Logger.__init__(self)
        #TODO respect dimensions
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([], [], 'b-')
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(x_range)
        #self.figure.name(name)
        self.ax.grid()

    def takeAction(self):
        self.lines.set_xdata(self.data['t'])
        self.lines.set_ydata(self.data['x'][0])

        self.ax.relim()
        self.ax.autoscale_view()

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        return

