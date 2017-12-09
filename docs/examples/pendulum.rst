==========================
Tandem Pendulum (pendulum)
==========================

Two pendulums are fixed on a cart, which can move in the horizontal direction.
The cart has a mass :math:`m_0`. The friction between the cart and the surface causes a frictional force :math:`F_{\textup{r}} = d_0 \cdot \dot{s}`, 
opposing the movement of the cart.
Each pendulum has a mass :math:`m_i`, a moment of intertia :math:`J_i`, a length :math:`l_i` and an angle of deflection :math:`\varphi_i`.
The friction in the joint where the pendulums are mounted on the cart causes a frictional torque :math:`M_{\textup{r},i} = d_i \cdot \dot{\varphi}_i`,
opposing the rotational movement of the pendulums.
The task is to control the position :math:`s` of the cart and to stabilize the pendulums in either the upward or downward position. 
Actuating variable is the force F.
The system is shown in :numref:`fig-pendulum`.

.. _fig-pendulum:
.. figure:: ../pictures/pendulum.png
    :align: center
    :alt: Image of Pendulum System
    
    The pendulum system

The example comes with three models.
A point mass model, a rigid body model and a partially linearized model.
The state vector :math:`\boldsymbol{x}` is chosen in all three models as:

.. math::
    
    \boldsymbol{x} 
    =
    \begin{pmatrix}
        x_1 \\
        x_2 \\
        x_3 \\
        x_4 \\
        x_5 \\
        x_6
    \end{pmatrix} 
    =
    \begin{pmatrix}
        s \\
        \dot{s} \\
        \varphi_1 \\
        \dot{\varphi}_1 \\
        \varphi_2 \\
        \dot{\varphi}_2 
    \end{pmatrix} .

The class :py:class:`TwoPendulumModel` is the implementation of a point mass model.
The mass of each pendulum is considered concentrated at the end of its rod.
The resulting model equations 

.. math::

    \dot{x}
    =
    \begin{pmatrix}
        \dot{x}_1 \\
        \dot{x}_2 \\
        \dot{x}_3 \\
        \dot{x}_4 \\
        \dot{x}_5 \\
        \dot{x}_6
    \end{pmatrix} 
    =
    \begin{pmatrix}
        x_2 \\
        \frac{1}{M} \left( F_1 + F_2 + F - d_0 x_2 - \frac{d_1 x_4}{l_1} \cos(x_3) - \frac{d_2 x_6}{l_2} \cos(x_5) \right)\\
        x_4 \\
        \frac{g}{l_1}\sin(x_3) - \frac {d_1 x_4}{m_1 l_1^2} + \frac{\cos(x_3)}{l_1 M} \left( F_1 + F_2 + F - d_0 x_2 - \frac{d_1 x_4}{l_1} \cos(x_3) - \frac{d_2 x_6}{l_2} \cos(x_5) \right) \\
        x_6 \\
        \frac{g}{l_2}\sin(x_5) - \frac {d_2 x_6}{m_2 l_2^2} + \frac{\cos(x_5)}{l_2 M} \left( F_1 + F_2 + F - d_0 x_2 - \frac{d_1 x_4}{l_1} \cos(x_3) - \frac{d_2 x_6}{l_2} \cos(x_5) \right)
    \end{pmatrix}

with

.. math::
    
    M &= m_0 + m_1 \sin^2(x_3) + m_2 \sin^2(x_5)\\
    F_1 &= m_1 \sin(x_3)(g \cos(x_3) - l_1 x_4^2) \\
    F_2 &= m_2 \sin(x_5)(g \cos(x_5) - l_2 x_6^2)
    
are relatively simple and moments of inertia do not appear.

The class :py:class:`TwoPendulumRigidBodyModel` is the implementation of a rigid body model.
The rods are considered to have a mass which can not be neglected,
each pendulum has a moment of inertia :math:`J_{\textup{DP},i}`.
The model equations result in

