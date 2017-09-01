import pymoskito as pm


class MassMetricMetaProcessor(pm.XYMetaProcessor):

    def __init__(self):
        sort_key = ["modules", "Controller", "type"]
        x_path = ["modules", "Model", "M"]
        y_path = ["metrics", "L1NormITAE"]

        pm.XYMetaProcessor.__init__(self, x_path, y_path, sort_key)

pm.register_processing_module(pm.MetaProcessingModule, MassMetricMetaProcessor)
