# ----------------------------------------------------------------------------
# -- Parts 3D
# -- comps library
# -- Python scripts to create 3D parts models in FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

# classes that creates objects to be 3D printed

import FreeCAD;
import Part;
import logging
import os
import Draft;
#import copy;
#import Mesh;

# can be taken away after debugging
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)


import fcfun
import kcomp    # import material constants and other constants
import comps    # import my CAD components
import beltcl   # import my CAD components
import partgroup  # import my CAD components

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL


logging.basicConfig(level=logging.DEBUG)
                    #format='%(%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------- class EndShaftSlider ----------------------------------------
# Creates the slider that goes on a rod and supports the end of another
# rod. The slider runs on 2 linear bearings
# The slider is referenced on the slider axis
# Creates both sides, the upper part and the lower part, it also creates the
# linear bearings

#     slidrod_r : radius of the rod where the slider runs on
#     holdrod_r : radius of the rod that this slider holds
#     holdrod_sep : separation between the rods that are holded
#     holdrod_cen : 1: if the piece is centered on the perpendicular 
#     side        : 'left' or 'right' (slidding on axis Y)
#                 : 'bottom' or 'top' (slidding on axis X)
#
#          Y      axis= 'y'    side='left'
#          |
#          |                                  
#          |
#          |
#      ____|_________
#     |  |   |   ____|
#     |  |   |  |____|
#     |  |   |       |
#     |  |   |       |
#     |  |   |       |---------------- X: holdrod_cen = 1
#     |  |   |       |
#     |  |   |   ____|
#     |  |   |  |____|
#     |__|___|_______|________________ X: holdrod_cen = 0
#
#
#
#      ____|_________ __________________________________________ length
#     |  |   |   ____|
#     |  |   |  |____| ----------------------- holdrod_sep
#     |  |   |       |
#     |  |   |       |                        |
#     |  |   |       |
#     |  |   |       |                        |
#     |  |   |   ____|
#     |  |   |  |____|----- holdrod2end --------
#     |__|___|_______|__________________________________________ 
#
#          |    |
#          |----|----> slide2holdrod (+)
#


# --- Atributes:
# length : length of the slider, on the direction of the slidding axis
# width  : width of the slider, on the direction perpendicular to the slidding
#          axis. On the direction of the holding axis
# partheight : heigth of each part of the slider. So the total height will be
#              twice this height
# holdrod_sep : separation between the 2 rods that are holded and forms the 
#               perpendicular axis movement
# slide2holdrod : distance from the sliding rod (axis) to
#                 the beginning of the hold rod (axis). Positive
# slide2holdrod_sign : distance from the sliding rod (axis) to
#                 the beginning of the hold rod (axis). Positive
#                 or negative depending on the sign
# dent_w  : width of the dent, if no dent is needed, just dent_w = 0
# dent_l  : length of the dent, 
# dent_sl : small dimension of the dent length
# ovdent_w  : width of the dent, including the overlap to make the union
# ovdent_l  : length of the dent, including the overlap to make the union 
# idlepull_axsep : separation between the axis iddle pulleys
# belt_sep : separation between the inner part of the iddle pulleys
#                   that is where the belts are. So it is
#                   idlepull_axsep - 2* radius of the bearing
# idlepulls : FreeCad object of the idle pulleys
# bearings : FreeCad object of the bearings
# top_slide : FreeCad object of the top part of the slider
# bot_slide : FreeCad object of the bottm part of the slider
# base_place: position of the 3 elements: All of them have the same base
#             position.
#             It is (0,0,0) when initialized, it has to be changed using the
#             function Base_Place

class EndShaftSlider (object):

    # Separation from the end of the linear bearing to the end of the piece
    # on the Heigth dimension (Z)
    OUT_SEP_H = 3.0

    # Minimum separation between the bearings, on the slide direction
    MIN_BEAR_SEP = 3.0

    # Ratio between the length of the rod (shaft) that is inserted in the slider
    # and the diameter of the holded shaft
    HOLDROD_INS_RATIO = 2.0

    # Radius to fillet the sides
    FILLT_R = 2.0

    # Space for the sliding rod, to be added to its radius, and to be cut
    SLIDEROD_SPACE = 1.5

    # tolerance on their length for the bearings. Larger because the holes
    # usually are too tight and it doesn't matter how large is the hole
    #TOL_BEARING_L = 2.0 # printed in black and was too loose
    TOL_BEARING_L = 1.0 # reduced

    MTOL = TOL - 0.1 # reducing the tolrances, it was too tolerant :)
    MLTOL = TOL - 0.05 # reducing the tolrances, it was too tolerant :)

    # Bolts to hold the top and bottom parts:
    BOLT_D = 4
    BOLT_HEAD_R = kcomp.D912_HEAD_D[BOLT_D] / 2.0
    BOLT_HEAD_L = kcomp.D912_HEAD_L[BOLT_D] + MTOL
    BOLT_HEAD_R_TOL = BOLT_HEAD_R + MTOL/2.0 
    BOLT_SHANK_R_TOL = BOLT_D / 2.0 + MTOL/2.0
    BOLT_NUT_R = kcomp.NUT_D934_D[BOLT_D] / 2.0
    BOLT_NUT_L = kcomp.NUT_D934_L[BOLT_D] + MTOL
    #  1.5 TOL because diameter values are minimum, so they may be larger
    BOLT_NUT_R_TOL = BOLT_NUT_R + 1.5*MTOL

    # Bolts for the pulleys
    BOLTPUL_R = 4
    BOLTPUL_SHANK_R_TOL = BOLTPUL_R / 2.0 + MTOL/2.0
    BOLTPUL_NUT_R = kcomp.NUT_D934_D[BOLTPUL_R] / 2.0
    BOLTPUL_NUT_L = kcomp.NUT_D934_L[BOLTPUL_R] + MTOL
    #  1.5 TOL because diameter values are minimum, so they may be larger
    BOLTPUL_NUT_R_TOL = BOLTPUL_NUT_R + 1.5*MTOL

    def __init__ (self, slidrod_r, holdrod_r, holdrod_sep, 
                  name, holdrod_cen = 1, side = 'left'):

        doc = FreeCAD.ActiveDocument
        self.base_place = (0,0,0)
        self.slidrod_r = slidrod_r
        self.holdrod_r = holdrod_r
        self.holdrod_sep = holdrod_sep
        self.holdrod_cen = holdrod_cen
    
        self.name        = name
        #self.axis        = axis

        # Separation from the end of the linear bearing to the end of the piece
        # on the width dimension (perpendicular to the movement)
        if self.BOLT_D == 3:
            self.OUT_SEP_W = 8.0
            # on the length dimension (parallel to the movement)
            self.OUT_SEP_L = 10.0
        elif self.BOLT_D == 4:
            self.OUT_SEP_W = 10.0
            self.OUT_SEP_L = 14.0
        else:
            print "not defined"

        bearing_l     = kcomp.LMEUU_L[int(2*slidrod_r)] 
        bearing_l_tol = bearing_l + self.TOL_BEARING_L
        bearing_d     = kcomp.LMEUU_D[int(2*slidrod_r)]
        bearing_d_tol = bearing_d + 2.0 * self.MLTOL
        bearing_r     = bearing_d / 2.0
        bearing_r_tol = bearing_r + self.MLTOL

        holdrod_r_tol =  holdrod_r + self.MLTOL/2.0

        holdrod_insert = self.HOLDROD_INS_RATIO * (2*slidrod_r) 

        self.slide2holdrod = bearing_r + self.MIN_BEAR_SEP 
        if side == 'right' or side == 'top':
            # the distance will be negative, either on the X axis (right)
            # or on the Y axis (top)
            self.slide2holdrod_sign = - self.slide2holdrod
        else:
            self.slide2holdrod_sign = self.slide2holdrod
    
        # calculation of the width
        # dimensions should not depend on tolerances
        self.width = (  bearing_d     #bearing_d_tol
                      + self.OUT_SEP_W
                      + holdrod_insert
                      + self.MIN_BEAR_SEP )


        # calculation of the length
        # it can be determined by the holdrod_sep (separation of the hold rods)
        # or by the dimensions of the linear bearings. It will be the largest
        # of these two: 
        # tlen: total length ..
        tlen_holdrod = holdrod_sep + 2 * self.OUT_SEP_L + 2 * holdrod_r
        #tlen_holdrod = holdrod_sep + 2 * self.OUT_SEP_L + 2 * holdrod_r_tol
        #tlen_bearing = (  2 * bearing_l_tol
        tlen_bearing = (  2 * bearing_l
                        + 2* self.OUT_SEP_L
                        + self.MIN_BEAR_SEP)
        if tlen_holdrod > tlen_bearing:
            self.length = tlen_holdrod
            print "length comes from holdrod"
        else:
            self.length = tlen_bearing
            print "length comes from bearing: Check for errors"
       

        self.partheight = (  bearing_r
                           + self.OUT_SEP_H)

        
        # distance from the center of the hold rod to the end on the sliding
        # direction
        self.holdrod2end = (self.length - holdrod_sep)/2

