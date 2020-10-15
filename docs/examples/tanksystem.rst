============
2-Tanksystem
============

Two tanks are connected in series.
The inflow :math:`q_{\mathrm{in}}` of tank 1 is controlable by a pump with the voltage :math:`u_{\mathrm{A}}`,
whereby the in-, :math:`q_{1,2}` and outflow :math:`q_{\mathrm{out}}` of tank 2 are adjustable by valves.
Moreover, the height :math:`h_2` of tank 2 is measured and the height :math:`h_1` of tank 1 is unknown.
Both tanks have the same overall height :math:`H` and the same base area :math:`A_{\mathrm{T}`.


.. tikz::
    :include: ../tikz/tanksystem.tex

    The 2-Tanksystem


For the mathematical represenation both tanks are considered seperatly.

For the first tank:

.. math::

    A_{\mathrm{T} \dot{h}_1(t) & = q_{\mathrm{in}} - q_{1,2}

assuming the inflow

.. math::

    q_{\mathrm{in}} & = K u_{\mathrm{A}}

and the flow between the tanks

.. math::

    q_{1,2} & = C_{1,2}\sqrt{\rho g \left(h_1 - h_2\right)}

For the second tank:

.. math::

    A_{\mathrm{T} \dot{h}_2(t) & = q_{1,2} - q_{\mathrm{out}}

assuming the linear resistance to flow

.. math::

    q_{\mathrm{out}} & = C_{\mathrm{out}}\sqrt{\rho g h_2}

Violations of the model's boundary conditions are the water levels of both tanks exceed the maximal height :math:`H`

.. math::

    x_1 > H, \quad
    x_2 > H.

The height of tank 2

.. math::

    y & = x_2 = h_2

is chosen as output.

The example comes with two controllers.
The :py:class:`CppPIDController` implemenents a PID controller in C++ and uses :py:`pybind11` as binding between C++
and python.
The :py:class:`CppStateController` linearizes the nonlinear model in a chosen steady state
and applies static state feedback. The state feedback is implemented in C++ and uses :py:`pybind11` as binding between
C++ and python.

The example comes with one observers.
The :py:class:`CppObserver` implements a High-Gain observer for the nonlinear system in C++, which uses :py:`pybind11`
as binding between C++ and python.
The second of these improves its performance by using a different method of integration and the third uses the solver
for integration.

A 3D visualizer isn't implemented, but a 2D visualization can be used instead.

An external :py:data:`settings` file contains all parameters.
All implemented classes import their initial values from here.

At program start, the main loads two regimes from the file :py:data:`default.sreg`.
:py:data:`test-pid` is a setting of the PID controller to stabilize the water level of tank 2 at a specific height.
:py:data:`test-state` is a settings of the nonlinear observer and the linearized state feedback to stabilize the water
level of tank 2 at a specific height.

The structure of :py:data:`__main__.py` allows starting the example without navigating to the directory
and using an :py:data:`__init__.py` file to outsource the import commands for additional files.
