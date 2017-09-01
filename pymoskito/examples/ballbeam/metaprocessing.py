import pymoskito as pm


class MassMetricMetaProcessor(pm.XYMetaProcessor):

    def __init__(self):
        key = ""
        x_path = ["modules", "Model", "M"]
        y_path = ["modules", "Model", "J"]

        pm.XYMetaProcessor.__init__(self, key, x_path, y_path)

pm.register_processing_module(pm.MetaProcessingModule, MassMetricMetaProcessor)