
Closing the Control Loop
--------------------------------------------

Start PyMoskito loading the created files.

Choose the RodPendulum as model, the ODEInt as solver,
the BasicController as Conntroller, the AdditiveMixer as ModelMixer
and the SmoothTransition as Trajectory.
Change the solver's end time to 10 and Input A of ModelMixer to Controller.

.. image:: ../pictures/ControllerTest1.jpg

After simulating, you find a few more diagrams in the data section, 
i.e. the control error:

.. image:: ../pictures/ControllerTest2.jpg

Feel free to experiment with the settings and see, 
if the control loop reacts the way you would have predicted.