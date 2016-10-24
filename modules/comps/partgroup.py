# ----------------------------------------------------------------------------
# -- Groups of parts, components and objects
# -- comps library
# -- Python FreeCAD functions and classes that groups components
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
import DraftVecUtils
import logging

# ---------------------- can be taken away after debugging
import os
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging

import kcomp # before, it was called mat_cte
import fcfun
import comps

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, addCyl_pos, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole



logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ----------- class BearWashGroup ----------------------------------------
# Creates a group of bearings and washers to make idle pulleys
# Receives a list of names 
# ----- Arguments:
# holcyl_list:  list of objects kcomp.HollowCyl, that have the list of 
#               objects that will be on this group. The ordering will be
#               from bottom to top
# normal:   FreeCAD.Vector on the direction of the cylinder. The sign matters
# pos:      FreeCAD.Vector that defines the position of the center of the 
#           cylinder base       
# name:     string with the name
# ----- Attributes:
# holcyl_list:
# normal:   The normalized normal
# pos:      The position (argument)
# height:   The total height of all the components
# count:    The number of components
# fco_list: A list with all the freecad objects
# d_maxwash: The largest diameter of all the washers
# d_maxbear: The largest diameter of all the bearing
# r_maxwash: The largest radius of all the washers
# r_maxbear: The largest radius of all the bearing
# fco      : cad object of the compound

class BearWashGroup (object):

    def __init__ (self, holcyl_list,
                  name = "bearwashgr", 
                  normal = VZ, pos = V0):
        doc = FreeCAD.ActiveDocument

        self.holcyl_list = holcyl_list
        self.name = name

        group_h = 0 # the accumlated height
        # in case the length is not 1
        norm_normal = DraftVecUtils.scaleTo(normal,1)  

        self.normal = norm_normal
        elem_pos = pos

        d_maxwash = 0
        d_maxbear = 0
        fco_list = [] # list of the freecad objects
        for ind, elem in enumerate(holcyl_list):
            fco = fcfun.addCylHolePos(r_out = elem.r_out,
                                      r_in  = elem.r_in,
                                      h     = elem.thick,
                                      name  = name + str(ind+1),
                                      normal = norm_normal,
                                      pos   = elem_pos)
            fco_list.append(fco)
            # adding the height on the same direction
            elem_pos += DraftVecUtils.scaleTo(norm_normal, elem.thick)
            #print 'index: ' + str(ind)  +' thick: ' +
            #       str(elem.thick) + ' elem_pos: ' + str(elem_pos)
            group_h += elem.thick
            if elem.part == 'washer':
                if d_maxwash < elem.d_out :
                    d_maxwash = elem.d_out
            elif elem.part == 'bearing':
                if d_maxbear < elem.d_out :
                    d_maxbear = elem.d_out
            
        self.height = group_h
        self.fco_list = fco_list
        self.d_maxwash = d_maxwash
        self.d_maxbear = d_maxbear
        self.r_maxwash = d_maxwash/2.
        self.r_maxbear = d_maxbear/2.
        self.count  = len(fco_list)

        bearwashgroup = doc.addObject("Part::Compound", name)
        bearwashgroup.Links = fco_list

        self.fco = bearwashgroup
        doc.recompute()
        

# ----------- end class BearWashGroup ----------------------------------------
            

#doc = FreeCAD.newDocument()
#hcyl0 = kcomp.HollowCyl (part = 'washer', size = 6, kind= 'large')
#hcyl1 = kcomp.HollowCyl (part = 'washer', size = 4, kind= 'regular')
#hcyl2 = kcomp.HollowCyl (part = 'bearing', size = 624) # 624ZZ
#hcyl3 = kcomp.HollowCyl (part = 'washer', size = 4, kind= 'regular')
#hcyl4 = kcomp.HollowCyl (part = 'washer', size = 6, kind= 'large')
#hcyl5 = kcomp.HollowCyl (part = 'washer', size = 4, kind= 'large')

#pul_list = [hcyl0,hcyl1,hcyl2,hcyl3,hcyl4, hcyl5]

#pul_0 = BearWashGroup (holcyl_list = pul_list,
#                       name = 'idelpul_0',
#                       normal = VZ,
#                       pos = FreeCAD.Vector(0,0,0)) 

#doc.recompute()
