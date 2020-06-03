"""
Jython script to reslice a 3D stack in any arbitrary plane, as defined by 3 user-selected
points.

Requirements
------------
>= ImageJ 1.52r
ThreePointChoice.ijm
TransformJ 
	(If not already under Plugins, add to Fiji by checking the ImageScience update site. 
	Help > Update ..., then click "Manage update sites" and add ImageScience. 
	Restart ImageJ for changes to take effect.)

How it works:
1. The unit vector normal to the plane is calculated from the three points
2. Angle between the defined plane to xz- and yz-planes is calculated
3. Rotation required to orient the stack to the plane is calculated
4. TransformJ is called to rotate the stack orientation to match the defined plane.

Maintained by: Elaine Ho (@elainehoml on Github)
Created: 03 June 2020
Last Updated: 03 June 2020
"""

#@ UpdateService updateService
if not updateService.getUpdateSite("ImageScience").isActive():
	print "Please activate the ImageScience update site. (Help > Update ... Manage update sites)"

import os, sys, math
from ij import IJ
from ij.plugin.frame import RoiManager

imp = IJ.getImage()

def run_macro(script_dir, script_fname):
	""" Run any IJ macro

	Parameters
	----------
	script_dir : str
		Directory of script to run
	script_fname : str
		Name of script to run

	"""
	IJ.runMacroFile(os.path.join(script_dir, script_fname))

def read_xyz_from_RoiManager():
	""" Reads x,y,z coordinates from 3 points in RoiManager

	Parameters
	----------
	None

	Returns
	-------
	P0, P1, P2 : array-like, shape=(3,)
		x,y,z coordinates of points P0, P1 and P2.

	"""
	points = []
	RoiM = RoiManager.getInstance()
	for i in range(RoiM.getCount()):
		roi = RoiM.getRoi(i)
		x = roi.getContainedPoints()[0].getX()
		y = roi.getContainedPoints()[0].getY()
		z = roi.getPosition()
		points.append([x,y,z])
	P0 = points[0]
	P1 = points[1]
	P2 = points[2]
	return P0, P1, P2

def calc_cross_product(A, B):
	""" Calculates cross product of two 3-D vectors A and B

	Parameters
	----------
	A, B : array-like, shape=(3,)
		Vectors to cross

	Returns
	-------
	array-like, shape=(3,)
		Cross product A x B
	
	"""
	C = [A[1]*B[2] - A[2]*B[1], A[2]*B[0] - A[0]*B[2], A[0]*B[1] - A[1]*B[0]]
	return C

def calc_sqrt_sum_squared(A):
	""" Calculates square root of sum of squares

	Parameters
	----------
	A : array-like, shape=(3,)
		Values to calculate square root of sum of squares of

	Returns
	-------
	float
		sqrt(sum of squares)

	"""
	sqrt_sum_squared = (A[0]**2 + A[1]**2 + A[2]**2) ** 0.5
	return sqrt_sum_squared

def calc_unit_vector_plane_normal(P0, P1, P2):
	""" Calculates unit vector plane normal for given coordinates
	Plane normal is determined by calculating cross product of vectors between
	the three points (here we use vector between P0 and P1 and P0 and P2)
	The unit vector of this plane normal is returned.
	
	Parameters
	----------
	P0, P1, P2 : array-like, shape=(3,)
	    (x,y,z) coordinates of P0, P1, P2
	
	Returns
	-------
	array-like, shape=(3,)
	    Unit vector normal to plane
	    
	"""
	vector_01 = map(lambda a, b : a - b, P1, P0) # vector between P0 and P1 (P1-P0)
	vector_02 = map(lambda a, b : a - b, P2, P0) # vector between P0 and P2 (P2-P0)
	plane_normal = calc_cross_product(vector_01, vector_02)
	sqrt_sum_squared = calc_sqrt_sum_squared(plane_normal)
	unit_vector_plane_normal = map(lambda a : a/sqrt_sum_squared, plane_normal)
	return unit_vector_plane_normal

def calc_angle(unit_vector_plane_normal):
	"""
	Calculate angle between unit_vector_plane_normal and x-z or y-z plane
	Angle theta between vectors A and B:
	    cos(theta) = A.B/|A||B|
	Angle to rotate the plane_normal by to align with the xz or yz plane is
	    sin(theta) = A.B/|A||B|
	
	Parameters
	----------
	unit_vector_plane_normal : array-like, shape=(3,)
	    3-D unit vector normal to histology plane, output from calculate_plane
	
	Returns
	-------
	xz_angle : float
	    Angle to align plane_normal with xz plane in degrees.
	yz_angle : float
	    Angle to align plane_normal with yz plane in degrees.
	
	"""
	# setup coefficient variables
	a = unit_vector_plane_normal[0]
	b = unit_vector_plane_normal[1]
	c = unit_vector_plane_normal[2]
	
	xz_angle = math.degrees(math.asin(b/calc_sqrt_sum_squared(unit_vector_plane_normal)))
	yz_angle = math.degrees(math.asin(a/calc_sqrt_sum_squared(unit_vector_plane_normal)))

	return xz_angle, yz_angle

def get_sign(x):
	""" Returns -1 if x is negative, +1 if x is positive or 0. """
	if x < 0:
		out = -1
	if x >= 0:
		out = 1
	return out

def get_rot_angle(unit_vector_plane_normal, xz_angle, yz_angle):
	"""
	Calculate rotation angles for use in TransformJ
	In general, rotation about y-axis is +ve (rot_yz) when x and z components
	of the unit vector plane normal have opposite signs, and vice versa.
	Rotation about x-axis is +ve (rot_xz) when y and z components of the unit
	vector plane normal have the same signs.
	
	Parameters
	----------
	unit_vector_plane_normal : array-like, shape=(3,)
	    x,y,z components of unit vector normal to histology plane.
	xz_angle : float
	    angle between xz-plane and histology plane in degrees.
	yz_angle : float
	    angle between yz-plane and histology plane in degrees.
	
	Returns
	-------
	rot_x : float
	    angle to rotate around the x-axis by in TransformJ.
	rot_y : float
	    angle to rotate around the y-axis by in TransformJ.
	
	"""
	x_sign = get_sign(unit_vector_plane_normal[0])
	y_sign = get_sign(unit_vector_plane_normal[1])
	z_sign = get_sign(unit_vector_plane_normal[2])

	# do x and z have different signs?
	if x_sign != z_sign: # x and z have different signs
		if yz_angle >= 0:
			rot_y = yz_angle # rot_y is positive
		elif yz_angle < 0:
			rot_y = - yz_angle
	elif x_sign == z_sign: # x and z have same signs
		if yz_angle >= 0:
			rot_y = - yz_angle # rot_y is negative
		elif yz_angle < 0:
			rot_y = yz_angle

	# do y and z have different signs?
	if y_sign == z_sign: # y and z have same signs
		if xz_angle >= 0:
			rot_x = xz_angle # rot_x is positive
		elif xz_angle < 0:
			rot_x = - xz_angle
	elif y_sign != z_sign: # y and z have different signs
		if xz_angle >= 0:
			rot_x = - xz_angle # rot_x is negative
		elif xz_angle < 0:
			rot_x = xz_angle

	IJ.log("Rotating by {:.2f} deg about y and {:.2f} deg about x".format(rot_y, rot_x))

	return rot_x, rot_y
	
# Main
script_dir = os.path.dirname(sys.argv[0])
IJM_fname = "ThreePointChoice.ijm"
run_macro(script_dir, IJM_fname)
P0, P1, P2 = read_xyz_from_RoiManager()
unit_vector_plane_normal = calc_unit_vector_plane_normal(P0, P1, P2)
xz_angle, yz_angle = calc_angle(unit_vector_plane_normal)
rot_x, rot_y = get_rot_angle(unit_vector_plane_normal, xz_angle, yz_angle)
IJ.run("TransformJ Rotate", "z-angle=0.0 y-angle=" + str(rot_y) + " x-angle=" + str(rot_x) + " interpolation=[Quintic B-Spline] background=0.0 adjust");
