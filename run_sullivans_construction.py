""" This Script Sets up   a PAR Sullivans Creek Catchment Test Run

PROJ_DESC=UTM Zone -56 / AGD84 / meters
PROJ_DATUM=AUSTRALIAN GEODETIC 1984

"""

#+++++START_MODULES_BLOCK
#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------

# Standard modules
import os
import time
import sys
from os.path import join
from math import pi
import numpy

# Related major packages
import anuga
import string
import glob


from anuga import distribute, myid, numprocs, finalize
from anuga import Inlet_operator, Boyd_box_operator


from sullivans import *

if myid == 0:
    print 'Got all  Modules...'


#+++++END_MODULES_BLOCK
verbose=False
if myid == 0 : verbose = True


#+++++START_SCENARIOS_BLOCK
#------------------------------------------------------------------------------
# Define scenarios - Here have the ability to easily create multiple scenarios if Reqd.
#------------------------------------------------------------------------------
EVENT_OPTIONS = ['50pc','20pc','10pc','5pc','1pc','p2pc','pmf']

ENTIRE_CATCHMENT = True

#-------------------------------
# Simple TEST simulation EXISTING
RAIN_EVENT = '1pc'
RAINFALL_POLYGON = Small_Rain_Polygon
#RAINFALL_POLYGON = Catchment_Rain_Polygon
Outname_Ext = '_12000_'
starttime = 0*3600 # time to fill up lake
duration =  8*3600  # duration in seconds
yieldstep = 300 # 5 min
Start_Tide = 558.0
RAIN_FALL = True
CONSTRUCTION = True
    
basename = anuga.join('01_DEM','Sullivans_DEM_1_10_50')

outname = anuga.join('Sullivans'+ Outname_Ext+RAIN_EVENT )
meshname =anuga.join('Sullivans.tsh')

if myid == 0: print 'Basename ',basename

#+++++END_SCENARIOS_BLOCK

#+++++START_PREPARE TERRAIN_BLOCK
#------------------------------------------------------------------------------
# Preparation of topographic data
# Convert ASC 2 DEM 2 PTS using source data and store result in source data
#------------------------------------------------------------------------------
if myid == 0: print ' Preparing Terrain'
#+++++START_SETUP_MESH_BLOCK
if myid == 0: print ' Setup Mesh to be the Computational Grid'

#------------------------------------------------------------------------------
# Set up Computational Domain from an Extent and possibly  a Catchment Polygon
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Create the triangular mesh based on overall clipping polygon with a tagged
# boundary and interior regions defined in project.py along with
# resolutions (maximal area of per triangle) for each polygon
#------------------------------------------------------------------------------
#  Main Valley
MAIN_VALLEY_EXT = False
# W=689800.0
# N=6104700.0
# E=700300.0
# S=6091500.0

W=689801.0
N=6104600.0
E=700200.0
S=6091501.0


RangeX=E-W
RangeY=N-S
domain_Area= RangeX*RangeY
if myid == 0 : print' Domain is',RangeX,' x ',RangeY,' = ',domain_Area,' m2'
bounding_polygon = [[W, S], [E, S], [E, N], [W, N]]
alpha = 0.99                                # smoothing of mesh (0 is not smooth 1 is smoothest)


#Catchment_Rain_Polygon = read_polygon(join('02POLYS','02_RAIN_POLY','Catchment_Bdy.csv'))

if ENTIRE_CATCHMENT == True:
    #Catchment_Rain_Polygon = anuga.read_polygon(join('02_POLYS','Catchment_Ext_10m.csv'))   
    
    interior_regions = [[Catchment_Rain_Polygon,300],
                        [Valley_Refine_Polygon1,75],
                        [ANU_Polygon,25]]#+mesh_refine_defined
    

    riverWall={ 'Barry_Embackment': Barry_Embackment_Polyline,
               'Union_Court_Embackment': Union_Court_Embackment_Polyline}

    #interior_regions = [[Catchment_Rain_Polygon,250],[Valley_Refine_Polygon1,100]]#+mesh_refine_defined

#------------------------------------------------------------------------------
#           DEFINING INTERIOR HOLES IN THE MESH
#------------------------------------------------------------------------------
Interior_Holes_directory=anuga.join('02_POLYS','06_HOLES_USED')
interior_holes = anuga.get_polygon_list_from_files(Interior_Holes_directory, verbose = verbose)

#print len(interior_holes)

# -------------------------------------------------------------------------
#     Set up mesh for Parallel
#--------------------------------------------------------------------------

