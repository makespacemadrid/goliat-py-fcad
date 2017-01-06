# ----------------------------------------------------------------------------
# -- Goliat 3D printer and mill
# -- Python scripts for FreeCAD. Copied from Enrique Vaquero's Oscad version
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- (c) Enrique Vaquero
# -- MakeSpace Madrid. http://makespacemadrid.org/
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

# to execute from the FreeCAD console:
#  execute freecad from the cmd console on the directory
# "C:\Program Files\FreeCAD 0.16\bin\freecad" goliat.py

# to excute from command line in windows:
# "C:\Program Files\FreeCAD 0.16\bin\freecadcmd" goliat.py

# name of the file
filename = "goliat"

import os
import sys
import FreeCAD;
import FreeCADGui;
import Part;
import Draft;
import logging  # to avoid using print statements
#import copy;
#import Mesh;


# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()

# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
# Either one of these 2 to select the path, inside the tree, copied by
# git subtree, or in its one place
sys.path.append(filepath + '/' + 'modules/comps')
#sys.path.append(filepath + '/' + '../comps')

# where the freecad document is going to be saved
savepath = filepath + "/"
#savepath = filepath + "/../../freecad/goliat/py/"

import fcfun   # import my functions for freecad. FreeCad Functions
import kcomp   # import material constants and other constants
import comps   # import my CAD components

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL

# Taking the same axis as the 3D printer:
#
#    Z   Y
#    | /               USING THIS ONE
#    |/___ X
#
# In this design, the base will be centered on X

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

doc = FreeCAD.newDocument()

Gui.ActiveDocument = Gui.getDocument(doc.Label)
guidoc = Gui.getDocument(doc.Label)

# real scale is 1. but you may want to have it to a different scale
SCALE = 1 

#   FRAME:
#             ___________
#            /          /|
#           /          / |
#          /          /  |
#         /          /  /|
#        /_________ /  / |
#       |          |  /  |
#       |          | /
#       |__________|/
#       |          |
#
##   moveable GANTRY (symbols '=' and 'H')
#             ___________
#            /          /|
#           /==========/ |   Top:  '=' are 30x30
#          /          /H |   Side: 'H' are 50x50
#         /==========/ H/|
#        /_________ /H / |
#       |          | H/  |
#       |          | /
#       |__________|/
#       |          |

#


# Rectangular Rounded bar dimensions for the frame:
FRAM_RBAR_W = 40. * SCALE # Width, the section is a square

# the bars of the moveable gantry have different dimensions. 
# Rectangular Rounded bar dimensions for the moving part (on the X axis):
TOPGTRY_RBAR_W = 30. * SCALE # Base
SIDEGTRY_RBAR_W = 50. * SCALE # Height

RBAR_R = 4. * SCALE # Radius of the corners (it is rounded)
RBAR_T = 2. * SCALE # inside thickness of the bar. The bar is hollow

# Dimensions of the frame
FRAME_H = 1000. * SCALE
FRAME_L = 1580. * SCALE
FRAME_W = 1580. * SCALE

# Height of the horizontal bottom (lower) frame bars
# Distance to the center of the bar (added FRAM_RBAR_W/2.)
HB_FRAME_H = (196. + FRAM_RBAR_W/2.) * SCALE

# RODS on the Y axis
RODY_R = 10. * SCALE # Radius

# Height of the bottom (lower) rods on the Y axis
# CHECK: didn't measure. I just added SIDEGTRY_RBAR_W, but should be a number
B_RODY_H = HB_FRAME_H + SIDEGTRY_RBAR_W + 20*SCALE 
# Height of the top (higher) rods on the Y axis
T_RODY_H = B_RODY_H + 620. * SCALE - 2*RODY_R

# Length of the gantry. ie. length of the gantry on the y axis
# including the width of the bars
GANTRY_L = 400. * SCALE

