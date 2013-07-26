NukeFXSExporter
===============
Nuke .fxs (Silhouette Shape format) exporter.


If you like it and use it frequently, please consider a small donation to the author.


This script will export Nuke shapes to a silhouette shape format .sfx file
SUPPORTED FEATURES:
Shape position/animation (baked)
Shape Opacity Animation
Shape Motion Blur
Shape Overlay Color
Shape Blending Modes
Shape Inverted attribute
Shape Open/Closed
OTHER:
Delete repeated baked keyframes when possible


KNOW LIMITATIONS
For now shapes will be baked on all keyframes, removing tracked layers info  and additional transforms
B-spline Tension is not supported yet
Feather not supported

USAGE

Select the Roto or Rotopaint node and run the script
You can set a the default folder/file path on init.py or menu.py with the code below:
os.environ['FXSEXPORTPATH'] = '/path/to/your/fxsfile'