#        if axis == 'x':
#            slid_x = self.length
#            slid_y = self.width
#            slid_z = self.partheight
#        else: # 'y': default
        slid_x = self.width
        slid_y = self.length
        slid_z = self.partheight

        if holdrod_cen == 1:
            # offset if it is centered on the y
            y_offs = - slid_y/2.0
        else:
            y_offs = 0


        slid_posx = - (bearing_r + self.OUT_SEP_W)


        bearing0_pos_y = self.OUT_SEP_L
        # Not bearing_l_tol, because the tol will be added on top and bottom
        # automatically
        bearing1_pos_y = self.length - (self.OUT_SEP_L + bearing_l)
         
        # adding the offset
        bearing0_pos_y = bearing0_pos_y + y_offs
        bearing1_pos_y = bearing1_pos_y + y_offs


        topslid_box = addBox(slid_x, slid_y, slid_z, "topsideslid_box")
        topslid_box.Placement.Base = FreeCAD.Vector(slid_posx, y_offs, 0)

        botslid_box = addBox(slid_x, slid_y, slid_z, "bosidetslid_box")
        botslid_box.Placement.Base = FreeCAD.Vector(slid_posx, y_offs,
                                                    -self.partheight)

        topslid_fllt = fillet_len (topslid_box, slid_z, 
                                  self.FILLT_R, "topsideslid_fllt")
        botslid_fllt = fillet_len (botslid_box, slid_z,
                                  self.FILLT_R, "botsideslid_fllt")

        # list of elements that cut:
        cutlist = []

        sliderod = fcfun.addCyl_pos (r = slidrod_r + self.SLIDEROD_SPACE,
                               h = slid_y +2,
                               name = "sliderod",
                               axis = 'y',
                               h_disp = y_offs - 1)

        cutlist.append (sliderod)

        h_lmuu_0 = comps.LinBearing (
                         r_ext = bearing_r,
                         r_int = slidrod_r,
                         h     = bearing_l,
                         name  = "lm" + str(int(2*slidrod_r)) + "uu_0",
                         axis  = 'y',
                         h_disp = bearing0_pos_y,
                         r_tol  = self.MLTOL,
                         h_tol  = self.TOL_BEARING_L)

        cutlist.append (h_lmuu_0.bearing_cont)

        h_lmuu_1 = comps.LinBearingClone (
                                      h_lmuu_0,
                                      "lm" + str(int(2*slidrod_r)) + "uu_1",
                                      namadd = 0)
        h_lmuu_1.BasePlace ((0, bearing1_pos_y - bearing0_pos_y, 0))
        cutlist.append (h_lmuu_1.bearing_cont)


        # ------------ hold rods ----------------

        holdrod_0 = fcfun.addCyl_pos (
                                r = holdrod_r_tol,
                                h = holdrod_insert + 1,
                                name = "holdrod_0",
                                axis = 'x',
                                h_disp = bearing_r + self.MIN_BEAR_SEP )
                                #h_disp = bearing_r_tol + self.MIN_BEAR_SEP )

        holdrod_0.Placement.Base = FreeCAD.Vector(
                                     0,
                                     self.holdrod2end + y_offs,
                                     0)
        cutlist.append (holdrod_0)

        holdrod_1 = fcfun.addCyl_pos (
                                r = holdrod_r_tol,
                                h = holdrod_insert + 1,
                                name = "holdrod_1",
                                axis = 'x',
                                h_disp = bearing_r + self.MIN_BEAR_SEP )
                                #h_disp = bearing_r_tol + self.MIN_BEAR_SEP )

        holdrod_1.Placement.Base = FreeCAD.Vector(
                                       0,
                                       self.length - self.holdrod2end + y_offs,
                                       0)
        cutlist.append (holdrod_1)

        # -------------------- bolts and nuts
        bolt0 = addBoltNut_hole (
                            r_shank   = self.BOLT_SHANK_R_TOL,
                            l_bolt    = 2 * self.partheight,
                            r_head    = self.BOLT_HEAD_R_TOL,
                            l_head    = self.BOLT_HEAD_L,
                            r_nut     = self.BOLT_NUT_R_TOL,
                            l_nut     = self.BOLT_NUT_L,
                            hex_head  = 0, extra=1,
                            supp_head = 1, supp_nut=1,
                            headdown  = 0, name="bolt_hole")

        #bolt_left_pos_x =  -(  bearing_r_tol
        bolt_left_pos_x =  -(  bearing_r
                             + self.OUT_SEP_W
                             + sliderod.Base.Radius.Value) / 2.0

        #bolt_right_pos_x =   (  bearing_r_tol
        bolt_right_pos_x =   (  bearing_r
                              + self.MIN_BEAR_SEP
                              + 0.6 * holdrod_insert )

        bolt_low_pos_y =  self.OUT_SEP_L / 2.0 + y_offs
        bolt_high_pos_y =  self.length - self.OUT_SEP_L / 2.0 + y_offs

        bolt_lowmid_pos_y =  1.5 * self.OUT_SEP_L + 2 * holdrod_r + y_offs
        bolt_highmid_pos_y = (  self.length
                             - 1.5 * self.OUT_SEP_L
                             - 2 * holdrod_r  # no _tol
                             + y_offs)

        bolt_pull_pos_x =   (  bearing_r_tol
                              + self.MIN_BEAR_SEP
                              + 0.25 * holdrod_insert )
        #bolt_pullow_pos_y =  2.5 * self.OUT_SEP_L + 2 * holdrod_r_tol + y_offs
        bolt_pullow_pos_y =  2.5 * self.OUT_SEP_L + 2 * holdrod_r + y_offs
        bolt_pulhigh_pos_y = (  self.length
                             - 2.5 * self.OUT_SEP_L
                             - 2 * holdrod_r  # no _tol
                             + y_offs)

        bolt0.Placement.Base = FreeCAD.Vector (bolt_left_pos_x,
                                               self.length/2 + y_offs,
                                               -self.partheight)
        bolt0.Placement.Rotation = FreeCAD.Rotation (VZ, 90)
        cutlist.append (bolt0)

