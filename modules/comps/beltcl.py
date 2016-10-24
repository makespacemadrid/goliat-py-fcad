# ----------------------------------------------------------------------------
# -- Belt Clamp Tensioner
# -- comps library
# -- Python classes and functions to make belt tensioner in FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD;
import Part;
import Draft;

import kcomp  # import material constants and other constants
import fcfun      # import my functions for freecad



from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL



# --------------------------- belt clamp and tensioner
# radius of the cylinder
"""                           
          TOPVIEW                    
                CLAMPBLOCK          
                    CB             
                    ____     
           CB_W  {  XXXX       ___
           CB_IW {  ____      /   \
 0,1 or 2: CB_MW {  XXXX      |   |   CCYL: CLAMPCYL 
           CB_IW {  ____      \___/
           CB_W  {  XXXX     
        
                    CB_L  CS


    Y A  (width)
      |
      |---> X (length)

"""
# Arguments:
#  midblock: 0 or 1. It will add a none/single width middle block
#                   In the future I may consider a double middle block (2)
#  base_h:  height of the base


# Attributes:
# fco : the FreeCAD Object of the belt clamp
# BaseOffset : the FreeCAD object of the belt clamp offset. To make a cut
#              on the FreeCAD object where the belt tensioner will be.


class Gt2BeltClamp (object):

    # space for the 2 belts to clamp them
    # the GT2 belt is 1.38mm width. 2 together facing teeth will be about 2mm
    # I make it 2.8mm
    # Internal Width of the Clamp Block
    CB_IW = 2.8
    # Width of the exterior clamp blocks (Y axis)
    CB_W = 4.0
    # Length of the clamp blocks (X axis)
    CB_L = 12.0
    # GT2 height is 6 mm, making the heigth 8mm
    C_H = 8.0
    # GT2 Clamp Cylinder radius
    CCYL_R = 4.0
    # separation between the clamp blocks and the clamp cylinder
    CS = 3.0

    # separation of the nut hole from the edge
    NUT_HOLE_EDGSEP = 3 


    """
    how much the rail is inside

     ________________________________________________    
    |        
    |   __________________________
     \                        ____ CBASERAILIND 
      |       
     /  _____ CBASE_RAIL ___
    |
    |_________________________ CBASE_WALL _________ CBASE_H

    |-|
      CBASERAILIND_SIG (it is 45 degrees). SIG: can be + or -

    if midblock > 0 this will be the indentation, 
    if midblock == 0 it will be outward, like this:
        _________
       |         |
      /           \ 
     |             |
      \           /
       |_________|
      
    """
  
    CBASE_L = CB_L + CS + 2*CCYL_R

    def __init__(self, base_h, midblock, name):
        doc = FreeCAD.ActiveDocument
        # Clamp base
        self.CBASE_H = base_h
        # divides how much is rail and how much is wall
        # It has to be greater than 1. If it is 1, there is no wall.
        # if it is 2. Half is wall, half is indent
        self.CBASE_RAIL_DIV = 1.6 #2.0
        self.CBASE_RAIL = self.CBASE_H / self.CBASE_RAIL_DIV # rail for the base
        # the part that is wall, divided by 2, because one goes at the bottom
        # and the other on top
        # rail for the base
        self.CBASE_WALL = (self.CBASE_H - self.CBASE_RAIL)/2.0 
        # Indentation, if midblock == 0, the Indentation is negative, which
        # means it will be outward, otherwise, inward
        self.CBASERAILIND = self.CBASE_RAIL/3.0

        self.midblock = midblock
        # Width of the interior/middle clamp blocks
        self.CB_MW = midblock * self.CB_W
        if midblock == 0:
            self.CBASE_W =     self.CB_IW + 2 * self.CB_W 
            self.CBASERAILIND_SIG = - self.CBASERAILIND 
            # Since the indentation is outwards, we have to add it
            self.TotW = self.CBASE_W + 2 *  self.CBASERAILIND
            # external indent, so all the internal elements have to have this
            # nternal offset. In Y axis
            self.extind = self.CBASERAILIND 
        else:
            self.CBASE_W = 2 * self.CB_IW + 2 * self.CB_W + self.CB_MW
            self.CBASERAILIND_SIG = self.CBASERAILIND 
            # Since the indentation is inward, it is just the base
            self.TotW = self.CBASE_W 
            # no external indent, so the internal elements don't have to have 
            # this internal offset
            self.extind = 0
  
        gt2_clamp_list = []
        # we make it using points-plane and extrusions
        #gt2_base =addBox (self.CBASE_L, self.CBASE_W, self.CBASE_H, "gt2_base")
        gt2_cb_1 = addBox (self.CB_L, self.CB_W, self.C_H+1, name + "_cb1")
        gt2_cb_1.Placement.Base = FreeCAD.Vector (self.CBASE_L-self.CB_L,
                                                  self.extind,
                                                  self.CBASE_H-1)
        gt2_clamp_list.append (gt2_cb_1)
        if midblock > 0:
          gt2_cb_2 = addBox (self.CB_L, self.CB_MW, self.C_H+1, name + "_cb2")
          gt2_cb_2.Placement.Base = FreeCAD.Vector (self.CBASE_L-self.CB_L,
		                                   self.CB_W + self.CB_IW + self.extind,
		                                   self.CBASE_H-1)
          gt2_clamp_list.append (gt2_cb_2)

        gt2_cb_3 = addBox (self.CB_L, self.CB_W, self.C_H + 1, name + "_cb3")
        gt2_cb_3.Placement.Base = FreeCAD.Vector (self.CBASE_L-self.CB_L,
                                        self.CBASE_W - self.CB_W + self.extind,
		                                self.CBASE_H-1)
        gt2_clamp_list.append (gt2_cb_3)
 
        gt2_cyl = addCyl (self.CCYL_R,  self.C_H + 1, name + "_cyl")
        gt2_cyl.Placement.Base = FreeCAD.Vector (self.CCYL_R, 
                                             self.CBASE_W/2 + self.extind,
                                             self.CBASE_H-1)
        gt2_clamp_list.append (gt2_cyl)

        # base
        # calling to the method that gets a list of the points to make 
        # the polygon of the base
        #gt2_base_list = self.get_base_list_v()
        # doing this because the carriage is already printed, so I am going
        # to make the base smaller to fit. CHANGE to the upper sentence
        gt2_base_list = self.get_base_list_v(offs_y = -TOL/2, offs_z = - TOL)
        """
        gt2_base_plane_yz = Part.makePolygon(gt2_base_list)
        gt2_base = gt2_base_plane_xy.extrude(FreeCAD.Vector(self.CBASE_L,0,0))
        """
        gt2_base_plane_yz = doc.addObject("Part::Polygon",
                                           name + "base_plane_yz")
        gt2_base_plane_yz.Nodes = gt2_base_list
        gt2_base_plane_yz.Close = True
        gt2_base = doc.addObject("Part::Extrusion",
                                           name + "extr_base")
        gt2_base.Base = gt2_base_plane_yz
        gt2_base.Dir = (self.CBASE_L,0,0)
        gt2_base.Solid = True

        gt2_clamp_list.append(gt2_base)

        gt2_clamp_basic = doc.addObject("Part::MultiFuse", name + "clamp_base")
        gt2_clamp_basic.Shapes = gt2_clamp_list

        # creation of the same base, but with a little offset to be able to 
        # cut the piece where it will be inserted
        #gt2_baseof_list = self.get_base_list_v(offs_y = TOL, offs_z = TOL/2.0)
        # CHANGE TO THE UPPER SENTENCE
        gt2_baseof_list = self.get_base_list_v(offs_y = TOL, offs_z = 0)
        gt2_baseof_plane_yz = doc.addObject("Part::Polygon",
                                           name + "_baseof_plane_yz")
        gt2_baseof_plane_yz.Nodes = gt2_baseof_list
        gt2_baseof_plane_yz.Close = True
        gt2_baseof = doc.addObject("Part::Extrusion",
                                   name + "_baseof")
        gt2_baseof.Base = gt2_baseof_plane_yz
        gt2_baseof.Dir = (self.CBASE_L,0,0)
        gt2_baseof.Solid = True

        self.BaseOffset = gt2_baseof

        # hole for the leadscrew bolt
        # the head is longer because it can be inserted deeper into the piece
        # so a shorter bolt will be needed
        gt2_base_lscrew = addBolt (kcomp.M3_SHANK_R_TOL, self.CBASE_L,
                                   kcomp.M3_HEAD_R_TOL, 2.5*kcomp.M3_HEAD_L,
                                   extra = 1, support = 0,
                                   name= name + "_base_lscrew")
    
        gt2_base_lscrew.Placement.Base = FreeCAD.Vector (self.CBASE_L,
                                                self.CBASE_W/2.0 + self.extind,
                                                self.CBASE_H/2.0)
        gt2_base_lscrew.Placement.Rotation = FreeCAD.Rotation (VY, -90)

        # ------------ hole for a nut, also M3, for the leadscrew 
        gt2_base_lscrew_nut = doc.addObject("Part::Prism", 
                                            name + "_base_lscrew_nut")
        gt2_base_lscrew_nut.Polygon = 6
        gt2_base_lscrew_nut.Circumradius = kcomp.M3_NUT_R_TOL
        gt2_base_lscrew_nut.Height = kcomp.M3NUT_HOLE_H 
        gt2_base_lscrew_nut.Placement.Rotation = \
                                      gt2_base_lscrew.Placement.Rotation 
                  # + TOL so it will be a little bit higher, so more room
        gt2_base_lscrew_nut.Placement.Base = FreeCAD.Vector (
                  #(self.CBASE_L-kcomp.M3_HEAD_L)/2.0 - kcomp.M3NUT_HOLE_H/2.0,
                               self.NUT_HOLE_EDGSEP,
                               self.CBASE_W/2.0 + self.extind,
                               self.CBASE_H/2.0 + TOL) 
        gt2_base_lscrew_nut.Placement.Rotation = FreeCAD.Rotation (VY, 90)
        # ------------ hole to reach out the nut hole
 
        # X is the length: M3NUT_HOLE_H. Y is the width. M3_2APOT_TOL
        gt2_base_lscrew_nut2 = addBox (kcomp.M3NUT_HOLE_H,
                                       kcomp.M3_2APOT_TOL,
                                       self.CBASE_H/2.0 + TOL,
                                       name + "_base_lscrew_nut2")
        gt2_base_lscrew_nut2.Placement.Base = (
                    #((self.CBASE_L-kcomp.M3_HEAD_L) - kcomp.M3NUT_HOLE_H)/2.0,
                       self.NUT_HOLE_EDGSEP,
                       (self.CBASE_W - kcomp.M3_2APOT_TOL)/2.0 + self.extind,
                       0)

        gt2_base_holes_l = [ gt2_base_lscrew,
                             gt2_base_lscrew_nut,
                             gt2_base_lscrew_nut2]

        # fuse the holes
        gt2_clamp_holes = doc.addObject("Part::MultiFuse", name + "_clamp_hole")
        gt2_clamp_holes.Shapes = gt2_base_holes_l
        # Substract the holes 
        gt2_clamp = doc.addObject("Part::Cut", name)
        gt2_clamp.Base = gt2_clamp_basic
        gt2_clamp.Tool = gt2_clamp_holes

        self.fco = gt2_clamp   # the FreeCad Object

    # --------------------------------------------------------------------
    # obtains the list of vectors for the base of the clamp
    # offs_y: if zero it takes normal points
    # offs_z added because it didn't fit
    # offs_z: if zero it takes normal points
    #  CBASERAILIND_SIG <0:              CBASERAILIND_SIG > 0
    #  lv5         _________               ___________
    #  lv4        |         |             |
    #  lv3       /           \             \ 
    #  lv2      |             |             |
    #  lv1       \           /             / 
    #  lv0        |_________|             |_
    #         
    #
    #
    def get_base_list_v(self, offs_y = 0, offs_z = 0):

        if self.CBASERAILIND_SIG < 0:
            offs_zsig = - offs_z
        else:
            offs_zsig =  offs_z

        # Points that make the shape of the base
        # left side (offs is negative
        gt2_base_lv00 = FreeCAD.Vector (0,
                                        0 - offs_y,
                                        0)
        # offs_z higher when CBASERAILIND_SIG > 0
        gt2_base_lv01 = FreeCAD.Vector (0,
                                        0 - offs_y,
                                        self.CBASE_WALL + offs_zsig)
        gt2_base_lv02 = FreeCAD.Vector (
                                0,
                                self.CBASERAILIND_SIG - offs_y,
                                self.CBASE_WALL + self.CBASERAILIND + offs_zsig)
        # offs_z negative (lower)
        gt2_base_lv03 = FreeCAD.Vector (0,
                            self.CBASERAILIND_SIG - offs_y,
                            self.CBASE_WALL + 2*self.CBASERAILIND - offs_zsig)
        gt2_base_lv04 = FreeCAD.Vector (0,0 - offs_y,
                                self.CBASE_WALL + self.CBASE_RAIL - offs_zsig)
        gt2_base_lv05 = FreeCAD.Vector (0,0 - offs_y,
                                        self.CBASE_H)
        # right side (offs_y is positive
        gt2_base_rv00 = FreeCAD.Vector (0,
                                        self.CBASE_W + offs_y,
                                        0)
        gt2_base_rv01 = FreeCAD.Vector (0,
                                        self.CBASE_W + offs_y,
                                        self.CBASE_WALL + offs_zsig)
        gt2_base_rv02 = FreeCAD.Vector (0,
                               self.CBASE_W - self.CBASERAILIND_SIG + offs_y,
                               self.CBASE_WALL + self.CBASERAILIND + offs_zsig)
        gt2_base_rv03 = FreeCAD.Vector (0,
                             self.CBASE_W - self.CBASERAILIND_SIG + offs_y,
                             self.CBASE_WALL + 2*self.CBASERAILIND - offs_zsig)
        gt2_base_rv04 = FreeCAD.Vector (0,
                             self.CBASE_W + offs_y,
                             self.CBASE_WALL + self.CBASE_RAIL - offs_zsig)
        gt2_base_rv05 = FreeCAD.Vector (0,
                                        self.CBASE_W + offs_y,
                                        self.CBASE_H)
    
        gt2_base_list = [
                         gt2_base_lv00,
                         gt2_base_lv01,
                         gt2_base_lv02,
                         gt2_base_lv03,
                         gt2_base_lv04,
                         gt2_base_lv05,
                         gt2_base_rv05,
                         gt2_base_rv04,
                         gt2_base_rv03,
                         gt2_base_rv02,
                         gt2_base_rv01,
                         gt2_base_rv00
                        ]

        # if it is negative, the indentation will be outwards, so we will
        # make the Y=0 on the most outward point, except for the offs_y
        # that will be negative when Y=0
        if self.CBASERAILIND_SIG < 0:
            addofs = FreeCAD.Vector (0, - self.CBASERAILIND_SIG,0)
            gt2_base_list = [x + addofs for x in gt2_base_list]

        return gt2_base_list
    
# end class Gt2BeltClamp:

