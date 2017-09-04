
The default File
---------------------

A regime is a preset of settings. 
It can be loaded from or saved into a file.
If you want your example to start up with a loaded regime, or maybe multiple, 
you need a file called::

	default.sreg
	
Since most editing programs do not know this format, it might be easier to copy
and work with the default file from here::

	pymoskito/docs/tutorial/basic_files/default.sreg
	
This file will be loaded by the code in lines 26-29 of the `main file 
<https://pymoskito.readthedocs.io/en/stable/Tutorial/creating_main.html>`_.

To create a file with multiple regimes, just add the following code at the 
bottom of your existing default file again:

.. literalinclude:: basic_files/default.sreg
	:linenos: