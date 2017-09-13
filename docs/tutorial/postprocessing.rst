============================
Comparing Simulation Results
============================

After succesfully simulating your model, you might want to 
vary some of your variables to evaluate robustness or look for 
optimal values. 

Start the 'Ball and Beam' example again, run the simulation
and save the results to a .pmr file using the second button
in the top left corner of the interface.
Change the value of the mass (M) to 0.06, simulate again and
save the results. It is important that the second file is named
differently than the first.
Repeat this process with a mass of 0.07.

Open the Post-Processor using the second button from the right
in the top right corner of the interface. It appears in an
additional interface:

.. image:: ../pictures/postpr.*

Click on the button in the top left to load the three .pmr files.
Double-click on the postprocessor 'StepResponse' and cancel creating
an export folder. This will automatically present you the alternative
of the directory, where your .pmr files are stored.
You will be asked three times for the export folder. Use this to name
your results differently.

In the directory you chose, now there are 6 new files. 3 of them are
.pdf files, illustrating the step responses of the three simulations.

Load the remaining 3 .pof files into your MetaProcessor by clicking
the button in the top right corner of the interface.

Start the MetaProcessor by clicking on its name.
As a result, you receive a metric over mass diagram:

.. image:: ../pictures/postpr_result.*