# Lead screw Plate
LSPLATE_B = 140. * SCALE # base
LSPLATE_H = 130. * SCALE # height
LSPLATE_T =  20. * SCALE # thickness 
LSPLATE_R =  10. * SCALE # Radius of the corners (it is rounded)


# list of the frame components
frame_list = []

# --------------- Vertical Frame Bars  ---------------------------
# os: translate([-77, -77, 0]) rounded_square(4, 4, 100, 1); /oscad command
h_framez_00 = comps.RectRndBar (Base = FRAM_RBAR_W, Height = FRAM_RBAR_W,
                                Length = FRAME_H, Radius = RBAR_R, 
                                Thick = RBAR_T, inrad_same = False,
                                axis= 'z', baseaxis = 'x',
                                name = "framez_00",
                                cx = True, cy= True, cz=False)

framez_00 = h_framez_00.fco # the FreeCad Object
frame_list.append (framez_00)
frame_posx = FRAME_W/2 - FRAM_RBAR_W/2.
print "frame_pos_x "  + str(frame_posx) +  ' has to be 770'
frame_posy = FRAME_L/2 - FRAM_RBAR_W/2.

framez_00.Placement.Base = FreeCAD.Vector(-frame_posx, -frame_posy, 0)

# os: translate([77, -77, 0]) rounded_square(4, 4, 100, 1);
framez_10 = Draft.clone(framez_00)
framez_10.Label = 'framez_10'
framez_10.Placement.Base = FreeCAD.Vector(frame_posx, -frame_posy, 0)
frame_list.append (framez_10)

# os: translate([-77, 77, 0]) rounded_square(4, 4, 100, 1);
framez_01 = Draft.clone(framez_00)
framez_01.Label = 'framez_01'
framez_01.Placement.Base = FreeCAD.Vector(-frame_posx, frame_posy, 0)
frame_list.append (framez_01)

# os: translate([77, 77, 0]) rounded_square(4, 4, 100, 1);
framez_11 = Draft.clone(framez_00)
framez_11.Label = 'framez_11'
framez_11.Placement.Base = FreeCAD.Vector(frame_posx, frame_posy, 0)
frame_list.append (framez_11)


# --------------- Horizontal Frame Bars  ---------------------------
# Y lower Bar 
# os: translate([-77, 75, 10]) rotate([90, 0, 0]) rounded_square(4, 4, 150, 1);
# smaller length, take away the vertical bars thickness
framey_l = FRAME_L - 2*FRAM_RBAR_W
print "framey_l "  + str(framey_l) + ' has to be 1500'
h_framey_00 = comps.RectRndBar (Base = FRAM_RBAR_W, Height = FRAM_RBAR_W,
                                Length = framey_l, Radius = RBAR_R, 
                                Thick = RBAR_T, inrad_same = False,
                                axis= 'y', baseaxis = 'x',
                                name = "framey_00",
                                cx = True, cy= False, cz=True)
framey_00 = h_framey_00.fco
frame_list.append (framey_00)

framey_00.Placement.Base = FreeCAD.Vector(- frame_posx,
                                          -(frame_posy-FRAM_RBAR_W/2.),
                                            HB_FRAME_H)
# os: translate([77, 75, 10]) rotate([90, 0, 0]) rounded_square(4, 4, 150, 1);
framey_10 = Draft.clone(framey_00)
framey_10.Label = 'framey_10'
framey_10.Placement.Base = FreeCAD.Vector(  frame_posx,
                                          -(frame_posy-FRAM_RBAR_W/2.),
                                            HB_FRAME_H)
frame_list.append (framey_10)
# X lower Bar 
# os: translate([-75, -77, 10]) rotate([0, 90, 0]) rounded_square(4, 4, 150, 1);
framex_l = FRAME_W - 2*FRAM_RBAR_W
print "framex_l "  + str(framex_l) + ' has to be 1500'
h_framex_00 = comps.RectRndBar (Base = FRAM_RBAR_W, Height = FRAM_RBAR_W,
                                Length = framex_l, Radius = RBAR_R, 
                                Thick = RBAR_T, inrad_same = False,
                                axis= 'x', baseaxis = 'y',
                                name = "framex_00",
                                cx = True, cy= True, cz=True)
