

import anuga
from os.path import join
import numpy as np
import anuga.utilities.spatialInputUtil as su


#================================================================================
# Setup lot of polygons
#================================================================================
Catchment_Rain_Polygon = su.read_polygon(join('02_POLYS','Catchment_Bdy_Simple.csv'))
Valley_Refine_Polygon1 = su.read_polygon(join('02_POLYS','Refine_Poly.csv'))



Gods_Embackment    = su.readShp_1PolyGeo(join('05_SHAPEFILES','Gods_Embackment.shp'), dropLast=False)
Gods_Library_Lane  = su.readShp_1PolyGeo(join('05_SHAPEFILES','Gods_Library_Lane.shp'), dropLast=False)
Fellows_Creek      = su.readShp_1PolyGeo(join('05_SHAPEFILES','Fellows_Oval.shp'), dropLast=False)
Arts_Center_Creek  = su.readShp_1PolyGeo(join('05_SHAPEFILES','Arts_Center_Creek.shp'), dropLast=False)
Union_Creek        = su.readShp_1PolyGeo(join('05_SHAPEFILES','Union_Creek.shp'), dropLast=False)
Dedman_Pond        = su.readShp_1PolyGeo(join('05_SHAPEFILES','Dedman_Pond.shp'), dropLast=False)
Toad_Creek         = su.readShp_1PolyGeo(join('05_SHAPEFILES','Toad_Creek.shp'), dropLast=False)
Barry_Drive_Bridge = su.readShp_1PolyGeo(join('05_SHAPEFILES','Barry_Drive_Bridge.shp'), dropLast=False)
Masson_Street      = su.readShp_1PolyGeo(join('05_SHAPEFILES','Masson_Bridge.shp'), dropLast=False)
Bowling            = su.readShp_1PolyGeo(join('05_SHAPEFILES','Bowling.shp'), dropLast=False)
Condamine_Street   = su.readShp_1PolyGeo(join('05_SHAPEFILES','Condamine_Bridge.shp'), dropLast=False)
David_Street       = su.readShp_1PolyGeo(join('05_SHAPEFILES','David.shp'), dropLast=False)
MacArthur_Ave      = su.readShp_1PolyGeo(join('05_SHAPEFILES','MacArthur_Ave.shp'), dropLast=False)
Wattle             = su.readShp_1PolyGeo(join('05_SHAPEFILES','Wattle.shp'), dropLast=False)
Wet_Lands          = su.readShp_1PolyGeo(join('05_SHAPEFILES','Wet_Lands.shp'), dropLast=False)
Goodwin            = su.readShp_1PolyGeo(join('05_SHAPEFILES','Goodwin.shp'), dropLast=False)
Mouat              = su.readShp_1PolyGeo(join('05_SHAPEFILES','Mouat.shp'), dropLast=False)


Small_Rain_Polygon = [[696743.104096,6097658.42999],
                      [695253.508944,6098171.40315],
                      [693497.562342,6097845.86249],
                      [692442.021407,6096652.21339],
                      [692146.07535,6094481.94231],
                      [692836.616149,6093436.26625],
                      [695677.698292,6093416.53651],
                      [697029.185284,6096168.83483],
                      [696743.104096,6097658.42999]]



ANU_Polygon = [[693209,6094505],
                 [692666,6094189],
                 [692563,6093994],
                 [692695,6093831],
                 [693000,6093989],
                 [693174,6094013],
                 [693302,6094443]]

# 
# Construction =[[692888.372198,6094063.62932],
#                [692836.344809,6094102.79601],
#                [692821.145797,6094082.92038],
#                [692805.946784,6094095.78108],
#                [692864.404525,6094157.74629],
#                [692899.479169,6094186.97516],
#                [692943.322474,6094222.0498],
#                [692955.014022,6094229.64931],
#                [692991.842398,6094203.34332],
#                [692888.372198,6094063.62932]]

Construction = su.readShp_1PolyGeo(join('05_SHAPEFILES','Construction.shp'), dropLast=False)


#================================================================================
# Setup polylines
#================================================================================

East_Bank = su.readShp_1LineGeo(join('05_SHAPEFILES','East_Bank.shp'))
West_Bank = su.readShp_1LineGeo(join('05_SHAPEFILES','West_Bank.shp'))



#==================================================================================
# Riverwalls
#==================================================================================

Barry_Embackment = su.readShp_1LineGeo(join('05_SHAPEFILES','Barry_Embackment.shp'))


def PolylineToRiverwall(polyline, elevation):
    
    riverwall_polyline = []
    
    for point in polyline:
        #print point
        point_elev = point + [elevation]
        riverwall_polyline.append(point_elev)
        
    return riverwall_polyline

def RiverwallToPolyline(riverwall_polyline):
    
    polyline = []
    
    for point_elev in riverwall_polyline:
        #print point_elev
        point = point_elev[0:2]
        polyline.append(point)
        
    return polyline




#Barry_Embackment_Polyline = su.readShp_1LineGeo(join('05_SHAPEFILES','Mouat.shp'), dropLast=False)
#assert np.allclose(Mouat, Mouat_expected)


Union_Court_Embackment_Polyline = [[693030.843,6094235.092,563],
            [693020.514059,6094249.56128,563],
            [692979.454517,6094250.43992,563],
            [692939.621496,6094217.21333,563],
            [692909.856213,6094197.40282,563],
            [692870.980474,6094163.18201,563],
            [692817.129353,6094160.43879,563],
            [692773.719815,6094142.86704,563],
            [692727.606554,6094090.30097,563]]



