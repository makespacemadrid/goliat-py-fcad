# ----------------------------------------------------------------------------
# -- Component Constants
# -- comps library
# -- Constants about different components, materials, parts and 3D printer
# --   settings
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

# ---------------------- Tolerance in mm
TOL = 0.4
STOL = TOL / 2.0       # smaller tolerance

# height of the layer to print. To make some supports, ie: bolt's head
LAYER3D_H = 0.3  

# ---------------------- Bearings
LMEUU_L = { 10: 29.0, 12: 32.0 }; #the length of the bearing
LMEUU_D = { 10: 19.0, 12: 22.0 }; #diamenter of the bearing 



# E3D V6 extrusor dimensions
"""
    ___________
   |           |   outup
    -----------
      |     |
      |     |      in
    ___________
   |           |   outbot
    -----------
"""

E3DV6_IN_DIAM = 12.0
E3DV6_IN_H = 6.0
E3DV6_OUT_DIAM = 16.0
E3DV6_OUTUP_H = 3.7
E3DV6_OUTBOT_H = 3.0

# separation of the extruders.
# with the fan, the extruder are about 30mm wide. So 15mm from the center.
# giving 10mm separation, results in 40mm separation
# and total length of 70mm
extrud_sep = 40.0

# DIN-912 bolt dimmensions
# head: the index is the M, i.e: M3, M4, ..., the value is the diameter of the head of the bolt
D912_HEAD_D = {3: 5.5, 4: 7.0, 5: 8.5, 6:10.0, 8:13.0, 10:18.0} 
# length: the index is the M, i.e: M3, M4, ..., the value is the length of the head of the bolt
# well, it is the same as the M, never mind...
D912_HEAD_L =  {3: 3.0,4: 4.0, 5: 5.0,  6:6.0, 8:8.0,  10:10.0} 

M3_HEAD_R = D912_HEAD_D[3] / 2.0
M3_HEAD_L = D912_HEAD_L[3] + TOL
M3_HEAD_R_TOL = M3_HEAD_R + TOL/2.0 # smaller TOL, because it's small
M3_SHANK_R_TOL = 3 / 2.0 + TOL/2.0

# Nut DIN934 dimensions
"""
       ___     _
      /   \    |   s_max: double the apothem
      \___/    |_

   r is the circumradius,  usually called e_min
"""

# the circumdiameter, min value
NUT_D934_D = {3: 6.01, 4: 7.66, 5: 8.79}
# double the apotheme, max value
NUT_D934_2A = {3: 5.5, 4: 7.0,  5: 8.0}
# the heigth, max value
NUT_D934_L  = {3: 2.4, 4: 3.2,  5: 4.0}

M3_NUT_R = NUT_D934_D[3] / 2.0
M3_NUT_L = NUT_D934_L[3] + TOL
#  1.5 TOL because diameter values are minimum, so they may be larger
M3_NUT_R_TOL = M3_NUT_R + 1.5*TOL

# constant related to inserted nuts. For example, to make a leadscrew
# The nut height multiplier to have enough space to introduce it
NUT_HOLE_MULT_H = 1.8 
M3NUT_HOLE_H = NUT_HOLE_MULT_H * M3_NUT_L  

#M3_2APOT_TOL = NUT_D934_2A[3] +  TOL
# Apotheme is: R * cos(30) = 0.866
M3_2APOT_TOL = 2* M3_NUT_R_TOL * 0.866

# tightening bolt with added tolerances:
# Bolt's head radius
#tbolt_head_r = (tol * d912_head_d[sk_12['tbolt']])/2 
# Bolt's head lenght
#tbolt_head_l = tol * d912_head_l[sk_12['tbolt']] 
# Mounting bolt radius with added tolerance
#mbolt_r = tol * sk_12['mbolt']/2

# ------------- DIN 125 Washers (wide) -----------------------

# The Index reffers to the Metric (M3,...
# Inner Diameter (of the hole). Minimum diameter.
WASH_D125_DI = {
                  3:  3.2,
                  4:  4.3,
                  5:  5.3,
                  6:  6.4,
                  7:  7.4,
                  8:  8.4,
                 10: 10.5 }

# Outer diameter (maximum size)
WASH_D125_DO = {
                  3:   7.0,
                  4:   9.0,
                  5:  10.0,
                  6:  12.0,
                  7:  14.0,
                  8:  16.0,
                 10:  20.0 }

# Thickness (Height) of the washer
WASH_D125_T  = {
                  3:   0.5,
                  4:   0.8,
                  5:   1.0,
                  6:   1.6,
                  7:   1.6,
                  8:   1.6,
                 10:   2.0 }


# ------------- DIN 9021 Washers (wide) -----------------------

# The Index reffers to the Metric (M3,...
# Inner Diameter of the hole. Minimum diameter.
WASH_D9021_DI = {
                  3:  3.2,
                  4:  4.3,
                  5:  5.3,
                  6:  6.4,
                  7:  7.4,
                  8:  8.4,
                 10: 10.5 }

