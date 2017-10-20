
Implementing a Model
--------------------

Now, we can start by creating a file called::

	model.py

The first lines should import the library NumPy_, the OrderedDictionary
class and PyMoskito itself:

.. _NumPy: http://www.numpy.org/

.. literalinclude:: minimalSystem/model.py
	:end-before: #settings
	:lineno-match:

Store the initial values of your model in variables at the beginning
of your code:

.. literalinclude:: minimalSystem/model.py
	:start-after: #settings
	:end-before: #class
	:lineno-match:
	
Name your class and make pm.Model its base class.
Create an OrderedDict called public_settings. All entries in this
dictionary will be accessable in the graphical interface of PyMoskito
during runtime.
While you have the freedom to name these entries as you like,
the entry "initial state" is obligatory and must contain the
initial state vector 
:
	
.. literalinclude:: minimalSystem/model.py
	:start-after: #class
	:end-before: #init
	:lineno-match:

Within the constructor, you must update the settings with the number of 
states and the number of inputs as seen in lines 36 and 37. 
It also is obligatory to call the constructor of the base class at the end.
To update the output information as seen in lines 38-41 is optional,
this will be added to the output diagrams:
	
.. literalinclude:: minimalSystem/model.py
	:start-after: #init
	:end-before: # shortcuts
	:lineno-match:

To prevent the model equations from resulting in huge lines of code, 
we highly recommend storing the model values in variables with short names:

.. literalinclude:: minimalSystem/model.py
	:start-after: # shortcuts
	:end-before: #state
	:lineno-match:
	
The calculation of the state derivatives takes place in a method,
that returns the results as an array:
	
.. literalinclude:: minimalSystem/model.py
	:start-after: #state
	:end-before: #root
	:lineno-match:
	
To create a valid derivation of the model base class, add these lines to your code:
	
.. literalinclude:: minimalSystem/model.py
	:start-after: #root
	:end-before: #output
	:lineno-match:

Everything the method calc_output returns will be defined as model output
and will therefore be displayed in an additional diagram Model.NAME.
In case you added information to the output vector in the constructor, 
NAME will be whatever you chose here:
	
.. literalinclude:: minimalSystem/model.py
	:start-after: #output
	:end-before: #register
	:lineno-match:

Do not forget to link your model to the toolbox at the 
very bottom of your code:
	
.. literalinclude:: minimalSystem/model.py
	:start-after: #register
	:lineno-match:
