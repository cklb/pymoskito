import pymoskito as pm


class PolesITAEMetaProcessor(pm.XYMetaProcessor):
    """
    Metaprocessor to evaluate the ITAE error for different pole placements of
    different controllers.

    Run the `StepResponse` postprocessor with the results from the `pp_regimes`
    file the create the required input data.
    """

    def __init__(self):
        sort_key = ["modules", "Controller", "type"]
        x_path = ["modules", "Controller", "poles"]
        y_path = ["metrics", "L1NormITAE"]

        pm.XYMetaProcessor.__init__(self, x_path, y_path, sort_key, x_idx=0,
                                    title="ITAE Error over Pole Placement",
                                    x_label="Pole 0", y_label="ITAE Error",
                                    # line_style="bar"
        )


class MassMetricMetaProcessor(pm.XYMetaProcessor):

    def __init__(self):
        sort_key = ["modules", "Controller", "type"]
        x_path = ["modules", "Model", "M"]
        y_path = ["metrics", "L1NormITAE"]

        pm.XYMetaProcessor.__init__(self, x_path, y_path, sort_key)


pm.register_processing_module(pm.MetaProcessingModule, PolesITAEMetaProcessor)
pm.register_processing_module(pm.MetaProcessingModule, MassMetricMetaProcessor)
