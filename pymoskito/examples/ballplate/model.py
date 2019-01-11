import numpy as np
from collections import OrderedDict

import pymoskito as pm

from . import settings as st


class BallPlateModel(pm.Model):
    """
    Implementation of the Ball and Beam System
    """
    public_settings = OrderedDict([("M", st.M),
                                   ("R", st.R),
                                   ("J", st.J),
                                   ("Jb", st.Jb),
                                   ("G", st.G),
                                   ("beam length", st.beam_length),
                                   ("beam width", st.beam_width),
                                   ("beam depth", st.beam_depth),
                                   ("initial state", st.initial_state)
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=2)
        settings.update({"output_info": {
            0: {"Name": "ball position", "Unit": "m"},
            1: {"Name": "beam angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input tau
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        # tau = args[0]     darf ich das so schreiben?

        u = args[0]
        ddu = -st.K @ st.A_Ableitung @ st.A_Ableitung @ x
        # dx1 = x2
        # dx2 = st.G*Winkel_2
        # dx3 = x4
        # dx4 = -st.G*Winkel_1

        # return np.array([dx1, dx2, dx3, dx4])
        return st.A@x+st.B_1@u+st.B_2@ddu

    def root_function(self, x):
        """
        is not used
        :param x: state
        :return:
        """
        return [False]

    def check_consistency(self, x):
        """
        Check if the ball remains on the beam
        :param x: state
        """
        if abs(x[0]) > float(self._settings['beam length']) / 2:
            raise pm.ModelException('Ball fell down.')
        if abs(x[2]) > float(self._settings['beam depth']) / 2:
            raise pm.ModelException('Ball fell down.')

    def calc_output(self, input_vector):
        """
        return ball position as output
        :param input_vector: input values
        :return: ball position
        """
        return np.array([input_vector[0], input_vector[2]])


class BallPlateModel_nonlinear(pm.Model):
    """
    Implementation of the Ball and Beam System
    """
    public_settings = OrderedDict([("M", st.M),
                                   ("R", st.R),
                                   ("J", st.J),
                                   ("Jb", st.Jb),
                                   ("G", st.G),
                                   ("beam length", st.beam_length),
                                   ("beam width", st.beam_width),
                                   ("beam depth", st.beam_depth),
                                   ("initial state", st.initial_state)
                                   ])

    def __init__(self, settings):
        # add specific "private" settings
        settings.update(state_count=4)
        settings.update(input_count=2)
        settings.update({"output_info": {
            0: {"Name": "ball position", "Unit": "m"},
            1: {"Name": "beam angle", "Unit": "rad"},
        }})
        pm.Model.__init__(self, settings)

        # shortcuts for readability

    def state_function(self, t, x, args):
        """
        Calculations of system state changes
        :param x: state
        :param t: time
        :type args: system input tau
        """

        # definitional
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        x4 = x[3]
        # tau = args[0]     darf ich das so schreiben?

        u = -st.K @ x
        du = -st.K @ st.A_Ableitung @ x
        ddu = -st.K @ st.A_Ableitung @ st.A_Ableitung @ x
        Winkel_1 = -st.K_1 @ x
        Winkel_2 = -st.K_2 @ x
        dWinkel_1 = -st.K_1 @ st.A_Ableitung @ x
        dWinkel_2 = -st.K_2 @ st.A_Ableitung @ x
        ddWinkel_1 = -st.K_1 @ st.A_Ableitung @ st.A_Ableitung @ x
        ddWinkel_2 = -st.K_2 @ st.A_Ableitung @ st.A_Ableitung @ x
        A_21 = 1 / 2 * dWinkel_1 ** 2 + dWinkel_2 ** 2 - 1 / 2 * np.cos(2 * Winkel_2) * dWinkel_1 ** 2
        A_22 = 0
        A_23 = np.sin(Winkel_2) * ddWinkel_1
        A_24 = 2 * np.sin(Winkel_2) * dWinkel_1
        A_41 = -np.sin(Winkel_2) * ddWinkel_1 - 2 * np.cos(Winkel_2) * dWinkel_1 * dWinkel_2
        A_42 = -2 * np.sin(Winkel_2) * dWinkel_1
        A_43 = dWinkel_1 ** 2
        A_44 = 0
        b_2 = st.G * np.cos(Winkel_1) * np.sin(Winkel_2) - (st.Abstand_b * np.sin(Winkel_2) + 1 / 2 * st.Abstand_a * np.sin(2 * Winkel_2)) * dWinkel_1 ** 2 - st.Abstand_a * ddWinkel_2
        b_4 = -st.G * np.sin(Winkel_1) + (st.Abstand_b + st.Abstand_a * np.cos(Winkel_2)) * ddWinkel_1 - 2 * st.Abstand_a * np.sin(Winkel_2) * dWinkel_1 * dWinkel_2

        A = np.array([[0, 1, 0, 0],
                      [A_21, A_22, A_23, A_24],
                      [0, 0, 0, 1],
                      [A_41, A_42, A_43, A_44]])
        b = np.array([[0],
                      [b_2],
                      [0],
                      [b_4]])
        dx1 = x2
        dx2 = A_21 + A_22 + A_23 + A_24 + b_2
        dx3 = x4
        dx4 = A_41 + A_42 + A_43 + A_44 + b_4
        return np.array([dx1, dx2, dx3, dx4])
        # return A@x+b

    def root_function(self, x):
        """
        is not used
        :param x: state
        :return:
        """
        return [False]

    def check_consistency(self, x):
        """
        Check if the ball remains on the beam
        :param x: state
        """
        if abs(x[0]) > float(self._settings['beam length']) / 2:
            raise pm.ModelException('Ball fell down.')
        if abs(x[2]) > float(self._settings['beam depth']) / 2:
            raise pm.ModelException('Ball fell down.')

    def calc_output(self, input_vector):
        """
        return ball position as output
        :param input_vector: input values
        :return: ball position
        """
        return np.array([input_vector[0], input_vector[2]])


pm.register_simulation_module(pm.Model, BallPlateModel)
pm.register_simulation_module(pm.Model, BallPlateModel_nonlinear)