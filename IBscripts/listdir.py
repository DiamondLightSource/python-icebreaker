import sys 
import os
import mrcfile
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from scipy import ndimage,misc
import filter_designer as fd
import filter_designer_not_normalized as fdnn
import window_mean as wm
import show_gradient as sg
import local_mask as lm
import KNN_segmenter as KNN_seg
import average_mask as am
import original_mask as om

x_patches = 40
y_patches = 40
num_of_segments = 16

cc = 0
def load_img (img_path):
	with mrcfile.open(img_path,'r',permissive=True) as mrc:
		img = mrc.data
		#plt.imshow(img, cmap='gray')
		#plt.show()
		return img

outdir = 'icegroups/'
#define image path, number of patches, num of regions

filelist =[]
outputs =[]
dir = sys.argv[1]
path1 = dir+outdir
try:
    os.mkdir(path1)
except OSError:
    print ("Creation of the directory %s failed" % path1)
else:
    print ("Successfully created the directory %s " % path1)

for filename in os.listdir(dir):
	#if filename.endswith(".mrc"): #or filename.endswith(".py"):
	if (filename.endswith(".mrc")):
		filelist.append(filename)
		print(filelist)	
	#outputs.append(str(filename[:-4]) +'_'+str(x_patches)+'_'+str(y_patches)+'_'+str(num_of_segments)+'.mrc')
	else:
		continue

for filename in filelist:
	img = load_img(dir+filename)
	print(path1+filename)
with mrcfile.new((path1+str(filename[:-4]) +'_'+str(x_patches)+'x'+str(y_patches)+'x'+str(num_of_segments)+'_original_mean'+'.mrc'), overwrite=True) as out_image:
	print(filename)
	out_image.set_data(img)

