=======================
Ball in Tube Model
=======================

A fan at the bottom of a tube produces an air stream moving upwards.
A ball levitates in the air stream.

The fan rotates with the rotational speed :math:`\eta`.
It produces an air stream with the velocity :math:`v`.
The factor :math:`k_L` describes the proportionality between the air's volume flow rate and the fan's rotational speed.
The motor driving the fan is modeled as a PT2-element with the amplification :math:`k_s`,
the damping :math:`d` and the time constant :math:`T`.
An Arduino Uno controls the motor,
its discrete control signal :math:`u_{pwm}` has a range of :math:`0 - 255`
and amplifies the supply voltage :math:`V_{cc}`.

The ball covers an area :math:`A_B` and has a mass :math:`m`.
Its distance to the tube's bottom is the position :math:`z`.
The gap between the ball and the tube covers an area :math:`A_{Sp}`.
The factor :math:`k_V` describes the proportionality between
the force of flow resistance and the velocity of the air streaming through the gap.

The tube has a height :math:`h`.

The task is to control the ball's position :math:`z`.
Actuating variable is the motor's control signal :math:`u_{pwm}`.

.. figure:: ../../pictures/balltube.png
    :align: center
    :alt: Image of Ball in Tube System
    
    The ball in tube system in detail

TWith the state vector 

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
        \eta \\
        \dot{\eta} \\
        z \\
        \dot{z}
    \end{pmatrix} ,

the model equations are given by

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
        -\frac{1}{T^2} x_1 - \frac{2 d}{T} x_2 + \frac{k_s}{T^2} \frac{u_{pwm}}{255} V_{cc} \\
        x_4 \\
        \frac{k_L}{m}(\frac{k_V x_1 - A_B x_4}{A_{Sp}})^2-g
    \end{pmatrix}.
    
In case of the ball falling down and reaching a position :math:`x_3 < 0` below the fan,
the root function of the model overrides the ball's position :math:`x_3 = 0` and velocity :math:`x_4 = 0`.
    
The model's boundary condition is violated if the ball leaves the tube on the upper end:

.. math::
    
    x_3 > h

The ball's position 

.. math::

    y = x_3 = z

is chosen as output.