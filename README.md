# CSV-Processor
A desktop tool built in Python that converts raw IQMaps CSV exports into the format used in Carlson Survey. 
Eliminates manual reformatting by handling column cleanup, point renumbering, elevation calculation, feature normalisation, and group tagging.
All in a few seconds.

The Problem:
Every IQMaps survey export needed to be cleaned by hand before Carlson could use it. Wrong column order, inconsistent labels, values that needed calculating. One mistake and the CSV processing would fail, creating even more work.
It was slow, repetitive, and easy to get wrong.

The Solution:
This tool does it all automatically. Pick the raw file, get a clean output. Done.

CSV Processor:
*Removes unnecessary columns
*Renumbers survey points
*Re-calculates elevation
*Fixes inconsistent feature labels
*Groups, tags, and fills features across rows
*Merges notes
*Saves a clean output, keeps the original file.

Want a proper .exe that anyone can double-click? Here's all you need to do:
1. Install PyInstaller
2. Run this command in the terminal -> pyinstaller --onefile --windowed --add-data "logo.png;." --icon=icon.ico --name "CSV Processor" csv_processor.py
3. Open the dist/ folder that appeared in your project folder. Your CSV Processor.exe is in there, ready to go.

Author:
Erick Lucas Martins — github: @pumpkimhead
