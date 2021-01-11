#@ File (label="Select image to patch", style="file") img_filename
#@ Integer (label="Number of patches in x", value=20) x_patches
#@ Integer (label="Number of patches in y", value=20) y_patches
#@ File (label="Select output directory", style="directory") output_directory

setBatchMode(true);
open(img_filename);
getPixelSize(unit, pixelWidth, pixelHeight);
width = getWidth();
height = getHeight();
x_size = Math.floor(width / x_patches);
y_size = Math.floor(height / y_patches);

IJ.log("Patch size = " + x_size + "x" + y_size + " pixels or " + x_size*pixelWidth + "x" + y_size*pixelHeight + " " + unit);
IJ.log("Number of patches in x = " + x_patches);
IJ.log("Number of patches in y = " + y_patches);
IJ.log("Total number of patches = " + x_patches * y_patches);

current_x = 0;
current_y = 0;

for (i=0; i<x_patches; i++) {
	for (j=0; j<y_patches; j++) {
		makeRectangle(current_x, current_y, x_size, y_size);
		run("Duplicate...", " ");
		current_patch += 1;
		if (current_patch < 10) {
			current_patch_str = "000" + toString(current_patch);
		}
		else if (current_patch < 100) {
			current_patch_str = "00" + toString(current_patch);
		}
		else if (current_patch < 1000) {
			current_patch_str = "0" + toString(current_patch);
		}
		else {
			current_patch_str = toString(current_patch);
		}
		
		patch_filepath = output_directory + "/" + File.getNameWithoutExtension(img_filename) + "_Patch" + current_patch_str + ".tif";
		saveAs("tiff", patch_filepath);
		IJ.log("Patch " + current_patch_str + " saved as " + patch_filepath);
		close();
		current_x += x_size;
	}
	current_y += y_size;
	current_x = 0; // reset
}

saveAs("Text", output_directory + "/" + File.getNameWithoutExtension(img_filename) + "_patches-log.txt");
run("Close");
