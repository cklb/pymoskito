========================
Starting the Program
========================

For PyMoskito to start, an application needs to launch the toolbox and execute it.

To do so, create a file in the same directory as the model and name it::

    __main__.py

Copy the following code into your main file: 

.. literalinclude:: minimalSystem/__main__.py
    :language: python
    :lines: 1-6,8-11,13-21
    :linenos:

Note the :py:data:`import` command in line :py:data:`6`, 
which includes the earlier implemented model file in the application.
The command in line :py:data:`10` registers the model to the toolbox.
This lets PyMoskito know that this module is available 
and adds it to the eligible options in the interface.
    
Use the command line to navigate to the directory of the main file and the model file
and start the toolbox with the command::

    $ python __main__.py

The upstarting interface of PyMoskito
gives you the possibility to test the implemented model, which is the next step to do.