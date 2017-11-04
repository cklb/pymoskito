========================
Ball and Beam (ballbeam)
========================

This example is a simulation study of the "Ball and Beam" system, as it is
described in [Hauser92]_ .

Model equations:

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
    
    \boldsymbol{\dot{x}} 
    =
    \begin{pmatrix}
        \dot{x_1} \\
        \dot{x_2} \\
        \dot{x_3} \\
        \dot{x_4}
    \end{pmatrix} 
    =
    \begin{pmatrix}
        x_2 \\
        B (x_1 x_4^2 - G \sin(x_3)) \\
        x_4 \\
        \frac{\tau - M \cdot (2x_1 x_2 x_4 + G x_1 \cos(x_3))}{M x_1^2 + J + J_b}
    \end{pmatrix} 

    B = \frac{M}{\frac{J_b}{R^2} + M}
    
Consistency Checks ("Check if the ball remains on the beam"):

.. math::

    x_1 > \frac{beam \ length}{2}, "Ball \ fell \ down"
    
    x_3 > \frac{\pi}{2}, "Beam \ reached \ critical \ angle"
    
Input: :math:`\tau` as Torque (?)

Output:

.. math::

    y = x_1 = r, Ball \ Position

    
.. image:: ../pictures/ballbeam.*

.. [Hauser92] Hauser, J.; Sastry, S.; Kokotovic, P.
    Nonlinear Control Via Approximate
    Input-Output-Linearization: The Ball and Beam Example. IEEE Trans. on
    Automatic Control, 1992, vol 37, no. 3, pp. 392-398