#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time
from PyQt4.QtCore import QObject, pyqtSignal

#--------------------------------------------------------------------- 
# data logging helper
#--------------------------------------------------------------------- 
class Logger(QObject):
    """ Main Data Logger
    """

    def __init__(self):
        self.subscribers = []
        self.data = {}
        self.timestep = 0
        self.filename = '../logs/'+time.strftime('%Y%m%d-%H%M%S')+'_logdata'

    def __enter__(self):
        return self

    def log(self, input_data):
        for key, val in input_data.iteritems():
            if key not in self.data:
                self.data.update({key: [val]})
            else:
                if len(self.data[key]) != self.timestep:
                    print 'ERROR in Logging Data! Too much input from: ', key
                    print self.timestep, '>',  len(self.data[key])
                self.data[key].append(val)

        if 't' in input_data:
            self.timestep += 1

    def update(self):
        for item in self.subscribers:
            #build paket
            paket = {}
            for element in item[1]:
                paket.update({element: self.data[element]})
            #send it
            item[0](paket)
        return

    def subscribe(self, keys, callback):
        for item in self.subscribers:
            if item[0] == callback:
                item[1].append(keys)

        self.subscribers.append((callback, keys))

    def __exit__(self, exc_type, exc_value, traceback):
        ''' dump data to disk
        '''
        with open(self.filename, 'w+') as f:
            f.write(repr(self.data))
    

