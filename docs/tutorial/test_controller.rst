
Closing the Control Loop
--------------------------------------------

Start PyMoskito loading the created files.
Choose the :py:class:`RodPendulum` as :py:data:`Model`, the :py:data:`ODEInt` as :py:data:`Solver`,
the :py:data:`BasicController` as :py:data:`Controller`, the :py:data:`AdditiveMixer` as :py:data:`ModelMixer`
and the :py:data:`SmoothTransition` as :py:data:`Trajectory`.
Change the end time of :py:data:`Solver` to 10 and Input A of :py:data:`ModelMixer` to Controller.
To enter string values, type :py:data:`'Controller'` or :py:data:`"Controller"` and press enter to confirm the input.
The Properties window should now look like :numref:`fig-ControllerTest1`

.. _fig-ControllerTest1:
.. figure:: ../pictures/ControllerTest1.jpg
    :align: center
    :width: 55%
    :alt: Properties with Changes
    
    The properties window with changes for testing applied

After simulating, you find a few more diagrams in the data section.
:numref:`fig-ControllerTest2` shows the example of the control error.

.. _fig-ControllerTest2:
.. figure:: ../pictures/ControllerTest2.jpg
    :align: center
    :width: 80%
    :alt: Interface with Control Error
    
    PyMoskito's interface with the control error diagram displayed

Feel free to experiment with the settings and see, 
if the control loop reacts the way you would have predicted.
Keep in mind that the implemented controller is static.
The control law does not adapt to changes of the model parameters,
since the controller gain is calculated from values stored in the controller class.
You can use this effect to simulate the situation,
where the controller design was based on model parameters 
that differ from the real parameters of the process.

These were all the fundamental functions of PyMoskito considered necessary to work with it.
One more important, but also more advanced feature is the system's visualization in 2D or 3D.
This animation appears in the window at the top right, which remained grey during this tutorial 
(see :numref:`fig-ModelTest1`, :numref:`fig-ModelTest3`, :numref:`fig-ControllerTest2`).
For more information on this topic, see the :doc:`lection on visualization <../guide/visualization>`.
