# Boundary Visual Effects - Silhouette Exporter
# Version 1.023
#
# For greeting, bugs, and requests email me at mborgo[at]boundaryvfx.com
# Compatibility: Silhouette v4.1 and up, not tested in previous versions
#
# If you like it and use it frequently, please consider a small donation to the author,
# via Paypal on the email mborgo[at]boundaryvfx.com

#===============================================================================
# This script will export Nuke shapes to a silhouette shape format .sfx file
#===============================================================================
# SUPPORTED FEATURES:
# Shape position/animation (baked)
# Shape Opacity Animation
# Shape Motion Blur
# Shape Overlay Color
# Shape Blending Modes
# Shape Inverted attribute
# Shape Open/Closed
# OTHER:
# Delete repeated baked keyframes when possible
#===============================================================================
# KNOW LIMITATIONS
#===============================================================================
# For now shapes will be baked on all keyframes, removing tracked layers info  and additional transforms
# B-spline Tension is not supported yet
# Feather not supported
#===============================================================================
# TO DO
#===============================================================================
# if env variable is not used, ask for a file path to save (this could go into other scripts too)
# Layer opacity multiplier
# Root layer transforms - check if its being used.
# Do not bake the node, its not needed. Maybe copy node before baking leaving the original intact
# bake curves mode like on the stroke script
# verify matrix translation nuke/sil (check mocha weird value)
#===============================================================================
#===============================================================================
# Version Log
# v1.023 2013/07/22
# remove all baked repeated keyframes.
# fixed bezier handle position on export.
# shape overlay/invert/blendmode/mblur/open/visibility support added
# v1.01 
# Implemented opacity animation
# Node is copyed before running the script prevent changes on the original node
# v1 (2013/06/06)
# Initial release
#===============================================================================
#===============================================================================
# USAGE
#===============================================================================
# Select the Roto or Rotopaint node and run the script
# You can set a the default folder/file path on init.py or menu.py with the code below:
# os.environ['FXSEXPORTPATH'] = '/path/to/your/fxsfile'



# Copyright (c) 2013, Magno Borgo
# All rights reserved.
#
# BSD-style license:
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Magno Borgo or its contributors may be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
#BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
#OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import nuke, nukescripts, nuke.rotopaint as rp, nuke.splinewarp as sw, math
import time, threading
import sys, os
import xml.etree.ElementTree as ET

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def rptsw_walker(obj, list):
    for i in obj:
        x = i.getAttributes()  
        if isinstance(i, nuke.rotopaint.Shape):
            list.append([i, obj]) 
        if isinstance(i, nuke.rotopaint.Layer):
            list.append([i, obj])
            rptsw_walker(i, list)
    return list

    
def rptsw_TransformToMatrix(point, transf, f):
    
    extramatrix = transf.evaluate(f).getMatrix()
    vector = nuke.math.Vector4(point[0], point[1], 1, 1)
    x = (vector[0] * extramatrix[0]) + (vector[1] * extramatrix[1]) + extramatrix[2] + extramatrix[3]
    y = (vector[0] * extramatrix[4]) + (vector[1] * extramatrix[5]) + extramatrix[6] + extramatrix[7]
    z = (vector[0] * extramatrix[8]) + (vector[1] * extramatrix[9]) + extramatrix[10] + extramatrix[11]
    w = (vector[0] * extramatrix[12]) + (vector[1] * extramatrix[13]) + extramatrix[14] + extramatrix[15]
    vector = nuke.math.Vector4(x, y, z, w)
    vector = vector / w
    return vector
  
def rptsw_TransformLayers(point, Layer, f, rotoRoot, rptsw_shapeList):
    if Layer == rotoRoot:
 
        transf = Layer.getTransform()
        newpoint = rptsw_TransformToMatrix(point, transf, f)
       
    else:

        transf = Layer.getTransform()
        newpoint = rptsw_TransformToMatrix(point, transf, f)
        for x in rptsw_shapeList: #look the layer parent
            if x[0] == Layer:
                newpoint = rptsw_TransformLayers(newpoint, x[1], f, rotoRoot, rptsw_shapeList)
    return newpoint

def rptsw_Relative_transform(relPoint, centerPoint, centerPointBaked, transf, f, rotoRoot, rptsw_shapeList, shape):
    transfRelPoint = [0,0]
    count = 0
    for pos in relPoint:
        transfRelPoint[count] = centerPoint[count] + (relPoint[count] * -1)
        count +=1
    transfRelPoint = rptsw_TransformToMatrix(transfRelPoint, transf, f)                             
    transfRelPoint = rptsw_TransformLayers(transfRelPoint, shape[1], f, rotoRoot, rptsw_shapeList)
    count = 0
    for pos in relPoint:    
        relPoint[count] = (transfRelPoint[count] + (centerPointBaked[count] * -1)) *-1
        count+=1
    return relPoint


def worldToImageTransform(value,rotoNode,axis):
    """
    converts values to Silhouette values (image transform, project resolution independent)
    """
    nodeFormat = rotoNode['format'].value()
    if axis == "x":
        transform = ((value - (nodeFormat.width()/2))/nodeFormat.height())* nodeFormat.pixelAspect()
    else:
        transform = ((nodeFormat.height()-value) - (nodeFormat.height()/2))/nodeFormat.height()
    return transform
    
def parseShapeFlags(flags):
    flaglist = []
    NukeFlags = ["eBreakFlag","eTangentLengthLockFlag","eKeySelectedFlag",
                 "eLeftTangentSelectedFlag","eRightTangentSelectedFlag",
                 "eOpenFlag","eSelectedFlag","eActiveFlag","eVisibleFlag",
                 "eRenderableFlag","eLockedFlag","ePressureInZFlag","eNukeAnimCurveEvalFlag",
                 "eRelativeTangentFlag"]
    #allflags = "000000000011111111111111"
    #===========================================================================
    # converts integers to binary for flag check
    #===========================================================================
    getBin = lambda x, n: x >= 0 and str(bin(x))[2:].zfill(n) or "-" + str(bin(x))[3:].zfill(n)
    binflags = getBin(flags,len(NukeFlags))
    for pos in range(0,len(NukeFlags)):
        if binflags[pos] == "1":
            flaglist.append(NukeFlags[len(NukeFlags)-1-pos])
#             print "FLAG: %s" % NukeFlags[len(NukeFlags)-1-pos]

    return flaglist


def bakeShapes(shape, fRange, rotoNode, rptsw_shapeList,task,fxsExport):
    #===========================================================================
    # CHECK FOR 1 POINT SHAPE AND IGNORE IT
    #===========================================================================
    if len(shape[0]) <= 1:
        return
    curvetype = ""

    
    shapeRawInfo = shape[0].serialise()
    shapeRawInfo = shapeRawInfo.split('\n')
    if [True for string in ["{curvegroup ", "{cubiccurve "] if shapeRawInfo[0].count(string) > 0]:
        curve = shapeRawInfo[0].split()
        curvetype = curve[3]
    shapetype = "Bezier" if curvetype == "bezier" else "Bspline"

    #===========================================================================
    # get shape flags / cubic curve flags
    #===========================================================================
    shapeFlags = int(shapeRawInfo[0].split()[2])
    shapeFlags = parseShapeFlags(shapeFlags)
    ccshapeFlags = shapeRawInfo[2]
    ccshapeFlags = int(ccshapeFlags[1:-1].split()[1]) #str formatting
    ccshapeFlags  = parseShapeFlags(ccshapeFlags)
#     flags = int(flags.split()[1])
    #===========================================================================
    
    
    global cancel
    count = 0
    rotoCurve = rotoNode['curves']
    rotoRoot = rotoCurve.rootLayer
    transf = shape[0].getTransform()
    allAttributes = shape[0].getAttributes()
  
    #===========================================================================
    # xml export block 01
    #===========================================================================
    #===========================================================================
    # visibility
    #===========================================================================
    hidden = "True" if allAttributes.getValue(0,'vis') == 0 else "False"
    locked = "True" if "eLockedFlag" in shapeFlags else "False"
    #===========================================================================
    # visibility end
    #===========================================================================
    
    
    fxsShape = ET.SubElement(fxsExport,'Shape',{'type':'Shape', 'label':shape[0].name, 'shape_type':shapetype, 'hidden':hidden,'locked':locked})
    fxsProperties = ET.SubElement(fxsShape,'Properties')
    #===========================================================================
    # end of xml export block 01
    #===========================================================================

    #===========================================================================
    # opacity export
    #===========================================================================
    for n in range(0,len(allAttributes)):
        if allAttributes.getName(n) == "opc":
            opcindex = n
            break
    if allAttributes.getCurve('opc').getNumberOfKeys() > 0:
        fxsOpacity = ET.SubElement(fxsProperties, 'Property', {'id':'opacity'})
        for key in range(0,allAttributes.getCurve('opc').getNumberOfKeys()):
#             print "key",key
            fxsOpcKey =  ET.SubElement(fxsOpacity ,'Key',{'frame':str(allAttributes.getKeyTime(opcindex,key)-nuke.root().firstFrame()), 'interp':'hold'})
            fxsOpcKey.text = str(allAttributes.getValue(allAttributes.getKeyTime(opcindex,key),'opc')*100)
#            newshapeattrib.addKey(allAttributes.getKeyTime(n,key),allAttributes.getName(n),allAttributes.getValue(allAttributes.getKeyTime(n,key),n))
    else:
        fxsOpacity = ET.SubElement(fxsProperties, 'Property', {'constant':'True','id':'opacity'})
        fxsOpacityValue = ET.SubElement(fxsOpacity, 'Value')
        fxsOpacityValue.text = str(allAttributes.getValue(allAttributes.getKeyTime(opcindex,0),'opc')*100)
    #===========================================================================
    # end of opacity        
    #===========================================================================
    #===========================================================================
    # shape motion blur start
    #===========================================================================
    fxsMblur = ET.SubElement(fxsProperties, 'Property', {'constant':'True','id':'motionBlur'})
    fxsMblurValue = ET.SubElement(fxsMblur, 'Value')
    fxsMblurValue.text = "false" if allAttributes.getValue(0,'mbo') == 0 else "true"
    #===========================================================================
    # shape motion blur end
    #===========================================================================
    #===========================================================================
    # shape overlay color
    #===========================================================================
#     print allAttributes.getValue(0,'ro'),allAttributes.getValue(0,'go'),allAttributes.getValue(0,'bo')
    
    fxsOutlineColor = ET.SubElement(fxsProperties, 'Property', {'constant':'True','id':'outlineColor'})
    fxsOutlineColorValue = ET.SubElement(fxsOutlineColor, 'Value')
    fxsOutlineColorValue.text = "(" + str(allAttributes.getValue(0,'ro')) + "," + str(allAttributes.getValue(0,'go'))+ "," + str(allAttributes.getValue(0,'bo'))+ ")"
    #===========================================================================
    # shape overlay color end
    #===========================================================================
    #===========================================================================
    # shape blending mode
    #===========================================================================
    fxsBlendingMode = ET.SubElement(fxsProperties, 'Property', {'constant':'True','id':'mode'})
    fxsBlendingModeValue = ET.SubElement(fxsBlendingMode, 'Value')
    modes = {0:"Add", 12:"Subtract",13:"Difference", 4:"Max", 5:"Inside"}
    if modes.get(allAttributes.getValue(0,'bm')) != None:
        fxsBlendingModeValue.text = modes.get(allAttributes.getValue(0,'bm'))
    else:
        fxsBlendingModeValue.text = "Add"
    #===========================================================================
    # shape blending mode end
    #===========================================================================
    #===========================================================================
    # shape inverted
    #===========================================================================
    fxsInvert = ET.SubElement(fxsProperties, 'Property', {'constant':'True','id':'invert'})
    fxsInvertedValue = ET.SubElement(fxsInvert, 'Value')
    if allAttributes.getValue(0,'inv') == 1:
        fxsInvertedValue.text = "true"
    else:
        fxsInvertedValue.text = "false"
    
    
    #===========================================================================
    # shape inverted end
    #===========================================================================
    
    fxsPath = ET.SubElement(fxsProperties, 'Property', {'id':'path'})
    for point in shape[0]:
        task.setMessage( 'baking ' + shape[0].name + ' point ' + str(count+1) + " of " + str(len(shape[0])) )#
        if cancel:
            return

        newtypes = [point.center,point.leftTangent, point.rightTangent]#, point.featherLeftTangent, point.featherRightTangent]
        #===============================================================
        # bake all the keyframes before starting processing point
        #===============================================================
        for f in fRange:
            task.setProgress(int( float(f)/fRange.last() * 100 ))
            if task.isCancelled():
                cancel = True
                break                
            if cancel:
                break
            transf.addTransformKey(f)
            point_c = [point.center.getPositionAnimCurve(0).evaluate(f),point.center.getPositionAnimCurve(1).evaluate(f)]
            newtypes[0].addPositionKey(f, (point_c[0],point_c[1]))
            
        #===============================================================
        # end of baking process
        #===============================================================
        count+=1
        
    #===========================================================================
    # track test setup
    #===========================================================================
    #===========================================================================
    # trackNode = nuke.createNode('Tracker3', inpanel=False)
    # trackNode["track1"].setAnimated(0)
    # trackNode["track1"].setAnimated(1)
    # trackNode["track2"].setAnimated(0)
    # trackNode["track2"].setAnimated(1)
    #===========================================================================
    #===========================================================================
    pathclosed = False if "eOpenFlag" in ccshapeFlags else True
    for f in fRange:
        fxsPathKey = ET.SubElement(fxsPath,'Key',{'frame':str(f-nuke.root().firstFrame()), 'interp':'linear'})
        fxsPathKeyPath = ET.SubElement(fxsPathKey,'Path',{'closed':str(pathclosed), 'type':shapetype})
#         <Path closed="True" type="Bspline">
#         <Key frame="-1" interp="linear">

        for point in shape[0]:
            if task.isCancelled():
                cancel = True
                break                
            if cancel:
                break
            point_c = [point.center.getPositionAnimCurve(0).evaluate(f),point.center.getPositionAnimCurve(1).evaluate(f)]
            point_lt =[point.center.getPositionAnimCurve(0).evaluate(f)+(point.leftTangent.getPositionAnimCurve(0).evaluate(f)*-1),point.center.getPositionAnimCurve(1).evaluate(f)+(point.leftTangent.getPositionAnimCurve(1).evaluate(f)*-1)]
            point_rt =[point.center.getPositionAnimCurve(0).evaluate(f)+(point.rightTangent.getPositionAnimCurve(0).evaluate(f)*-1),point.center.getPositionAnimCurve(1).evaluate(f)+(point.rightTangent.getPositionAnimCurve(1).evaluate(f)*-1)]
            
            
            transf = shape[0].getTransform()
            center_xy = rptsw_TransformToMatrix(point_c, transf, f)                    
            center_xy = rptsw_TransformLayers(center_xy, shape[1], f, rotoRoot, rptsw_shapeList)
            point_lt = rptsw_TransformToMatrix(point_lt, transf, f)  
            point_lt  = rptsw_TransformLayers(point_lt, shape[1], f, rotoRoot, rptsw_shapeList)
            point_rt = rptsw_TransformToMatrix(point_rt, transf, f)  
            point_rt  = rptsw_TransformLayers(point_rt, shape[1], f, rotoRoot, rptsw_shapeList)

            x = center_xy[0]
            y = center_xy[1]
            ltx = point_lt[0]
            rtx = point_rt[0]
            lty = point_lt[1]
            rty = point_rt[1]
            x = worldToImageTransform(x,rotoNode,"x")
            y = worldToImageTransform(y,rotoNode,"y")  
            ltx = worldToImageTransform(ltx,rotoNode,"x")
            lty = worldToImageTransform(lty,rotoNode,"y")
            rtx = worldToImageTransform(rtx,rotoNode,"x")
            rty = worldToImageTransform(rty,rotoNode,"y")

            fxsPoint = ET.SubElement(fxsPathKeyPath ,'Point')#"",text = "tst")
            if shapetype == "Bspline":
                fxsPoint.text = "(%f,%f)" % (x,y) #%f otherwise silhouette may reject the imported shapes.
            else:
                fxsPoint.text = "(%f,%f),(%f,%f),(%f,%f)" % (x,y,rtx,rty,ltx,lty)


    #===========================================================================
    # remove repeated keyframes optimization
    #===========================================================================
    shapePath = fxsShape.findall(".//Path")
    removelist = []
    for n in range(len(shapePath)):#[::-1]:
        if n > 0 and n < len(shapePath)-1:
            totalp = 0
            for nn in range(len(shapePath[n])):
                #if this keyframe is equal to previous and next one
                if shapePath[n][nn].text == shapePath[n-1][nn].text and shapePath[n][nn].text == shapePath[n+1][nn].text:
                    totalp +=1
            if totalp == len(shapePath[n]):
                removelist.append(n)
    mainpath = fxsShape.findall(".//Property")
    for prop in mainpath:
        if prop.attrib.get('id') == "path":
            keys = prop.findall(".//Key")
            keysn = len(keys)-1
            for k in keys[::-1]:
                if keysn in removelist:
                    prop.remove(k)
                keysn -=1
                
def silhouetteFxsExporter():
    try:
        rotoNode = nuke.selectedNode()
        if rotoNode.Class() not in ('Roto', 'RotoPaint'):
            if nuke.GUI:
                nuke.message( 'Unsupported node type. Selected Node must be Roto or RotoPaint' )
            return
    except:
        if nuke.GUI:
            nuke.message('Select a Roto or RotoPaint Node')
            return
    #===========================================================================
    # panel setup
    #===========================================================================
    p = nukescripts.panels.PythonPanel("Silhouette Shape Exporter")
    k = nuke.String_Knob("framerange","FrameRange")
    k.setFlag(nuke.STARTLINE)    
    k.setTooltip("Set the framerange to bake the shapes, by default its the project start-end. Example: 10-20")
    p.addKnob(k)
    k.setValue("%s-%s" % (nuke.root().firstFrame(), nuke.root().lastFrame()))    
    #===========================================================================
#     k = nuke.Boolean_Knob("rev", "Reverse Bezier Tangents")
#     k.setFlag(nuke.STARTLINE)
#     k.setTooltip("If the imported shapes tangents are wrong, check this box.")
#     p.addKnob(k)
#     
    #===========================================================================
#     may not be needed after all
    # k = nuke.Enumeration_Knob('sourceCurveType', 'Shapes Software Source', ['Nuke', 'Mocha', 'Silhouette'])
    # k.setFlag(nuke.STARTLINE)
    # k.setTooltip("Adjust this to export Bezier handles correctly")
    # p.addKnob(k)
    #===========================================================================
    
    # k = nuke.Boolean_Knob("mt", "MultiThread")
    # k.setFlag(nuke.STARTLINE)
    # k.setTooltip("This will speed up the script but without an accurate progress bar")
    # p.addKnob(k)
    # k.setValue(True)
    #===========================================================================
    result = p.showModalDialog()    
    
    if result == 0:
        return # Canceled
    try:
        fRange = nuke.FrameRange(p.knobs()["framerange"].getText())
    except:
        if nuke.GUI:
            nuke.message( 'Framerange format is not correct, use startframe-endframe i.e.: 0-200' )
        return
    #===========================================================================
    # end of panel
    #===========================================================================
    start_time = time.time()
    rptsw_shapeList = []
    global cancel
    cancel = False
    
    if nuke.NUKE_VERSION_MAJOR > 6:
        nukescripts.node_copypaste()
#         sourceCurveType = p.knobs()["sourceCurveType"].value() 
#         reverse = p.knobs()["rev"].value()
        rptsw_shapeList = []
        rotoNode = nuke.selectedNode()
        rotoCurve = rotoNode['curves']
        rotoRoot = rotoCurve.rootLayer
        rptsw_shapeList = rptsw_walker(rotoRoot, rptsw_shapeList)  
        task = nuke.ProgressTask( 'Silhouette Shape Exporter' )
        nodeFormat = rotoNode['format'].value()
        fxsExport = ET.Element('Silhouette',{'width':str(nodeFormat.width()),'height':str(nodeFormat.height()),'workRangeStart':str(fRange.first()),'workRangeEnd':str(fRange.last()),'sessionStartFrame':str(fRange.first())})
        
        for shape in rptsw_shapeList[::-1]: #reverse list order to get the correct order on Silhouette
            if isinstance(shape[0], nuke.rotopaint.Shape):
                    bakeShapes(shape, fRange, rotoNode, rptsw_shapeList,task, fxsExport)
        rotoCurve.changed()
    else:
        nuke.message( 'Shape Exporter is for Nuke v7 only' )
    
    #===========================================================================
    # EXPORT the fxs file
    #===========================================================================
    path = os.getenv('FXSEXPORTPATH')
    if path == None:
         path = nuke.getFilename('Save the .fxs file', '*.fxs',"fxsExport.fxs")
         if path == None:
             if nuke.GUI:
                 nuke.message('Aborting Script, you need to save the export to a file' ) 
                 return
         else:
             base = os.path.split(path)[0]
             ext = os.path.split(path)[1][-4:]
             #adds extension if not present on the filename
             if ext != ".fxs": 
                 ext = ext + ".fxs"
                 path =  os.path.join(base,ext)
    else:
        print "Saving file to: %s" % path 
    

    indent(fxsExport)
    ET.ElementTree(fxsExport).write(path)
    nuke.delete(rotoNode)
    if cancel:
        nuke.undo()
    print "Time elapsed: %s seconds" % (time.time() - start_time)
    

if __name__ == '__main__':
    silhouetteFxsExporter()

