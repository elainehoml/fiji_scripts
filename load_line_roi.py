from ij import IJ
from ij.plugin.frame import RoiManager

RM = RoiManager()
rm = RM.getRoiManager()

with open("C:/Users/emlh1n13/Downloads/Coronary Sinus/Case2_View2_F15/ROIs.csv", "r") as roiFile:
	next(roiFile) # skip header
	for line in roiFile:
		elements = line.rstrip().split(',')
		x, y, w, h = elements[4], elements[5], elements[6], elements[7]
		x1 = int(x)
		y1 = int(y)
		x2 = x1 + int(w)
		y2 = y1 + int(h)	
		roi = IJ.makeLine(x1, y1, x2, y2)
		rm.addRoi(roi)
		