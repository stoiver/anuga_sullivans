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
import pylab
from os.path import join
from math import pi
import numpy

# Related major packages
import anuga
import string
import glob


verbose=True

# Flag to only print on processor 0 and if verbose set
if verbose and anuga.myid == 0 :
    print_flag = True
else:
    print_flag = False

if print_flag: print(' ABOUT to Start Simulation')

#+++++START_SCENARIOS_BLOCK
#------------------------------------------------------------------------------
# Define scenarios - Here have the ability to easily create multiple scenarios if Reqd.
#------------------------------------------------------------------------------
EVENT_OPTIONS = ['50pc','20pc','10pc''5pc','1pc','p2pc','pmf']

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
    

basename = anuga.join('01_DEM','Sullivans_DEM_1_10_50')

outname = anuga.join('Sullivans'+ Outname_Ext+RAIN_EVENT )
meshname =anuga.join('Sullivans.tsh')


if print_flag : print('Basename ',basename)


W=689801.0
N=6104600.0
E=700200.0
S=6091501.0


RangeX=E-W
RangeY=N-S
domain_Area= RangeX*RangeY
if print_flag: print(' Domain is',RangeX,' x ',RangeY,' = ',domain_Area,' m2')


bounding_polygon = [[W, S], [E, S], [E, N], [W, N]]

Catchment_Rain_Polygon = anuga.read_polygon(join('02_POLYS','Catchment_Bdy_Simple.csv'))
Valley_Refine_Polygon1 = anuga.read_polygon(join('02_POLYS','Refine_Poly.csv'))
    
#interior_regions = [[Catchment_Rain_Polygon,3000],[Valley_Refine_Polygon1,500]]
interior_regions = [[Catchment_Rain_Polygon,12000],[Valley_Refine_Polygon1,2000]]

#------------------------------------------------------------------------------
#           DEFINING INTERIOR HOLES IN THE MESH
#------------------------------------------------------------------------------
Interior_Holes_directory=anuga.join('02_POLYS','06_HOLES_USED')
interior_holes = anuga.get_polygon_list_from_files(Interior_Holes_directory)

# -------------------------------------------------------------------------
#     Set up mesh for Parallel
#--------------------------------------------------------------------------

if anuga.myid == 0:
    if print_flag: print(' Creating Mesh')
    
    domain = anuga.create_domain_from_regions(bounding_polygon,
                     boundary_tags={'south': [0],
                                    'east': [1],
                                    'north': [2],
                                    'west': [3]},
                     maximum_triangle_area=10000,
                     interior_regions=interior_regions,
                     #interior_holes=interior_holes,
                     mesh_filename=meshname,
                     use_cache=False,
                     verbose=False)

    
    domain.set_zone(55)
    if print_flag: print(domain.geo_reference)

    # Do not store water shallower than 50 cm
    domain.set_minimum_storable_height(0.005) # Eg 0.05 = 50mm
    if print_flag: print(domain.statistics())
    
    domain.set_name(outname)

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
    if print_flag: print(' Setting Quantities for Elevation over Domain... from...',basename +'.csv')
        
    domain.set_quantity('elevation',filename=join('01_DEM','Test_Sullivans_Grd.grd.asc'))
    domain.set_quantity('stage',558)

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

    if print_flag: print(' Setting Quantities for Roughness....')
    base_friction = 0.0452 # this sets the roughness of the roads
    domain.set_quantity('friction', base_friction)   # Set all to 1friction for NOW  !!!!


else:
    domain = None

if print_flag: print('DISTRIBUTING DOMAIN')
domain = anuga.distribute(domain)

#------------------------------------------------------------------------------
#      SET UP ANY CULVERTS
#-----------------------------------------------------------------------------




#------------------------------------------------------------------------------
# Set a Initial Water Level over the Domain or over an area defined by a polyline
# eg if u have a basin that has water in it already u can nominate a polyline
# and set the stage level inside that polyline
#------------------------------------------------------------------------------
if print_flag: print(' Setting Quantities for Initial Water Levels...')

base_stage = Start_Tide # Set starting tide....




#------------------------------------------------------------------------------
# APPLY RAINFALL
#------------------------------------------------------------------------------





#+++++START_BOUNDARY_CONDITIONS_BLOCK
#------------------------------------------------------------------------------
# ****** Setup BOUNDARY CONDITIONS AT THE START OF THE RUN ******
#------------------------------------------------------------------------------

Br = anuga.Reflective_boundary(domain)
Bd = anuga.Dirichlet_boundary([base_stage,0,0])


print('Available boundary tags for proc',anuga.myid, 'are', domain.get_boundary_tags())


