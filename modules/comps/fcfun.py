# ----------------------------------------------------------------------------
# -- FreeCad Functions
# -- comps library
# -- Python functions for FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD;
import Part;
import math;
import logging;
import DraftVecUtils;

from FreeCAD import Base

# ---------------------- can be taken away after debugging
import os;
import sys;
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging


import kcomp # before was mat_cte

from kcomp import LAYER3D_H


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# vector constants
V0 = FreeCAD.Vector(0,0,0)
VX = FreeCAD.Vector(1,0,0)
VY = FreeCAD.Vector(0,1,0)
VZ = FreeCAD.Vector(0,0,1)
VXN = FreeCAD.Vector(-1,0,0)
VYN = FreeCAD.Vector(0,-1,0)
VZN = FreeCAD.Vector(0,0,-1)

# color constants
WHITE  = (1.0, 1.0, 1.0)
BLACK  = (0.0, 0.0, 0.0)

RED    = (1.0, 0.0, 0.0)
GREEN  = (0.0, 1.0, 0.0)
BLUE   = (0.0, 0.0, 1.0)

YELLOW = (1.0, 1.0, 0.0)
MAGENT = (1.0, 0.0, 1.0)
CIAN   = (0.0, 1.0, 1.0)

ORANGE = (1.0, 0.5, 0.0)

RED_05    = (1.0, 0.5, 0.5)
GREEN_05  = (0.5, 1.0, 0.5)
BLUE_05   = (0.5, 0.5, 1.0)

YELLOW_05 = (1.0, 1.0, 0.5)
MAGENT_05 = (1.0, 0.5, 1.0)
CIAN_05   = (0.5, 1.0, 1.0)

# no rotation vector
V0ROT = FreeCAD.Rotation(VZ,0)


def addBox(x, y, z, name, cx= False, cy=False):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    box =  doc.addObject("Part::Box",name)
    box.Length = x
    box.Width  = y
    box.Height = z
    xpos = 0
    ypos = 0
    # centered 
    if cx == True:
        xpos = -x/2
    if cy == True:
        ypos = -y/2
    box.Placement.Base =FreeCAD.Vector(xpos,ypos,0)
    return box


# adds a box, centered on the specified axis, with its
# Placement and Rotation at zero. So it can be referenced absolutely from
# its given position

def addBox_cen(x, y, z, name, cx= False, cy=False, cz=False):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    if cx == True:
        x0 = -x/2.0
        x1 =  x/2.0
    else:
        x0 =  0
        x1 =  x
    if cy == True:
        y0 = -y/2.0
        y1 =  y/2.0
    else:
        y0 =  0
        y1 =  y
    if cz == True:
        z0 = - z/2.0
    else:
        z0 = 0

    p00 = FreeCAD.Vector (x0,y0,z0)
    p10 = FreeCAD.Vector (x1,y0,z0)
    p11 = FreeCAD.Vector (x1,y1,z0)
    p01 = FreeCAD.Vector (x0,y1,z0)
    sq_list = [p00, p10, p11, p01]
    square =  doc.addObject("Part::Polygon",name + "_sq")
    square.Nodes =sq_list
    square.Close = True
    square.ViewObject.Visibility = False
    box = doc.addObject ("Part::Extrusion", name)
    box.Base = square
    box.Dir = (0,0, z)
    box.Solid = True
    # we need to recompute if we want to do operations on this object
    doc.recompute()
    
    return box


# adds a shape of box, referenced on the specified axis, with its
# Placement and Rotation at zero. So it can be referenced absolutely from
# its given position

def shp_boxcen(x, y, z, cx= False, cy=False, cz=False, pos=V0):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    if cx == True:
        x0 = -x/2.0
        x1 =  x/2.0
    else:
        x0 =  0
        x1 =  x
    if cy == True:
        y0 = -y/2.0
        y1 =  y/2.0
    else:
        y0 =  0
        y1 =  y
    if cz == True:
        z0 = - z/2.0
    else:
        z0 = 0

    p00 = FreeCAD.Vector (x0,y0,z0) + pos
    p10 = FreeCAD.Vector (x1,y0,z0) + pos
    p11 = FreeCAD.Vector (x1,y1,z0) + pos
    p01 = FreeCAD.Vector (x0,y1,z0) + pos
    # the square
    shp_wire_sq = Part.makePolygon([p00, p10, p11, p01, p00])
    # the face
    shp_face_sq = Part.Face(shp_wire_sq)
    shp_box = shp_face_sq.extrude(FreeCAD.Vector(0,0,z))

    doc.recompute()
    
    return shp_box

# same as shp_bxcen but with a filleted dimension
def shp_boxcenfill (x, y, z, fillrad,
                   fx=False, fy=False, fz=True,
                   cx= False, cy=False, cz=False, pos=V0):

    shp_box = shp_boxcen (x=x, y=y, z=z, cx=cx, cy=cy, cz=cz, pos=pos)
    edg_list = []
    for ind, edge in enumerate(shp_box.Edges):
        vertex0 = edge.Vertexes[0]
        vertex1 = edge.Vertexes[1]
        p0 = vertex0.Point
        p1 = vertex1.Point
        vdif = p1 - p0
        if vdif.x != 0 and fx==True:
            edg_list.append(edge)
        elif vdif.y != 0 and fy==True:
            edg_list.append(edge)
        elif vdif.z != 0 and fz==True:
            edg_list.append(edge)
    shp_boxfill = shp_box.makeFillet(fillrad, edg_list)
    return (shp_boxfill)


# Add cylinder r: radius, h: height 
def addCyl (r, h, name):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    cyl =  doc.addObject("Part::Cylinder",name)
    cyl.Radius = r
    cyl.Height = h
    return cyl

# Add cylinder in a position. So it is in a certain position, with its
# Placement and Rotation at zero. So it can be referenced absolutely from
# its given position
#     r: radius,
#     h: height 
#     name 
#     axis: 'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
#     h_disp: displacement on the height. 
#             if 0, the base of the cylinder will be on the plane
#             if -h/2: the plane will be cutting h/2
def addCyl_pos (r, h, name, axis = 'z', h_disp = 0):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    cir =  doc.addObject("Part::Circle", name + "_circ")
    cir.Radius = r

    if axis == 'x':
        rot = FreeCAD.Rotation (VY, 90)
        cir.Placement.Base = (h_disp, 0, 0)
        extdir = (h,0,0) # direction for the extrusion
    elif axis == 'y':
        rot = FreeCAD.Rotation (VX, -90)
        cir.Placement.Base = (0, h_disp, 0)
        extdir = (0,h,0)
    else: # 'z' or any other 
        rot = FreeCAD.Rotation (VZ, 0)
        cir.Placement.Base = (0, 0, h_disp)
        extdir = (0,0,h)

    cir.Placement.Rotation = rot

    # to hide the circle
    if cir.ViewObject != None:
      cir.ViewObject.Visibility=False

    cyl = doc.addObject ("Part::Extrusion", name)
    cyl.Base = cir 
    cyl.Dir  = extdir 
    cyl.Solid  = True 

    return cyl



# same as addCyl_pos, but avoiding the creation of many FreeCAD objects
# Add cylinder
#     r: radius,
#     h: height 
#     name 
#     normal: FreeCAD.Vector pointing to the normal (if its module is not one,
#             the height will be larger than h
#     pos: position of the cylinder

def addCylPos (r, h, name, normal = VZ, pos = V0):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    cir =  Part.makeCircle (r,   # Radius
                            pos,     # Position
                            normal)  # direction

    #print "circle: %", cir_out.Curve

    wire_cir = Part.Wire(cir)
    face_cir = Part.Face(wire_cir)

    dir_extrus = DraftVecUtils.scaleTo(normal, h)
    shp_cyl = face_cir.extrude(dir_extrus)

    cyl = doc.addObject("Part::Feature", name)
    cyl.Shape = shp_cyl

    return cyl


# same as addCylPos, but just creates the shape
# Add cylinder
#     r: radius,
#     h: height 
#     normal: FreeCAD.Vector pointing to the normal (if its module is not one,
#             the height will be larger than h
#     pos: position of the cylinder

def shp_cyl (r, h, normal = VZ, pos = V0):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    cir =  Part.makeCircle (r,   # Radius
                            pos,     # Position
                            normal)  # direction

    #print "circle: %", cir_out.Curve

    wire_cir = Part.Wire(cir)
    face_cir = Part.Face(wire_cir)

    dir_extrus = DraftVecUtils.scaleTo(normal, h)
    shpcyl = face_cir.extrude(dir_extrus)

    return shpcyl



# Add cylinder, with inner hole:
#     r_ext: external radius,
#     r_int: internal radius,
#     h: height 
#     name 
#     axis: 'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
#     h_disp: displacement on the height. 
#             if 0, the base of the cylinder will be on the plane
#             if -h/2: the plane will be cutting h/2

def addCylHole (r_ext, r_int, h, name, axis = 'z', h_disp = 0):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    cyl_ext =  addCyl (r_ext, h, name + "_ext")
    cyl_int =  addCyl (r_int, h + 2, name + "_int")

    if axis == 'x':
        rot = FreeCAD.Rotation (VY, 90)
        cyl_ext.Placement.Base = (h_disp, 0, 0)
        cyl_int.Placement.Base = (h_disp-1, 0, 0)
    elif axis == 'y':
        rot = FreeCAD.Rotation (VX, -90)
        cyl_ext.Placement.Base = (0, h_disp, 0)
        cyl_int.Placement.Base = (0, h_disp-1, 0)
    else: # 'z' or any other 
        rot = FreeCAD.Rotation (VZ, 0)
        cyl_ext.Placement.Base = (0, 0, h_disp)
        cyl_int.Placement.Base = (0, 0, h_disp-1)

    cyl_ext.Placement.Rotation = rot
    cyl_int.Placement.Rotation = rot

    cylHole = doc.addObject("Part::Cut", name)
    cylHole.Base = cyl_ext
    cylHole.Tool = cyl_int

    return cylHole


# same as addCylHole, but avoiding the creation of many FreeCAD objects
# Add cylinder, with inner hole:
#     r_out: outside radius,
#     r_in : inside radius,
#     h: height 
#     name 
#     normal: FreeCAD.Vector pointing to the normal (if its module is not one,
#             the height will be larger than h
#     pos: position of the cylinder

def addCylHolePos (r_out, r_in, h, name, normal = VZ, pos = V0):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument

    cir_out =  Part.makeCircle (r_out,   # Radius
                                pos,     # Position
                                normal)  # direction
    cir_in =  Part.makeCircle (r_in,   # Radius
                                pos,     # Position
                                normal)  # direction

    #print "in: %", cir_in.Curve
    #print "out: %", cir_out.Curve

    wire_cir_out = Part.Wire(cir_out)
    wire_cir_in  = Part.Wire(cir_in)
    face_cir_out = Part.Face(wire_cir_out)
    face_cir_in  = Part.Face(wire_cir_in)

    face_cir_hole = face_cir_out.cut(face_cir_in)
    dir_extrus = DraftVecUtils.scaleTo(normal, h)
    shp_cyl_hole = face_cir_hole.extrude(dir_extrus)

    cyl_hole = doc.addObject("Part::Feature", name)
    cyl_hole.Shape = shp_cyl_hole

    return cyl_hole

# ------------------- def shpRndRectWire
# Creates a wire (shape), that is a rectangle with rounded edges.
# if r== 0, it will be a rectangle
# x: dimension of the base, on the X axis
# y: dimension of the height, on the Y axis
# r: radius of the rouned edge. 
# The wire will be centered
#
#                   Y
#                   |_ X
#               
#       ______     ___ y
#      /      \ r
#      |      |
#      |      |              z=0
#      |      |
#      \______/    ___
#      
#      |_______| x


def shpRndRectWire (x=1, y=1, r= 0.5, zpos = 0):

    #doc = FreeCAD.ActiveDocument

    if 2*r >= x or 2*r >= y:
        print "Radius too large: addRoundRectan"
        if x > y:
            r = y/2.0 - 0.1 # otherwise there will be a problem
        else:
            r = x/2.0 - 0.1 
    
    # points as if they were on X - Y
    #        lyy
    #    r_y      rx_y
    #       ______     
    # 0_ry /      \ x_ry
    #      |      |
    # lx0  |      |        lxx
    # 0_r  |      | x_r
    #      \______/  
    #      r_0  rx_0
    #         ly0


    x_0  =   - x/2.0
    x_r  = r - x/2.0
    x_rx = x/2.0 - r
    x_x  = x/2.0 
    y_0  =   - y/2.0
    y_r  = r - y/2.0
    y_ry = y/2.0 - r
    y_y  = y/2.0 

    # Lines:
    p_r_0  = FreeCAD.Vector(x_r,  y_0, zpos)
    p_rx_0 = FreeCAD.Vector(x_rx, y_0, zpos)
    # toShape, because otherwise we couldn't make the wire.
    # by doing this we are creating an edge
    # an alternative would be to use makeLine
    ly0 = Part.Line(p_r_0, p_rx_0).toShape() # Horizontal lower line

    p_x_r  = FreeCAD.Vector(x_x   ,y_r, zpos)
    p_x_ry = FreeCAD.Vector(x_x   ,y_ry, zpos)
    lxx = Part.Line(p_x_r, p_x_ry).toShape() # vertical on the right

    p_r_y  = FreeCAD.Vector(x_r,  y_y, zpos)
    p_rx_y = FreeCAD.Vector(x_rx, y_y, zpos)
    lyy = Part.Line(p_r_y, p_rx_y).toShape() # Horizontal top line

    p_0_r  = FreeCAD.Vector(x_0, y_r,  zpos)
    p_0_ry = FreeCAD.Vector(x_0, y_ry, zpos)
    lx0 = Part.Line(p_0_r, p_0_ry).toShape()  # vertical on the left
    # if I wanted to see these shapes
    #fc_ly0 = doc.addObject("Part::Feature", "ly0")
    #fc_ly0.Shape = ly0
    #fc_lxx = doc.addObject("Part::Feature", "lxx")
    #fc_lxx.Shape = lxx
    #fc_lyy = doc.addObject("Part::Feature", "lyy")
    #fc_lyy.Shape = lyy
    #fc_lx0 = doc.addObject("Part::Feature", "lx0")
    #fc_lx0.Shape = lx0

    if r > 0:
        # center points of the 4 archs:
        pcarch_00 = FreeCAD.Vector (x_r,  y_r,zpos)
        pcarch_x0 = FreeCAD.Vector (x_rx, y_r,zpos)
        pcarch_0y = FreeCAD.Vector (x_r,  y_ry,zpos)
        pcarch_xy = FreeCAD.Vector (x_rx, y_ry,zpos)
        dircir = FreeCAD.Vector (0,0,1)

        # ALTERNATIVE 1: Making the OpenCascade shape,
        # and adding it to a Freecad Object
        arch_00 = Part.makeCircle (r, pcarch_00, dircir, 180, 270) 
        arch_x0 = Part.makeCircle (r, pcarch_x0, dircir, 270, 0) 
        arch_0y = Part.makeCircle (r, pcarch_0y, dircir, 90, 180) 
        arch_xy = Part.makeCircle (r, pcarch_xy, dircir, 0, 90) 
        # freecad object
        #fc_arch_00 = doc.addObject("Part::Feature", "arch_00")
        #fc_arch_00.Shape = arch_00
        #fc_arch_x0 = doc.addObject("Part::Feature", "arch_x0")
        #fc_arch_x0.Shape = arch_x0
        #fc_arch_0y = doc.addObject("Part::Feature", "arch_0y")
        #fc_arch_0y.Shape = arch_0y
        #fc_arch_xy = doc.addObject("Part::Feature", "arch_xy")
        #fc_arch_xy.Shape = arch_xy
 
        # ALTERNATIVE 2: using the Part::Circle
        # you have to place it with Placement
        #cir_00 = doc.addObject("Part::Circle","cir_00")
        #cir_00.Angle0 = 180
        #cir_00.Angle1 = 270
        #cir_00.Radius = r
        #cir_00.Placement.Base = pcarch_00

        # Make a wire
        # it seems that it matters the order
        # for this example, it doesnt work if I do Part.Shape as in the 
        # example:
        # http://freecadweb.org/wiki/index.php?title=Topological_data_scripting
        wire_rndrect = Part.Wire ([
                                     lx0,
                                     arch_00,
                                     ly0,
                                     arch_x0,
                                     lxx,
                                     arch_xy,
                                     lyy,
                                     arch_0y
                                    ])
    else: # just a rectangle
        wire_rndrect = Part.Wire ([
                                     lx0,
                                     ly0,
                                     lxx,
                                     lyy,
                                    ])


    return wire_rndrect



