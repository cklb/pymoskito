# -*- coding: utf-8 -*-

import numpy as np
from collections import OrderedDict

import pymoskito as pm
from . import settings as st


class HighGainObserver(pm.Observer):
    """
    High Gain Observer for nonlinear systems
    """
    public_settings = OrderedDict([
        ("initial state", [0, 0]),
        ("poles", [-2, -2]),
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
    ])

    def __init__(self, settings):
        settings.update(output_dim=2)
        super().__init__(settings)

        self.output = np.array(self._settings["initial state"], dtype=float)

    def _observe(self, time, system_input, system_output):
        if system_input is None:
            return self.output

        y = system_output[0]
        uA = system_input[0]

        uA0 = self.settings['uA0']
        g = self.settings['g']
        Ku = self.settings['Ku']
        AS1 = self.settings['AS1']
        AS2 = self.settings['AS2']
        AT1 = self.settings['AT1']
        AT2 = self.settings['AT2']
        poles = self.settings['poles']

        a1 = AS1 * np.sqrt(2 * g / (AT1 ** 2 - AS1 ** 2))
        a2 = AS2 * np.sqrt(2 * g / (AT2 ** 2 - AS2 ** 2))

        if uA < uA0:
            u = 0
        else:
            u = uA - uA0

        dx1 = - a1 * np.sign(self.output[0]) * np.sqrt(np.abs(self.output[0])) + Ku / AT1 * u + \
              poles[0] * (self.output[0] - y)
        dx2 = - a2 * np.sign(self.output[1]) * np.sqrt(np.abs(self.output[1])) + \
              a1 * np.sign(self.output[0]) * np.sqrt(np.abs(self.output[0])) * AT1 / AT2 + \
              poles[1] * (self.output[0] - y)

        obsDx = np.array([dx1, dx2])

        self.output += self.step_width * obsDx

        return self.output


class CppHighGainObserver(pm.CppObserver):
    """
    Luenberger Observer that uses a simple euler forward integration
    """
    public_settings = OrderedDict([
        ("initial state", [0, 0]),
        ("poles", [-10, -10]),
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
    ])

    def __init__(self, settings):
        settings.update(output_dim=2)
        super().__init__(settings)

        self.output = np.array(self._settings["initial state"], dtype=float)

    def _observe(self, time, system_input, system_output):
        return self.output


pm.register_simulation_module(pm.Observer, HighGainObserver)
pm.register_simulation_module(pm.Observer, CppHighGainObserver)
