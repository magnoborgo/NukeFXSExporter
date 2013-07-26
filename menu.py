import nuke
nuke.tprint('Loading silhouetteFXSExporter.py')
try:
    from silhouetteFXSExporter import *
except:
    pass

#===============================================================================
# BVFX ToolBar Menu definitions
#===============================================================================
toolbar = nuke.menu("Nodes")
bvfxt = toolbar.addMenu("BoundaryVFX Tools", "BoundaryVFX.png")
bvfxt.addCommand('Silhouette FXS exporter', 'silhouetteFxsExporter()', icon='BoundaryVFX.png')