
Implementing a Controller
-------------------------

To close the loop a controller has to be added. 
This can easily be done by deriving from the :py:class:`~pymoskito.simulation_modules.Controller` class.
Its task is to stabilize the pendulum by calculating a suitable input for the model.

To keep things simple, the controller is linear in this scenario
and it is based on the linearized system which is given by

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
    
with
    
.. math::
    
    z = J (M+m) - m^{2}l^{2}.
    
The linear control law is given by

.. math::
    
    u = -\boldsymbol{K} \boldsymbol{x} + \boldsymbol{V} \boldsymbol{y_d}

with the control gain :math:`\boldsymbol{K}`
and the prefilter :math:`\boldsymbol{V}`.
One possibility to calculate the control gain is by using the Ackermann formula.
    
With all necessary equations, the implementation of the controller class can begin.
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
which can be used as seen in lines :py:data:`49-50`. 
The method :py:data:`place_siso()` is an implementation of the Ackermann formula:

.. literalinclude:: minimalSystem/controller.py
    :start-after: #init
    :end-before: #control
    :lineno-match:

The only method to implement contains the control law and will be called by the solver during runtime.
Its parameters are the current time, the current values of trajectory,
feedforward and controller input.
The parameter :py:data:`**kwargs` is free to be used as needed, 
in this case it is ignored.
Since this controller will be stabilizing the system in the steady state [0,0,0,0],
it has to be subtracted to work on the small signal scale.

.. literalinclude:: minimalSystem/controller.py
    :start-after: #control
    :lineno-match:

Finally, import the controller file and register the controller class to PyMoskito
by adding two lines to the __main__.py file as done before for the model class:

.. literalinclude:: minimalSystem/__main__.py
    :lines: 7
    :lineno-match:
    
.. literalinclude:: minimalSystem/__main__.py
    :lines: 12
    :lineno-match:
    