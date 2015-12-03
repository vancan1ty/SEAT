SEAT -- Simple EEG Analysis Tool
===========================================

SEAT is a tool which provides features for EEG visualization and manipulation.  It is built around MNE-Python, and also calls into a number of other open-source libraries and tools.

Screenshot
-------------------------------------------
![Screenshot](SCREENSHOT.png?raw=true "Screenshot")

Features
-------------------------------------------
Currently the primary features of SEAT are:

1. EDF data import.
2. OpenGL-based EEG Visualization.
3. Easy channel selection, scrolling, amplitude adjustment, and frequency filtering. 
4. Integrated IPython shell for easy scripting and extension.
5. Time-Frequency decomposition and Spectral Maps.

Features in progress include:

1. Arbitrary dataset sizes (currently limited by memory).
2. Properly working spike detection (current algorithm is very poor).
3. Full annotation support

Credits
-------------------------------------------

SEAT was built for a Georgia Tech Senior Capstone project.  The group members were Currell Berry, Johnny Farrow, Utkarsh Garg, Justin Jackson, and Michael Long.

Currell Berry and Justin Jackson were the primary developers.