framex_00 = h_framex_00.fco

framex_00.Placement.Base = FreeCAD.Vector(  0, # already centered
                                          - frame_posy,
                                            HB_FRAME_H)
frame_list.append (framex_00)
# os: translate([-75, 77, 10]) rotate([0, 90, 0]) rounded_square(4, 4, 150, 1);
framex_10 = Draft.clone(framex_00)
framex_10.Label = 'framex_10'
framex_10.Placement.Base = FreeCAD.Vector(  0, # already centered
                                            frame_posy,
                                            HB_FRAME_H)
frame_list.append (framex_10)

# Y top Bars 
# os: translate([77, 75, 98]) rotate([90, 0, 0]) rounded_square(4, 4, 150, 1);
framey_01 = Draft.clone(framey_00)
framey_01.Label = 'framey_01'
framey_01.Placement.Base = FreeCAD.Vector(- frame_posx,
                                          -(frame_posy-FRAM_RBAR_W/2.),
                                            FRAME_H-FRAM_RBAR_W/2.)
frame_list.append (framey_01)
# os: translate([77, 75, 98]) rotate([90, 0, 0]) rounded_square(4, 4, 150, 1);
framey_11 = Draft.clone(framey_00)
framey_11.Label = 'framey_11'
framey_11.Placement.Base = FreeCAD.Vector(  frame_posx,
                                          -(frame_posy-FRAM_RBAR_W/2.),
                                            FRAME_H-FRAM_RBAR_W/2.)
frame_list.append (framey_11)

# X top Bars 
# os: translate([-75, -77, 10]) rotate([0, 90, 0]) rounded_square(4, 4, 150, 1);
framex_01 = Draft.clone(framex_00)
framex_01.Label = 'framex_01'
framex_01.Placement.Base = FreeCAD.Vector(  0, # already centered
                                          - frame_posy,
                                            FRAME_H-FRAM_RBAR_W/2.)
frame_list.append (framex_01)

# os: translate([-75, 77, 10]) rotate([0, 90, 0]) rounded_square(4, 4, 150, 1);
framex_11 = Draft.clone(framex_00)
framex_11.Label = 'framex_11'
framex_11.Placement.Base = FreeCAD.Vector(  0, # already centered
                                            frame_posy,
                                            FRAME_H-FRAM_RBAR_W/2.)
frame_list.append (framex_11)

frame = doc.addObject("Part::Compound", "frame")
frame.Links = frame_list


# --------------- Y Rods  ---------------------------

# os: translate([-77, 75, 15]) rotate([90, 0, 0])
#                cylinder(r = 1, h = 150, $fn = 100);
rody_00 = fcfun.addCyl_pos (r = RODY_R, h= framey_l, name='rody_00',
                            axis = 'y',
                            h_disp =  -(frame_posy-FRAM_RBAR_W/2.))

# the y position is already set
rody_00.Placement.Base = FreeCAD.Vector (- frame_posx, 0, B_RODY_H)

# os: translate([77, 75, 15]) rotate([90, 0, 0])
#                cylinder(r = 1, h = 150, $fn = 100);
rody_10 = Draft.clone(rody_00)
rody_10.Label = 'rody_10'
rody_10.Placement.Base = FreeCAD.Vector( frame_posx, 0, B_RODY_H)

# os: translate([-77, 75, 90]) rotate([90, 0, 0])
#                cylinder(r = 1, h = 150, $fn = 100);
rody_01 = Draft.clone(rody_00)
rody_01.Label = 'rody_01'
rody_01.Placement.Base = FreeCAD.Vector(-frame_posx, 0, T_RODY_H)