#doc = FreeCAD.newDocument()

#wire1 = shpRndRectWire (x=10, y=12,  r=0)

#wire2 = shpaddRndRectWire (x=10-2, y=12-2, r= 0 )


#rndrect_1 = doc.addObject("Part::Feature", "rndrect_1")
#rndrect_1.Shape = wire1
#rndrect_2 = doc.addObject("Part::Feature", "rndrect_2")
#rndrect_2.Shape = wire2
#face1 = Part.Face(wire1)
#face2 = Part.Face(wire2)
#cut = face1.cut(face2)
#extr = cut.extrude(Base.Vector(0,0,5))
#Part.show(extr)

    #extr_rndrect = doc.addObject("Part::Extrusion", name)
    #extr_rndrect.Base = rndrect
    #extr_rndrect.Dir = (0,0,2)
    #extr_rndrect.Solid = True
    #shp_rndrect = Part.Shape 
    #fc_rndrect = doc.addObject("Part::Feature", "fc_rndrect")
    #fc_rndrect.Shape = shp_rndrect

#doc.recompute()
    

# ------------------- def wire_sim_xy
# Creates a wire (shape), from a list of points on the positive quadrant of XY
# the wire is simmetrical to both X and Y
# vecList: list of FreeCAD Vectors, the have to be in order clockwise
# if the first or the last points are not on the axis, a new point will be
# created
#
#                   Y
#                   |_ X
#               
#       __|__  
#      /  |  \ We receive these points
#      |  |  |
#      |  |--------          z=0
#      |     |
#      \_____/  
#      

def wire_sim_xy (vecList):

    edgList = []
    if vecList[0].x != 0:
        # the first element is not on the Y axis,so we create a first point
        vec = FreeCAD.Vector (0, vecList[0].y, vecList[0].z)
        seg = Part.Line(vec, vecList[0]) # segment
        edg = seg.toShape() # edge
        edgList.append(edg) # append to the edge list
    listlen = len(vecList)
    for index, vec in enumerate(vecList):
        if vec.x < 0 or vec.y < 0:
            logger.error('WireSimXY with negative points')
        if index < listlen-1: # it is not the last element
            seg = Part.Line(vec, vecList[index+1])
            edg = seg.toShape()
            edgList.append(edg)
        index += 1
    if vecList[-1].y != 0: # the last element is not on the X axis
        vec = FreeCAD.Vector (vecList[-1].x, 0, vecList[-1].z)
        seg = Part.Line(vecList[-1], vec)
        edg = seg.toShape()
        edgList.append(edg)
    # the wire for the first cuadrant, quarter
    quwire = Part.Wire(edgList)
    # mirror on Y axis
    MirY = FreeCAD.Matrix()
    MirY.scale(FreeCAD.Vector(-1,1,1))
    mir_quwire = quwire.transformGeometry(MirY)
    # another option
    # mir_quwire   = quwire.mirror(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))

    #halfwire = Part.Wire([quwire, mir_quwire]) # get the half wire
    halfwire = Part.Wire([mir_quwire, quwire]) # get the half wire
    # otherwise it doesnt work because the edges are not aligned
    halfwire.fixWire() 
    # mirror on X axis
    MirX = FreeCAD.Matrix()
    MirX.scale(FreeCAD.Vector(1,-1,1))
    mir_halfwire = halfwire.transformGeometry(MirX)
    totwire = Part.Wire([mir_halfwire, halfwire]) # get the total wire
    totwire.fixWire() 

    return totwire

# ------------------- end def wire_sim_xy

            

            


"""  -------------------- addBolt  ---------------------------------
   the hole for the bolt shank and the head or the nut
   Tolerances have to be included
   r_shank: Radius of the shank (tolerance included)
   l_bolt: total length of the bolt: head & shank
   r_head: radius of the head (tolerance included)
   l_head: length of the head
   hex_head: inidicates if the head is hexagonal or rounded
              1: hexagonal
              0: rounded
   h_layer3d: height of the layer for printing, if 0, means that the support
              is not needed
   extra: 1 if you want 1 mm on top and botton to avoid cutting on the same
               plane pieces after making cuts (boolean difference) 
   support: 1 if you want to include a triangle between the shank and the head
              to support the shank and not building the head on the air
              using kcomp.LAYER3D_H
   headdown: 1 if the head is down. 0 if it is up
"""

def addBolt (r_shank, l_bolt, r_head, l_head,
             hex_head = 0, extra=1, support=1, headdown = 1, name="bolt"):

    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    elements = []
    # shank
    shank =  doc.addObject("Part::Cylinder", name + "_shank")
    shank.Radius = r_shank
    shank.Height = l_bolt + 2*extra
    pos = FreeCAD.Vector(0,0,-extra)
    shank.Placement = FreeCAD.Placement(pos, V0ROT, V0)
    elements.append (shank)
    # head:
    if hex_head == 0:
        head =  doc.addObject("Part::Cylinder", name + "_head")
        head.Radius = r_head
    else:
        head =  doc.addObject("Part::Prism", name + "_head")
        head.Polygon = 6
        head.Circumradius = r_head

    head.Height = l_head + extra
    if headdown == 1:
        zposhead = -extra
    else:
        zposhead = l_bolt - l_head
    poshead =  FreeCAD.Vector(0,0,zposhead)
    head.Placement.Base = poshead
    elements.append (head)
    # support for the shank:
    if support==1 and kcomp.LAYER3D_H > 0:
        sup1 = doc.addObject("Part::Prism", name + "_sup1")
        sup1.Polygon = 3
        sup1.Circumradius = r_shank * 2
        # we could put it just on top of the head, but since we are going to 
        # make an union, we put it from the bottom (no need to include extra)
        # sup1.Height = kcomp.LAYER3D_H
        # pos1 = FreeCAD.Vector(0,0,l_head)
        # rot30z = FreeCAD.Rotation(VZ,30)
        # sup1.Placement = FreeCAD.Placement(pos1, rot30z, V0)
        sup1.Height = l_head + kcomp.LAYER3D_H
        # rotation make only make sense for hexagonal head, but it doesn't
        # matter for rounded head
        rot30z = FreeCAD.Rotation(VZ,30)
        if headdown == 1:
            zposheadsup1 = 0
        else:
            zposheadsup1 = l_bolt - l_head - kcomp.LAYER3D_H
        sup1.Placement.Base = FreeCAD.Vector(0,0,zposheadsup1)
        sup1.Placement.Rotation = rot30z
        # take vertex away:
        if hex_head == 0:
            sup1away = doc.addObject("Part::Cylinder", name + "_sup1away")
            sup1away.Radius = r_head
        else:
            sup1away = doc.addObject("Part::Prism", name + "_sup1away")
            sup1away.Polygon = 6
            sup1away.Circumradius = r_head
        # again, we take all the height
        sup1away.Height =  l_head + kcomp.LAYER3D_H
        sup1away.Placement.Base = sup1.Placement.Base
        sup1cut = doc.addObject("Part::Common", "sup1cut")
        sup1cut.Base = sup1
        sup1cut.Tool = sup1away
        elements.append (sup1cut)
        # another support
        # 1.15 is the relationship between the Radius and the Apothem
        # of the hexagon: sqrt(3)/2 . I make it slightly smaller
        sup2 = doc.addObject("Part::Prism", name + "_sup2")
        sup2.Polygon = 6
        sup2.Circumradius = r_shank * 1.15
        sup2.Height = l_head + 2* kcomp.LAYER3D_H
        if headdown == 1:
            zposheadsup2 = 0
        else:
            zposheadsup2 = l_bolt - l_head - 2* kcomp.LAYER3D_H
        sup2.Placement.Base = FreeCAD.Vector(0,0,zposheadsup2)
        elements.append (sup2)
  
    # union of elements
    bolt =  doc.addObject("Part::MultiFuse", name)
    bolt.Shapes = elements
    return bolt
