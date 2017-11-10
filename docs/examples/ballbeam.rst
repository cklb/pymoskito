========================
Ball and Beam (ballbeam)
========================

A beam is pivoted on a bearing in its middle.
The position of a ball on the beam is controlable by applying a torque into the bearing.

<i-wo erwähnen, dass System in der Mitte nicht wohldefiniert!>

The ball has a mass :math:`M`, a radius :math:`R` and a moment of inertia :math:`J_b`.
Its distance :math:`r` to the beam center is counted positively to the right.
For the purpose of simplification, the ball can only move in the horizontal direction.

The beam has a length :math:`L`, a moment of inertia :math:`J`
and its deflection from the horizontal line is the angle :math:`\theta`.

The task is to control the position  :math:`r` of the ball.
Actuating variable is the torque :math:`\tau`.

The system is taken from the publication [Hauser92]_ .

.. image:: ../pictures/ballbeam.png

The state vector :math:`\boldsymbol{x}` is chosen as:

.. math::
    
    \boldsymbol{x} 
    =
    \begin{pmatrix}
        x_1 \\
        x_2 \\
        x_3 \\
        x_4
    \end{pmatrix} 
    =
    \begin{pmatrix}
        r \\
        \dot{r} \\
        \theta \\
        \dot{\theta}
    \end{pmatrix} 

The nonlinear model equations are given as:

.. math::
    
    \boldsymbol{\dot{x}} 
    =
    \begin{pmatrix}
        \dot{x}_1 \\
        \dot{x}_2 \\
        \dot{x}_3 \\
        \dot{x}_4
    \end{pmatrix} 
    =
    \begin{pmatrix}
        x_2 \\
        \frac{M R^2}{J_b + M R^2} (x_1 x_4^2 - g \sin(x_3)) \\
        x_4 \\
        \frac{\tau - M \cdot (2x_1 x_2 x_4 + g x_1 \cos(x_3))}{M x_1^2 + J + J_b}
    \end{pmatrix} 
    
Violations of the model's boundary conditions are the ball leaving the beam
or the beam's deflection reaching the vertical line:

.. math::

    |x_1| > \frac{L}{2}

.. math::

    |x_3| > \frac{\pi}{2}

The ball's position is chosen as output:

.. math::

    y = x_1 = r

The example comes with five controllers.
<controllers>
<fcontroller>
<gcontroller>
<jcontroller>
<lsscontroller>
<pixcontroller>

<feedforward><compensates linear part of system>

<Four different observer classes>
<3 Luenberger>
<1 high gain for nonlinear systems>

A 3D visualizer is implemented.
In case of missing VTK, a 2D visualization can be used instead.
  
An external :py:data:`settings` file contains all parameters.
All implemented classes import their initial values from here.

At program start, the main loads two regimes from the file :py:data:`default.sreg`.
<regimes>
<This regime shows a transition of the ball from the left to the right side
of the beam using a nonlinear controller>
<This regimes shows a typical step response of a linear controller>

The example also provides ten different modules for postprocessing. 
They plot different combinations of results in two formats, one of them being :py:data:`.pdf`.
The second format of files can be given to a metaprocessor.
<10x postprocessing>

The structure of :py:data:`__main__.py` allows starting the example without navigating to the directory
and using an :py:data:`__init__.py` file to outsource the import commands for additional files.
    
.. [Hauser92] Hauser, J.; Sastry, S.; Kokotovic, P.
    Nonlinear Control Via Approximate
    Input-Output-Linearization: The Ball and Beam Example. IEEE Trans. on
    Automatic Control, 1992, vol 37, no. 3, pp. 392-398