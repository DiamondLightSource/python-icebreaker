import cv2
import numpy as np

def segmenter (img_to_segment, num_of_segments):
	rolled_resizedZ = img_to_segment.copy()
	Z = rolled_resizedZ.reshape((-1,1))
	Z = np.float32(Z)
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 20.0)
	K = num_of_segments
	ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

	# Now convert back into uint8, and make original image
	center = np.uint8(center)
	res = center[label.flatten()]
	res2 = res.reshape((rolled_resizedZ.shape))
	ret,thresh1 = cv2.threshold(rolled_resizedZ,90,255,cv2.THRESH_BINARY)

	return res2
