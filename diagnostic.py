
import anuga.utilities.plot_utils as utils


swwfile = 'Sullivans_12000_1pc.sww'

print('Opening sww file')
mesh = utils.get_output(swwfile)

print('Calculating centroid values')
c = utils.get_centroids(mesh, velocity_extrapolation=False)


print('extent')
print(utils.get_extent(mesh))


print(c.stage[:,540000])
print(c.stage[:,1222222])

print('Plotting')


point = [500,600]

#id = utils.get_triangle_containing_point(mesh,point)


id = 540000
c_height = c.stage[:,id]-c.elev[id]

print(c_height)
print(c.stage[:,id])
print(c.elev)

print(id)

import pylab
pylab.ion()
pylab.plot(c.time,c_height)
pylab.savefig('height_%g.png'%id)








