/*
* This script reslices a 3D stack to in an arbitrary plane defined by three user-selected
* points.
*
* How it works:
* 1. The unit vector normal to the plane is calculated from the three points
* 2. Angle between the defined plane to xz- and yz-planes is calculated
* 3. Rotation required to orient the stack to the plane is calculated
* 4. TransformJ is called to rotate the stack orientation to match the defined plane.
*
* Maintained by: Elaine Ho (@elainehoml on Github)
* Created: 03 June 2020
* Last Updated: 03 June 2020
*
*/

requires("1.52r");
print("\\Clear");

function choose_points() {
	// Choose 3 points in the current image, return its coordinates as an array

	// Tell user to choose points
	roiManager("reset");
	setTool("point");
	Dialog.createNonBlocking("Choose three points to define plane");
	Dialog.addMessage("Choose 3 points in the 3D stack that matches any point in the 2D image. Add the points to ROI manager and select OK when complete");
	Dialog.show();

	// Get ROI coordinates
	n_points = roiManager("count");
	if (n_points != 3) {
		exit("Please select 3 points, only " + n_points + " selected.");
	}
	for (point=0; point<n_points; point++) {
		roiManager("select", point);
		Roi.getCoordinates(x,y);
		Roi.getPosition(c,z,f);
		print("P" + point + " coords are (" + x[0] + "," + y[0] + "," + z + ")");
	}
}

choose_points();
