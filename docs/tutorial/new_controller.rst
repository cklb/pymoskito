
Implementing a Controller
-------------------------

To close the loop, we need a file called::
	
	controller.py

The Controller needs to do the same imports as the model:

.. literalinclude:: minimalSystem/controller.py
	:end-before: #settings
	:lineno-match:

Store the initial values of your model in variables:

.. literalinclude:: minimalSystem/controller.py
	:start-after: #settings
	:end-before: #class begin
	:lineno-match:
	
The same lines of code in two files is not the most elegant way of coding, 
but in this case it results in a minimum amount of files. 
Another way to structure you code could be to 
:doc:`store the settings in an additional file and import them <../guide/new_settings>`.
	
Name your controller and make pm.Controller its base class.
Create public_settings like before in your model.
Its entries will be accessable in the graphical interface of PyMoskito during runtime:

.. literalinclude:: minimalSystem/controller.py
	:start-after: #class begin
	:end-before: #init
	:lineno-match:

Within the constructor, it is obligatory to set the input order and an input type. 
The input order determines, how many derivatives of the trajectory will be required.
Valid input types are *system_state*, *system_output*, *Observer* and *Sensor*.
After all necessary updates, call the constructor of the base class:

.. literalinclude:: minimalSystem/controller.py
	:start-after: #init
	:end-before: #matrices
	:lineno-match:

Store the linearized system matrices and the equilibrium state. 
Additionally, initilize an output variable.
To make matrix operations possible, use the array type provided by NumPy:

.. literalinclude:: minimalSystem/controller.py
	:start-after: #matrices
	:end-before: #calculations
	:lineno-match:

PyMoskito's :doc:`Controltools <../modules/controltools>` provide functions
to calculate the values of a linear state feedback and a prefilter:

.. literalinclude:: minimalSystem/controller.py
	:start-after: #calculations
	:end-before: #control
	:lineno-match:

The only method to implement contains the control law.
Since the controller stabilizes the system in [0,0,0,0],
the subtraction of the equilibrium state is necessary
:
	
.. literalinclude:: minimalSystem/controller.py
	:start-after: #control
	:end-before: #register
	:lineno-match:

In case you would like to implement more than one controller, 
you can do so within the same file.
	
Do not forget to link all your controllers to the toolbox at the 
very bottom of your code:
	
.. literalinclude:: minimalSystem/controller.py
	:start-after: #register
	:lineno-match:
	
Finally, register the controller file by importing it in the __init__.py file:

.. literalinclude:: minimalSystem/__init__.py
	:lines: 2
	:lineno-match: