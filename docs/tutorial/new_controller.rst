
Implementing a Controller
-------------------------

A controller closes the loop, a class derived from the abstract class
:py:class:`~pymoskito.simulation_modules.Controller`.
Its only function calculates the controller output,
which acts as the actuating variable for the model.

In this scenario, the controller is linear. 
The linearization of the nonlinear model needs to be done beforehand
and is given in this tutorial as:

.. math::
    
    \boldsymbol{A} =
    \begin{pmatrix}
        0 & 0 & 1 & 0\\
        0 & 0 & 0 & 1\\
        0 & \frac{m^{2}l^{2}g}{z} & -\frac{JD}{z} & \frac{mld}{z}\\
        0 & -\frac{(M+m)mlg}{z} & \frac{mlD}{z} & -\frac{(M+m)d}{z}\\
    \end{pmatrix} 
    \ \
    \boldsymbol{B} =
    \begin{pmatrix}
        0\\
        0\\
        \frac{J}{z}\\
        -\frac{ml}{z}\\
    \end{pmatrix} 
    \ \
    \boldsymbol{C} =
    \begin{pmatrix}
        1 & 0 & 0 & 0\\
    \end{pmatrix} 
    
.. math::
    
    z = (M+m)\cdot J - m^{2}l^{2}
    
The linear control law is given with the control gain :math:`\boldsymbol{K}`
and the prefilter :math:`\boldsymbol{V}` as:

.. math::
    
    u = -\boldsymbol{K} \boldsymbol{x} + \boldsymbol{V} \boldsymbol{y_d}

Start by creating a file called::

    controller.py

Import the same classes as in the model class:

.. literalinclude:: minimalSystem/controller.py
    :end-before: #class begin
    :lineno-match:

Name your controller and make :py:class:`~pymoskito.simulation_modules.Controller` its base class.
Create :py:data:`public_settings` like before in your model.
Its entries will be accessable in the graphical interface of PyMoskito during runtime:

.. literalinclude:: minimalSystem/controller.py
    :start-after: #class begin
    :end-before: #init
    :lineno-match:

Within the constructor, it is obligatory to set the input order and an input type. 
The input order determines, how many derivatives of the trajectory will be required.
Valid input types are *system_state*, *system_output*, *Observer* and *Sensor*.
After all necessary updates, call the constructor of the base class as seen in line :py:data:`20`.

Store the linearized system matrices and the equilibrium state.
To make matrix operations possible, use the array type provided by NumPy.

PyMoskito's :doc:`Controltools <../modules/controltools>` provide functions
to calculate the values of a linear state feedback and a prefilter,
which can be used as seen in lines :py:data:`49-50`:

.. literalinclude:: minimalSystem/controller.py
    :start-after: #init
    :end-before: #control
    :lineno-match:

The only method to implement contains the control law and will be called by the solver during runtime.
Its parameters are the current time, the current values of trajectory,
feedforward and controller input.
The parameter :py:data:`**kwargs` is free to be used as needed, 
in this case it is ignored.
Since the controller stabilizes the system in [0,0,0,0],
the subtraction of the equilibrium from the state vector is necessary:

.. literalinclude:: minimalSystem/controller.py
    :start-after: #control
    :lineno-match:

Finally, import the controller file and register the controller class to PyMoskito
by adding two lines to the __main__.py file:

.. literalinclude:: minimalSystem/__main__.py
    :lines: 7
    :lineno-match:
    
.. literalinclude:: minimalSystem/__main__.py
    :lines: 12
    :lineno-match:
    