from __future__ import division

import pymoskito.pymoskito as pm
from pymoskito.processing_core import MetaProcessingModule
from pymoskito.generic_processing_modules import XYMetaProcessor

__author__ = 'stefan'

class ErrorProcessor(XYMetaProcessor):

    def __init__(self):
        XYMetaProcessor.__init__(self, ["modules", "Controller"], ["modules", "Solver", "end time"],
                                 ["metrics", "L1NormITAE"])


pm.register_processing_module(MetaProcessingModule, ErrorProcessor)
