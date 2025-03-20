Currnt final version is V3. 

Required code file to run: 

  Autoalign_GUI_v{version number}.py : GUI code

  Autoalign_pv_v{version number}.py: autoalign code calling actual PVs

Autoalign_sim_v{version number}.py is not necessary for runnning the alignment, it is just for debug using the simulated data without actually moving motors.

Package needed: tkinter, matplotlib, numpy, epics, scipy, threading

Autoalign_2theta_GUI.py and Autoalign_2theta.py is for align the arm 2theta angle for each detector, can be adapted to very simple scan for the aim of pre-slewscan check.
