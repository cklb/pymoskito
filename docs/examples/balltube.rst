=======================
Ball in Tube (balltube)
=======================

This example is a simulation study of a levitating ball in a tube.

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
        ? \\
        \dot{?} \\
        z \\
        \dot{z}
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
        -\frac{1}{T^2} x_1 - \frac{2 d}{T} x_2 + \frac{k_s Vcc}{255 T^2} u\\
        x_4 \\
        \frac{k_L}{m}(\frac{k_V x_1 - A_B x_4}{A_{Sp}})^2-g
    \end{pmatrix} 
    
Spring model only:

.. math::
    
    ( if(x_3) < 0 ) \ \dot{x_4} = \frac{K x_3}{m} - \frac{D x_4}{m} + \frac{k_L}{m}(\frac{k_V x_1 - A_B x_4}{A_{Sp}})^2-g
    
Consistency Checks ():

.. math::
    
    x_3 > tube \ length, "Ball \ flew \ out \ of \ the \ tube"
    
Root function("in this case this means zero crossing detection for the balls elevation."):
    
    x_3 <= 0, setze \ x_3=x_4=0
    
    x_1 <= 0, setze \ x_1=x_2=0
 
Input: :math:`u` as (?)

Output:

.. math::

    y = x_3 = z, Ball \ Position

.. image:: ../pictures/balltube.*