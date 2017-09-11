
Implementing a Model
--------------------

Now, we can start by creating a file called::

	model.py

The first lines should import the library NumPy_, the ordered
dictionary class and PyMoskito itself. It is highly recommended to
store the initial values of your classes in an extra file called
settings.py and import it, as well:

.. _NumPy: http://www.numpy.org/

.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:end-before: #class
	:lineno-match:

Name your class and make pm.Model its base class.
Create an OrderedDict called public_settings. All entries in this
dictionary will be displayed in the 'Properties' window of PyMoskito:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #class
	:end-before: #init
	:lineno-match:

Within the constuctor, you can add settings that are not supposed
to be changed during runtime using settings.update(). This way,
it is possible to add information to the output diagram/s.
The last line of the constructor must call the constructor of
the base class:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #init
	:end-before: # shortcuts
	:lineno-match:
	
The calculation of the state derivatives takes place in a method,
that returns the results as an array:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #state
	:end-before: #root
	:lineno-match:
	
In case your model contains discontinuities, the solver needs
to be reseted. The method root_function() must return true 
and the state to continue with if a switching point is reached.
In this example, their are no discontinuities. If you are interested
in this method, please take a look at the 'Ball in Tube' example.

.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #root
	:end-before: #consistency
	:lineno-match:
	
Every model needs boundary conditions. 
In case they are violated, the following method must throw
an exception and the simulation will be stopped:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #consistency
	:end-before: #output
	:lineno-match:

Everything the method calc_output returns will be displayed
in PyMoskito in an extra diagram,
including the information you added in the constructor:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #output
	:end-before: #register
	:lineno-match:

Do not forget to link your model to the toolbox at the 
very bottom of your code:
	
.. literalinclude:: ../../pymoskito/examples/ballbeam/model.py
	:start-after: #register
	:lineno-match: