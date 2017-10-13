============================
Simulating a Simple Pendulum
============================

The system we will work with is a pendulum, fixed on a movable
cart. System input is the force F, system output the 
position s of the cart. 

.. image:: ../pictures/rodPendulum.png

The state vector x is given as:

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
		s \\
		\varphi \\
		\dot{s} \\
		\dot{\varphi}
	\end{pmatrix} 

The model equations are given as:

.. math:: 

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
		\dot{s} \\
		\dot{\varphi} \\
		a \\
		\frac{a_{1}gm_{1}\sin(\varphi) - d_{1}\dot{\varphi}}
		{J_1 + a_1^2 m_1} + \frac{a_{1}m_{1}\cos(\varphi)}{J_1 + a_1^2 m_1} \cdot a
	\end{pmatrix} 

whereas 

.. math::

	a = \frac {F}{m_0}

The position `s` of the cart is the output of the system: 
	
.. math::

	y = x_1 = s


Create a folder with a path of your choice and name it simplePendulum.
All files created during this tutorial need to be stored here.	
To implement the presented system in PyMoskito, the mimimum to do is:

.. toctree::
  :maxdepth: 2

  new_main
  new_init
  new_model
  new_controller
  
All code is written in Python. If you want to refresh or expand 
your knowledge about this language, see the `Python Tutorial`_. 

.. _`Python Tutorial`: https://docs.python.org/3/tutorial/index.html