
the __init__ file
---------------------

In the same directory as your main file, there should be an initializing file called::

	__init__.py

Every additional module you create needs to be registered in this document, so it will be loaded
when starting PyMoskito. To register a new module called MODULE_NAME.py,
add the following line to __init__.py::

	from . import MODULE_NAME
	