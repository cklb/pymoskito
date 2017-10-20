
Testing the Model 
--------------------------------------------
To test your source code, but also the equations of your model,
use PyMoskito to simulate your system with no input or controller.
Choose initial states that make the prediction of the systems
reaction easy and compare them with the simulation results.

After succesfully starting the program, 
you will see the interface of the toolbox:

.. image:: ../pictures/ModelTest1.jpg

Use the Properties Window (1) to choose the RodPendulumModel, 
the ODEInt Solver and the AdditiveMixer as ModelMixer. 
Change the initial state of the model to [0,100.0, 0,0]
and the end time of the solver to 20:

.. image:: ../pictures/ModelTest2.jpg

Click the button (2) or use the drop-down menu (3) to start the simulation.  

After a succesful simulation, all created diagrams will be listed in the Data Window (4).
Double click on one to display it:

.. image:: ../pictures/ModelTest3.jpg