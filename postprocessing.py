# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class PostProcessor(QtCore.QObject):

    def __init__(self, parent =None):
        QtCore.QObject.__init__(self, parent)