.. math::

    \dot{x}
    =
    \begin{pmatrix}
        \dot{x}_1 \\
        \dot{x}_2 \\
        \dot{x}_3 \\
        \dot{x}_4 \\
        \dot{x}_5 \\
        \dot{x}_6
    \end{pmatrix} 
    =
    \begin{pmatrix}
        x_2 \\
        {\Phi_1}^{-1}(\Phi_2 \ + \ \Phi_3 \ + \ \Phi_4) \\
        x_4 \\
        \frac {1}{J_{\textup{DP},1}} \left( m_1^* l_1^* \cos(x_3) \dot{x}_2 + M_1 - d_1 x_4 +  m_1^* l_1^* g \sin(x_3)\right)\\
        x_6 \\
        \frac {1}{J_{\textup{DP},2}} \left( m_2^* l_2^* \cos(x_5) \dot{x}_2 + M_2 -  d_2 x_6 + m_2^* l_2^* g \sin(x_5)\right)
    \end{pmatrix}

with

.. math::
    
    \Phi_1 &= m_0^* + m_1^* + m_2^* - \frac{m_1^{*2} l_1^{*2} \cos^2(x_3)}{J_{\textup{DP},1}} - \frac{m_2^{*2} l_2^{*2} \cos^2(x_5)}{J_{\textup{DP},2}}\\
    \Phi_2 &= \frac {m_1^* l_1^* \cos(x_3) }{J_{\textup{DP},1}} (M_1 -  d_1 x_4 + m_1^* l_1^* g \sin(x_3))\\
    \Phi_3 &= \frac {m_2^* l_2^* \cos(x_5) }{J_{\textup{DP},2}}(M_2 - d_2 x_6 + m_2^* l_2^* g \sin(x_5)) \\
    \Phi_4 &= F - d_0 x_2 - m_1^* l_1^* x_4^2 \sin(x_3) - m_2^* l_2^* x_6^2 \sin(x_5) .
    
The class :py:class:`TwoPendulumModelParLin` is the implementation of the partially linearized point mass model.
The input is chosen as

.. math::

    u_{\textup{tr}} = \frac{1}{M} \left( F_1 + F_2 + F - d_0 x_2 - \frac{d_1 x_4}{l_1} \cos(x_3) - \frac{d_2 x_6}{l_2} \cos(x_5) \right),

with :math:`M`, :math:`F_1` and :math:`F_2` as before in :py:class:`TwoPendulumModel`. 
This transforms the model equations into the input affine form

.. math::

    \dot{x}
    =
    \begin{pmatrix}
        \dot{x}_1 \\
        \dot{x}_2 \\
        \dot{x}_3 \\
        \dot{x}_4 \\
        \dot{x}_5 \\
        \dot{x}_6
    \end{pmatrix} 
    =
    \begin{pmatrix}
        x_2 \\
        0 \\
        x_4 \\
        \frac{g}{l_1}\sin(x_3) - \frac {d_1 x_4}{m_1 l_1^2} \\
        x_6 \\
        \frac{g}{l_2}\sin(x_5) - \frac {d_2 x_6}{m_2 l_2^2}
    \end{pmatrix}
    +
    \begin{pmatrix}
        0 \\
        1 \\
        0 \\
        \frac{\cos(x_3)}{l_1}\\
        0\\
        \frac{\cos(x_5)}{l_2}
    \end{pmatrix}
    u_{\textup{tr}}.

    
All three models define the cart's position

.. math::

    y = x_1 = s

as the output of the system.
    
The example comes with five controllers.
The module :py:data:`symbolic_calculation` is used to calculate the gain and prefilter of the
classes :py:class:`LinearStateFeedback` and :py:class:`LinearStateFeedbackParLin`.
The :py:class:`LinearQuadraticRegulator`
calculates its gain and prefilter by solving the continuous algebraic Riccati equation.
The :py:class:`LjapunovController` is designed with the method of Ljapunov to stabilize the pendulums in the upward position.
And finally the :py:class:`SwingUpController`, especially designed to swing up the system using the :py:class:`LjapunovController` and 
to stabilize the system by switching to :py:class:`LinearStateFeedback` once the pendulums point upwards.

A 3D visualizer is implemented.
In case of missing VTK, a 2D visualization can be used instead.
An external :py:data:`settings` file contains all parameters.
All implemented classes import their initial values from here.
At program start, the main loads eleven regimes from the file :py:data:`default.sreg`.
The provided regimes not only show the stabilization of the system in different
steady-states (e.g. both pendulums pointing downwards or both pointing upwards)
but also ways to transition them between those states (e.g. swinging them up).
