==========================
Tandem Pendulum (pendulum)
==========================

Two pendulums are fixed on a cart, which can move in the horizontal direction.

The cart has a mass :math:`m_0`. The friction between the cart and the surface causes a frictional force :math:`F_R`, in opposite direction as the velocity :math:`\dot{s}` of the cart.

Each pendulum has a mass :math:`m_i`, a moment of intertia :math:`J_i`, a length :math:`l_i` and an angle of deflection :math:`\varphi_i`.
The friction in the joint where the pendulums are mounted on the cart causes a frictional torque :math:`M_{ir}`,
in opposite direction as the speed of rotation :math:`\dot{\varphi}_i`.

The task is to control the position :math:`s` of the cart and the deflection angles :math:`\varphi_i` of the pendulums. 
Actuating variable is the force F.

.. image:: ../pictures/pendulum.png




old text below:

This example is a simulation study of a tandem or parallel double pendulum.
The provided regimes not only show the stabilization of the system in different
steady-states. (e.g. both pendulums pointing downwards or both pointing upwards)
but also ways to transition them between those states. (e.g. swinging them up)

Besides a rigid body model, this example features a pout mass model and also
a partially linearized version.

