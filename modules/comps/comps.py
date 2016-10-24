# ----------------------------------------------------------------------------
# -- Components
# -- comps library
# -- Python classes that creates useful parts for FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


import FreeCAD;
import Part;
import logging
import os
import Draft;
#import copy;
#import Mesh;

# ---------------------- can be taken away after debugging
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging

import kcomp # before, it was called mat_cte
import fcfun

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, addCyl_pos, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole


logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')
#
#        _______       _______________________________  TotH = H
#       |  ___  |                     
#       | /   \ |      __________ HoleH = h
#       | \___/ |  __
#     __|       |__ /| __
#    |_____________|/  __ TotD = L ___________________
#
#     <- TotW  = W->
#
# hole_x: 1 the depth along X axis 
#           Hole facing X
#         0 the depth along Y axis 
#           Hole facing Y
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# upsdown:  NOT YET
#            0: Normal vertical position, referenced to 0
#            1:  z0 is the center of the hexagon (nut)
#              it can be done because it is a new shape formed from the union


class Sk (object):

    """
     SK dimensions:
     dictionary for the dimensions
     mbolt: is mounting bolt. it corresponds to its metric
     tbolt: is the tightening bolt.
    SK12 = { 'd':12.0, 'H':37.5, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
             'h':23.0, 'A':21.0, 'b': 5.0, 'g':6.0,  'I':20.0,
              'mbolt': 5, 'tbolt': 4} 
    """
    SK12 = kcomp.SK12

    # separation of the upper side (it is not defined). Change it
    # measured for sk12 is 1.2
    up_sep_dist = 1.2

    # tolerances for holes 
    holtol = 1.1

    def __init__(self, size, name, hole_x = 1, cx=0, cy=0):
        self.size = size
        self.name = name
        self.cx = cx
        self.cy = cy

        if size != 12:
            logging.warning("only size 12 supported")
            print ("only size 12 supported")
            
        else:
            doc = FreeCAD.ActiveDocument
            # Total height:
            sk_z = kcomp.SK12['H'];
            self.TotH = sk_z
            # Total width (Y):
            sk_y = kcomp.SK12['W'];
            self.TotW = sk_y
            # Total depth (x):
            sk_x = kcomp.SK12['L'];
            self.TotD = sk_x
            # Base height
            sk_base_z = 6;
            # center width
            sk_center_y = 20;
            # Axis height:
            sk_axis_z = 23;
            self.HoleH = sk_axis_z;
    
            # tightening bolt with added tolerances:
            # Bolt's head radius
            tbolt_head_r = (self.holtol
                            * kcomp.D912_HEAD_D[kcomp.SK12['tbolt']])/2.0
            # Bolt's head lenght
            tbolt_head_l = (self.holtol
                            * kcomp.D912_HEAD_L[kcomp.SK12['tbolt']] )
            # Mounting bolt radius with added tolerance
            mbolt_r = self.holtol * kcomp.SK12['mbolt']/2
    
            # the total dimensions: LxWxH
            # we will cut it
            total_box = addBox(x = sk_x,
                               y = sk_y,
                               z = sk_z,
                               name = "total_box",
                               cx = False, cy=True)

            # what we have to cut from the sides
            side_box_y = (sk_y - kcomp.SK12['I'])/2
            side_box_z = sk_z - kcomp.SK12['g']
    
            side_cut_box_r = addBox (sk_x, side_box_y, side_box_z,
                                     "side_box_r")
            side_cut_pos_r = FreeCAD.Vector(0,
                                            kcomp.SK12['I']/2,
                                            kcomp.SK12['g'])
            side_cut_box_r.Placement.Base = side_cut_pos_r

            side_cut_box_l= addBox (sk_x, side_box_y, side_box_z,
                                     "side_box_l")
            side_cut_pos_l = FreeCAD.Vector(0,-sk_y/2,kcomp.SK12['g'])
            side_cut_box_l.Placement.Base = side_cut_pos_l

            # union 
            side_boxes = doc.addObject("Part::Fuse", "side_boxes")
            side_boxes.Base = side_cut_box_r
            side_boxes.Tool = side_cut_box_l

            # difference 
            sk_shape = doc.addObject("Part::Cut", "sk_shape")
            sk_shape.Base = total_box
            sk_shape.Tool = side_boxes

            # Shaft hole, its height has +2 to make it throughl L all de way
            shaft_hole = addCyl(kcomp.SK12['d']/2,
                                sk_x+2,
                                "shaft_hole")

            """
            First argument defines de position: -1, 0, h
            Second argument rotation: 90 degrees rotation in Y.
            Third argument the center of the rotation, in this case,
                  it is in the cylinder
            axis at the base of the cylinder 
            """
            shaft_hole.Placement = FreeCAD.Placement(
                                         FreeCAD.Vector(-1,0,kcomp.SK12['h']),
                                         FreeCAD.Rotation(VY,90),
                                         V0)

            # the upper sepparation
            up_sep = addBox( sk_x +2,
                             self.up_sep_dist,
                             sk_z-kcomp.SK12['h'] +1,
                             "up_sep")
            up_sep_pos = FreeCAD.Vector(-1,
                                        -self.up_sep_dist/2,
                                         kcomp.SK12['h']+1)
            up_sep.Placement.Base = up_sep_pos

            """
             Tightening bolt shaft hole, its height has +2 to make it
             throughl L all de way
             kcomp.SK12['tbolt'] is the diameter of the bolt: (M..) M4, ...
             tbolt_head_r: is the radius of the tightening bolt's head
             (including tolerance), which its bottom either
             - is at the middle point between
               - A: the total height :sk_z
               - B: the top of the shaft hole: kcomp.SK12['h']+kcomp.SK12['d']/2
               - so the result will be (A + B)/2
             or it is aligned with the top of the 12mm shaft, whose height is: 
                 kcomp.SK12['h']+kcomp.SK12['d']/2
            """
            tbolt_shaft = addCyl(kcomp.SK12['tbolt']/2,kcomp.SK12['I']+2,
                                      "tbolt_shaft")
            tbolt_shaft_pos = FreeCAD.Vector(sk_x/2,
                    kcomp.SK12['I']/2+1,
                    kcomp.SK12['h']+kcomp.SK12['d']/2+tbolt_head_r/self.holtol)
                    #(sk_z + kcomp.SK12['h']+kcomp.SK12['d']/2)/2)
            tbolt_shaft.Placement = FreeCAD.Placement(tbolt_shaft_pos,
                                                 FreeCAD.Rotation(VX,90),
                                                 V0)

            # Head of the thigthening bolt
            tbolt_head = addCyl(tbolt_head_r,tbolt_head_l+1, "tbolt_head")
            tbolt_head_pos = FreeCAD.Vector(sk_x/2,
                   kcomp.SK12['I']/2+1,
                   kcomp.SK12['h']+kcomp.SK12['d']/2+tbolt_head_r/self.holtol)
                   #(sk_z + kcomp.SK12['h']+kcomp.SK12['d']/2)/2)
            tbolt_head.Placement = FreeCAD.Placement(tbolt_head_pos,
                                         FreeCAD.Rotation(VX,90),
                                         V0)


            #Make an union of all these parts

            fuse_shaft_holes = doc.addObject("Part::MultiFuse",
                                             "fuse_shaft_holes")
            fuse_shaft_holes.Shapes = [tbolt_head,
                                       tbolt_shaft,
                                       up_sep, shaft_hole]

            #Cut from the sk_shape

            sk_shape_w_holes = doc.addObject("Part::Cut", "sk_shape_w_holes")
            sk_shape_w_holes.Base = sk_shape
            sk_shape_w_holes.Tool = fuse_shaft_holes

            #Mounting bolts
            mbolt_sh_r = addCyl(mbolt_r,kcomp.SK12['g']+2, "mbolt_sh_r")
            mbolt_sh_l = addCyl(mbolt_r,kcomp.SK12['g']+2, "mbolt_sh_l")

            mbolt_sh_r_pos = FreeCAD.Vector(sk_x/2,
                                            kcomp.SK12['B']/2,
                                            -1)

            mbolt_sh_l_pos = FreeCAD.Vector(sk_x/2,
                                            -kcomp.SK12['B']/2,
                                            -1)

            mbolt_sh_r.Placement.Base = mbolt_sh_r_pos
            mbolt_sh_l.Placement.Base = mbolt_sh_l_pos

            """ Equivalente expresions to the ones above
            mbolt_sh_l.Placement = FreeCAD.Placement(mbolt_sh_l_pos, v0rot, v0)
            mbolt_sh_r.Placement = FreeCAD.Placement(mbolt_sh_r_pos, v0rot, v0)
            """

            mbolts_sh = doc.addObject("Part::Fuse", "mbolts_sh")
            mbolts_sh.Base = mbolt_sh_r
            mbolts_sh.Tool = mbolt_sh_l

            # Instead of moving all the objects from the begining. I do it here
            # so it is easier, and since a new object will be created, it is
            # referenced correctly
            # Now, it is centered on Y, having the width on X, hole facing X
            # on the positive side of X
            if hole_x == 1:
                # this is how it is, no rotation
                rot = FreeCAD.Rotation(VZ,0)
                if cx == 1: #we want centered on X,bring back the half of depth
                    xpos = -self.TotD/2.0
                else:
                    xpos = 0 # how it is
                if cy == 1: # centered on Y, how it is
                    ypos = 0
                else:
                    ypos = self.TotW/2.0 # bring forward the width
            else: # hole facing Y
                rot = FreeCAD.Rotation (VZ,90)
                # After rotating, it is centered on X, 
                if cx == 1: # centered on X, how it is
                    xpos = 0
                else:
                    xpos = self.TotW /2.0
                if cy == 1: # we want centered on Y, bring back
                    ypos = - self.TotD/2.0
                else:
                    ypos = 0
             

            sk_shape_w_holes.Placement.Base = FreeCAD.Vector (xpos, ypos, 0)
            mbolts_sh.Placement.Base = FreeCAD.Vector (xpos, ypos, 0)
            sk_shape_w_holes.Placement.Rotation = rot
            mbolts_sh.Placement.Rotation = rot
 

            sk_final = doc.addObject("Part::Cut", name)
            sk_final.Base = sk_shape_w_holes
            sk_final.Tool = mbolts_sh

            self.fco = sk_final   # the FreeCad Object