"""
    bolt =  doc.addObject("Part::Fuse", name)
    bolt.Base = shank
    bolt.Tool = head
"""

"""  -------------------- addBoltNut_hole  ------------------------------
   the hole for the bolt shank, the head and the nut. The bolt head will be
   at the botton, and the nut will be on top
   Tolerances have to be already included in the argments values
   r_shank: Radius of the shank (tolerance included)
   l_bolt: total length of the bolt: head & shank
   r_head: radius of the head (tolerance included)
   l_head: length of the head
   r_nut : radius of the nut (tolerance included)
   l_nut : length of the nut. It doesn't have to be the length of the nut
           but how long you want the nut to be inserted
   hex_head: inidicates if the head is hexagonal or rounded
              1: hexagonal
              0: rounded
   zpos_nut: inidicates the height position of the nut, the lower part     
   h_layer3d: height of the layer for printing, if 0, means that the support
              is not needed
   extra: 1 if you want 1 mm on top and botton to avoid cutting on the same
               plane pieces after makeing differences 
   support: 1 if you want to include a triangle between the shank and the head
              to support the shank and not building the head on the air
              using kcomp.LAYER3D_H
"""


def addBoltNut_hole (r_shank,        l_bolt, 
                     r_head,         l_head,
                     r_nut,          l_nut,
                     hex_head = 0,   extra=1,
                     supp_head=1,    supp_nut=1,
                     headdown=1,     name="bolt"):


    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    elements = []
    bolt = addBolt  (r_shank  = r_shank,
                     l_bolt   = l_bolt,
                     r_head   = r_head,
                     l_head   = l_head,
                     hex_head = hex_head,
                     extra    = extra,
                     support  = supp_head,
                     headdown = headdown,
                     name     = name + "_bolt")

    nut = doc.addObject("Part::Prism", name + "_nut")
    nut.Polygon = 6
    nut.Circumradius = r_nut
    nut.Height = l_nut + extra
    if headdown == 1:
        pos = FreeCAD.Vector (0, 0, l_bolt - l_nut)
    else:
        pos = FreeCAD.Vector (0, 0, -extra)
    nut.Placement = FreeCAD.Placement(pos, V0ROT, V0)
    elements.append (bolt)
    elements.append (nut)
    # support for the nut
    if supp_nut == 1 and kcomp.LAYER3D_H > 0:
        supnut1 = doc.addObject("Part::Prism", name + "_nutsup1")
        supnut1.Polygon = 3
        supnut1.Circumradius = r_shank * 2
        supnut1.Height = l_nut + kcomp.LAYER3D_H
        if headdown == 1:
            pos_supnut1 = FreeCAD.Vector (0, 0,
                                          l_bolt - l_nut - kcomp.LAYER3D_H)
        else:
            pos_supnut1 = V0
        rot30z = FreeCAD.Rotation(VZ,30)
        supnut1.Placement = FreeCAD.Placement(pos_supnut1, rot30z, V0)
        # take vertex away:
        supnut1away = doc.addObject("Part::Prism", name + "_supnut1away")
        supnut1away.Polygon = 6
        supnut1away.Circumradius = r_nut
        supnut1away.Height =  supnut1.Height
        supnut1away.Placement = FreeCAD.Placement(pos_supnut1, V0ROT, V0)
        supnut1cut = doc.addObject("Part::Common", "supnut1_cut")
        supnut1cut.Base = supnut1
        supnut1cut.Tool = supnut1away
        elements.append (supnut1cut)
        # the other support
        # 1.15 is the relationship between the Radius and the Apothem
        # of the hexagon: sqrt(3)/2 . I make it slightly smaller
        supnut2 = doc.addObject("Part::Prism", name + "_supnut2")
        supnut2.Polygon = 6
        supnut2.Circumradius = r_shank * 1.15
        supnut2.Height = l_nut + 2* kcomp.LAYER3D_H
        if headdown == 1:
            pos_supnut2 = FreeCAD.Vector(0,0,
                                         l_bolt - l_nut - 2*kcomp.LAYER3D_H)
        else:
            pos_supnut2 = V0
        supnut2.Placement = FreeCAD.Placement(pos_supnut2, V0ROT, V0)
        elements.append (supnut2)

    boltnut = doc.addObject("Part::MultiFuse", "boltnut")
    boltnut.Shapes = elements
    return boltnut
      
  