# boundary conditions for slide scenario
domain.set_boundary({'west': Br,
                     'south': Br,
                     'east':Br,
                     'north': Br})



#---------------------------------------
# Read in some rainfall data
#---------------------------------------

from anuga.rain.grid_data import Calibrated_radar_rain

start_time = '20120301_0000'
final_time = '20120301_1800'
BASE_DIR = "/home/steve/RAINFALL/RADAR/AUS_RADAR/Calibrated_Radar_Data/ACT_netcdf"
RADAR_DIR          = join(BASE_DIR, 'RADAR_Rainfall/140/2012' )    
Catchment_file     = join(BASE_DIR,'ACT_Bdy/ACT_Entire_Catchment_Poly_Simple_UTM_55.csv')
State_boundary_file = join(BASE_DIR,'ACT_Bdy/ACT_State_Bdy_UTM_55.csv')


    
anuga.barrier()

rain = Calibrated_radar_rain(RADAR_DIR, 
                             start_time=start_time, 
                             final_time=final_time, 
                             verbose=print_flag)

if anuga.myid == 0:
    print(rain.extent)
    print(bounding_polygon)
    stats = rain.accumulate_data_stats(polygon=Catchment_Rain_Polygon, print_stats=True)



from anuga import Quantity
Q = Quantity(domain, name='rain', register=True)

rain_raster = (rain.x, rain.y, rain.data_slices[0])



if anuga.myid == 0: 
    import pylab as pl
    pl.ion()
    p2 = anuga.read_polygon(Catchment_file)
    p3 = anuga.read_polygon(State_boundary_file)
    
    #rain.plot_data(0, show=True, polygons=[p2,p3])
    

domain.set_quantity('rain', raster=rain_raster, location="centroids")
 
rain_fall = anuga.collect_value(Q.get_integral())

if anuga.myid == 0:
    print('Accum Rain', rain_fall)
    

rain_operator = anuga.Rate_operator(domain, 
                                    rate=Q, 
                                    factor=1.0/600.0, 
                                    default_rate = 0.0,
                                    polygon=Catchment_Rain_Polygon)
        


#+++++START_EVOLVE_BLOCK

#------------------------------------------------------------------------------
# EVOLVE SYSTEM THROUGH TIME
#------------------------------------------------------------------------------

if anuga.myid == 0 and verbose: print('EVOLVE')
if anuga.myid == 0 and verbose: print('START Computation for Model Scenario EVOLUTION...')


time0 = time.time()

starttime = rain.start_time
domain.set_starttime(starttime)

if anuga.myid == 0:
    print('Start_Time: ' + domain.get_datetime())

duration = 60*60*8
yieldstep = 60 # 1 min

lower = starttime
upper = rain.times[0]
j = 0
for t in domain.evolve(yieldstep = yieldstep, duration = duration): # All day 87300, and a bit... 90000

    abs_t = domain.get_time(relative_time=False)
    if abs_t >= lower and abs_t < upper :
        pass
    else:
        # update rainslice
        lower = upper
        j = j+1
        if j < len(rain.times):
            upper = upper = rain.times[j]
            rain_raster = (rain.x, rain.y, rain.data_slices[j])
            domain.set_quantity('rain',raster=rain_raster,location="centroids")
            if anuga.myid == 0:
                print("UPDATING TO TIMESLICE %g"% j)
                #rain.plot_data(j, show=True, polygons=[p2,p3])
                #import time
                #time.sleep(0.05)
        else:
            # At end of slices
            if anuga.myid == 0:
                print("AFTER LAST TIMESLICE")
            upper = float("inf")
            domain.set_quantity('rain', 0.0, location="centroids")
            

    water_volume = domain.get_water_volume()
    
    if numpy.allclose(t,0.0):
        initial_water_volume = water_volume
        
    if anuga.myid == 0:
        print(domain.timestepping_statistics())
        print('  Added water volume',water_volume - initial_water_volume)
        
        
        
if anuga.myid == 0:
    pl.show()
    pl.ioff()

if anuga.myid == 0:
    print('Number of processors %g ' %anuga.numprocs)
    print('That took %.2f seconds' %(time.time()-time0))
    print('Communication time %.2f seconds'%domain.communication_time)
    print('Reduction Communication time %.2f seconds'%domain.communication_reduce_time)
    print('Broadcast time %.2f seconds'%domain.communication_broadcast_time)

if anuga.myid == 0 and verbose: print('END OF RUN............')



domain.sww_merge(delete_old=True)

anuga.finalize()

if anuga.myid == 0 and verbose: print('Finished')

#================    END OF RUN FILE ===================================