# Outer diameter (maximum size)
WASH_D9021_DO = {
                  3:   9.0,
                  4:  12.0,
                  5:  15.0,
                  6:  18.0,
                  7:  22.0,
                  8:  24.0,
                 10:  30.0 }

# Height of the washer (thickness)
WASH_D9021_T  = {
                  3:   0.8,
                  4:   1.0,
                  5:   1.2,
                  6:   1.6,
                  7:   2.0,
                  8:   2.0,
                 10:   2.5 }

# ------------- Ball Bearings           -----------------------

# Inner diameter
BEAR_DI = {
            608:  8.0,
            624:  4.0
          }

# Outer diameter
BEAR_DO = {
            608: 22.0,
            624: 13.0
          }

# Thickness (Height)
BEAR_T  = {
            608:  7.0,
            624:  5.0
          }


# to acces more easily to the dimensions of objects that are just
# a hollow cylinder, such as washers and bearings
# Arguments:
# part: 'bearing' or 'washer'
# size: metric size for the washers, and model (608, 624) for bearings
# kind: 'regular' or 'large' for washers

class HollowCyl(object):

    def __init__ (self, part, size, kind = 'regular'):

        self.part = part
        self.size = size
        self.kind = kind
        if part == 'washer':
            if kind == 'large': # DIN 9021
                self.model = 'DIN9021'
                self.d_in  = WASH_D9021_DI[size]  # inner diameter
                self.d_out  = WASH_D9021_DO[size]  # outer diameter
                self.thick  = WASH_D9021_T[size]   # thickness
            elif kind == 'regular': # DIN 125
                self.model = 'DIN125'
                self.d_in   = WASH_D125_DI[size]
                self.d_out  = WASH_D125_DO[size]
                self.thick  = WASH_D125_T[size]
            else:
                logger.error('Unkowon kind: HollowCyl')
        elif part == 'bearing':
            self.model  = size
            self.d_in   = BEAR_DI[size]
            self.d_out  = BEAR_DO[size]
            self.thick  = BEAR_T[size]
        self.r_in   = self.d_in/2.   # inner radius
        self.r_out  = self.d_out/2.   # outer radius


# ----------------------------- shaft holder SK dimensions --------

SK12 = { 'd':12.0, 'H':37.5, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
         'h':23.0, 'A':21.0, 'b': 5.0, 'g':6.0,  'I':20.0,
         'mbolt': 5, 'tbolt': 4} 

# ------------------------- T8 Nut for leadscrew ---------------------
#   
#  1.5|3.5| 10  | 
#      __  _____________________________ d_ext: 22
#     |__|
#     |__|   screw_d: 0.35  --- d_screw_pos: 16
#    _|  |______     ________ d_shaft_ext: 10.2
#   |___________|    --- d_T8 (threaded) 
#   |___________|    ---   
#   |_    ______|    ________
#     |__|
#     |__|  -------------------
#     |__|  ____________________________
#
#   
#      10  |3.5| 1.5
#           __  _____________________________ d_flan: 22
#          |__|
#          |__|   screw_d: 0.35  --- d_screw_pos: 16
#    ______|  |_    ________ d_shaft_ext: 10.2
#   |___________|    ___ d_T8 (threaded) 
#   |___________|    ___   
#   |_______   _|    ________
#          |__|
#          |__|  -------------------
#          |__|  ____________________________
#
#          |  |
#           nut_flan_l: 3.5
#   |  nut_l:15  |
#
#              | |
#               T8NUT_SHAFT_OUT: 1.5

T8N_SCREW_D     = 3.5
T8N_D_FLAN      = 22.0
T8N_D_SCREW_POS = 16.0
T8N_D_SHAFT_EXT = 10.2
T8N_D_T8        = 8.0
T8N_L           = 15.0
T8N_FLAN_L      = 3.5
T8N_SHAFT_OUT   = 1.5

# ------------------------- T8 Nut Housing ---------------------

# Box dimensions:
T8NH_L = 30.0
T8NH_W = 34.0
T8NH_H = 28.0

# separation between the screws that attach to the moving part
T8NH_ScrLSep  = 18.0
T8NH_ScrWSep =  24.0

# separation between the screws to the end
T8NH_ScrL2end = (T8NH_L - T8NH_ScrLSep)/2.0
T8NH_ScrW2end = (T8NH_W - T8NH_ScrWSep)/2.0

# Screw dimensions, that attach to the moving part: M4 x 7
T8NH_ScrD = 4.0
T8NH_ScrR = T8NH_ScrD / 2.0
T8NH_ScrL = 7.0

# Screw dimensions, that attach to the Nut Flange: M3 x 10
T8NH_FlanScrD = 3.0
T8NH_FlanScrL = 10.0