# Naming convention for the bolts
#      ______________ 
#     |lu|   |   _ru_|       right up
#     |  |   |  |____|
#     |  |   |    rmu|       right middle up
#     |  |   | pu    |  pulley up
#     |0 |   | r     | right
#     |  |   | pd    |  pulley down
#     |  |   |   _rmd|       right middle down
#     |  |   |  |____|
#     |ld|___|____rd_|       right down
#       
        # Right
        boltr = Draft.clone(bolt0)
        boltr.Label = "bolt_hole_r"
        boltr.Placement.Base =  FreeCAD.Vector (-bolt_left_pos_x,
                                                self.length/2 + y_offs,
                                               -self.partheight)
        boltr.Placement.Rotation = FreeCAD.Rotation (VZ, 30)
        cutlist.append (boltr)


        # Left Up
        boltlu = Draft.clone(bolt0)
        boltlu.Label = "bolt_hole_lu"
        boltlu.Placement.Base =  FreeCAD.Vector (bolt_left_pos_x,
                                                bolt_low_pos_y,
                                               -self.partheight)
        boltlu.Placement.Rotation = FreeCAD.Rotation (VZ, 0)
        cutlist.append (boltlu)
        
        # Left Down
        boltld = Draft.clone(bolt0)
        boltld.Label = "bolt_hole_ld"
        boltld.Placement.Base =  FreeCAD.Vector (bolt_left_pos_x,
                                                bolt_high_pos_y,
                                               -self.partheight)
        boltld.Placement.Rotation = FreeCAD.Rotation (VZ, 0)
        cutlist.append (boltld)

        # Right Up 
        boltru = Draft.clone(bolt0)
        boltru.Label = "bolt_hole_ru"
        boltru.Placement.Base =  FreeCAD.Vector (bolt_right_pos_x,
                                                bolt_high_pos_y,
                                               -self.partheight)
        boltru.Placement.Rotation = FreeCAD.Rotation (VZ, 0)
        cutlist.append (boltru)

        # Right Down
        boltrd = Draft.clone(bolt0)
        boltrd.Label = "bolt_hole_rd"
        boltrd.Placement.Base =  FreeCAD.Vector (bolt_right_pos_x,
                                                bolt_low_pos_y,
                                               -self.partheight)
        boltrd.Placement.Rotation = FreeCAD.Rotation (VZ, 0)
        cutlist.append (boltrd)

        # Right Middle Up 
        boltrmu = Draft.clone(bolt0)
        boltrmu.Label = "bolt_hole_rmu"
        boltrmu.Placement.Base =  FreeCAD.Vector (bolt_right_pos_x,
                                                  bolt_highmid_pos_y,
                                                 -self.partheight)
        boltrmu.Placement.Rotation = FreeCAD.Rotation (VZ, 0)
        cutlist.append (boltrmu)

        # Right Middle Down
        boltrmd = Draft.clone(bolt0)
        boltrmd.Label = "bolt_hole_rmd"
        boltrmd.Placement.Base =  FreeCAD.Vector (bolt_right_pos_x,
                                                bolt_lowmid_pos_y,
                                               -self.partheight)
        boltrmd.Placement.Rotation = FreeCAD.Rotation (VZ, 0)
        cutlist.append (boltrmd)

        # Hole for the upper Pulley bolt       
        boltpull0 = addBolt (
                            r_shank   = self.BOLTPUL_SHANK_R_TOL,
                            l_bolt    = 2 * self.partheight,
                            r_head    = self.BOLTPUL_NUT_R_TOL,
                            l_head    = self.BOLTPUL_NUT_L,
                            hex_head  = 1, extra=1,
                            support = 1, 
                            headdown  = 1, name="boltpul_hole")

        boltpull0.Placement.Base =  FreeCAD.Vector (bolt_pull_pos_x,
                                                    bolt_pulhigh_pos_y,
                                                   -self.partheight)
        boltpull0.Placement.Rotation = FreeCAD.Rotation (VZ, 30)
        cutlist.append (boltpull0)

        # idlepull_name_list is a list of the components for building
        # an idle pulley out of washers and bearings
        h_idlepull0 = partgroup.BearWashGroup (
                                   holcyl_list = kcomp.idlepull_name_list,
                                   name = 'idlepull_0',
                                   normal = VZ,
                                   pos = boltpull0.Placement.Base + 
                                         FreeCAD.Vector(0,0,2*self.partheight))
        idlepull0 = h_idlepull0.fco

        # separation between the axis iddle pulleys
        self.idlepull_axsep = bolt_pulhigh_pos_y - bolt_pullow_pos_y
        # separation between the inner part of the iddle pulleys
        # ie: idlepull_axsep - the diameter of the pulley (bearing)
        # -1 is because the belt is 1.38mm thick. So in each side we can
        # substract 0.5 mm
        self.belt_sep = self.idlepull_axsep - h_idlepull0.d_maxbear - 1

        # Hole for Pulley Down
        boltpull1 = Draft.clone(boltpull0)
        boltpull1.Label = "boltpul_hole_1"
        boltpull1.Placement.Base =  FreeCAD.Vector (bolt_pull_pos_x,
                                                    bolt_pullow_pos_y,
                                                   -self.partheight)
        boltpull1.Placement.Rotation = FreeCAD.Rotation (VZ, 30)
        cutlist.append (boltpull1)

        # the other pulley:
        idlepull1 = Draft.clone(idlepull0)
        idlepull1.Label = "idlepull_1"
        idlepull1.Placement.Base.y = bolt_pullow_pos_y - bolt_pulhigh_pos_y

        idlepull_list = [ idlepull0, idlepull1]
        idlepulls = doc.addObject("Part::Compound", "idlepulls")
        idlepulls.Links = idlepull_list

        # --- make a dent in the interior to save plastic
        # points: p dent

        pdent_ur = FreeCAD.Vector ( self.width + slid_posx + 1,
                                    bolt_highmid_pos_y - 1,
                                   -self.partheight - 1)
        pdent_ul = FreeCAD.Vector ( bolt_pull_pos_x + 1,
                                    bolt_pulhigh_pos_y - self.OUT_SEP_L ,
                                   -self.partheight - 1)
        pdent_dr = FreeCAD.Vector ( self.width + slid_posx + 1,
                                    bolt_lowmid_pos_y +1,
                                   -self.partheight - 1)
        pdent_dl = FreeCAD.Vector ( bolt_pull_pos_x + 1,
                                    bolt_pullow_pos_y + self.OUT_SEP_L ,
                                   -self.partheight - 1)

        # dent dimensions
        # the length is actually shorter, because it is 1 mm inside.
        #         
        #        ur  ____ ovdent_l
        #         /|                 h_over= (1/ovdent_w)*(ovdent_l-dent_sl)/2.
        #        /_| ___ dent_l      h_over= triang_h_ov / ovdent_w
        #       /| |    
        #      / | |          dent_l = ovdent_l -2*lm
        #     /  | |          
        # ul /___|_| __ dent_sl
        #    |     |
        #    |     |
        #    |     |
        # dl |_____| __
        #    \   | |
        #     \  | |
        #      \ | |
        #       \|_| ___
        #        \ |
        #         \| ____
        #          dr
        #         1
        #    |---|  dent_w
        #    |-----| ovdent_w 
        #
        # the dimensions of the dent overlaped (ov), to make the shape
        self.ovdent_w = abs(pdent_ur.x - pdent_ul.x) # longer width
        self.dent_w   = self.ovdent_w - 1
        self.ovdent_l = abs(pdent_ur.y - pdent_dr.y) # longer  Length 
        self.dent_sl  = abs(pdent_ul.y - pdent_dl.y) # shorter Length 
        # the height of the overlap triangle
        triang_h_ov = abs(pdent_ur.y - pdent_ul.y)
        self.dent_l = ( self.ovdent_l 
                       - 2*(triang_h_ov / self.ovdent_w)) # h_over

        pdent_list = [ pdent_ur, pdent_ul, pdent_dl, pdent_dr]

        dent_plane = doc.addObject("Part::Polygon", "dent_plane")
        dent_plane.Nodes = pdent_list
        dent_plane.Close = True
        dent_plane.ViewObject.Visibility = False
        dent = doc.addObject("Part::Extrusion", "dent")
        dent.Base = dent_plane
        dent.Dir = (0,0, 2*self.partheight +2)
        dent.Solid = True
        cutlist.append (dent)

        holes = doc.addObject("Part::MultiFuse", "holes")
        holes.Shapes = cutlist


        if side == 'right':
            holes.Placement.Rotation = FreeCAD.Rotation (VZ, 180)
            idlepulls.Placement.Rotation = FreeCAD.Rotation (VZ, 180)
            topslid_fllt.Placement.Rotation = FreeCAD.Rotation (VZ, 180)
            botslid_fllt.Placement.Rotation = FreeCAD.Rotation (VZ, 180)
            # h_lmuu_0.bearing. bearings stay the same
            if holdrod_cen == False:
                holes.Placement.Base = FreeCAD.Vector (0, self.length,0)
                idlepulls.Placement.Base = FreeCAD.Vector (0, self.length,0)
                topslid_fllt.Placement.Base = FreeCAD.Vector (0, self.length,0)
                botslid_fllt.Placement.Base = FreeCAD.Vector (0, self.length,0)
        elif side == 'bottom':
            holes.Placement.Rotation = FreeCAD.Rotation (VZ, 90)
            idlepulls.Placement.Rotation = FreeCAD.Rotation (VZ, 90)
            topslid_fllt.Placement.Rotation = FreeCAD.Rotation (VZ, 90)
            botslid_fllt.Placement.Rotation = FreeCAD.Rotation (VZ, 90)
            h_lmuu_0.bearing.Placement.Rotation =  FreeCAD.Rotation (VZ, 90)
            # lmuu_1 has relative position to lmuu_0, so if rotating it
            # to the other side and reseting its position will put it in its
            # place
            if holdrod_cen == True:
                h_lmuu_1.bearing.Placement.Rotation = FreeCAD.Rotation (VZ, -90)
                h_lmuu_1.bearing.Placement.Base = FreeCAD.Vector (0,0,0)
            if holdrod_cen == False:
                holes.Placement.Base = FreeCAD.Vector (self.length,0,0)
                idlepulls.Placement.Base = FreeCAD.Vector (self.length,0,0)
                topslid_fllt.Placement.Base = FreeCAD.Vector (self.length,0,0)
                botslid_fllt.Placement.Base = FreeCAD.Vector (self.length,0,0)
                h_lmuu_0.bearing.Placement.Base = FreeCAD.Vector (
                                                          self.length,0,0)
                h_lmuu_1.bearing.Placement.Base = FreeCAD.Vector (
                           self.length - h_lmuu_1.bearing.Placement.Base.y ,0,0)
                h_lmuu_1.bearing.Placement.Rotation =  FreeCAD.Rotation (VZ, 90)
        elif side == 'top':
            holes.Placement.Rotation = FreeCAD.Rotation (VZ, -90)
            idlepulls.Placement.Rotation = FreeCAD.Rotation (VZ, -90)
            topslid_fllt.Placement.Rotation = FreeCAD.Rotation (VZ, -90)
            botslid_fllt.Placement.Rotation = FreeCAD.Rotation (VZ, -90)
            h_lmuu_0.bearing.Placement.Rotation =  FreeCAD.Rotation (VZ, -90)
            # lmuu_1 has relative position to lmuu_0, so if rotating it
            # to the other side and reseting its position will put it in its
            # place
            if holdrod_cen == True:
                h_lmuu_1.bearing.Placement.Rotation =  FreeCAD.Rotation (VZ, 90)
                h_lmuu_1.bearing.Placement.Base = FreeCAD.Vector (0,0,0)
            if holdrod_cen == False:
                #holes.Placement.Base = FreeCAD.Vector (self.length,0,0)
                #topslid_fllt.Placement.Base = FreeCAD.Vector (self.length,0,0)
                #botslid_fllt.Placement.Base = FreeCAD.Vector (self.length,0,0)
                #h_lmuu_0.bearing.Placement.Base = FreeCAD.Vector (
                                                          #self.length,0,0)
                h_lmuu_1.bearing.Placement.Base = FreeCAD.Vector (
                                         h_lmuu_1.bearing.Placement.Base.y ,0,0)
                h_lmuu_1.bearing.Placement.Rotation = FreeCAD.Rotation (VZ, -90)


        # elif side == 'left':
            # don't do anything, default condition

        self.idlepulls = idlepulls

        bearings = doc.addObject("Part::Fuse", name + "_bear")
        bearings.Base = h_lmuu_0.bearing
        bearings.Tool = h_lmuu_1.bearing
        self.bearings = bearings

        top_slide = doc.addObject("Part::Cut", name + "_top")
        top_slide.Base = topslid_fllt 
        top_slide.Tool = holes 
        self.top_slide = top_slide

        bot_slide = doc.addObject("Part::Cut", name + "_bot")
        bot_slide.Base = botslid_fllt 
        bot_slide.Tool = holes 
        self.bot_slide = bot_slide

    # ---- end of __init__  EndShaftSlider

    # move both sliders (top & bottom) and the bearings
    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.idlepulls.Placement.Base = FreeCAD.Vector(position)
        self.bearings.Placement.Base = FreeCAD.Vector(position)
        self.top_slide.Placement.Base = FreeCAD.Vector(position)
        self.bot_slide.Placement.Base = FreeCAD.Vector(position)
        


