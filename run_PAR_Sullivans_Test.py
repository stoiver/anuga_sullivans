""" This Script Sets up   a PAR Sullivans Creek Catchment Test Run

PROJ_DESC=UTM Zone -56 / AGD84 / meters
PROJ_DATUM=AUSTRALIAN GEODETIC 1984




"""
print(' ABOUT to Start Simulation:- Importing Modules')
#+++++START_MODULES_BLOCK
#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------

# Standard modules
import os
import time
import sys
import pylab
from os.path import join
from math import pi
#from numpy import choose, greater, ones, sin, exp,cosh
import numpy

# Related major packages
import anuga
import string
import glob

print('Got all std Serial Modules...')


#+++++END_MODULES_BLOCK
TESTING_ONLY = True

Parallel = True

#+++++START_SCENARIOS_BLOCK
#------------------------------------------------------------------------------
# Define scenarios - Here have the ability to easily create multiple scenarios if Reqd.
#------------------------------------------------------------------------------
EVENT_OPTIONS = ['50pc','20pc','10pc','05pc','1pc','p2pc','pmf']

ENTIRE_CATCHMENT = True

#-------------------------------
# Simple TEST simulation EXISTING
RAIN_EVENT = '1pc'
Outname_Ext = '_12000_'
starttime = 0.0
finaltime = 7200
yieldstep = 60 # 15 min
Start_Tide =558.0
RAIN_FALL = True
    
if Parallel == True:
    #------------------------------------------------------------------------------
    # PARALLEL INTERFACE
    #------------------------------------------------------------------------------

    from anuga import distribute, myid, numprocs, finalize
    from anuga import Inlet_operator, Boyd_box_operator
    """
       Note for Parallel to run you must issue the following command:
        mpirun -np 4 python run_parallel_sw_meribula.py

        so adding  mpirun -np 4    { Where 4 is the number of cores being run on...
        to the usual
        python run_parallel_sw_meribula.py
    """

basename = anuga.join('01_DEM','Sullivans_DEM_1_10_50')

outname = anuga.join('Sullivans'+ Outname_Ext+RAIN_EVENT )
meshname =anuga.join('Sullivans.tsh')
print('Basename ',basename)
#+++++END_SCENARIOS_BLOCK

#+++++START_PREPARE TERRAIN_BLOCK
#------------------------------------------------------------------------------
# Preparation of topographic data
# Convert ASC 2 DEM 2 PTS using source data and store result in source data
#------------------------------------------------------------------------------
print(' Preparing Terrain')
#+++++START_SETUP_MESH_BLOCK
print(' Setup Mesh to be the Computational Grid')
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
print(' Domain is',RangeX,' x ',RangeY,' = ',domain_Area,' m2')
bounding_polygon = [[W, S], [E, S], [E, N], [W, N]]
alpha = 0.99                                # smoothing of mesh (0 is not smooth 1 is smoothest)
verbose=True

#Catchment_Rain_Polygon = read_polygon(join('02POLYS','02_RAIN_POLY','Catchment_Bdy.csv'))

if ENTIRE_CATCHMENT == True:
    #Catchment_Rain_Polygon = anuga.read_polygon(join('02_POLYS','Catchment_Ext_10m.csv'))
    Catchment_Rain_Polygon = anuga.read_polygon(join('02_POLYS','Catchment_Bdy_Simple.csv'))
    Valley_Refine_Polygon1 = anuga.read_polygon(join('02_POLYS','Refine_Poly.csv'))
    
    interior_regions = [[Catchment_Rain_Polygon,12000],[Valley_Refine_Polygon1,2000]]#+mesh_refine_defined

#------------------------------------------------------------------------------
#           DEFINING INTERIOR HOLES IN THE MESH
#------------------------------------------------------------------------------
Interior_Holes_directory=anuga.join('02_POLYS','06_HOLES_USED')
interior_holes = anuga.get_polygon_list_from_files(Interior_Holes_directory)

# -------------------------------------------------------------------------
#     Set up mesh for Parallel
#--------------------------------------------------------------------------

