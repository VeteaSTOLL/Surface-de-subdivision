# -*- coding: latin-1 -*-

import numpy as	np

def face_points(faces:list, verts) -> list:
	"""renvoie une liste des points au centre de chaque face"""
	res = []
	for face in faces:		
		res.append(face_point(face, verts))
	return res

def face_point(face:list, verts) -> list:
	"""calcule la moyenne des points d'une face'"""
	liste_points = []
	for point in face:
		liste_points.append(verts[point])
	return moyenne_points(liste_points)


def edges(faces:list) -> dict:
	"""renvoie un dictionnaire avec comme clés : les arêtes sous forme d'un tuple de 2 points (leurs indices)
	et avec comme valeur une liste, généralement de longueur 2, contenant les indices des faces connectées à cette arête"""
	res = {} # forme : {(0,1) : [0, 2], ... }
			 #         { edge : [indice_face1, indice_face2], ... }
	for i in range(len(faces)):
		for j in range(len(faces[i])):
			edge = (faces[i][j], faces[i][(j+1)%len(faces[i])])
			edge2 = (edge[1], edge[0]) # car l'ordre n'importe pas : (0,1) = (1,0)
			if edge in res:
				res[edge].append(i)
			elif edge2 in res:
				res[edge2].append(i)
			else:
				res[edge] = [i]
	return res

def edge_points(edges:dict, face_points:list, verts) -> list:
	"""renvoie une liste des points pour chaque arête du mesh"""
	res = []
	for edge in edges.keys():		
		res.append(edge_point(edge, edges, face_points, verts))
	return res

def edge_point(edge:tuple, edges:dict, face_points:list, verts) -> list:
	"""calcule le point d'arête "edge" """
	liste_points = [verts[edge[i]] for i in range(2)] # on met les 2 premiers points dans la liste dont on va ensuite calculer la moyenne

	if len(edges[edge]) == 2: # s'il n'y a qu'une face associée à cette arête, on ignore cette partie
		for i in range(2):
			liste_points.append(face_points[edges[edge][i]])
			
	return moyenne_points(liste_points)



def new_vertex_points(verts, faces:list, face_points:list, edges:dict) -> list:
	"""renvoie un array numpy des nouvelles positions des sommets du mesh"""
	res = []
	for i in range(len(verts)):
		P = verts[i]

		points_F = face_points_touching_P(i, faces, face_points)
		F = moyenne_points(points_F)

		points_R = edge_midpoints_touching_P(i, edges, verts)
		R = moyenne_points(points_R)

		n = len(points_R) # n : le nombre d'arête associées au sommet

		new_vertex_point = [(F[i] + 2*R[i] + (n-3)*P[i]) / n for i in range(3)] # Le barycentre de P, F et R de poids respectifs : (n-3), 2 et 1
		res.append(new_vertex_point)
	return res
	
def face_points_touching_P(P, faces:list, face_points:list) -> list:
	"""renvoie la liste des points centraux de toutes les faces associées au point d'indice P'"""
	res = []
	for i in range(len(faces)):		
		if P in faces[i]:
			res.append(face_points[i])
	return res			
	
def edge_midpoints_touching_P(P, edges:dict, verts) -> list:
	"""renvoie la liste des points centraux de toutes les arêtes associées au point d'indice P'"""
	res = []
	for edge in edges.keys():
		if P in edge:
			res.append((verts[edge[0]] + verts[edge[1]]) / 2)
	return res


# /!\ pas fonctionnel
def new_faces(new_verts:list, faces:list, face_points:list, edges:dict, edge_points:list):
	res = []
	for i in range(len(faces)):
		for j in range(len(faces[i])):
			point1 = i # point central de la face
			point2 = len(face_points) + indice_edge((j, (j-1) % len(faces[i])), list(edges.keys())) # point d'arête gauche
			point3 = len(face_points) + len(edge_points) + faces[i][j] # new_vertex_point
			point4 = len(face_points) + indice_edge((j, (j+1) % len(faces[i])), list(edges.keys())) # point d'arête droite
			res.append([point1, point2, point3, point4])	
	return res

# /!\ pas fonctionnel
def subdivision(verts, faces:list):
	f_points = face_points(faces, verts)
	edges_dict = edges(faces)
	e_points = edge_points(edges_dict, f_points, verts)
	n_vertex_points = new_vertex_points(verts, faces, f_points, edges_dict)

	res1 = f_points + e_points + n_vertex_points # new verts
	res2 = new_faces(res1, faces, f_points, edges_dict, e_points) # new faces
	return (res1, res2)


def moyenne_points(points:list) -> list:
	"""fait la moyenne des points mis dans la liste "points" """	
	somme_x = 0
	somme_y = 0
	somme_z = 0
	for point in points:
		somme_x += point[0]
		somme_y += point[1]
		somme_z += point[2]
	return [somme_x / len(points), somme_y / len(points), somme_z / len(points)]



def indice_edge(edge:tuple, edges:list) -> int:
	"""fait une recherche linéaire pour trouver l'indice de l'arête désirée"""
	i = 0
	termine = False
	indice = -1
	while i < len(edges) and not termine:
		if edges[i] == edge or edges[i] == (edge[1],edge[0]):
			indice = i
			termine == True
		i += 1
	return indice

