# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np

import pymoskito as pm
from . import settings as st


class CppHighGainObserver(pm.Observer, pm.CppBase):
    """
    High Gain Observer implemented in cpp with pybind11
    """
    public_settings = OrderedDict([
        ("initial state", [0.0, 0.0]),
        ("poles", [-1, -1]),
        ("tick divider", 1),
        ("AT1", st.AT1),
        ("AT2", st.AT2),
        ("hT1", st.hT1),
        ("hT2", st.hT2),
        ("AS1", st.AS1),
        ("AS2", st.AS2),
        ("g", st.g),
        ("Ku", st.Ku),
        ("uA0", st.uA0),
        ("dt", 0.1),
    ])

    def __init__(self, settings):
        settings.update(output_dim=2)
        pm.Observer.__init__(self, settings)
        pm.CppBase.__init__(self,
                            module_name='HighGainObserver',
                            module_path=__file__)

        obsClass = self.get_class_from_module('HighGainObserver')
        self.obs = obsClass(self._settings["AT1"],
                            self._settings["AT2"],
                            self._settings["AS1"],
                            self._settings["AS2"],
                            self._settings["Ku"],
                            self._settings["uA0"],
                            self._settings['dt'])
        self.obs.setInitialState(np.array(self._settings["initial state"]))
        self.obs.setGain(np.array(self._settings["poles"]))

    def _observe(self, time, system_input, system_output):
        if system_input is None:
            return np.array(self._settings["initial state"])

        y = system_output[0]
        uA = system_input[0]
        res = self.obs.compute(y, uA)

        return np.array(res)


pm.register_simulation_module(pm.Observer, CppHighGainObserver)