# os: translate([-77, 75, 90]) rotate([90, 0, 0])
#                cylinder(r = 1, h = 150, $fn = 100);
rody_11 = Draft.clone(rody_00)
rody_11.Label = 'rody_11'
rody_11.Placement.Base = FreeCAD.Vector( frame_posx, 0, T_RODY_H)

# --------------- Gantry  ---------------------------

gantry_list = []

# it is not the same position as the frame, because these gantry rounded
# rods are wider
gantry_posx = FRAME_W/2 - SIDEGTRY_RBAR_W/2.

# Gantry Vertical Bars
# os: translate([-77, -8, 17]) rounded_square(4, 4, 71, 1);
gantryz_l = T_RODY_H - B_RODY_H - RBAR_H
print "gantryz_l: "  + str(gantryz_l) +  ' has to be 710'

h_gantryz_00 = comps.RectRndBar (Base = SIDEGTRY_RBAR_W,
                                Height = SIDEGTRY_RBAR_W,
                                Length = gantryz_l, Radius = RBAR_R, 
                                Thick = RBAR_T, inrad_same = False,
                                axis= 'z', baseaxis = 'x',
                                name = "gantryz_00",
                                cx = True, cy= True, cz=False)
gantryz_00 = h_gantryz_00.fco

gantry_posy = GANTRY_L/2. - SIDEGTRY_RBAR_W/2.
print "gantry_posy: "  + str(gantry_posy) +  ' has to be 80'
gantry_posz = B_RODY_H + RBAR_H/2.
print "gantry_posz: "  + str(gantry_posz) +  ' has to be 170'
gantryz_00.Placement.Base = FreeCAD.Vector(- gantry_posx,
                                           -gantry_posy,
                                            gantry_posz)
gantry_list.append(gantryz_00)
# os: translate([-77, 8, 17]) rounded_square(4, 4, 71, 1);
gantryz_01 = Draft.clone(gantryz_00)
gantryz_01.Label = 'gantryz_01'
gantryz_01.Placement.Base = FreeCAD.Vector(-gantry_posx,
                                            gantry_posy,
                                            gantry_posz)
gantry_list.append(gantryz_01)
# os: translate([77, -8, 17]) rounded_square(4, 4, 71, 1);
gantryz_10 = Draft.clone(gantryz_00)
gantryz_10.Label = 'gantryz_10'
gantryz_10.Placement.Base = FreeCAD.Vector( gantry_posx,
                                           -gantry_posy,
                                            gantry_posz)
gantry_list.append(gantryz_10)
# os: translate([77, 8, 17]) rounded_square(4, 4, 71, 1);
gantryz_11 = Draft.clone(gantryz_00)
gantryz_11.Label = 'gantryz_11'
gantryz_11.Placement.Base = FreeCAD.Vector( gantry_posx,
                                            gantry_posy,
                                            gantry_posz)
gantry_list.append(gantryz_11)
# Gantry Horizontal Y Bars
# os: translate([-77, 10, 15]) rotate([90, 0, 0]) rounded_square(4, 4, 20, 1);
h_gantryy_00 = comps.RectRndBar (Base = SIDEGTRY_RBAR_W,
                                 Height = SIDEGTRY_RBAR_W,
                                 Length = GANTRY_L, Radius = RBAR_R, 
                                 Thick = RBAR_T, inrad_same = False,
                                 axis= 'y', baseaxis = 'x',
                                 name = "gantryy_00",
                                 cx = True, cy= True, cz=True)
gantryy_00 = h_gantryy_00.fco
gantryy_00.Placement.Base = FreeCAD.Vector(- gantry_posx,
                                            0,  # already centered on Y
                                            B_RODY_H)
gantry_list.append(gantryy_00)
# os: translate([-77, 10, 90]) rotate([90, 0, 0]) rounded_square(4, 4, 20, 1);
gantryy_01 = Draft.clone(gantryy_00)
gantryy_01.Label = 'gantryy_01'
gantryy_01.Placement.Base = FreeCAD.Vector(-gantry_posx,
                                            0,  # already centered on Y
                                            T_RODY_H)