"""

    # Move the bearing and its container
    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.bearing.Placement.Base = FreeCAD.Vector(position)
        self.bearing_cont.Placement.Base = FreeCAD.Vector(position)
"""


# ---------- class CentralSlider ----------------------------------------
# Creates the central slider that moves on the X axis
# The slider runs on 1 or 2 pairs of linear bearings.
# The slider is referenced on its center
# Creates both sides, the upper part and the lower part, it also creates the
# linear bearings
# Arguments:
#     rod_r   : radius of the rods where the slider runs on
#     rod_sep : separation between the rods 
#     belt_sep: separation between the belt
#     dent_w  : width of the dent, if no dent is needed, just dent_w = 0
#     dent_l  : length of the dent, 
#     dent_sl : small dimension of the dent length
#
#           Y   
#           |
#      _____|_____     ______________________           
#     |  _______  |
#     |_|       |_| -------------
#     |_         _|
#     | |_______| |
#     |           | ---------
#     |           |
#     |           |----X
#     |           |
#     |  _______  | --------- belt_sep
#     |_|       |_|
#     |_         _|
#     | |_______| | ------------- rod_sep
#     |___________|__________________________ length
#
#     |__ width __|

#               Y   
#               |
#          _____|_____     ______________________           
#         |  _______  |
#         |_|       |_| -------------
#         |_         _|
#         | |_______| |  __________________
#        /             \
#       /               \   __________
#      |                 |
#      |                 |
#      |                 |  __________ dent_sl
#       \               /
#        \   _______   /___________________ dent_l
#         |_|       |_|
#         |_         _|
#         | |_______| | ------------- rod_sep
#         |___________|__________________________ length
#      |--|dent_w

      #
        #          ___ ovdent_l
        #        /|\
        #       /_|_\   __ dent_l
        #      /| | |\
        #     / | | | \           dent_l = (dent_w/ovdent_w)*ovdent_l
        #    /  | | |  \
        #   /___|_|_|___\
        #          1

