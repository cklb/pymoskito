
Implementing a Model
--------------------

At first, a new class derived from the abstract class :py:class:`~pymoskito.simulation_modules.Model` is necessary.
Its basic functions will be calculating the state derivatives and the output from the model parameters, the current state and the input values.

Create a folder within a path of your choice.
All files created during this tutorial need to be stored here.
Create a file called::

    model.py

With the first lines of code, import the library NumPy_, 
the OrderedDictionary class and PyMoskito itself:

.. _NumPy: http://www.numpy.org/

.. literalinclude:: /../pymoskito/examples/simple_pendulum/model.py
    :end-before: # class
    :lineno-match:

Derive your class from :py:class:`~pymoskito.simulation_modules.Model`.
Next, create an :py:class:`OrderedDict` called :py:data:`public_settings`.
All entries in this dictionary will be accessible in the graphical interface of PyMoskito during runtime.
While you have the freedom to name these entries as you like,
the entry ``initial state`` is obligatory and must contain the initial state vector.
All values entered will be the initial values for the model parameters:

.. literalinclude:: /../pymoskito/examples/simple_pendulum/model.py
    :start-after: # class
    :end-before: # init
    :lineno-match:

Within the constructor, you must define the number of inputs and states.
Do so by storing these values in settings as seen in lines :py:data:`24` and :py:data:`25`. 
Adding output information as seen in line :py:data:`26` is optional,
this will make it easier to distinguish between several outputs of bigger systems.
It is obligatory to call the constructor of the base class at the end. 
The constructor's argument :py:data:`settings` is a copy of :py:data:`public_settings`
with all changes the user made in the interface:

.. literalinclude:: /../pymoskito/examples/simple_pendulum/model.py
    :start-after: # init
    :end-before: # state
    :lineno-match:

The calculation of the state derivatives takes place in a method
that returns the results as an array.
The method's parameters are the current time :py:data:`t`, the current state vector :py:data:`x`,
and the parameter :py:data:`args`. The later is free to be defined as you need it,
in this case it will be the force :py:data:`F` as the model input.
To keep the model equations compact and readable,
it is recommended to store the model values in variables with short names:

.. literalinclude:: /../pymoskito/examples/simple_pendulum/model.py
    :start-after: # state
    :end-before: # output
    :lineno-match:

The output of the system is calculated in a method with the current state vector as parameter.
Returning the results as an array as previously would be possible.
But in this case, the output is simply the position :py:data:`s` of the cart,
so extracting it from the state vector and returning it as a scalar is sufficient
:

.. literalinclude:: /../pymoskito/examples/simple_pendulum/model.py
    :start-after: # output
    :lineno-match:
    
This now fully implemented model class has a yet unknown behavior. 
To test it, the next step is to start PyMoskito for simulation purposes.
