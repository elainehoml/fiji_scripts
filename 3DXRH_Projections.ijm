// Create and save z-projections for XRH image stacks

// User choice of start and end slices
#@ Integer (label="Starting slice", description="First slice to include in z-projection", min=1) startSlice
#@ Integer (label="Ending slice", description="Last slice to include in z-projection", min=2) endSlice
#@ File (label="Target directory", description="Directory where images will be saved", style="directory") saveDir

// User choice of image to use
img_list = getList("image.titles");
Dialog.create("Create z-projections");
Dialog.addChoice("Image to use", img_list);
Dialog.show()
img = Dialog.getChoice();

// Generate projections
proj_type = newArray("Average Intensity", "Max Intensity", "Standard Deviation");
proj_name = newArray("AVG_", "MAX_", "STD_");
for (i=0; i<proj_type.length; i++) {
	selectWindow(img);
	run("Z Project...", "start=" + startSlice + " stop=" + endSlice + " projection=[" + proj_type[i] + "]");
	saveAs("Tiff", saveDir + "\\" + proj_name[i] + "Slice" + startSlice + "-" + endSlice + "_" + img);
	print("Saved " + proj_type[i] + " projection for " + img);
}
