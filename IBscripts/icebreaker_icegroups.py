import sys
import mrcfile
import cv2
import numpy as np
import os

import filter_designer as fd
import window_mean as wm
import KNN_segmenter as KNN_seg
import original_mask as om

cc = 0
def load_img (img_path):
	with mrcfile.open(img_path,'r',permissive=True) as mrc:
		img = mrc.data
		return img

filelist =[]
outputs =[]
indir = sys.argv[1]
outdir = 'icegroups/'
path1 = indir+outdir
try:
	os.mkdir(path1)
except OSError: 
	print ("Creation of the directory %s failed" % path1)
else:
	print ("Successfully created the directory %s " % path1)

for filename in os.listdir(indir):
	if (filename.endswith(".mrc")):
		filelist.append(filename)
	else:
		continue

for filename in filelist:
	img = load_img(indir+filename)
	x_patches = 40
	y_patches = 40
	num_of_segments=16

	filter_mask = fd.lowpass(img,0.85,20,'cos',50)
	lowpass,mag = fd.filtering(img, filter_mask)
	lowpass = cv2.GaussianBlur(lowpass, (45,45),0)
	lowpass12=img
	rolled = wm.window(lowpass, x_patches,y_patches)
	rolled_resized = cv2.resize(rolled,(185,190),interpolation=cv2.INTER_AREA)
	rolled_resized = cv2.GaussianBlur(rolled_resized, (5,5),0)
	KNNsegmented = KNN_seg.segmenter(rolled_resized, num_of_segments)
	upscaled_region = cv2.resize(KNNsegmented, (lowpass.shape[1],lowpass.shape[0]),interpolation=cv2.INTER_AREA)

	regions_vals = np.unique(KNNsegmented)
	averaged_loc = np.zeros((lowpass.shape[0],lowpass.shape[1],num_of_segments),np.float32)
	res = np.zeros((lowpass.shape[0],lowpass.shape[1]),np.float32)
	for i in range (len(regions_vals)):
		averaged_loc[:,:,i] = om.original_mask(lowpass,KNNsegmented,regions_vals[i],img,lowpass12)
		res[:,:] += averaged_loc[:,:,i]

	final_image = ndimage.median_filter(res, size=10)	
	
	with mrcfile.new((path1+str(filename[:-4]) +'_'+str(x_patches)+'x'+str(y_patches)+'x'+str(num_of_segments)+'_original_mean'+'.mrc'), overwrite=True) as out_image:
		out_image.set_data(final_image)

	cc += 1
	print(str(cc) + '/' + str(len(filelist)))