gantry_list.append(gantryy_01)
# os: translate([77, 10, 15]) rotate([90, 0, 0]) rounded_square(4, 4, 20, 1);
gantryy_10 = Draft.clone(gantryy_00)
gantryy_10.Label = 'gantryy_10'
gantryy_10.Placement.Base = FreeCAD.Vector( gantry_posx,
                                            0,  # already centered on Y
                                            B_RODY_H)
gantry_list.append(gantryy_10)
# os: translate([77, 10, 90]) rotate([90, 0, 0]) rounded_square(4, 4, 20, 1);
gantryy_11 = Draft.clone(gantryy_00)
gantryy_11.Label = 'gantryy_11'
gantryy_11.Placement.Base = FreeCAD.Vector( gantry_posx,
                                            0,  # already centered on Y
                                            T_RODY_H)
gantry_list.append(gantryy_11)

# Gantry Horizontal X Bars
# os: translate([-75,-8, 90]) rotate([0, 90, 0]) rounded_square(4, 4, 150, 1);

h_gantryx_0 = comps.RectRndBar (Base = TOPGTRY_RBAR_W, Height = TOPGTRY_RBAR_W,
                                Length = framex_l, Radius = RBAR_R, 
                                Thick = RBAR_T, inrad_same = False,
                                axis= 'x', baseaxis = 'y',
                                name = "gantryx_0",
                                cx = True, cy= True, cz=True)

# Since these bars are smaller, their position is different
topgantry_posy = GANTRY_L/2. - TOPGTRY_RBAR_W/2.

gantryx_0 = h_gantryx_0.fco
gantryx_0.Placement.Base = FreeCAD.Vector(  0, # already centered
                                           -topgantry_posy,
                                            T_RODY_H)
gantry_list.append(gantryx_0)

# os: translate([-75, 8, 90]) rotate([0, 90, 0]) rounded_square(4, 4, 150, 1);
gantryx_1 = Draft.clone(gantryx_0)
gantryx_1.Label = 'gantryx_1'
gantryx_1.Placement.Base = FreeCAD.Vector( 0, # already centered
                                           topgantry_posy,
                                           T_RODY_H)
gantry_list.append(gantryx_1)

gantry = doc.addObject("Part::Compound", "gantry")
gantry.Links = gantry_list

# ---------------- plates for the leadscrew or ballscrew
# os: translate([0, -77, 87]) rounded_square(14, 2, 13, 1);
# PONER LAS DIMENSIONES MEJOR. O MEJOR NO USAR UN RectRndBar para esto
h_lsplate_0 = comps.RectRndBar (Base = LSPLATE_B, Height = LSPLATE_T,
                                Length = LSPLATE_H, Radius = LSPLATE_R, 
                                Thick = 0, inrad_same = False,
                                axis= 'z', baseaxis = 'x',
                                name = "lsplate_0",
                                cx = True, cy= True, cz=False)
lsplate_0 = h_lsplate_0.fco
lsplate_0.Placement.Base = FreeCAD.Vector (0,-frame_posy, FRAME_H-LSPLATE_H)

# os: translate([0, 77, 87]) rounded_square(14, 2, 13, 1);
lsplate_1 = Draft.clone(lsplate_0)
lsplate_1.Label = 'lsplate_1'
lsplate_1.Placement.Base = FreeCAD.Vector (0, frame_posy, FRAME_H-LSPLATE_H)

# ---------------- leadscrew or ballscrew
# os: translate([0, 75, 90]) rotate([90, 0, 0])
#        cylinder(r = 1, h = 150, $fn = 100);
leadscrew = Draft.clone(rody_00)
leadscrew.Label = 'leadscrew'
leadscrew.Placement.Base = FreeCAD.Vector( 0, 0, T_RODY_H)


doc.recompute()

# to se the origin and the axis
guidoc.ActiveView.setAxisCross(True)

doc.saveAs (savepath + filename + '.FCStd')
