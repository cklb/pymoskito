========================
Ball and Beam (ballbeam)
========================

A beam is pivoted on a bearing in its middle.
The position of a ball on the beam is controlable by applying a torque into the bearing.

The ball has a mass :math:`M`, a radius :math:`R` and a moment of inertia :math:`J_b`.
Its distance :math:`r` to the beam center is counted positively to the right.
For the purpose of simplification, the ball can only move in the horizontal direction.

The beam has a length :math:`L`, a moment of inertia :math:`J`
and its deflection from the horizontal line is the angle :math:`\theta`.

The task is to control the position  :math:`r` of the ball.
Actuating variable is the torque :math:`\tau`.

The system is taken from the publication [Hauser92]_ .

.. image:: ../pictures/ballbeam.*

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



.. [Hauser92] Hauser, J.; Sastry, S.; Kokotovic, P.
    Nonlinear Control Via Approximate
    Input-Output-Linearization: The Ball and Beam Example. IEEE Trans. on
    Automatic Control, 1992, vol 37, no. 3, pp. 392-398