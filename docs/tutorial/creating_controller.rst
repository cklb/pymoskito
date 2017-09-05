
Creating a Controller
---------------------

Describe how to create a controller.

Please note that all explanations are based on the model 
of the 'Ball and Beam' example.

Beschreibung import

.. literalinclude:: basic_files/controller_example.py
	:end-before: #import end
	:lineno-match:

Beschreibung Klassenkopf

.. literalinclude:: basic_files/controller_example.py
	:start-after: #class begin
	:end-before: #init
	:lineno-match:

Beschreibung init

.. literalinclude:: basic_files/controller_example.py
	:start-after: #init
	:end-before: #control
	:lineno-match:

Beschreibung control
	
.. literalinclude:: basic_files/controller_example.py
	:start-after: #control
	:end-before: #class end
	:lineno-match:

Do not forget to link all your controllers to the toolbox at the 
very bottom of your code:
	
.. literalinclude:: basic_files/controller_example.py
	:start-after: #register
	:lineno-match: