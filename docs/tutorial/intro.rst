=============================
Minimal PyMoskito
=============================
PyMoskito simulates the control loop as seen in the schematics
below. This tutorial will focus on the part highlighted in blue,
since these modules are essential to run the toolbox:

.. image:: ../pictures/ctrl_loop_intro.png

Every block in this diagram represents an abstract class or base class, that PyMoskito offers.
By deriving from these base classes, it is easy to make sure
that implemented classes work well within the context of the toolbox.

From the highlighted classes, the trajectory generator and the model mixer are considered reusable,
therefore PyMoskito provides these classes fully implemented ready to use.
On the other hand, the model and the controller are determined by 
the specific system and have to be implemented to suit your problem.

If you would like to implement one of the not highlighted classes,
see the :doc:`Users Guide <../guide/index>` for help.