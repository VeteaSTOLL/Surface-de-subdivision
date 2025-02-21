# -*- coding: latin-1 -*-
import numpy as	np

class Surface:
	verts = [[]]

	opp = [] #donne l'indice de la demi-arête opposée
	next_= [] #donne l'indice de la demi-arête suivante
	face_ = [] #donne l'indice de la face associée à la demi-arête (-1 si il n'y en a pas)
	to_vertex = [] #donne l'indice du point auquel la demi-arête pointe

	w_vertex = [] #donne l'indice d'une demi-arête qui pointe vers ce point (arbitraire)
	w_face = [] #donne l'indice d'une demi-arête qui est associée a la face (arbitraire)

	def __init__(self, nb_demi_arete, nb_points, nb_faces, list_verts):
		self.init_lists(nb_demi_arete, nb_points, nb_faces)
		self.verts = list_verts

	def init_lists(self, nb_demi_arete, nb_points, nb_faces):
		"""Initialise les listes"""

		self.opp = [-1 for _ in range(nb_demi_arete)]
		self.next_ = [-1 for _ in range(nb_demi_arete)]
		self.face_ = [-1 for _ in range(nb_demi_arete)]
		self.to_vertex = [-1 for _ in range(nb_demi_arete)]
	
		self.w_vertex = [-1 for _ in range(nb_points)]
		self.w_face = [-1 for _ in range(nb_faces)]

	def affiche_listes(self):
		"""procédure permettant d'afficher les listes opp, next_, face_, to_vertex, w_vertex et w_face"""
	
		print("opp =", self.opp)
		print("next_ =", self.next_)
		print("face_ =", self.face_)
		print("to_vertex =", self.to_vertex)

		print("w_vertex =", self.w_vertex)
		print("w_face =", self.w_face)

	def expand_lists(self, nb_demi_arete, nb_points, nb_faces):
		self.verts += [[] for _ in range(nb_points)]

		self.opp += [-1 for _ in range(nb_demi_arete)]
		self.next_ += [-1 for _ in range(nb_demi_arete)]
		self.face_ += [-1 for _ in range(nb_demi_arete)]
		self.to_vertex += [-1 for _ in range(nb_demi_arete)]
	
		self.w_vertex += [-1 for _ in range(nb_points)]
		self.w_face += [-1 for _ in range(nb_faces)]

	def next_bord(self, indice:int) -> int:
		"""donne l'indice de la demi-arête suivante pour une demi-arête au bord du mesh"""
		target = self.to_vertex[indice]
		res = self.opp[indice]
		while self.face_[res] != -1:
			while self.to_vertex[res] != target:
				res = self.next_[res]
			res = self.opp[res]
		return res

	def indice_edge(self, edge:tuple, edges) -> int:
		"""donne l'indice d'une aréte"""
		for i in range(len(edges)):
			if edges[i] == edge:
				return i
		return -1

	def edges_bord(self, edges) -> list:
		"""renvoie une liste dess demi-arêtes situées au bord de la surface"""
		res = []
		for i in range(len(edges)):
			if self.face_[i] == -1:
				res.append(i)
		return res



def nb_arete_uniques(faces:list):
	res = 0
	ed = []
	for face in faces:
		for p in range(len(face)):
			origin = face[p] #indice du point 1
			dest = face[(p+1)%len(face)] #indice du point 2
			edge = (origin, dest) #représentation en tuple de la demi-arête
			opp = (dest, origin)
			if not opp in ed: #on évite les doublons
				res += 1
				ed.append(edge)				
	return res

def conversion(faces:list, verts):
	"""converti la structure de données en arêtes demi-ailées"""

	nb_demi_arete = nb_arete_uniques(faces) * 2
	nb_faces = len(faces)
	nb_points = len(verts)

	edges = [(-1, -1) for _ in range(nb_demi_arete)]

	surface = Surface(nb_demi_arete, nb_points, nb_faces, verts.tolist())

	i = 0
	for f in range (len(faces)): #indice de la face
		face = faces[f] #représentation de la face sous forme d'une liste d'indices de points
		for p in range(len(face)):

			origin = face[p] #indice du point 1
			dest = face[(p+1)%len(face)] #indice du point 2
			edge = (origin, dest) #représentation en tuple de la demi-arête

			#On regarde si la demi-arête existe déjé
			if edge in edges:
				#On modifie la face de la demi-arête
				indice = surface.indice_edge(edge, edges)
				surface.face_[indice] = f
			else:
				#définie une demi-arête ainsi que son opposé

				indice = i

				# défini opp, face et to_vertex
				surface.opp[i] = i + 1
				surface.face_[i] = f
				surface.to_vertex[i] = dest

				edges[i] = edge
				i += 1
				
				# défini opp, face et to_vertex pour l'aréte opposée
				surface.opp[i] = i - 1
				surface.face_[i] = -1
				surface.to_vertex[i] = origin

				edges[i] = (dest, origin)
				i += 1

			#Remplie le tableau next_ pour les arêtes intérieures
			if p == 0:
				indice_premier = indice
			else:
				surface.next_[indice_precedent] = indice
				if p == len(face)-1:
					surface.next_[indice] = indice_premier
			indice_precedent = indice


			surface.w_vertex[dest] = indice
		surface.w_face[f] = indice

	bord = surface.edges_bord(edges)

	#Remplie le tableau next_ pour les arêtes extérieures
	for j in range(len(bord)):
		surface.next_[bord[j]] = surface.next_bord(bord[j])
	
	return surface

def deconversion(surface) -> list:
	"""reconverti la surface pour étre utilisable par polyscope"""

	faces = []
	for edge in surface.w_face:
		face = []
		current_edge = edge
		
		current_edge = surface.next_[current_edge]
		face.append(surface.to_vertex[current_edge])
		while current_edge != edge:
			current_edge = surface.next_[current_edge]			
			face.append(surface.to_vertex[current_edge])

		faces.append(face)
	return faces



def somme_pts_par_face(surface):
	res = 0
	for f in surface.w_face:
		res += pts_dans_face(surface, f)
	return res

def pts_dans_face(surface, w_edge):
	res = 0
	current_Wedge = w_edge
	target = current_Wedge

	res += 1
	current_Wedge = surface.next_[current_Wedge]
	while current_Wedge != target:
		res += 1
		current_Wedge = surface.next_[current_Wedge]
	return res

def average(liste_points):
	return [sum([liste_points[i][j] for i in range(len(liste_points))])/len(liste_points) for j in range(3)]

def weighted_average(liste_points, liste_poids):
	return [sum([liste_points[i][j] * liste_poids[i] for i in range(len(liste_points))])/sum(liste_poids) for j in range(3)]

def face_point(surface, indice_face):
	points = []

	current_Wedge = surface.w_face[indice_face]
	target = current_Wedge
	
	#do while codé en dur car n'existe pas en python
	points.append(surface.verts[surface.to_vertex[current_Wedge]])
	current_Wedge = surface.next_[current_Wedge]
	while (current_Wedge != target):
		points.append(surface.verts[surface.to_vertex[current_Wedge]])
		current_Wedge = surface.next_[current_Wedge]

	return average(points)

def edge_point(surface, indice_wedge, face_points):
	
	#two endpoints of the edge
	M = surface.verts[surface.to_vertex[indice_wedge]]
	E = surface.verts[surface.to_vertex[surface.opp[indice_wedge]]]

	if surface.face_[indice_wedge] == -1 or surface.face_[surface.opp[indice_wedge]] == -1:
		return average([M, E])

	#two neighbouring face points
	A = face_points[surface.face_[indice_wedge]]
	F = face_points[surface.face_[surface.opp[indice_wedge]]]

	return average([M, E, A, F])

def subdivision_catmull_clark(surface):
	somme_pts = somme_pts_par_face(surface)

	face_points = [face_point(surface, i) for i in range(len(surface.w_face))]

	# new points

	new_points = [-1 for _ in range(len(surface.w_vertex))]

	for i in range(len(new_points)):
		P = surface.verts[i]
		face_points_P = []
		edge_midpoints_P = []

		current_Wedge = surface.w_vertex[i]
		target = current_Wedge
		current_Wedge = boucle_new_points(surface, face_points, P, current_Wedge, face_points_P, edge_midpoints_P)		
		while current_Wedge != target:
			current_Wedge = boucle_new_points(surface, face_points, P, current_Wedge, face_points_P, edge_midpoints_P)

		F = average(face_points_P)
		R = average(edge_midpoints_P)

		new_points[i] = weighted_average([F, R, P], [1, 2, len(edge_midpoints_P)-3])


	# Partie 1 : subdivision des arêtes

	nb_demi_arete = len(surface.next_)
	indice_point = len(surface.verts)

	surface.expand_lists(nb_demi_arete, nb_demi_arete // 2, 0)

	for i in range(0, nb_demi_arete, 2):
		surface.verts[indice_point] = edge_point(surface, i, face_points)

		subdivide_arete(surface, nb_demi_arete, i, indice_point)
		indice_point += 1
	
	# Partie 2 : subdivision des faces

	indice_demi_arete = len(surface.next_)
	indice_point = len(surface.verts)
	indice_face = 0

	nb_demi_arete = somme_pts * 2
	nb_points = len(surface.w_face)
	nb_face = somme_pts - nb_points

	surface.expand_lists(nb_demi_arete, nb_points, 0)

	new_w_face = [-1 for _ in range(len(surface.w_face) + nb_face)]

	for f in range(len(surface.w_face)):
		indice_Wedge_face = surface.w_face[f]
		nb_pts = pts_dans_face(surface, indice_Wedge_face) // 2
		subdivide_face(surface, new_w_face, nb_pts, indice_Wedge_face, indice_demi_arete, indice_point, indice_face)
		
		surface.verts[indice_point] = face_points[f]

		indice_demi_arete += 2 * nb_pts
		indice_point += 1
		indice_face += nb_pts

	surface.w_face = new_w_face

	for i in range(len(new_points)):
		surface.verts[i] = new_points[i]

def boucle_new_points(surface, face_points, P, current_Wedge, face_points_P, edge_midpoints_P):
	if (surface.face_[current_Wedge] != -1):
		face_points_P.append(face_points[surface.face_[current_Wedge]])
	current_Wedge = surface.next_[current_Wedge]
	edge_midpoints_P.append(average([P, surface.verts[surface.to_vertex[current_Wedge]]]))
	return surface.opp[current_Wedge]

def subdivide_arete(surface, nb_demi_arete, indice_Wedge, indice_point):
	#deuxième demie arête (ne sert à rien)	
	# indice = indice_Wedge
	# surface.opp[indice] = indice + 1 # / surface.opp[indice_Wedge]
	# surface.next_[indice] = surface.next_[indice_Wedge]
	# surface.face_[indice] = surface.face_[indice_Wedge]
	# surface.to_vertex[indice] = surface.to_vertex[indice_Wedge]

	#première demie arête
	indice = nb_demi_arete + indice_Wedge
	surface.opp[indice] = indice + 1
	surface.next_[indice] = indice_Wedge
	surface.face_[indice] = surface.face_[indice_Wedge]
	surface.to_vertex[indice] = indice_point #POINT D'INTERET

	surface.w_vertex[indice_point] = indice

	surface.next_[surface.next_.index(indice_Wedge)] = indice

	#première demie arête opposée
	indice = nb_demi_arete + indice_Wedge + 1
	surface.opp[indice] = indice - 1
	surface.next_[indice] = surface.next_[indice_Wedge + 1]
	surface.face_[indice] = surface.face_[indice_Wedge + 1]
	surface.to_vertex[indice] = surface.to_vertex[indice_Wedge + 1]
	
	surface.w_vertex[surface.to_vertex[indice_Wedge + 1]] = indice

	face_opposee = surface.face_[indice_Wedge + 1]
	if face_opposee != -1:
		surface.w_face[face_opposee] = indice #important pour pt2

	#deuxième demie arête opposée
	indice = indice_Wedge + 1
	# surface.opp[indice] = indice - 1 #inutile
	surface.next_[indice] = nb_demi_arete + indice_Wedge + 1
	# surface.face_[indice] = surface.face_[indice_Wedge + 1] #inutile
	surface.to_vertex[indice] = indice_point #POINT D'INTERET

def subdivide_face(surface, new_w_face, nb_pts, indice_Wedge_face, indice_demi_arete, indice_point, indice_face):
	indice_initial = indice_Wedge_face
	indice_initial_suivant = surface.next_[surface.next_[indice_initial]]

	for i in range(nb_pts):

		# arête 1
		indice = indice_initial

		surface.face_[indice] = indice_face + i

		# arête 2
		indice = surface.next_[indice_initial]

		surface.face_[indice] = indice_face + i
		surface.next_[indice] = indice_demi_arete + 2 * i

		# arête 3
		indice = indice_demi_arete + 2 * i
		
		surface.opp[indice] = indice + 1
		surface.next_[indice] = indice_demi_arete + (2 * i - 1) % (nb_pts*2)
		surface.face_[indice] = indice_face + i
		surface.to_vertex[indice] = indice_point

		# arête 4
		indice = indice_demi_arete + (2 * i - 1) % (nb_pts*2)

		surface.opp[indice] = indice - 1
		surface.next_[indice] = indice_initial
		surface.face_[indice] = indice_face + i
		surface.to_vertex[indice] = surface.to_vertex[surface.opp[indice_initial]]

		new_w_face[indice_face + i] = indice_initial

		
		indice_initial = indice_initial_suivant
		indice_initial_suivant = surface.next_[surface.next_[indice_initial]]
	
	surface.w_vertex[indice_point] = indice_demi_arete

	return