# --------------------------------------------------------------------
# Creates a Misumi Aluminun Profile 30x30 Series 6 Width 8
# length:   the length of the profile
# axis      'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# cz:     1 if you want the coordinates referenced to the z center of the piece

class MisumiAlu30s6w8 (object):

    # filename of Aluminum profile sketch
    skfilename = "misumi_profile_hfs_serie6_w8_30x30.FCStd"
    ALU_W = 30.0
    ALU_Wh = ALU_W / 2.0  # half of it

    def __init__ (self, length, name, axis = 'x',
                  cx=False, cy=False, cz=False):
        doc = FreeCAD.ActiveDocument
        self.length = length
        self.name = name
        self.axis = axis
        self.cx = cx
        self.cy = cy
        self.cz = cz
        # filepath
        path = os.getcwd()
        #logging.debug(path)
        self.skpath = path + '/../../freecad/comps/'
        doc_sk = FreeCAD.openDocument(self.skpath + self.skfilename)

        list_obj_alumprofile = []
        for obj in doc_sk.Objects:
            """
            if (hasattr(obj,'ViewObject') and obj.ViewObject.isVisible()
                and hasattr(obj,'Shape') and len(obj.Shape.Faces) > 0 ):
               # len(obj.Shape.Faces) > 0 to avoid sketches
                list_obj_alumprofile.append(obj)
            """
            if len(obj.Shape.Faces) == 0:
                orig_alumsk = obj

        FreeCAD.ActiveDocument = doc
        self.Sk = doc.addObject("Sketcher::SketchObject", 'sk_' + name)
        self.Sk.Geometry = orig_alumsk.Geometry
        self.Sk.Constraints = orig_alumsk.Constraints
        self.Sk.ViewObject.Visibility = False

        FreeCAD.closeDocument(doc_sk.Name)
        FreeCAD.ActiveDocument = doc #otherwise, clone will not work

        # The sketch is on plane XY, facing Z
        if axis == 'x':
            self.Dir = (length,0,0)
            # rotation on Y
            rot = FreeCAD.Rotation(VY,90)
            if cx == True:
                xpos = - self.length / 2.0
            else:
                xpos = 0
            if cy == True:
                ypos = 0
            else:
                ypos = self.ALU_Wh  # half of the aluminum profile width
            if cz == True:
                zpos = 0
            else:
                zpos = self.ALU_Wh
        elif axis == 'y':
            self.Dir = (0,length,0)
            # rotation on X
            rot = FreeCAD.Rotation(VX,-90)
            if cx == True:
                xpos = 0
            else:
                xpos = self.ALU_Wh
            if cy == True:
                ypos = - self.length / 2.0
            else:
                ypos = 0
            if cz == True:
                zpos = 0
            else:
                zpos = self.ALU_Wh
        elif axis == 'z':
            self.Dir = (0,0,length)
            # no rotation
            rot = FreeCAD.Rotation(VZ,0)
            if cx == True:
                xpos = 0
            else:
                xpos = self.ALU_Wh
            if cy == True:
                ypos = 0
            else:
                ypos = self.ALU_Wh
            if cz == True:
                zpos = - self.length / 2.0
            else:
                zpos = 0
        else:
            logging.debug ("wrong argument")
              
        self.Sk.Placement.Rotation = rot
        self.Sk.Placement.Base = FreeCAD.Vector(xpos,ypos,zpos)

        alu_extr = doc.addObject("Part::Extrusion", name)
        alu_extr.Base = self.Sk
        alu_extr.Dir = self.Dir
        alu_extr.Solid = True

        self.fco = alu_extr   # the FreeCad Object


