
Starting the Program
--------------------

For PyMoskito to start, an application needs to launch the toolbox and execute it.
To do so, create a file in the same directory as the model and name it::

    main.py

Copy the following code into your main file: 

.. literalinclude:: /../pymoskito/examples/simple_pendulum/main.py
    :language: python
    :lines: 1-5,9-13,21-24
    :linenos:
    :emphasize-lines: 5,10,13

Note the :py:data:`import` command in line :py:data:`5`,
which includes the earlier implemented model file in the application.
The command in line :py:data:`10` registers the model to the toolbox.
This lets PyMoskito know that this module is available 
and adds it to the eligible options in the interface.
Line :py:data:`13` finally starts our application.
    
Use the command line to navigate to the directory of the main file and the model file
and start the toolbox with the command::

    $ python main.py

The upstarting interface of PyMoskito
gives you the possibility to test the implemented model in the next step.
