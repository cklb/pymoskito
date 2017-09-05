
Implementing a Model
--------------------


Please note that all explanations are based on the model 
of the 'Ball and Beam' example.

The first lines should import the library NumPy_, the ordered
dictionary class and PyMoskito itself. It is highly recommended to
store the initial values of your classes in an extra file called
settings.py and import it, as well:

.. _NumPy: http://www.numpy.org/

.. literalinclude:: basic_files/model_example.py
	:end-before: #class
	:lineno-match:

Name your class and make pm.Model its base class.
Create an OrderedDict called public_settings. All entries in this
dictionary will be displayed when starting PyMoskito:
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #class
	:end-before: #init
	:lineno-match:

The constructor must 
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #init
	:end-before: #state
	:lineno-match:
	
::Beschreibung state-function	
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #state
	:end-before: #root
	:lineno-match:
	
::Beschreibung root-function	
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #root
	:end-before: #consistency
	:lineno-match:
	
::Beschreibung consistency-function	
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #consistency
	:end-before: #output
	:lineno-match:

::Beschreibung output-function	
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #output
	:end-before: #register
	:lineno-match:

Do not forget to link your model to the toolbox at the 
very bottom of your code:
	
.. literalinclude:: basic_files/model_example.py
	:start-after: #register
	:lineno-match: