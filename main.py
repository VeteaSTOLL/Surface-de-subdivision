# -*- coding: latin-1 -*-

import polyscope as ps
import numpy as	np
from conversion import *
from wavefront import *

#obj = load_obj('LEMMING.obj')

ps.init()

#verts = obj.only_coordinates()
#faces = obj.only_faces()

verts=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[1.,1.,0.],[0.,0.,1.],[1.,0.,1.],[0.,1.,1.],[1.,1.,1.]])
faces=[[0,2,3,1],[1,3,7,5],[5,7,6,4],[4,6,2,0],[2,6,7,3],[0,1,5,4]]

surface = conversion(faces, verts)

for i in range(3):
	subdivision_catmull_clark(surface)

verts = np.array(surface.verts)
faces = deconversion(surface)

ps.register_surface_mesh("mesh", verts, faces, transparency=0.75, color=(0.3, 0.3, 0.3))

ps.show()