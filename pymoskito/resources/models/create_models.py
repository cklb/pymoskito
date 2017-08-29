import os
import pickle
import numpy as np
from scipy.signal import StateSpace, TransferFunction, step
import pyqtgraph as pg

"""
This module contains functions that will create pickle files which can be used
for the :py:class:`pm.LinearStateSpaceModel` and 
:py:class:`pm.LinearStateSpaceController` . 
"""


def export_model(steady_state_inputs, steady_state_outputs, ss, name):
    """
    Export the given state space model to a file.

    This file can be loaded by py:class:`pm.LinearStateSpaceModel` and
    :py:class:`pm.LinearStateSpaceController` .

    Args:
        steady_state_inputs (ndarray): Input used for linearisation.
        steady_state_outputs (ndarray): Output used for linearisation.
        ss (StateSpace): Statespace formulation of the system.
        name: Name of the System

    """
    data = dict(op_inputs=steady_state_inputs,
                op_outputs=steady_state_outputs,
                system=ss)
    own_path = os.path.dirname(__file__)
    with open(own_path + os.path.sep + name + ".pkl", "wb") as f:
        pickle.dump(data, f)


def create_pt1_model(k, t, plot=False):
    """
    Create the state space formulation of a PT1 plant.

    """
    tf = TransferFunction([k], [t, 1])
    ss = tf.to_ss()

    if plot:
        # let's have a look at the behavior
        t = np.linspace(0, 20)
        _, y = step(ss, 0, t)
        pg.mkQApp()
        pg.plot(t, y)
        pg.QAPP.exec_()

    return ss


if __name__ == '__main__':
    # run tests
    ss = create_pt1_model(1, 5, plot=True)
    export_model(np.zeros((1,)), np.zeros((1,)), ss, name="PT1Model")
