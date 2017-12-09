=========================
Ball in Tube (balltube)
=========================

A fan at the bottom of a tube produces an air stream moving upwards.
A ball levitates in the air stream.
The task is to control the ball's position :math:`z`.
Actuating variable is the motor's control signal :math:`u_{\textup{pwm}}`.
The system is shown in :numref:`fig-balltube_min`.

.. _fig-balltube_min:
.. figure:: ../../pictures/balltube_min.png
    :align: center
    :alt: Image of Ball in Tube System
    
    The ball in tube system

The example comes with two models, which differ in the reaction to the ball falling down.
The :py:class:`BallInTubeModel` makes the ball stick to the ground once it falls down.
The :py:class:`BallInTubeSpringModel` lets the ball to jump back up again.
These two classes are documented in detail in the following sections.

.. toctree::

  model1
  model2

The flatness based feedforward module described in the next section can be used to apply an input to the model during simulation.

.. toctree::
  
  ff1

The :py:class:`OpenLoop` controller ignores the current state and output of the model,
as well as trajectory values.
Instead it gives the opportunity to set the actuating variable :math:`u_{pwm}` manually.
A 3D visualizer is implemented.
In case of missing VTK, a 2D visualization can be used instead.
An external :py:data:`settings` file contains all parameters.
All implemented classes import their initial values from here.
Regimes are stored in two files.
At program start, the main function loads six regimes from the file :py:data:`default.sreg`.
In addition, nine regimes can be loaded manually from the file :py:data:`experiments.sreg`.
The example also provides a module for symbolic calculation.