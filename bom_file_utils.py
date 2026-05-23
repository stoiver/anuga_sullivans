from anuga.config import netcdf_mode_r, netcdf_mode_w, netcdf_mode_a
from anuga.config import netcdf_float

from pprint import pprint

import numpy
import os
import warnings


def bom_rainfall2array(filename, convert_utm=False, verbose=False):
    """Read precipitation from bom file with following NetCDF format (.nc)

    Example:
    
    Dimensions:
    x_loc
    y_loc
    
    Variables:

    x_loc(x_loc)
    y_loc(y_loc)
    start_time
    valid_time


    precipitation(x_loc,y_loc)
    precip(x_loc,y_loc)
    rain_value(x_loc,y_loc)

    """

    from anuga.file.netcdf import NetCDFFile


    msg = 'Filename must be a text string'
    assert isinstance(filename, basestring), msg
    
    msg = 'Extension should be .nc'
    assert os.path.splitext(filename)[1] in ['.nc'], msg
    
    precip_names = ['precipitation', 'precip']

    # Get NetCDF
    infile = NetCDFFile(filename, netcdf_mode_r) 

    if verbose: log.critical('Reading rain from %s' % (filename))

    nx = int(infile.dimensions['x_loc'])
    ny = int(infile.dimensions['y_loc'])
    lat = float(infile.reference_latitude)  # Lat Location of station
    long = float(infile.reference_longitude)  # Long Location ofstation

    from anuga.coordinate_transforms.lat_long_UTM_conversion import LLtoUTM
    zone, x_offset, y_offset = LLtoUTM(lat,long)
    #print zone, x_offset, y_offset
    
    x = infile.variables['x_loc'][:]*1000.0 + x_offset
    y = infile.variables['y_loc'][:]*1000.0 + y_offset

    for name in precip_names:
        if name in infile.variables:
            precip = infile.variables[name][:]

    precip = precip.reshape(nx,ny)

    # Maybe the data needs to be flipped
    precip = numpy.flipud(precip)
    precip = precip.transpose()
    


    return x,y, precip


if __name__ == "__main__":

    pass
    #bom_rainfall2array(filename, convert_utm=False)