# ----------- class RectRndBar ---------------------------------------------
# Creates a rectangular bar with rounded edges, and with the posibility
# to be hollow
#
# Base:     the length of the base of the rectangle
# Height:   the length of the height of the rectangle
# Length:   the length of the bar, the extrusion 
# Radius:   the radius of the rounded edges (fillet)
# Thick:    the thikness of the bar (hollow bar)
#           If it is zero or larger than base or 
#               height, it will be full
# inrad_same : True: inradius = radius. When the radius is very small
#              False:  inradius = radius - thick 
# axis      'x', 'y' or 'z'
#           direction of the bar
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
# baseaxis  'x', 'y' or 'z'
#           in which axis the base is on. Cannot be the same as axis
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# cz:     1 if you want the coordinates referenced to the z center of the piece
# attributes:
# inRad : radius of the inner radius
# inBase : lenght of the inner rectangle
# inHeight : height of the inner rectangle
# hollow   : True, if it is hollow, False if it is not
# face     : the face has been extruded
# fco      : FreeCad Object

class RectRndBar (object):

    def __init__ (self, Base, Height, Length, Radius, Thick = 0, 
                  inrad_same = False, axis = 'x',
                  baseaxis = 'y', name = "rectrndbar",
                  cx=False, cy=False, cz=False):
        doc = FreeCAD.ActiveDocument
        self.Base = Base
        self.Height = Height
        self.Length = Length
        self.Radius = Radius
        self.Thick = Thick
        self.inrad_same = inrad_same
        self.name = name
        self.axis = axis
        self.baseaxis = baseaxis
        self.cx = cx
        self.cy = cy
        self.cz = cz

        self.inBase = Base - 2 * Thick
        self.inHeight = Height - 2 * Thick

        if Thick == 0 or Thick >= Base or Thick >= Height:
            self.Thick = 0
            self.hollow = False
            self.inRad = 0  
            self.inrad_same = False  
            self.inBase = 0
            self.inHeight = 0
        else :
            self.hollow = True
            if inrad_same == True:
               self.inRad = Radius
            else:
               if Radius > Thick:
                   self.inRad = Radius - Thick
               else:
                   self.inRad = 0  # a rectangle, with no rounded edges (inside)

        wire_ext = fcfun.shpRndRectWire (x=Base, y=Height, r=Radius,
                                         zpos= Length/2.0)
        face_ext = Part.Face(wire_ext)
        if self.hollow == True:
            wire_int = fcfun.shpRndRectWire (x=self.inBase, 
                                             y=self.inHeight,
                                             r=self.inRad,
                                             zpos= Length/2.0)
            face_int = Part.Face(wire_int)
            face = face_ext.cut(face_int)
        else:
            face = face_ext  # is not hollow

        self.face = face

        # Rotate and extrude in the appropiate direction

        # now is facing Z, I use vec2
        if axis == 'x': # rotate to Z, the 1 or -1 makes the extrusion different
           vec2 = (1,0,0)
           dir_extr = FreeCAD.Vector(Length,0,0)
        elif axis == 'y':
           vec2 = (0,1,0)
           dir_extr = FreeCAD.Vector(0,Length,0)
        elif axis == 'z':
           vec2 = (0,0,1)
           dir_extr = FreeCAD.Vector(0,0,Length)

        if baseaxis == 'x':
           vec1 = (1,0,0)
        elif baseaxis == 'y':
           vec1 = (0,1,0)
        elif baseaxis == 'z':
           vec1 = (0,0,1)

        vrot = fcfun.calc_rot (vec1,vec2)
        vdesp = fcfun.calc_desp_ncen (
                                      Length = self.Base,
                                      Width = self.Height,
                                      Height = self.Length ,
                                      vec1 = vec1, vec2 = vec2,
                                      cx = cx, cy=cy, cz=cz)

        face.Placement.Base = vdesp
        face.Placement.Rotation = vrot

        shp_extr = face.extrude(dir_extr)
        rndbar = doc.addObject("Part::Feature", name)
        rndbar.Shape = shp_extr

        self.fco = rndbar
        
# ----------- end class RectRndBar ----------------------------------------
            


# ---------- class LinBearing ----------------------------------------
# Creates a cylinder with a thru-hole object
# it also creates a copy of the cylinder without the hole, but a little
# bit larger, to be used to cut other shapes where this cylinder will be
# This will be useful for linear bearing/bushings container
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
#     r_tol : What to add to r_ext for the container cylinder
#     h_tol : What to add to h for the container cylinder, half on each side

# base_place: position of the 3 elements: All of them have the same base
#             position.
#             It is (0,0,0) when initialized, it has to be changed using the
#             function base_place

class LinBearing (object):

    def __init__ (self, r_ext, r_int, h, name, axis = 'z', h_disp = 0,
                  r_tol = 0, h_tol = 0):

        self.base_place = (0,0,0)
        self.r_ext  = r_ext
        self.r_int  = r_int
        self.h      = h
        self.name   = name
        self.axis   = axis
        self.h_disp = h_disp
        self.r_tol  = r_tol
        self.h_tol  = h_tol

        bearing = fcfun.addCylHole (r_ext = r_ext,
                              r_int = r_int,
                              h= h,
                              name = name,
                              axis = axis,
                              h_disp = h_disp)
        self.bearing = bearing

        bearing_cont = fcfun.addCyl_pos (r = r_ext + r_tol,
                                         h= h + h_tol,
                                         name = name + "_cont",
                                         axis = axis,
                                         h_disp = h_disp - h_tol/2.0)
        # Hide the container
        self.bearing_cont = bearing_cont
        if bearing_cont.ViewObject != None:
            bearing_cont.ViewObject.Visibility=False


    # Move the bearing and its container
    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.bearing.Placement.Base = FreeCAD.Vector(position)
        self.bearing_cont.Placement.Base = FreeCAD.Vector(position)


