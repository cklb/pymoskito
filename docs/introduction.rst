Introduction
============

What is PyMoskito ?
-------------------

PyMoskito aims to be a useful tool for students and researchers in the field of
control theory that performs repetitive task occurring in modelling as well as
controller and observer design.

The toolbox consists of two parts: Part one -the core- is a modular simulation
circuit whose parts (Model, Controller and many more)
can be easily fitted to one's personal needs by using one of the "ready to go"
variants or deriving from the more powerful base classes.

To configure this simulation loop and to analyse its results, part two
-the frontend- comes into play. The graphical user interfaces not only allows
one to accurately tune the parameters of each part of the simulation but also
allows to automate simulation runs e.g. to simulate different combinations of
modules or parameters.
This batch-like interface is feed by human readable yaml files
which make it easy to store and reproduce simulated setups.
Furthermore PyMoskito offers possibilities to run postprocessing on the
generated results and easily lets you create plots for step responses.


What is PyMoskito not ?
-----------------------

Although the simulation loop is quite flexible it is **not** a complete block
oriented simulation environment for model based-design but ideas for the
development in this direction are always appreciated.

