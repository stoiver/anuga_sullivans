import time
from numpy import float, array
from anuga.geospatial_data.geospatial_data import Geospatial_data
import csv
from anuga.file.netcdf import  NetCDFFile

filename = '500y_des_rain.csv'
outfilename = '500y_des_rain.tms'
fid = open(filename)
csvreader = csv.reader(fid, delimiter=',')         
time = []
rate = []
for row in csvreader:
    #print row
    time.append(float(row[0])) 
    rate.append(float(row[1]))
N = len(time)
T = array(time, float)  # Time (seconds)
R = array(rate, float)  # Values (mm)
fid = NetCDFFile(outfilename, 'w')
fid.institution = 'ANU'
fid.description = filename[-4:]
fid.starttime = 0.0
fid.createDimension('number_of_timesteps', len(T))
fid.createVariable('time', 'd', ('number_of_timesteps',))
fid.variables['time'][:] = T       
fid.createVariable('rate', 'd', ('number_of_timesteps',))
fid.variables['rate'][:] = R        
fid.close()
