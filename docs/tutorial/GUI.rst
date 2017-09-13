========================
The Interface
========================

After :doc:`starting the 'Ball and Beam' example <starting>` 
and clicking on simulate (3), PyMoskito should look somewhat like this:
 
.. image:: ../pictures/BnB_rNos.*

In this Window, you have the following options:

(1) Load a *.sreg* file containing regimes.	

(2) Save the results of the current simulation to a .pof file. 
    This file can be evaluated by the postprocessor.
	
(3) Start the simulation using the current settings in the 
    'Properties' window.
	
(4) Simulate all loaded regimes. The results will be stored to a folder 
    as .pof files. If running for the first time, a default folder 
    needs to be set up.
	
(5) Show the results of the last succesful simulation in the 'Animation'
    window.

(6) Stop the currently running playback.

(7) The progress of playback. Move the slider manually to see a point of time of your choice.

(8) Choose the playback speed.

(9) Open the interface for the `post- and metaprocessor`.

(10) Reset the 'Animation' window to its initial state.

(11) The list of all currently loaded regimes. Double click on a regime to 
     load its settings into the 'Properties' window. Click once on a regime and hit
     'delete' to remove it from this list.

(12) The settings of the simulation. Double-click on a property to see its variables.
     Double-click on a value to open its drop-down menu or to enter something
     directly.

(13) After running a successful simulation, the results will be stored here.
     Double click on a set of data to see its diagram.

(14) Notifications like state of the simulation and error messages are displayed here.

(15) Watch the simulation playback after clicking play (5) here. `(Camera Manipulation?)`

     In case you did not install VTK, the animation will be in 2D instead:

     .. image:: ../pictures/BnB_2D.*

(16) Opened diagrams will appear in the same dock as the 'Placeholder'. 
     Switch between them by clicking on their tab.
	 
