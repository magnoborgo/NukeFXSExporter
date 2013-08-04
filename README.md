NukeFXSExporter
===============
Nuke .fxs (Silhouette Shape format) exporter.
This script will export Nuke shapes to a silhouette shape format .sfx file

If you like it, use it frequently, or want to support further development please consider a small donation to the author.   
<a href='http://www.pledgie.com/campaigns/21123'><img alt='Click here to lend your support to: VFX tools coding project and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/21123.png?skin_name=chrome' border='0' /></a>

### SUPPORTED FEATURES: ###

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
Nuke animation curves are more complex then Silhouette ones, that will result in more keyframes on Silhouette.
B-spline Tension is not supported yet
Feather not supported

#### USAGE ####

Select the Roto or Rotopaint node and run the script

You can set a the default folder/file path on init.py or menu.py with the code below:   

    os.environ['FXSEXPORTPATH'] = '/path/to/your/fxsfile'

#### Licensing ####

This script is made avalable under a BSD Style license that is included in the package.