# ---------- class LinBearingClone ----------------------------------------
# Creates an object that is like LinBearing, but it has clones of it
# instead of original Cylinders
# h_bearing: is a LinBearing object. It has the h to indicate that it is
#            a handler, not a FreeCAD object. To get to the FreeCad object
#            take the attributes: bearing and bearing_cont (container)
# name     : name of the objects, depending on namadd, it will add it
#            to the original or not
# namadd   : 1: add to the original name
#            0: creates a new name

class LinBearingClone (LinBearing):

    def __init__ (self, h_bearing, name, namadd = 1):
        self.base_place = h_bearing.base_place
        self.r_ext      = h_bearing.r_ext
        self.r_int      = h_bearing.r_int
        self.h          = h_bearing.h
        if namadd == 1:
            self.name       = h_bearing.name + "_" + name
        else:
            self.name       = h_bearing.name
        self.axis       = h_bearing.axis
        self.h_disp     = h_bearing.h_disp
        self.r_tol      = h_bearing.r_tol
        self.h_tol      = h_bearing.h_tol

        bearing_clone = Draft.clone(h_bearing.bearing)
        bearing_clone.Label = self.name
        self.bearing = bearing_clone

        bearing_cont_clone = Draft.clone(h_bearing.bearing_cont)
        bearing_cont_clone.Label = self.name + "_cont"
        self.bearing_cont = bearing_cont_clone
        if bearing_cont_clone.ViewObject != None:
            bearing_cont_clone.ViewObject.Visibility=False


