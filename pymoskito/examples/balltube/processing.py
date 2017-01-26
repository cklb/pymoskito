import pymoskito.registry as pm
from pymoskito.processing_core import MetaProcessingModule
from pymoskito.generic_processing_modules import XYMetaProcessor


# TODO
class ErrorProcessor(XYMetaProcessor):

    def __init__(self):
        XYMetaProcessor.__init__(self, ["modules", "Controller"], ["modules", "Solver", "end time"],
                                 ["metrics", "L1NormITAE"])