# --- Atributes:
# length : length of the slider, direction perpendicular to the slidding axis.
#          on Y direction
# width  : width of the slider, on the direction of the slidding
#          axis (X) 
# partheight : heigth of each part of the slider. So the total height will be
#              twice this height
# rod_sep : separation between the 2 rods that are holded and forms the 
#               perpendicular axis movement
# belt_sep: separation between the belt
# dent_w  : width of the dent, if no dent is needed, just dent_w = 0
# dent_l  : length of the dent, 
# dent_sl : small dimension of the dent length
# dent_sl : small dimension of the dent length
# ovdent_w  : width of the dent including 1 mm of overlap
# ovdent_l  : length of the dent including the overlap 

# totwidth: the width including the dent
# parts : list of FreeCad objects that the slider contains
# idlepulls : FreeCad object of the idle pulleys
# bearings : FreeCad object of the bearings
# top_slide : FreeCad object of the top part of the slider
# bot_slide : FreeCad object of the bottm part of the slider
# base_place: position of the 3 elements: All of them have the same base
#             position.
#             It is (0,0,0) when initialized, it has to be changed using the
#             function BasePlace

class CentralSlider (object):

    # Separation from the end of the linear bearing to the end of the piece
    # on the Heigth dimension (Z)
    OUT_SEP_H = 2.0  # smaller to test 3.0

    # Minimum separation between the bearings, on the slide direction
    MIN_BEAR_SEP = 2.0  # smaller to test 3.0

    # Radius to fillet the sides
    FILLT_R = 3.0 # larger to 2.0

    # Space for the sliding rod, to be added to its radius, and to be cut
    ROD_SPACE = 1.5

    # tolerance on their length for the bearings. Larger because the holes
    # usually are too tight and it doesn't matter how large is the hole
    #TOL_BEARING_L = 2.0 # printed in black and was too loose
    TOL_BEARING_L = 1.0 # reduced, good

    MTOL = TOL - 0.1 # reducing the tolrances, it was too tolerant :)
    MLTOL = TOL - 0.05 # reducing the tolrances, it was too tolerant :)

    # Bolts to hold the top and bottom parts:
    BOLT_D = 4
    BOLT_HEAD_R = kcomp.D912_HEAD_D[BOLT_D] / 2.0
    BOLT_HEAD_L = kcomp.D912_HEAD_L[BOLT_D] + MTOL
    BOLT_HEAD_R_TOL = BOLT_HEAD_R + MTOL/2.0 
    BOLT_SHANK_R_TOL = BOLT_D / 2.0 + MTOL/2.0
    BOLT_NUT_R = kcomp.NUT_D934_D[BOLT_D] / 2.0
    BOLT_NUT_L = kcomp.NUT_D934_L[BOLT_D] + MTOL
    #  1.5 TOL because diameter values are minimum, so they may be larger
    BOLT_NUT_R_TOL = BOLT_NUT_R + 1.5*MTOL

    def __init__ (self, rod_r, rod_sep, name, belt_sep,
                  dent_w, dent_l, dent_sl):

        doc = FreeCAD.ActiveDocument
        self.base_place = (0,0,0)
        self.rod_r      = rod_r
        self.rod_sep    = rod_sep
        self.name       = name
        self.belt_sep   = belt_sep
        self.dent_w     = dent_w
        if dent_w == 0:
            self.dent_l     = 0
            self.dent_sl    = 0
            self.ovdent_w   = 0
            self.ovdent_l   = 0
        else:
            self.dent_l     = dent_l
            self.dent_sl    = dent_sl
            self.ovdent_w   = dent_w + 1
            ovdent_w        = self.ovdent_w

        bearing_l     = kcomp.LMEUU_L[int(2*rod_r)] 
        bearing_l_tol = bearing_l + self.TOL_BEARING_L
        bearing_d     = kcomp.LMEUU_D[int(2*rod_r)]
        bearing_d_tol = bearing_d + 2.0 * self.MLTOL
        bearing_r     = bearing_d / 2.0
        bearing_r_tol = bearing_r + self.MLTOL
        #
        #    |  _____  |
        #    |_|     |_|
        #    |_       _|
        #    | |_____| | ___
        #    |_________| ___ OUT_SEP_MOVPP: separation perpendicular to movement
        #      
        #    | |-----| bearing_l (+ MLTOL)
        #    |-| OUT_SEP_MOV : separacion on the direction of the movement
        #    |---------| length
        #   
        # separation from the end of the linear bearing to the end
        self.OUT_SEP_MOV = 4.0
        if self.BOLT_D == 3:
            self.OUT_SEP_MOVPP = 10.0
        elif self.BOLT_D == 4:
            self.OUT_SEP_MOVPP = 10.0
        else:
            print "Bolt Size not defined in CentralSlider"


        self.length = rod_sep + 2 * bearing_r + 2 * self.OUT_SEP_MOVPP
        self.width  = bearing_l + 2 * self.OUT_SEP_MOV
        self.partheight  = bearing_r + self.OUT_SEP_H
        self.totwidth  = self.width + 2*self.dent_w

        slid_x = self.width
        slid_y = self.length
        slid_z = self.partheight

        topcenslid_box = fcfun.addBox_cen (slid_x, slid_y, slid_z,
                                  "topcenslid_box",
                                  cx=True, cy=True, cz= False)
        #logger.debug('topcenslid_box %s ' % str(topcenslid_box.Shape))
        botcenslid_box = fcfun.addBox_cen (slid_x, slid_y, slid_z,
                                 "botcenslid_box",
                                  cx=True, cy=True, cz= False)
        botcenslid_box.Placement.Base = FreeCAD.Vector(0, 0, -self.partheight)

        # fillet
        topcenslid_fllt = fillet_len (box = topcenslid_box,
                                      e_len = slid_z,
                                      radius = self.FILLT_R,
                                      name = "topcenslid_fllt")
        botcenslid_fllt = fillet_len (botcenslid_box, slid_z, self.FILLT_R,
                                     "botcenslid_fllt")

        # list of elements to cut:
        cutlist = []
        # List to add to the bottom slider
        addbotlist = []
        # ----------------------------- outward dent
        #               t                         y
        #           tl ___ tr  (top right)        |_ x
        #         lt  /   \  rt (right top)
        #       lb   |     | rb (right bottom) r
        #             \   /
        #        bl    --- br  (bottom right)

        # we have dent_l, dent_w and ovdent_w (dent_w + 1)
        #         
        #     tr  ____ ovdent_l
        #    |\                 h_over = triang_h/dent_w
        #    | \  _  ___ dent_l
        #    | |\                triang_h
        #    | | \                    
        #    | |  \ rt    
        # ul |_|___\ __ dent_sl
        #    |     |
        #    |     |
        #    |     |
        # dl |_____| __
        #    | |   / rb
        #    | |  / 
        #    | | /  
        #    | |/    ___
        #    | /    
        #    |/      ____
        #     br
        #     1
        #      |---|  dent_w
        #    |-----| ovdent_w 
        #
        # the dimensions of the dent overlaped (ov), to make the shape
        # height of the triangle (no overlaped)
        if dent_w != 0:
            triang_h = (dent_l - dent_sl) / 2.
            h_over = triang_h / dent_w
            ovdent_l = dent_l + 2 * h_over
            self.ovdent_l = ovdent_l

            # slid_x-1 because the dent was calculated with 1mm of superposition
            # points:
            #p_dent_t  = FreeCAD.Vector(  0            , dent_l/2.0, 0)
            p_dent_tr = FreeCAD.Vector(  slid_x/2. -1 , ovdent_l/2., 0)
            p_dent_rt = FreeCAD.Vector(  slid_x/2. + dent_w , dent_sl/2., 0)
            #p_dent_r  = FreeCAD.Vector(  slid_x/2. -1 + dent_w , 0          , 0)
            dentwire = fcfun.wire_sim_xy([p_dent_tr, p_dent_rt])
            dentface = Part.Face(dentwire)
            shp_topdent = dentface.extrude(FreeCAD.Vector(0,0, slid_z))
            shp_botdent = dentface.extrude(FreeCAD.Vector(0,0,-slid_z))
            topdent = doc.addObject("Part::Feature", "topcenslidedent")
            topdent.Shape = shp_topdent
            botdent = doc.addObject("Part::Feature", "botcenslidedent")
            botdent.Shape = shp_botdent

            topcenslid_dent = doc.addObject("Part::Fuse","topcenslid_dent")
            topcenslid_dent.Base = topcenslid_fllt
            topcenslid_dent.Tool = topdent

            botcenslid_dent = doc.addObject("Part::Fuse","botcenslid_dent")
            botcenslid_dent.Base = botcenslid_fllt
            botcenslid_dent.Tool = botdent
        
            addbotlist.append (botcenslid_dent)

        # --------------------- Hole for the rods ---------------
        toprod = fcfun.addCyl_pos ( r = rod_r + self.ROD_SPACE,
                                    h = slid_x +2,
                                    name = "toprod",
                                    axis = 'x',
                                    h_disp = -slid_x/2.0 - 1)
        toprod.Placement.Base.y = rod_sep /2.0
        cutlist.append (toprod)

        botrod = fcfun.addCyl_pos ( r = rod_r + self.ROD_SPACE,
                                    h = slid_x +2,
                                    name = "botrod",
                                    axis = 'x',
                                    h_disp = -slid_x/2.0 - 1)
        botrod.Placement.Base.y = -rod_sep /2.0
        cutlist.append (botrod)

        # --------------------- Fixed belt clamps (fbcl)
        # the width of the belt_clamp (on the X axis):
        fbcl_w = beltcl.Gt2BeltClamp.CB_IW + 2*beltcl.Gt2BeltClamp.CB_W 
        # the length of the belt_clamp (on the Y axis):
        fbcl_l = beltcl.Gt2BeltClamp.CBASE_L
    
        # top (positive Y)
        # Y position:
        fbclt_pos_y = ( self.belt_sep /2.0 -1 )
        # X position will be on the intersection of the border of the slider
        # with the Y position (fbclt_po_y)
        # There are 3 parts:
        # above the dent: fbclt_pos_y > dent_l/2. 
        # on the dent: dent_l/2. > fbclt_pos_y > dent_sl/.2
        # below the dent: fbclt_pos_y < dent_sl/.2
        # the position is related to the center of the belt clamp. So we
        # have to substract fbcl_w/2.
        if fbclt_pos_y >= dent_l/2. :
            fbclt_pos_x = slid_x/2. - fbcl_w/2. 
        elif fbclt_pos_y <= dent_sl/2. :
            fbclt_pos_x = self.totwidth/2. - fbcl_w/2. 
        else:
            # calculate the intersection of the line with the fbclt_pos_y:
            #a triangle calculation: b/h = B/H
            h = fbclt_pos_y - dent_sl/2.
            b = h * (dent_w/triang_h)
            fbclt_pos_x =  self.totwidth/2. - fbcl_w/2. - b
        fbclt_pos = FreeCAD.Vector(fbclt_pos_x,
                                   fbclt_pos_y,
                                   self.partheight )
        #fco_fbclt = beltcl.fco_topbeltclamp (railaxis = '-y', bot_norm = '-z',
        #                 pos = fbclt_pos, extra = 1, name = "fbclt")
        shp_fbclt = beltcl.shp_topbeltclamp (railaxis = '-y', bot_norm = '-z',
                         pos = fbclt_pos, extra = 1)

        fbcl_xmin = fbclt_pos_x - fbcl_w/2. 

        fbcl_xmax = self.totwidth/2. + 1

        fbcl_ymax = dent_l / 2.
        fbcl_ymin = fbclt_pos_y - beltcl.Gt2BeltClamp.CBASE_L 

        doc.recompute()

        # base to add to the lower slider:
        bs_fbclt_p0 = FreeCAD.Vector (fbcl_xmin, fbcl_ymin, -1)
        bs_fbclt_p1 = FreeCAD.Vector (fbcl_xmax, fbcl_ymin, -1)
        bs_fbclt_p2 = FreeCAD.Vector (fbcl_xmax, fbcl_ymax, -1)
        bs_fbclt_p3 = FreeCAD.Vector (fbcl_xmin, fbcl_ymax, -1)
        bs_fbclt_wire = Part.makePolygon([bs_fbclt_p0,bs_fbclt_p1,
                                          bs_fbclt_p2,bs_fbclt_p3,
                                          bs_fbclt_p0])
        bs_fbclt_face = Part.Face(bs_fbclt_wire)
        shp_bs_fbclt_box = bs_fbclt_face.extrude(
                                     FreeCAD.Vector(0,0,self.partheight+1))
        shp_bs_fbclt = shp_bs_fbclt_box.common(topcenslid_dent.Shape)
        #all: base with the beltclt
        shp_afbclt = shp_bs_fbclt.fuse(shp_fbclt)
        afbclt = doc.addObject("Part::Feature", "fbclt")
        afbclt.Shape = shp_afbclt
        addbotlist.append (afbclt)
        afbclt.Placement.Base.z = -0.1

        # base to cut to the lower slider:
        cbs_fbclt_p0 = FreeCAD.Vector (fbcl_xmin -kcomp.TOL,
                                       fbcl_ymin -kcomp.TOL, -1)
        cbs_fbclt_p1 = FreeCAD.Vector (fbcl_xmax,
                                       fbcl_ymin -kcomp.TOL, -1)
        cbs_fbclt_p2 = FreeCAD.Vector (fbcl_xmax,
                                       fbcl_ymax +kcomp.TOL, -1)
        cbs_fbclt_p3 = FreeCAD.Vector (fbcl_xmin -kcomp.TOL,
                                       fbcl_ymax +kcomp.TOL, -1)
        cbs_fbclt_wire = Part.makePolygon([cbs_fbclt_p0,cbs_fbclt_p1,
                                          cbs_fbclt_p2,cbs_fbclt_p3,
                                          cbs_fbclt_p0])
        cbs_fbclt_face = Part.Face(cbs_fbclt_wire)
        shp_cbs_fbclt = cbs_fbclt_face.extrude(
                                     FreeCAD.Vector(0,0,self.partheight+2))
        cbs_fbclt = doc.addObject("Part::Feature", "cbs_cfbclt")
        cbs_fbclt.Shape = shp_cbs_fbclt

        cuttoplist = []
        cuttoplist.append (cbs_fbclt)

        # bottom belt clamp
        fbclb_pos = FreeCAD.Vector( fbclt_pos_x,
                                   -fbclt_pos_y,
                                   self.partheight )
        shp_fbclb = beltcl.shp_topbeltclamp (railaxis = 'y', bot_norm = '-z',
                         pos = fbclb_pos, extra = 1)

        # base to add to the lower slider:
        bs_fbclb_p0 = FreeCAD.Vector (fbcl_xmin,-fbcl_ymin, -1)
        bs_fbclb_p1 = FreeCAD.Vector (fbcl_xmax,-fbcl_ymin, -1)
        bs_fbclb_p2 = FreeCAD.Vector (fbcl_xmax,-fbcl_ymax, -1)
        bs_fbclb_p3 = FreeCAD.Vector (fbcl_xmin,-fbcl_ymax, -1)
        bs_fbclb_wire = Part.makePolygon([bs_fbclb_p0,bs_fbclb_p1,
                                          bs_fbclb_p2,bs_fbclb_p3,
                                          bs_fbclb_p0])
        bs_fbclb_face = Part.Face(bs_fbclb_wire)
        shp_bs_fbclb_box = bs_fbclb_face.extrude(
                                     FreeCAD.Vector(0,0,self.partheight+1))
        shp_bs_fbclb = shp_bs_fbclb_box.common(topcenslid_dent.Shape)
        #all: base with the beltclt
        shp_afbclb = shp_bs_fbclb.fuse(shp_fbclb)
        afbclb = doc.addObject("Part::Feature", "fbclb")
        afbclb.Shape = shp_afbclb
        addbotlist.append (afbclb)
        afbclb.Placement.Base.z = -0.2
        doc.recompute()

        # base to cut to the lower slider:
        cbs_fbclb_p0 = FreeCAD.Vector (fbcl_xmin -kcomp.TOL,
                                       -(fbcl_ymin -kcomp.TOL), -1)
        cbs_fbclb_p1 = FreeCAD.Vector (fbcl_xmax,
                                       -(fbcl_ymin -kcomp.TOL), -1)
        cbs_fbclb_p2 = FreeCAD.Vector (fbcl_xmax,
                                       -(fbcl_ymax +kcomp.TOL), -1)
        cbs_fbclb_p3 = FreeCAD.Vector (fbcl_xmin -kcomp.TOL,
                                       -(fbcl_ymax +kcomp.TOL), -1)
        cbs_fbclb_wire = Part.makePolygon([cbs_fbclb_p0,cbs_fbclb_p1,
                                          cbs_fbclb_p2,cbs_fbclb_p3,
                                          cbs_fbclb_p0])
        cbs_fbclb_face = Part.Face(cbs_fbclb_wire)
        shp_cbs_fbclb = cbs_fbclb_face.extrude(
                                     FreeCAD.Vector(0,0,self.partheight+2))
        cbs_fbclb = doc.addObject("Part::Feature", "cbs_cfbclb")
        cbs_fbclb.Shape = shp_cbs_fbclb

        cuttoplist.append (cbs_fbclb)

        doc.recompute()

        parts_list = []
        # --------------------- Idle Pulley
        # idlepull_name_list is a list of the components for building
        # an idle pulley out of washers and bearings
        # we dont have enough information for the position yet