# -------------------- NutHole -----------------------------
# adding a Nut hole (hexagonal) with a prism attached to introduce the nut
# tolerances are included
# nut_r : circumradius of the hexagon
# nut_h : height of the nut, usually larger than the actual nut height, to be
#         able to introduce it
# hole_h: the hole height, from the center of the hexagon to the side it will
#         see light
# name:   name of the object (string)
# extra:  1 if you want 1 mm out of the hole, to cut
# nuthole_x: 1 if you want that the nut height to be along the X axis
#           and the 2*apotheme on the Y axis
#           ie. Nut hole facing X
#         0 if you want that the nut height to be along the Y axis
#           ie. Nut hole facing Y
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# holedown:   0: the z0 is the bottom of the square (hole)
#             1: the z0 is the center of the hexagon (nut)
#              it can be done because it is a new shape formed from the union
#
#    0               1       
#       /\              __
#      |  |            |  |
#      |  |            |  |
#      |__|__ z = 0    |  | -- z = 0
#                       \/

class NutHole (object):

    def __init__(self, nut_r, nut_h, hole_h, name,
                 extra = 1, nuthole_x = 1, cx=0, cy=0, holedown = 0):
        self.nut_r   = nut_r
        self.nut_h   = nut_h
        self.nut_2ap = 2 * nut_r * 0.866    #Apotheme = R * cos (30)
        self.hole_h  = hole_h
        self.name    = name
        self.extra   = extra
        self.nuthole_x = nuthole_x
        self.cx      = cx
        self.cy      = cy
        self.holedown = holedown
  
        doc = FreeCAD.ActiveDocument
        self.doc     = doc

        # the nut
        nut = doc.addObject("Part::Prism", name + "_nut")
        nut.Polygon = 6
        nut.Circumradius = nut_r
        nut.Height = nut_h
        self.nutObj  = nut

        if nuthole_x == 1:
            x_hole = nut_h
            y_hole = self.nut_2ap
            nutrot = FreeCAD.Rotation(VY,90)
            if cx == 1: #centered on X,
                xpos_nut = - nut_h / 2.0
            else:
                xpos_nut = 0
            if cy == 1: #centered on Y, already is
                ypos_nut = 0
            else:
              # already starting on y=0
              ypos_nut = self.nut_2ap/2.0
        else : # nut h is on Y
            x_hole = self.nut_2ap
            y_hole = nut_h
            # the rotation of the nut will be on X
            # this is a rotation of Yaw and Pitch, because we want to have the
            # vertex on top, not the face of the hexagonal prism
            nutrot = FreeCAD.Rotation(90,90,0)
            if cx == 1: #centered on X, already is
                xpos_nut = 0
            else:
                # move to the half of the apotheme
                xpos_nut = self.nut_2ap/2.0
            if cy == 1: #centered on Y, 
                ypos_nut = - nut_h / 2.0
            else:
                # already starting on y=0
                ypos_nut = 0

        hole = addBox (x_hole, y_hole, hole_h + extra, name + "_hole",
                     cx = cx, cy = cy)
        self.holeObj = hole

        if holedown== 1:
            # the nut will be top
            zpos_nut = hole_h
            if extra > 0: # then we will have to bring down the z of the hole
              hole.Placement.Base =   hole.Placement.Base \
                                    + FreeCAD.Vector(0,0,-extra)
        else:
            zpos_nut = 0

        nut.Placement.Base = FreeCAD.Vector (xpos_nut, ypos_nut, zpos_nut)
        nut.Placement.Rotation = nutrot

        nuthole =  doc.addObject("Part::Fuse", name)
        nuthole.Base = nut
        nuthole.Tool = hole
        self.fco = nuthole   # the FreeCad Object




#  ---------------- Fillet on edges of a certain length
#   box:   is the original shape we want to fillet
#   e_len: the length of the edges that we want to fillet
#   radius: the radius of the fillet
#   name: the name of the shape we want to create

def fillet_len (box, e_len, radius, name):
    # we have to bring the active document
    doc = FreeCAD.ActiveDocument
    fllts_v = []
    edge_ind = 1
    #logger.debug('fillet_len: box %s - %s' %
    #                     ( str(box), str(box.Shape)))
    for edge_i in box.Shape.Edges:
        #logging.debug('fillet_len: edge Length: %s' % str(edge_i.Length))
        if edge_i.Length == e_len: # same length
        # the index is appeneded (edge_ind),not the edge itself (edge_i)
        # radius is twice, because it can be variable
            #logging.debug('fillet_len: append edge. Length: %s ' ,
            #               str(edge_i.Length))
            fllts_v.append((edge_ind, radius, radius))
        edge_ind += 1
    box_fllt = doc.addObject ("Part::Fillet", name)
    box_fllt.Base = box
    box_fllt.Edges = fllts_v
    # to hide the objects in freecad gui
    if box.ViewObject != None:
      box.ViewObject.Visibility=False
    return box_fllt

#  ---------------- calc_rot -----------------------------
#  ---------------- Yaw, Pitch and Roll transfor
#  Having an object with an orientation defined by 2 vectors
#  First vector direction (x,y,z) is (1,0,0) 
#  Second vector direction (x,y,z) is (0,0,-1) 
#  we want to rotate the object in an ortoghonal direction. The vectors
#  will be in -90, 180, or 90 degrees.
#  this function returns the Rotation given by yaw, pitch and roll

def calc_rot (vec1, vec2):
           
    # rotation calculation
    if vec1 == (1,0,0):
       yaw = 0
       pitch = 0
       if vec2 == (0,1,0):
           roll  = 90
       elif vec2 == (0,-1,0):
           roll  = -90
       elif vec2 == (0,0,1):
           roll  = 180
       elif vec2 == (0,0,-1):
           roll  = 0
       else:
           print "error 1 in yaw-pitch-roll"
    elif vec1 == (-1,0,0):
       yaw = 180
       pitch = 0
       if vec2 == (0,1,0):
           roll  = -90 #negative because of the yaw
       elif vec2 == (0,-1,0):
           roll  = 90 # positive because of the yaw = 180
       elif vec2 == (0,0,1):
           roll = 180
       elif vec2 == (0,0,-1):
           roll  = 0
       else:
           print "error 2 in yaw-pitch-roll"
    elif vec1 == (0,1,0):
       yaw = 90
       pitch = 0
       if vec2 == (1,0,0):
           roll  = -90
       elif vec2 == (-1,0,0):
           roll  = 90
       elif vec2 == (0,0,1):
           roll  = 180
       elif vec2 == (0,0,-1):
           roll  = 0
       else:
           print "error 3 in yaw-pitch-roll"
    elif vec1 == (0,-1,0):
       yaw = -90
       pitch = 0
       if vec2 == (1,0,0):
           roll  = 90 
       elif vec2 == (-1,0,0):
           roll  = -90 
       elif vec2 == (0,0,1):
           roll  = 180
       elif vec2 == (0,0,-1):
           roll  = 0
       else:
           print "error 4 in yaw-pitch-roll"
    elif vec1 == (0,0,1):
       pitch = -90
       yaw = 0
       if vec2 == (1,0,0):
           roll  = 0 
       elif vec2 == (-1,0,0):
           roll  = 180 
       elif vec2 == (0,1,0):
           roll  = 90
       elif vec2 == (0,-1,0):
           roll  = -90
       else:
           print "error 5 in yaw-pitch-roll"
    elif vec1 == (0,0,-1):
       pitch = 90
       yaw = 0
       if vec2 == (1,0,0):
           roll  = 180 
       elif vec2 == (-1,0,0):
           roll  = 0 
       elif vec2 == (0,1,0):
           roll  = 90
       elif vec2 == (0,-1,0):
           roll  = -90
       else:
           print "error 6 in yaw-pitch-roll"

    vrot = FreeCAD.Rotation(yaw,pitch,roll)
    return vrot

#  ---------------- calc_desp_ncen ------------------------
#  similar to calc_rot, but calculates de displacement, when we don't want
#  to have any of the dimensions centered

def calc_desp_ncen (Length, Width, Height, 
                     vec1, vec2, cx=False, cy=False, cz=False, H_extr = False):
           
    # rotation calculation
    x = 0
    y = 0
    z = 0
    if abs(vec1[0]) == 1: # X axis: vec1 == (1,0,0) or vec1 == (-1,0,0):
        if abs(vec2[1]) == 1:   # Y
            if cx == False:
                x = Length / 2.0
            if cy == False:
                y = Height / 2.0
            if cz == False:
                z = Width / 2.0
        elif abs(vec2[2]) == 1:    # Z
            if cx == False:
                x = Length / 2.0
            if cy == False:
                y = Width / 2.0
            if cz == False:
                z = Height / 2.0
        else:
            print "error 1 in calc_desp_ncen"
    elif abs(vec1[1]) == 1: # Y axis
        if abs(vec2[0]) == 1:   # X
            if cx == False:
                x = Height / 2.0
            if cy == False:
                y = Length / 2.0
            if cz == False:
                z = Width / 2.0
        elif abs(vec2[2]) == 1:    # Z
            if cx == False:
                x = Width / 2.0
            if cy == False:
                y = Length / 2.0
            if cz == False:
                z = Height / 2.0
        else:
            print "error 2 in calc_desp_ncen"
    elif abs(vec1[2]) == 1: # Z axis
        if abs(vec2[0]) == 1:   # X
            if cx == False:
                x = Height / 2.0
            if cy == False:
                y = Width / 2.0
            if cz == False:
                z = Length / 2.0
        elif abs(vec2[1]) == 1:    # Y
            if cx == False:
                x = Width / 2.0
            if cy == False:
                y = Height / 2.0
            if cz == False:
                z = Length / 2.0
        else:
            print "error 3 in calc_desp_ncen"
    else:
        print "error 3 in calc_desp_ncen"


    vdesp = FreeCAD.Vector(x,y,z)
    return vdesp


def getvecofname(axis):

    if axis == 'x':
        vec = (1,0,0)
    elif axis == '-x':
        vec = (-1,0,0)
    elif axis == 'y':
        vec = (0,1,0)
    elif axis == '-y':
        vec = (0,-1,0)
    elif axis == 'z':
        vec = (0,0,1)
    elif axis == '-z':
        vec = (0,0,-1)

    return vec