if myid == 0:
    print ' Creating Mesh'
    anuga.create_mesh_from_regions(bounding_polygon,
                     boundary_tags={'south': [0],
                                    'east': [1],
                                    'north': [2],
                                    'west': [3]},
                     maximum_triangle_area=2000,
                     interior_regions=interior_regions,
                     interior_holes=interior_holes,
                     breaklines=riverWall.values(),
                     filename=meshname,
                     use_cache=False,
                     verbose=True)
    #------------------------------------------------------------------------------
    #  Computational MESH Created
    #------------------------------------------------------------------------------
    #+++++END_SETUP_MESH_BLOCK

    #+++++START_SETUP_DOMAIN_BLOCK
    #------------------------------------------------------------------------------
    #  NOW Create an Instance of a computational DOMAIN from the Mesh
    #------------------------------------------------------------------------------
    domain = anuga.Domain(meshname, use_cache=False, verbose=True)
    # run parameters
    
    domain.geo_reference.zone = 55
    print domain.geo_reference

    domain.set_store_vertices_uniquely(False)
    #domain.set_maximum_allowed_speed(20.0)
    domain.set_flow_algorithm('DE1')
    """Set combination of slope limiting and time stepping

        Currently
           1
           1.5
           2
           2.5
           tsunami
           DE0
           DE1
           DE2
     """
    # Do not store water shallower than 5 cm
    domain.set_minimum_storable_height(0.05) # Eg 0.05 = 50mm
    
    print domain.statistics()
    domain.set_name(outname, timestamp=True)
    #------------------------------------------------------------------------------
    #  DOMAIN Created with parameters Set
    #------------------------------------------------------------------------------
    #+++++END_SETUP_DOMAIN_BLOCK

    #+++++START_SET_INITIAL_CONDITIONS_BLOCK
    #------------------------------------------------------------------------------
    # *****    Set INITIAL QUANTITIES of ELEVATION, ROUGHNESS   *******
    #------------------------------------------------------------------------------
    # Note that all quantities can now be varying over the evolution of the model see
    # anuga.abstract_2d_finite_volumes.quantity.Quantity    for details....................
    # Setting up initial conditions for a Flood model includes:
    # Setting A Base topography over the model domain
    # Setting the variation of Roughness over the terrain, which may be varied dependent on depth say
    # Setting initial water levels at BOundaries and in Lakes and Water Bodies.

    #------------------------------------------------------------------------------
    # SET ELEVATION to MESH to Describe the Terrain and set STAGE to fill lake
    #------------------------------------------------------------------------------
    print ' Setting Quantities for Elevation over Domain... from...',basename +'.csv'
    domain.set_quantity('elevation',
                filename=join('01_DEM','Test_Sullivans_Grd.grd.asc'),
                use_cache=False,
                verbose=True)
    

    domain.set_quantity('stage',Start_Tide)
    
    
    #-------------------------------------------------------------------------------
    # Cutout bridges
    #-------------------------------------------------------------------------------
    domain.set_quantity('elevation', 560.0, location='centroids',polygon=Arts_Center_Creek)
    domain.set_quantity('elevation', 560.1, location='centroids',polygon=Union_Creek)
    domain.set_quantity('elevation', 559.0, location='centroids',polygon=Dedman_Pond)
    domain.set_quantity('elevation', 560.3, location='centroids',polygon=Toad_Creek)
    domain.set_quantity('elevation', 561.0, location='centroids',polygon=Barry_Drive_Bridge)
    domain.set_quantity('elevation', 562.5, location='centroids',polygon=Masson_Street)
    domain.set_quantity('elevation', 563.4, location='centroids',polygon=Bowling)
    domain.set_quantity('elevation', 564.1, location='centroids',polygon=Condamine_Street)
    domain.set_quantity('elevation', 564.5, location='centroids',polygon=David_Street)
    domain.set_quantity('elevation', 565,   location='centroids',polygon=MacArthur_Ave) 
    domain.set_quantity('elevation', 565.5, location='centroids',polygon=Wattle)
    domain.set_quantity('elevation', 564,   location='centroids',polygon=Wet_Lands)
    domain.set_quantity('elevation', 565.5, location='centroids',polygon=Goodwin)  
    domain.set_quantity('elevation', 569,   location='centroids',polygon=Mouat)

    #------------------------------------------------------------------------------
    # Dig out Consruction
    #------------------------------------------------------------------------------
    if CONSTRUCTION: domain.set_quantity('elevation', 561,   location='centroids',polygon=Construction)

    #------------------------------------------------------------------------------
    #   SET the quantities to be placed in the SWW File (NORMAL APPLICATIONS)
    #------------------------------------------------------------------------------
    domain.set_quantities_to_be_stored({'elevation':1,'stage': 2,'xmomentum': 2,'ymomentum': 2})

    #  ------ To Record Mannings Roughness in the Model Used or Add
    #domain.set_quantities_to_be_stored({'friction': 1,'elevation': 1,'stage': 2,'xmomentum': 2,'ymomentum': 2})
    #  ------ FOR DEPTH VARYING MANNINGS USE
    #domain.set_quantities_to_be_stored({'friction': 2,'elevation': 2,'stage': 2,'xmomentum': 2,'ymomentum': 2})
    #------------------------------------------------------------------------------
    # Setup initial conditions
    #------------------------------------------------------------------------------
    # To use Polygons to Set Friction you need to import the following
    #------------------------------------------------------------------------------
    # APPLY MANNING'S ROUGHNESSES
    #------------------------------------------------------------------------------

    print ' Setting Quantities for Roughness....'
    base_friction = 0.0452 # this sets the roughness of the roads
    domain.set_quantity('friction', base_friction)   # Set all to 1friction for NOW  !!!!
    #domain.set_quantity('friction',0.1)

else:
    domain = None

if verbose: print 'DISTRIBUTING DOMAIN'

domain = distribute(domain)


#------------------------------------------------------------------------------
#      SET UP RIVERWALLS
#-----------------------------------------------------------------------------
domain.riverwallData.create_riverwalls(riverWall)

#      SET UP ANY CULVERTS
#-----------------------------------------------------------------------------



#------------------------------------------------------------------------------
# Set a Initial Water Level over the Domain or over an area defined by a polyline
# eg if u have a basin that has water in it already u can nominate a polyline
# and set the stage level inside that polyline
#------------------------------------------------------------------------------
if myid == 0: print ' Setting Quantities for Initial Water Levels...'
base_stage = Start_Tide # Set starting tide....



#+++++END_SETUP_DOMAIN_BLOCK



#------------------------------------------------------------------------------
# APPLY RAINFALL
#------------------------------------------------------------------------------

if RAIN_FALL == True:
    if RAIN_EVENT =='50pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','50pc_des_rain.tms'), quantities=['rate'])
    if RAIN_EVENT =='20pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','20pc_des_rain.tms'), quantities=['rate'])
    if RAIN_EVENT =='10pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','10pc_des_rain.tms'), quantities=['rate'])
    if RAIN_EVENT =='5pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','5pc_des_rain.tms'), quantities=['rate'])
    if RAIN_EVENT =='1pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','ACT_100yr_2hr.tms'), quantities=['rate'])
    if RAIN_EVENT =='p2pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','1_500yr_2hr.tms'), quantities=['rate'])
    if RAIN_EVENT =='pmf':
        rainfall = anuga.file_function(join('03_FORCEFUNC','PMF_60min_woodford.tms'), quantities=['rate'])


    if RAIN_EVENT in EVENT_OPTIONS :
        RAIN1 = anuga.Rate_operator(domain, rate=rainfall, factor=1.0e-3, relative_time=False, \
                          polygon=RAINFALL_POLYGON, default_rate = 0.0)
        
        
        



#+++++START_BOUNDARY_CONDITIONS_BLOCK
#------------------------------------------------------------------------------
# ****** Setup BOUNDARY CONDITIONS AT THE START OF THE RUN ******
#------------------------------------------------------------------------------

#print 'Available boundary tags', domain.get_boundary_tags()

Br = anuga.Reflective_boundary(domain)
Bd = anuga.Dirichlet_boundary([base_stage,0,0])


#print 'Available boundary tags are', domain.get_boundary_tags()


# boundary conditions for slide scenario
domain.set_boundary({'west': Bd,
                     'south': Bd,
                     'east':Br,
                     'interior': Br,
                     'north': Br})

#+++++END_BOUNDARY_CONDITIONS_BLOCK



#+++++START_EVOLVE_BLOCK

#------------------------------------------------------------------------------
# EVOLVE SYSTEM THROUGH TIME
#------------------------------------------------------------------------------

if myid == 0 and verbose: 
    print 'EVOLVE'
    print 'START Computation for Model Scenario EVOLUTION...'

domain.set_starttime(starttime)
time0 = time.time()

for t in domain.evolve(yieldstep = yieldstep, duration = duration + (-starttime) ): # All day 87300, and a bit... 90000
    if myid == 0:
        print domain.timestepping_statistics(relative_time=False)


if myid == 0:
    print 'Number of processors %g ' %numprocs
    print 'That took %.2f seconds' %(time.time()-time0)
    print 'Communication time %.2f seconds'%domain.communication_time
    print 'Reduction Communication time %.2f seconds'%domain.communication_reduce_time
    print 'Broadcast time %.2f seconds'%domain.communication_broadcast_time

if myid == 0: print 'END OF EVOLVE............'

time0 = time.time()

#------------------------------------------------------------------------------
# ****** Set up any post processing here
#------------------------------------------------------------------------------


#+++++END_POST_PROCESSING_OPTIONS_BLOCK

#domain.sww_merge(delete_old=True)


#if myid == 0:
#    print 'sww_merge took %.2f seconds' %(time.time()-time0)
#    print 'END OF RUN............'

finalize()

if myid == 0: print 'Finished'

#================    END OF RUN FILE ===================================
