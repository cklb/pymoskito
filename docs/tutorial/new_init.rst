
The __init__ File
---------------------

The second file should be an initializing file called::

	__init__.py

Every additional file containg modules you create needs to be registered 
in this document, so it will be loaded
when starting PyMoskito. To register a new file called FILE_NAME.py,
add the following line to __init__.py::

	from . import FILE_NAME

We will shortly  create files named model and controller.
Add these two lines to register them::
	
	from . import model
	from . import controller