if myid == 0:
    print(' Creating Mesh')
    if TESTING_ONLY == True:
        anuga.create_mesh_from_regions(bounding_polygon,
                         boundary_tags={'south': [0],
                                        'east': [1],
                                        'north': [2],
                                        'west': [3]},
                         maximum_triangle_area=10000,
                         interior_regions=interior_regions,
                         #interior_holes=interior_holes,
                         filename=meshname,
                         use_cache=False,
                         verbose=False)
    else:
        anuga.create_mesh_from_regions(bounding_polygon,
                         boundary_tags={'south': [0],
                                        'east': [1],
                                        'north': [2],
                                        'west': [3]},
                         maximum_triangle_area=1000,
                         interior_regions=interior_regions,
                         interior_holes=interior_holes,
                         filename=meshname,
                         use_cache=True,
                         verbose=False)
    #------------------------------------------------------------------------------
    #  Computational MESH Created
    #------------------------------------------------------------------------------
    #+++++END_SETUP_MESH_BLOCK

    #+++++START_SETUP_DOMAIN_BLOCK
    #------------------------------------------------------------------------------
    #  NOW Create an Instance of a computational DOMAIN from the Mesh
    #------------------------------------------------------------------------------
    domain = anuga.Domain(meshname, use_cache=True, verbose=True)
    # run parameters
    
    
    print(domain.geo_reference)

    #domain.set_store_vertices_uniquely(False)
    #domain.set_maximum_allowed_speed(20.0)
    #domain.set_default_order(2)
    #domain.set_flow_algorithm('2_0')
    """Set combination of slope limiting and time stepping

        Currently
           1
           1.5
           2
           2.5
           tsunami
     """
    # Do not store water shallower than 1 cm
    domain.set_minimum_storable_height(0.01) # Eg 0.05 = 50mm
    print(domain.statistics())
    domain.set_name(outname)
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
    # SET ELEVATION to MESH to Describe the Terrain
    #------------------------------------------------------------------------------
    print(' Setting Quantities for Elevation over Domain... from...',basename +'.csv')
    if TESTING_ONLY == True:
#         domain.set_quantity('elevation',
#                     filename=basename+'.csv',
#                     use_cache=True,
#                     verbose=True,
#                     alpha=alpha)
        
        Elev = domain.quantities['elevation']
        Elev.set_values_from_utm_grid_file(join('01_DEM','Test_Sullivans_Grd.grd.asc'),
                             location='vertices',
                             indices=None,
                             verbose=False)

        
        
    else:
        domain.set_quantity('elevation',
                    filename=basename+'.csv',
                    use_cache=False,
                    verbose=True,
                    alpha=alpha)

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

    print(' Setting Quantities for Roughness....')
    base_friction = 0.0452 # this sets the roughness of the roads
    domain.set_quantity('friction', base_friction)   # Set all to 1friction for NOW  !!!!
    #domain.set_quantity('friction',0.1)

else:
    domain = None

if myid == 0 and verbose: print('DISTRIBUTING DOMAIN')
domain = distribute(domain)

#------------------------------------------------------------------------------
#      SET UP ANY CULVERTS
#-----------------------------------------------------------------------------





#------------------------------------------------------------------------------
# Set a Initial Water Level over the Domain or over an area defined by a polyline
# eg if u have a basin that has water in it already u can nominate a polyline
# and set the stage level inside that polyline
#------------------------------------------------------------------------------
print(' Setting Quantities for Initial Water Levels...')
base_stage = Start_Tide # Set starting tide....

domain.set_quantity('stage',base_stage)



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
    if RAIN_EVENT =='05pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','05pc_des_rain.tms'), quantities=['rate'])
    if RAIN_EVENT =='1pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','ACT_100yr_2hr.tms'), quantities=['rate'])
    if RAIN_EVENT =='p2pc':
        rainfall = anuga.file_function(join('03_FORCEFUNC','1_500yr_2hr.tms'), quantities=['rate'])
    if RAIN_EVENT =='pmf':
        rainfall = anuga.file_function(join('03_FORCEFUNC','PMF_60min_woodford.tms'), quantities=['rate'])


    if RAIN_EVENT in EVENT_OPTIONS :
        RAIN1 = anuga.Rate_operator(domain, rate=rainfall, factor=1.0e-3, \
                          polygon=Catchment_Rain_Polygon , default_rate = 0.0)
        
        
        



#+++++START_BOUNDARY_CONDITIONS_BLOCK
#------------------------------------------------------------------------------
# ****** Setup BOUNDARY CONDITIONS AT THE START OF THE RUN ******
#------------------------------------------------------------------------------

print('Available boundary tags', domain.get_boundary_tags())

Br = anuga.Reflective_boundary(domain)
Bd = anuga.Dirichlet_boundary([base_stage,0,0])


print('Available boundary tags are', domain.get_boundary_tags())


# boundary conditions for slide scenario
domain.set_boundary({'west': Br,
                     'south': Br,
                     'east':Br,
                     #'east': Transmissive_Momentum_Set_Stage_boundary(domain, lambda t: tide),
                     'north': Br})
#+++++END_BOUNDARY_CONDITIONS_BLOCK



# #---------------------------------------
# # Read in some rainfall data
# #---------------------------------------
# directory = "04_RAINFALL"
# filepattern = "Sull_UTM_15*.asc" 
# import os
# import glob
# import os.path
# pattern = os.path.join(directory, filepattern)
# files = glob.glob(pattern)
# files.sort()
# print files
# 
# # list of quantites to be initialised by rain radar files
# rain_q = []
# 
# from anuga import Quantity
# 
# i=0
# for file in files:
#     Q = Quantity(domain, name='rain'+str(i))
#     Q.set_values_from_utm_grid_file(filename=file)
#     pylab.figure(i)
#     Q.plot_quantity()
#     rain_q.append(Q)
#     i += 1
# 
# # Lets make a rainfall operator
# # Data is mm/10mins  = 1m/1000mm / 10 mins x 1 min/ 60 sec 
# factor = 1.0/1000 * 0.1 /60 # m/s
# 
# rain_operator = anuga.Rate_operator(domain, rate=rain_q[0], factor=factor, default_rate = 0.0)
#         


#+++++START_EVOLVE_BLOCK

#------------------------------------------------------------------------------
# EVOLVE SYSTEM THROUGH TIME
#------------------------------------------------------------------------------

if myid == 0 and verbose: print('EVOLVE')
print('START Computation for Model Scenario EVOLUTION...')

domain.set_starttime(starttime)
time0 = time.time()

if TESTING_ONLY == True:
    starttime = 0.0
    finaltime = 3600*2
    yieldstep = 60 # 15 min


for t in domain.evolve(yieldstep = yieldstep, finaltime = finaltime): # All day 87300, and a bit... 90000


    # Manually work out which radar quantity we should use at this time.
    # There are 4 quantities
    # based on the 4 radar files, so just dividing finaltime/4 to use the 4 files
    #j = int(t/40)
    #print j
    
    # So at each yieldstep we assign a possibly new radar file to the rain operator
    #
    # Later we should setup an operator to keep track of the time and open the appropriate
    # data file (only once) for the given time interval
    #rain_operator.set_rate(rain_q[j])

    water_volume = domain.get_water_volume()
    
    if numpy.allclose(t,0.0):
        initial_water_volume = water_volume
        
    if myid == 0:
        print(domain.timestepping_statistics())
        print('  added water volume',water_volume - initial_water_volume)


if myid == 0:
    print('Number of processors %g ' %numprocs)
    print('That took %.2f seconds' %(time.time()-time0))
    print('Communication time %.2f seconds'%domain.communication_time)
    print('Reduction Communication time %.2f seconds'%domain.communication_reduce_time)
    print('Broadcast time %.2f seconds'%domain.communication_broadcast_time)

print('END OF RUN............')

#domain.dump_triangulation()

# raw_input("Press ENTER to exit.\n")
#+++++END_EVOLVE_BLOCK

#+++++START_POST_PROCESSING_OPTIONS_BLOCK
#------------------------------------------------------------------------------
# ****** Set up any post processing here
#------------------------------------------------------------------------------


#+++++END_POST_PROCESSING_OPTIONS_BLOCK

domain.sww_merge(delete_old=True)

finalize()

print('Finished')

#================    END OF RUN FILE ===================================