#        h_csidlepull0 = partgroup.BearWashGroup (
#                                   holcyl_list = kcomp.idlepull_name_list,
#                                   name = 'csidlepull_0',
#                                   normal = VZ,
#                                   pos = FreeCAD.Vector(0,0,self.partheight))
#        csidlepull0 = h_csidlepull0.fco
#        # 0.5 is for the thickness of the belt
#        bolt_pull_pos_y = self.belt_sep /2.0 - h_csidlepull0.r_maxbear -0.5 
#        csidlepull0.Placement.Base = FreeCAD.Vector(
#                                                  -slid_x/2.,
#                                                   bolt_pull_pos_y,
#                                                   0)
#        csidlepull1 = Draft.clone(csidlepull0)
#        csidlepull1.Label = "cisidlepull_1"
#        csidlepull1.Placement.Base = FreeCAD.Vector(
#                                                   slid_x/2.,
#                                                   bolt_pull_pos_y,
#                                                   0)
#
#        csidlepull_list = [ csidlepull0, csidlepull1]
#        csidlepulls = doc.addObject("Part::Compound", "csidlepulls")
#        csidlepulls.Links = csidlepull_list
#
#        # list of parts of the central slider, any part that is a FreeCad
#        # Object
#        parts_list.append (csidlepulls)
#
#        # Hole for the Idle Pulley bolt       
#        csboltpull0 = addBolt (
#                            r_shank   = EndShaftSlider.BOLTPUL_SHANK_R_TOL,
#                            l_bolt    = 2 * self.partheight,
#                            r_head    = EndShaftSlider.BOLTPUL_NUT_R_TOL,
#                            l_head    = EndShaftSlider.BOLTPUL_NUT_L,
#                            hex_head  = 1, extra=1,
#                            support = 1, 
#                            headdown  = 1, name="csboltpul_hole")
#
#        csboltpull0.Placement.Base =  FreeCAD.Vector (
#                                                   slid_x/2.,
#                                                   bolt_pull_pos_y,
#                                                   -self.partheight)
#        csboltpull0.Placement.Rotation = FreeCAD.Rotation (VZ, 30)
#
#        cutlist.append (csboltpull0)
#        # the other Idle Pulley bolt hole
#        csboltpull1 = Draft.clone(csboltpull0)
#        csboltpull1.Label = "csboltpul_hole_1"
#        csboltpull1.Placement.Base =  FreeCAD.Vector (
#                                                   -slid_x/2.,
#                                                   bolt_pull_pos_y,
#                                                   -self.partheight)
#        csboltpull1.Placement.Rotation = FreeCAD.Rotation (VZ, 30)
#        cutlist.append (csboltpull1)
#
#

        # --------------------- Linear Bearings -------------------
        h_lmuu_0 = comps.LinBearing (
                         r_ext = bearing_r,
                         r_int = rod_r,
                         h     = bearing_l,
                         name  = "cen_lm" + str(int(2*rod_r)) + "uu_0",
                         axis  = 'x',
                         h_disp = - bearing_l/2.0,
                         r_tol  = self.MLTOL,
                         h_tol  = self.TOL_BEARING_L)
        h_lmuu_0.BasePlace ((0, rod_sep / 2.0, 0))
        cutlist.append (h_lmuu_0.bearing_cont)

        h_lmuu_1 = comps.LinBearingClone (
                                      h_lmuu_0,
                                      "cen_lm" + str(int(2*rod_r)) + "uu_1",
                                      namadd = 0)
        h_lmuu_1.BasePlace ((0, - rod_sep / 2.0, 0))
        cutlist.append (h_lmuu_1.bearing_cont)

        # ---------- Belt tensioner

        h_bclten0 =  beltcl.Gt2BeltClamp (base_h = slid_z,
                                            midblock =0, name="bclten0")
        bclten0 = h_bclten0.fco   # the FreeCad Object
        parts_list.append(bclten0)
        bclten0_cont = h_bclten0.fco_cont   # the container
        # It is not centered. being one corner in (0,0,0)
        # the width is h_gt2clamp0.CBASE_W + 2 * h_gt2clamp0.extind
        #    _________
        #    |         |
        #   /           \ 
        #  |             |
        #   \           /
        #    |_________|
        #
        #  |_ 0 is here: I have to change it to be centered, and able to 
        #                rotate
      
        beltclamp_w = h_bclten0.CBASE_W + 2 * h_bclten0.extind
        #h_bclten0.BasePlace ((    -(self.width/2. +self.dent_w) 
        #                            + h_bclten0.CBASE_L ,

        h_bc_nuthole0 = NutHole (nut_r  = kcomp.M3_NUT_R_TOL,
                           nut_h  = kcomp.M3NUT_HOLE_H,
                           # + TOL to have a little bit more room for the nut
                           hole_h = slid_z/2. + TOL, 
                           name   = "bccr_nuthole0",
                           extra  = 1,
                           # the height of the nut on the X axis
                           nuthole_x = 1,
                           cx = 0, # not centered on x
                           cy = 1, # centered on y, on the center of the hexagon
                           holedown = 0)

        # fbcl_xmin is the x where the other clamp starts
        # the x min, of the nut hole
        bc_nuthole_x = (  fbcl_xmin
                        - h_bclten0.NUT_HOLE_EDGSEP
                        - h_bc_nuthole0.nut_h)
        # the end of the carriage
        bc_car_xend = bc_nuthole_x - h_bclten0.NUT_HOLE_EDGSEP

        bc_nuthole0 = h_bc_nuthole0.fco # the FreeCad Object
        bc_nuthole0.Placement.Base = FreeCAD.Vector(
                                             bc_nuthole_x,
                                             fbclt_pos_y,
                                             slid_z/2.)
        h_bclten0.BasePlace ((    bc_car_xend,
                                  fbclt_pos_y+ beltclamp_w/ 2.,
                                  0))
        bclten0.Placement.Rotation = FreeCAD.Rotation(VZ,180)
        bclten0_cont.Placement.Rotation = FreeCAD.Rotation(VZ,180)
        bclten0_cont_l =    bc_car_xend + self.width/2. +self.dent_w 
        bclten0_cont.Dir = (  bclten0_cont_l, 0,0)
        beltholes_l = []
        beltholes_l.append(bc_nuthole0)
        beltholes_l.append(bclten0_cont)

        # hole for the leadscrew of the belt clamp
        bcl_leads_h = ( self.width/2. + self.dent_w - bc_car_xend + 1)
        bcl_leads0 = fcfun.addCylPos (
                             r=kcomp.M3_SHANK_R_TOL,
                             h= bcl_leads_h,
                             name = "bcl_leads0",
                             normal = VX,
                             pos = FreeCAD.Vector (bc_car_xend-1,
                                                   fbclt_pos_y,
                                                   slid_z/2.))
        beltholes_l.append(bcl_leads0)
        # add a hole to see below
        shp_box_pos = FreeCAD.Vector (-slid_x/2., fbclt_pos_y, -slid_z-1)
        shp_boxb = fcfun.shp_boxcenfill( x= slid_x/2.+bc_car_xend -2,
                                         y= kcomp.M3_2APOT_TOL,
                                         z= slid_z + 2,
                                         fillrad = 2,
                                         fx=0, fy=0, fz=1,
                                         cx=0, cy=1, cz=0,
                                           pos = shp_box_pos)

        boxb = doc.addObject("Part::Feature", "boxb0")
        boxb.Shape = shp_boxb
        beltholes_l.append(boxb)

        beltholes_t = doc.addObject("Part::MultiFuse", "beltholes_t")
        beltholes_t.Shapes = beltholes_l
        doc.recompute()

        bclten1 = Draft.clone(bclten0)
        bclten1.Label = 'bclten1'
        bclten1.Placement.Base.x = 0 # just to move it a little bit
        bclten1.Placement.Base.y = - fbclt_pos_y + beltclamp_w/ 2.
        parts_list.append(bclten1)

        beltholes_b = Draft.clone(beltholes_t)
        beltholes_b.Label = 'beltholes_b'
        beltholes_b.Placement.Base.y = - 2* fbclt_pos_y

        doc.recompute()
        cutlist.append (beltholes_t)
        cutlist.append (beltholes_b)


        # --------------------- Motor -------------------
        h_nema14 = comps.NemaMotor(size=14, length=26.0, shaft_l=24.,
               circle_r = 0, circle_h=2.,
               name="nema14_my5602", chmf=2., rshaft_l = 0,
               bolt_depth = 3.5, bolt_out = 2 + self.partheight/2.,
               normal= FreeCAD.Vector(0,0,1),
               #pos = FreeCAD.Vector(0,0,-self.partheight))
               pos = FreeCAD.Vector(0,0,self.partheight/2.))

        parts_list.append (h_nema14.fco)
        shp_contnema14 = h_nema14.shp_cont  # this is a shape, not a fco

        h_nema17 = comps.NemaMotor(size=17, length=33.5, shaft_l=24.,
               circle_r = 12., circle_h=2.,
               name="nema17_ST4209S1006B", chmf=2., rshaft_l = 10.,
               bolt_depth = 4.5, bolt_out = 2 + self.partheight/2.,
               normal= FreeCAD.Vector(0,0,1),
               #pos = FreeCAD.Vector(0,0,-self.partheight))
               pos = FreeCAD.Vector(0,0,self.partheight/2.))

        parts_list.append (h_nema17.fco)
        shp_contnema17 = h_nema17.shp_cont  # this is a shape, not a fco
        shp_contmotors = shp_contnema17.fuse(shp_contnema14)

        contmotors = doc.addObject("Part::Feature", "contmotors")
        contmotors.Shape = shp_contmotors
        cutlist.append (contmotors)

        # ------ the small motor Nanotec STF2818X0504-A -- just the bolt holes
        mtol = kcomp.TOL - 0.1
        nanostf28_boltsep = 34.1
        bhole_motorstf0 = addBolt (
            r_shank =  1.5  + mtol/2., # nemabolt_d/2. + mtol/2.,
            l_bolt = 2 + self.partheight/2.,
            r_head = kcomp.D912_HEAD_D[3]/2. + mtol/2.,
            l_head = kcomp.D912_HEAD_L[3] + mtol,
            hex_head = 0, extra =1, support=1, headdown = 0,
            name ="bhole_notorstf0")

        bhole_motorstf1 = Draft.clone(bhole_motorstf0)
        bhole_motorstf1.Label = "bhole_notorstf1"

        bhole_motorstf0.Placement.Base = FreeCAD.Vector(
                                                -nanostf28_boltsep/2.,
                                                 0,
                                                 self.partheight/2.)
        bhole_motorstf1.Placement.Base = FreeCAD.Vector(
                                                 nanostf28_boltsep/2.,
                                                 0,
                                                 self.partheight/2.)
        bholes_motorstf = doc.addObject("Part::Fuse", "bholes_motorstf")
        bholes_motorstf.Base = bhole_motorstf0
        bholes_motorstf.Tool = bhole_motorstf1

        cutlist.append (bholes_motorstf)

        # ----------- final fusion of holes
        holes = doc.addObject("Part::MultiFuse", "censlid_holes")
        holes.Shapes = cutlist

        holes_top = doc.addObject("Part::MultiFuse", "censlid_tophles")
        holes_top.Shapes = cutlist + cuttoplist

        self.parts = parts_list

        doc.recompute()

        # bearings fusion:
        bearings = doc.addObject("Part::Fuse", name + "_bear")
        bearings.Base = h_lmuu_0.bearing
        bearings.Tool = h_lmuu_1.bearing
        self.bearings = bearings

        # ----- adding the belt clamps:
        botcenslid_cl = doc.addObject("Part::MultiFuse", name + "_bot_cl")
        botcenslid_cl.Shapes = addbotlist

        doc.recompute()
        # ----------- final cut
        topcenslid = doc.addObject("Part::Cut", name + "_top")
        topcenslid.Base = topcenslid_dent
        topcenslid.Tool = holes_top
        self.top_slide = topcenslid

        botcenslid = doc.addObject("Part::Cut", name + "_bot")
        botcenslid.Base = botcenslid_cl
        botcenslid.Tool = holes

        doc.recompute()
        #botcenslid.Shape = botcenslid.Shape.removeSplitter()

        self.bot_slide = botcenslid

        doc.recompute()


    # move both sliders (top & bottom) and the bearings
    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        for part in self.parts:
            part.Placement.Base = FreeCAD.Vector(position)
        self.bearings.Placement.Base = FreeCAD.Vector(position)
        self.top_slide.Placement.Base = FreeCAD.Vector(position)
        self.bot_slide.Placement.Base = FreeCAD.Vector(position)
        

doc = FreeCAD.newDocument()
#CentralSlider (rod_r = kcit.ROD_R, rod_sep = 150.0, name="central_slider")
cs = CentralSlider (rod_r = 6, rod_sep = 150.0, name="central_slider",
                    belt_sep = 100,  # check value
                    dent_w = 18,
                    dent_l = 122,
                    dent_sl = 68)
