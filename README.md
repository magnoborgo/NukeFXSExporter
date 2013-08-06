NukeFXSExporter
===============
Nuke .fxs (Silhouette Shape format) exporter.

This script will export Nuke shapes to a Silhouette Roto and Paint shape format .fxs file.    
That allows a Mocha to Silhouette shape export using Nuke.

If you like it, use it frequently, or want to support further development please consider a small donation to the author.   
<a href='http://www.pledgie.com/campaigns/21123'><img alt='Click here to lend your support to: VFX tools coding project and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/21123.png?skin_name=chrome' border='0' /></a>

You can find my contact info at http://boundaryvfx.com/tools

### SUPPORTED FEATURES: ###

Version 2.0: initial release Aug 5th 2013

This version introduces Shapes and Layers transforms exports: meaning "tracking data (point/cpin)" export
and avoiding baking the keyframes everywhere.

Version 2.0: initial release Aug 5th 2013

This version introduces Shapes and Layers transforms exports: meaning "tracking data (point/cpin)" export
and avoiding baking the keyframes everywhere.

* Shape position/animation
* Shape Opacity (Linear/Constant keyframes)
* Shape Motion Blur
* Shape Overlay Color
* Shape Blending Modes
* Shape Inverted attribute
* Shape Open/Closed
* Delete repeated baked keyframes when possible
* Layer nesting


#### COMPATIBILITY ####

Nukev7 and up

#### KNOW LIMITATIONS ####
* Nuke animation curves are more complex than Silhouette ones, that will result in more keyframes depending on the keyframe interpolation
* B-spline Tension not supported yet
* Feather not supported
* Rectangles are exported incorrectly (swapped tangents). 
  > Workaround: smooth and cusp the points back, it will fix the tangents.
* For heavy scenes, the script might take a while to give the task feedback, be patient.

#### USAGE ####

Select the Roto or Rotopaint node and run the script
You can set a the default folder/file path on init.py or menu.py with the code below:   

    os.environ['FXSEXPORTPATH'] = '/path/to/your/fxsfile'

#### Thanks ####
Kudos to the Silhouette team: Paul Miller and Perry Kivolowitz that helped me with important info.

#### Licensing ####
This script is made available under a BSD Style license that is included with the package.