# ---------- class T8Nut ----------------------
# T8 Nut of a leadscrew
# nutaxis: where the nut is going to be facing
#          'x', '-x', 'y', '-y', 'z', '-z'
#
#           __  
#          |__|
#          |__| 
#    ______|  |_ 
#   |___________| 
#   |___________|   ------- nutaxis = 'x' 
#   |_______   _| 
#          |__|
#          |__|  
#          |__| 
#
#             |
#              ------ this is the zero. Plane YZ=0

class T8Nut (object):

    NutL = kcomp.T8N_L
    FlangeL = kcomp.T8N_FLAN_L
    ShaftOut = kcomp.T8N_SHAFT_OUT
    LeadScrewD = kcomp.T8N_D_T8
    LeadScrewR = LeadScrewD / 2.0

    # Hole for the nut and the screw
    ShaftD = kcomp.T8N_D_SHAFT_EXT 
    ShaftR = ShaftD / 2.0
    FlangeD = kcomp.T8N_D_FLAN 
    FlangeR = FlangeD / 2.0
    # hole for the M3 bolts to attach the nut to the housing
    FlangeScrewHoleD = kcomp.T8N_SCREW_D
    # Diameter where the Flange Screws are located
    FlangeScrewPosD = kcomp.T8N_D_SCREW_POS

    def __init__ (self, name, nutaxis = 'x'):
        doc = FreeCAD.ActiveDocument
        self.name = name
        self.nutaxis = nutaxis

        flange_cyl = addCyl_pos (r = self.FlangeR,
                                 h = self.FlangeL,
                                 name = "flange_cyl",
                                 axis = 'z',
                                 h_disp = - self.FlangeL)
                      
        shaft_cyl = addCyl_pos ( r = self.ShaftR,
                                 h = self.NutL,
                                 name = "shaft_cyl",
                                 axis = 'z',
                                 h_disp = - self.NutL + self.ShaftOut)

        holes_list = []
                      
        leadscrew_hole = addCyl_pos ( r = self.LeadScrewR,
                                      h = self.NutL + 2,
                                      name = "leadscrew_hole",
                                      axis = 'z',
                                      h_disp = - self.NutL + self.ShaftOut -1)
        holes_list.append (leadscrew_hole)

        flangescrew_hole1 = addCyl_pos ( r = self.FlangeScrewHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangescrew_hole1",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangescrew_hole1.Placement.Base.x = self.FlangeScrewPosD /2.0
        holes_list.append (flangescrew_hole1)
       
        flangescrew_hole2 = addCyl_pos ( r = self.FlangeScrewHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangescrew_hole2",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangescrew_hole2.Placement.Base.x = - self.FlangeScrewPosD /2.0
        holes_list.append (flangescrew_hole2)
       
        flangescrew_hole3 = addCyl_pos ( r = self.FlangeScrewHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangescrew_hole3",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangescrew_hole3.Placement.Base.y = self.FlangeScrewPosD /2.0
        holes_list.append (flangescrew_hole3)
       
        flangescrew_hole4 = addCyl_pos ( r = self.FlangeScrewHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangescrew_hole4",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangescrew_hole4.Placement.Base.y = - self.FlangeScrewPosD /2.0
        holes_list.append (flangescrew_hole4)

        nut_holes = doc.addObject("Part::MultiFuse", "nut_holes")
        nut_holes.Shapes = holes_list

        nut_cyls = doc.addObject("Part::Fuse", "nut_cyls")
        nut_cyls.Base = flange_cyl
        nut_cyls.Tool = shaft_cyl

        if nutaxis == 'x':
            vrot = FreeCAD.Rotation (VY,90)
        elif nutaxis == '-x':
            vrot= FreeCAD.Rotation (VY,-90)
        elif nutaxis == 'y':
            vrot= FreeCAD.Rotation (VX,-90)
        elif nutaxis == '-y':
            vrot = FreeCAD.Rotation (VX,90)
        elif nutaxis == '-z':
            vrot = FreeCAD.Rotation (VX,180)
        else: # nutaxis =='z' no rotation
            vrot = FreeCAD.Rotation (VZ,0)

        nut_cyls.Placement.Rotation = vrot
        nut_holes.Placement.Rotation = vrot

        t8nut = doc.addObject("Part::Cut", "t8nut")
        t8nut.Base = nut_cyls
        t8nut.Tool = nut_holes
        # recompute before color
        doc.recompute()
        t8nut.ViewObject.ShapeColor = fcfun.YELLOW

        self.fco = t8nut  # the FreeCad Object
   
                      
    

# ---------- class T8NutHousing ----------------------
# Housing for a T8 Nut of a leadscrew
# nutaxis: where the nut is going to be facing
#          'x', '-x', 'y', '-y', 'z', '-z'
# screwface_axis: where the screws are going to be facing
#          it cannot be the same axis as the nut
#          'x', '-x', 'y', '-y', 'z', '-z'
# cx, cy, cz, if it is centered on any of the axis

class T8NutHousing (object):

    Length = kcomp.T8NH_L
    Width  = kcomp.T8NH_W
    Height = kcomp.T8NH_H

    # separation between the screws that attach to the moving part
    ScrewLenSep  = kcomp.T8NH_ScrLSep
    ScrewWidSep  = kcomp.T8NH_ScrWSep

    # separation between the screws to the end
    ScrewLen2end = (Length - ScrewLenSep)/2
    ScrewWid2end = (Width  - ScrewWidSep)/2

    # Screw dimensions, that attach to the moving part: M4 x 7
    ScrewD = kcomp.T8NH_ScrD
    ScrewR = ScrewD / 2.0
    ScrewL = kcomp.T8NH_ScrL + kcomp.TOL

    # Hole for the nut and the screw
    ShaftD = kcomp.T8N_D_SHAFT_EXT + kcomp.TOL # I don't know the tolerances
    ShaftR = ShaftD / 2.0
    FlangeD = kcomp.T8N_D_FLAN + kcomp.TOL # I don't know the tolerances
    FlangeR = FlangeD / 2.0
    FlangeL = kcomp.T8N_FLAN_L + kcomp.TOL
    FlangeScrewD = kcomp.T8NH_FlanScrD
    FlangeScrewR = FlangeScrewD / 2.0
    FlangeScrewL = kcomp.T8NH_FlanScrL + kcomp.TOL
    # Diameter where the Flange Screws are located
    FlangeScrewPosD = kcomp.T8N_D_SCREW_POS
  
    def __init__ (self, name, nutaxis = 'x', screwface_axis = 'z',
                  cx = 1, cy= 1, cz = 0):
        self.name = name
        self.nutaxis = nutaxis
        self.screwface_axis = screwface_axis
        self.cx = cx
        self.cy = cy
        self.cz = cz

        doc = FreeCAD.ActiveDocument
        # centered so it can be rotated without displacement, and everything
        # will be in place
        housing_box = fcfun.addBox_cen (self.Length, self.Width, self.Height,
                                  name= name + "_box", 
                                  cx=True, cy=True, cz=True)

        hole_list = []

        leadscr_hole = addCyl_pos (r=self.ShaftR, h= self.Length + 1,
                                   name = "leadscr_hole",
                                   axis = 'x', h_disp = -self.Length/2.0-1)
        hole_list.append(leadscr_hole)
        nutflange_hole = addCyl_pos (r=self.FlangeR, h= self.FlangeL + 1,
                                   name = "nutflange_hole",
                                   axis = 'x',
                                   h_disp = self.Length/2.0 - self.FlangeL)
        hole_list.append(nutflange_hole)
        # screws to attach the nut flange to the housing
        # M3 x 10
        screwflange_l = addCyl_pos (r = self.FlangeScrewR,
                                    h = self.FlangeScrewL + 1,
                                    name = "screwflange_l",
                                    axis = 'x',
                                    h_disp =   self.Length/2.0
                                             - self.FlangeL
                                             - self.FlangeScrewL)
        screwflange_l.Placement.Base = FreeCAD.Vector(0,
                                    - self.FlangeScrewPosD / 2.0,
                                   )
        hole_list.append(screwflange_l)
        screwflange_r = addCyl_pos (r = self.FlangeScrewR,
                                    h = self.FlangeScrewL + 1,
                                    name = "screwflange_r",
                                    axis = 'x',
                                    h_disp =   self.Length/2.0
                                             - self.FlangeL
                                             - self.FlangeScrewL)
        screwflange_r.Placement.Base = FreeCAD.Vector (0,
                                   self.FlangeScrewPosD / 2.0,
                                   0)
        hole_list.append(screwflange_r)


        # screws to attach the housing to the moving part
        # M4x7
        screwface_1 = fcfun.addCyl_pos (r = self.ScrewR, h = self.ScrewL + 1,
                                        name="screwface_1",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        screwface_1.Placement.Base = FreeCAD.Vector (
                                    - self.Length/2.0 + self.ScrewLen2end,
                                    - self.Width/2.0 + self.ScrewWid2end,
                                      0)
        hole_list.append (screwface_1)
        screwface_2 = fcfun.addCyl_pos (r = self.ScrewR, h = self.ScrewL + 1,
                                        name="screwface_2",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        screwface_2.Placement.Base = FreeCAD.Vector(
                                      self.ScrewLenSep /2.0,
                                    - self.Width/2.0 + self.ScrewWid2end,
                                      0)
        hole_list.append (screwface_2)
        screwface_3 = fcfun.addCyl_pos (r = self.ScrewR, h = self.ScrewL + 1,
                                        name="screwface_3",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        screwface_3.Placement.Base = FreeCAD.Vector (
                                    - self.Length/2.0 + self.ScrewLen2end,
                                      self.ScrewWidSep /2.0,
                                      0)
        hole_list.append (screwface_3)
        screwface_4 = fcfun.addCyl_pos (r = self.ScrewR, h = self.ScrewL + 1,
                                        name="screwface_4",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        screwface_4.Placement.Base = FreeCAD.Vector(
                                      self.ScrewLenSep /2.0,
                                      self.ScrewWidSep /2.0,
                                      0)
        hole_list.append (screwface_4)
        nuthouseholes = doc.addObject ("Part::MultiFuse", "nuthouse_holes")
        nuthouseholes.Shapes = hole_list
       
        # rotation vector calculation
        if nutaxis == 'x':
           vec1 = (1,0,0)
        elif nutaxis == '-x':
           vec1 = (-1,0,0)
        elif nutaxis == 'y':
           vec1 = (0,1,0)
        elif nutaxis == '-y':
           vec1 = (0,-1,0)
        elif nutaxis == 'z':
           vec1 = (0,0,1)
        elif nutaxis == '-z':
           vec1 = (0,0,-1)

        if screwface_axis == 'x':
           vec2 = (1,0,0)
        elif screwface_axis == '-x':
           vec2 = (-1,0,0)
        elif screwface_axis == 'y':
           vec2 = (0,1,0)
        elif screwface_axis == '-y':
           vec2 = (0,-1,0)
        elif screwface_axis == 'z':
           vec2 = (0,0,1)
        elif screwface_axis == '-z':
           vec2 = (0,0,-1)

        vrot = fcfun.calc_rot (vec1,vec2)
        vdesp = fcfun.calc_desp_ncen (
                                      Length = self.Length,
                                      Width = self.Width,
                                      Height = self.Height,
                                      vec1 = vec1, vec2 = vec2,
                                      cx = cx, cy=cy, cz=cz)

        housing_box.Placement.Rotation = vrot
        nuthouseholes.Placement.Rotation = vrot
        housing_box.Placement.Base = vdesp
        nuthouseholes.Placement.Base = vdesp

        t8nuthouse = doc.addObject ("Part::Cut", "t8nuthouse")
        t8nuthouse.Base = housing_box
        t8nuthouse.Tool = nuthouseholes

        self.fco = t8nuthouse  # the FreeCad Object


