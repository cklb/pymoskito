
Implementing a Controller
-------------------------

To close the loop, we need a file called::
	
	controller.py

Besides the same libraries and classes as in the model,
this specific controller imports pymoskito.controltools,
a package of :doc:`useful functions <../modules/controltools>`.
If you would like to outsource functions to another file,
you need to reimport them as done with linearise_system:

.. literalinclude:: ../../pymoskito/examples/ballbeam/controller.py
	:end-before: #import end
	:lineno-match:

Name your controller and make pm.Controller its base class.
Create public_settings like before in your model.
As you can guess from the line numbers, there is no restriction
to the amount of different controllers you can store in this file:

.. literalinclude:: ../../pymoskito/examples/ballbeam/controller.py
	:start-after: #class begin
	:end-before: #init
	:lineno-match:

Additionally to other updates within the constructor, it is obligatory
to set an input type before calling the base class constructor. 
Valid input types are *system_state*, *system_output*, *Observer* and *Sensor*.
Initialising the output is recommended.

To initialize the parameters K and V, which will later be used in the 
control law, functions from the earlier imported 
:doc:`package <../modules/controltools>` are used:

.. literalinclude:: ../../pymoskito/examples/ballbeam/controller.py
	:start-after: #init
	:end-before: #control
	:lineno-match:

The only method to implement contains the control law.
The parameters of this method are fix, but `**kwargs` can be substituted
by a parameter of your choice:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/controller.py
	:start-after: #control
	:end-before: #class end
	:lineno-match:

Do not forget to link all your controllers to the toolbox at the 
very bottom of your code:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/controller.py
	:start-after: #register
	:lineno-match: